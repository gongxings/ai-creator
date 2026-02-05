"""
OAuth账号管理API
"""
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.schemas.oauth import (
    OAuthAccountCreate,
    OAuthAccountManualCreate,
    OAuthAccountAuthorize,
    OAuthAccountResponse,
    OAuthAccountUpdate,
    OAuthUsageLogResponse,
    PlatformConfigResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from app.services.oauth.oauth_service import oauth_service
from app.services.oauth.litellm_proxy import litellm_proxy
from app.services.oauth.oauth_session import oauth_session_manager
from app.models.platform_config import PlatformConfig
from app.services.oauth.adapters import get_supported_platforms, get_adapter, PLATFORM_ADAPTERS

router = APIRouter(tags=["OAuth"])


@router.get("/platforms", response_model=List[PlatformConfigResponse])
async def get_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取支持的平台列表
    """
    platforms = db.query(PlatformConfig).filter(
        PlatformConfig.is_enabled == True
    ).all()
    result = []
    for platform in platforms:
        adapter = get_adapter(platform.platform_id, {
            "oauth_config": platform.oauth_config,
            "litellm_config": platform.litellm_config,
            "quota_config": platform.quota_config,
        })
        oauth_meta = adapter.get_platform_config() if adapter else None

        data = PlatformConfigResponse.from_orm(platform).dict()
        data["oauth_meta"] = oauth_meta
        result.append(data)

    return result


@router.post("/accounts/authorize", response_model=OAuthAccountResponse)
async def authorize_account(
    data: OAuthAccountAuthorize,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    授权OAuth账号（一次性授权）

    这个接口会启动浏览器授权流程
    在 Windows 上会打开非 headless 浏览器窗口，用户需要手动登录
    """
    print(f"收到OAuth授权请求: platform={data.platform}, account_name={data.account_name}")
    print(f"当前用户ID: {current_user.id}")
    print(f"浏览器模式: {'非 headless 模式（可见）' if os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'false' else 'headless 模式'}")

    try:
        account = await oauth_service.authorize_account(
            db=db,
            user_id=current_user.id,
            platform=data.platform,
            account_name=data.account_name,
        )

        # 获取平台配置信息
        account_dict = OAuthAccountResponse.from_orm(account).dict()
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == account.platform
        ).first()
        if platform_config:
            account_dict["platform_name"] = platform_config.platform_name
            account_dict["platform_icon"] = platform_config.platform_icon

        return account_dict

    except Exception as e:
        print(f"OAuth授权失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/authorize/start")
