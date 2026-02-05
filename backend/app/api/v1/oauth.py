"""
OAuth账号管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
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
from app.models.platform_config import PlatformConfig
from app.services.oauth.adapters import get_supported_platforms, get_adapter

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
    授权OAuth账号
    
    这个接口会启动浏览器授权流程
    """
    print(f"收到OAuth授权请求: platform={data.platform}, account_name={data.account_name}")
    print(f"当前用户ID: {current_user.id}")
    
    try:
        account = await oauth_service.authorize_account(
            db=db,
            user_id=current_user.id,
            platform=data.platform,
            account_name=data.account_name,
        )
        
        return account
        
    except Exception as e:
        print(f"OAuth授权失败: {str(e)}")
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
    
    return accounts


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
    
    return account


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