async def authorize_start(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    开始OAuth授权（分步授权流程）
    
    1. 打开浏览器并导航到登录页
    2. 点击登录按钮
    3. 返回会话ID
    """
    # 获取平台配置
    platform_config = db.query(PlatformConfig).filter(
        PlatformConfig.platform_id == platform
    ).first()
    
    if not platform_config:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
    
    if not platform_config.is_enabled:
        raise HTTPException(status_code=400, detail=f"Platform {platform} is disabled")
    
    # 获取适配器
    adapter_class = PLATFORM_ADAPTERS.get(platform)
    if not adapter_class:
        raise HTTPException(status_code=404, detail=f"Adapter for platform {platform} not found")
    
    adapter = adapter_class(platform, {
        "oauth_config": platform_config.oauth_config,
        "litellm_config": platform_config.litellm_config,
        "quota_config": platform_config.quota_config,
    })
    
    # 构建平台配置
    playwright_config = adapter.get_platform_config()
    
    # 创建授权会话
    session = await oauth_session_manager.create_session(
        user_id=current_user.id,
        platform=platform,
        platform_config=playwright_config,
    )
    
    return {
        "session_id": f"{current_user.id}:{platform}",
        "message": "授权会话已创建，请调用 /authorize/qr 获取二维码",
    }


@router.get("/authorize/qr")
async def authorize_get_qr(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取登录二维码
    
    返回base64编码的二维码图片
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 获取二维码
    qr_code = await session.get_qr_code()
    
    if qr_code:
        return {
            "qr_code": qr_code,
            "format": "base64",
            "message": "二维码获取成功，请扫码登录"
        }
    else:
        return {
            "qr_code": None,
            "message": "未找到二维码元素，可能需要账号密码登录"
        }


@router.get("/authorize/status")
async def authorize_check_status(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """
    检查登录状态
    
    轮询此接口检查是否已登录
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 检查登录状态
    is_logged_in = await session.check_login_status()
    
    return {
        "logged_in": is_logged_in,
        "message": "已登录，可以完成授权" if is_logged_in else "等待扫码登录..."
    }


@router.post("/authorize/complete", response_model=OAuthAccountResponse)
async def authorize_complete(
    platform: str,
    account_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    完成OAuth授权
    
    提取登录凭证并保存到数据库
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 检查是否已登录
    if not session.is_logged_in:
        raise HTTPException(status_code=400, detail="尚未登录，请先扫码登录")
    
    try:
        # 提取凭证
        credentials = await session.extract_credentials()
        
        # 验证凭证
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == platform
        ).first()
        
        if not platform_config:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
        
        adapter_class = PLATFORM_ADAPTERS.get(platform)
        if not adapter_class:
            raise HTTPException(status_code=404, detail=f"Adapter for platform {platform} not found")
        
        adapter = adapter_class(platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })
        
        if not adapter.validate_credentials(credentials):
            raise HTTPException(status_code=400, detail="凭证验证失败")
        
        # 加密凭证
        from app.services.oauth.encryption import encrypt_credentials
        encrypted_credentials = encrypt_credentials(credentials)
        
        # 检查是否已存在账号
        from sqlalchemy import and_
        from app.models.oauth_account import OAuthAccount
        existing_account = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.platform == platform
            )
        ).first()
        
        if existing_account:
            # 更新现有账号
            existing_account.credentials = encrypted_credentials
            existing_account.account_name = account_name or existing_account.account_name
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_account)
            
            # 关闭会话
            await oauth_session_manager.remove_session(current_user.id, platform)
            
            return existing_account
        
        # 创建新账号
        quota_limit = adapter.get_quota_limit()
        
        from datetime import datetime
        account = OAuthAccount(
            user_id=current_user.id,
            platform=platform,
            account_name=account_name or f"{platform}_account",
            credentials=encrypted_credentials,
            is_active=True,
            is_expired=False,
            quota_used=0,
            quota_limit=quota_limit,
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        # 关闭会话
        await oauth_session_manager.remove_session(current_user.id, platform)
        
        return account
        
    except Exception as e:
        print(f"OAuth授权完成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts/manual", response_model=OAuthAccountResponse)
async def create_account_manual(
    data: OAuthAccountManualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manual cookie submit for OAuth account
    """
    try:
        credentials = {
            "cookies": data.cookies,
            "tokens": data.tokens or {},
            "user_agent": data.user_agent or "",
        }
        account = oauth_service.create_or_update_account_with_credentials(
            db=db,
            user_id=current_user.id,
            platform=data.platform,
            account_name=data.account_name,
            credentials=credentials,
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts", response_model=List[OAuthAccountResponse])
async def get_accounts(
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户的OAuth账号列表
    """
    accounts = oauth_service.get_user_accounts(
        db=db,
        user_id=current_user.id,
        platform=platform,
        is_active=is_active,
    )

    result = []
    for account in accounts:
        account_dict = OAuthAccountResponse.from_orm(account).dict()
        # 获取平台配置信息
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == account.platform
        ).first()
        if platform_config:
            account_dict["platform_name"] = platform_config.platform_name
            account_dict["platform_icon"] = platform_config.platform_icon
        result.append(account_dict)

    return result


@router.get("/accounts/{account_id}", response_model=OAuthAccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取OAuth账号详情
    """
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account_dict = OAuthAccountResponse.from_orm(account).dict()
    # 获取平台配置信息
    platform_config = db.query(PlatformConfig).filter(
        PlatformConfig.platform_id == account.platform
    ).first()
    if platform_config:
        account_dict["platform_name"] = platform_config.platform_name
        account_dict["platform_icon"] = platform_config.platform_icon

    return account_dict


@router.put("/accounts/{account_id}", response_model=OAuthAccountResponse)
async def update_account(
    account_id: int,
    data: OAuthAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新OAuth账号
    """
    try:
        account = oauth_service.update_account(
            db=db,
            account_id=account_id,
            user_id=current_user.id,
            **data.dict(exclude_unset=True),
        )
        
        return account
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除OAuth账号
    """
    success = oauth_service.delete_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Account deleted successfully"}


@router.post("/accounts/{account_id}/check")
async def check_account_validity(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    检查账号凭证是否有效
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    is_valid = await oauth_service.check_account_validity(
        db=db,
        account_id=account_id,
    )
    
    return {
        "is_valid": is_valid,
        "message": "Account is valid" if is_valid else "Account credentials expired"
    }


@router.get("/accounts/{account_id}/usage", response_model=List[OAuthUsageLogResponse])
async def get_usage_logs(
    account_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取账号使用日志
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    logs = oauth_service.get_usage_logs(
        db=db,
        account_id=account_id,
        limit=limit,
    )
    
    return logs


@router.get("/accounts/{account_id}/models")
async def get_available_models(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取账号可用的模型列表
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    models = litellm_proxy.get_available_models(
        db=db,
        account_id=account_id,
    )
    
    return {"models": models}


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    data: ChatCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    执行聊天完成（使用OAuth账号）
    
    这个接口使用用户绑定的OAuth账号调用AI模型
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=data.account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        response = await litellm_proxy.chat_completion(
            db=db,
            account_id=data.account_id,
            messages=data.messages,
            model=data.model,
            stream=data.stream,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            top_p=data.top_p,
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
