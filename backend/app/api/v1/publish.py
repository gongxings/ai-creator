"""
发布管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.models.publish import PlatformAccount, PublishRecord
from app.schemas.publish import (
    PlatformInfo,
    PlatformLoginInfo,
    PlatformAccountCreate,
    PlatformAccountUpdate,
    PlatformAccountResponse,
    CookieUpdateRequest,
    CookieValidationResponse,
    PublishCreate,
    PublishRecordResponse,
    PublishStatusResponse
)
from app.services.publish.platforms import get_platform, PLATFORM_REGISTRY

router = APIRouter()


@router.get("/platforms", response_model=List[PlatformInfo])
async def get_platforms():
    """获取支持的平台列表"""
    platforms = []
    for name, publisher_class in PLATFORM_REGISTRY.items():
        publisher = publisher_class()
        platforms.append(PlatformInfo(
            platform=name,
            name=publisher.get_platform_name(),
            login_url=publisher.get_login_url(),
            supported_types=publisher.supported_types
        ))
    return platforms


@router.get("/platforms/{platform}/login-info", response_model=PlatformLoginInfo)
async def get_platform_login_info(platform: str):
    """获取平台登录信息"""
    try:
        publisher = get_platform(platform)
        return PlatformLoginInfo(
            platform=platform,
            name=publisher.get_platform_name(),
            login_url=publisher.get_login_url(),
            instructions=f"请在浏览器中登录{publisher.get_platform_name()}，然后返回此页面更新Cookie"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/platforms/accounts", response_model=PlatformAccountResponse)
async def create_platform_account(
    account_data: PlatformAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建平台账号"""
    # 检查是否已存在
    existing = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.platform == account_data.platform,
        PlatformAccount.account_name == account_data.account_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该平台账号已存在"
        )
    
    # 创建账号
    account = PlatformAccount(
        user_id=current_user.id,
        platform=account_data.platform,
        account_name=account_data.account_name,
        cookies_valid="unknown"
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return PlatformAccountResponse(
        id=account.id,
        platform=account.platform,
        account_name=account.account_name,
        cookies_valid=account.cookies_valid,
        cookies_updated_at=account.cookies_updated_at,
        is_active=account.is_active,
        created_at=account.created_at
    )


@router.get("/platforms/accounts", response_model=List[PlatformAccountResponse])
async def get_platform_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的平台账号列表"""
    accounts = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id
    ).all()
    
    return [
        PlatformAccountResponse(
            id=account.id,
            platform=account.platform,
            account_name=account.account_name,
            cookies_valid=account.cookies_valid,
            cookies_updated_at=account.cookies_updated_at,
            is_active=account.is_active,
            created_at=account.created_at
        )
        for account in accounts
    ]


@router.put("/platforms/accounts/{account_id}", response_model=PlatformAccountResponse)
async def update_platform_account(
    account_id: int,
    account_data: PlatformAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    if account_data.account_name is not None:
        account.account_name = account_data.account_name
    if account_data.is_active is not None:
        account.is_active = account_data.is_active
    
    db.commit()
    db.refresh(account)
    
    return PlatformAccountResponse(
        id=account.id,
        platform=account.platform,
        account_name=account.account_name,
        cookies_valid=account.cookies_valid,
        cookies_updated_at=account.cookies_updated_at,
        is_active=account.is_active,
        created_at=account.created_at
    )


@router.delete("/platforms/accounts/{account_id}")
async def delete_platform_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    db.delete(account)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/platforms/accounts/{account_id}/cookies", response_model=CookieValidationResponse)
async def update_cookies(
    account_id: int,
    cookie_data: CookieUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新平台账号Cookie"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    try:
        # 获取平台发布器
        publisher = get_platform(account.platform)
        
        # 保存Cookie
        publisher.set_cookies(account, cookie_data.cookies, db)
        
        # 验证Cookie
        is_valid = await publisher.validate_cookies(account)
        
        return CookieValidationResponse(
            valid=is_valid,
            message="Cookie验证成功" if is_valid else "Cookie验证失败，请重新登录",
            cookies_updated_at=account.cookies_updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新Cookie失败: {str(e)}"
        )


@router.post("/platforms/accounts/{account_id}/validate", response_model=CookieValidationResponse)
async def validate_cookies(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证平台账号Cookie"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    try:
        publisher = get_platform(account.platform)
        is_valid = await publisher.validate_cookies(account)
        
        return CookieValidationResponse(
            valid=is_valid,
            message="Cookie有效" if is_valid else "Cookie已失效，请重新登录",
            cookies_updated_at=account.cookies_updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证Cookie失败: {str(e)}"
        )


@router.post("/publish", response_model=PublishStatusResponse)
async def publish_content(
    publish_data: PublishCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布内容到平台（创建草稿）"""
    # 获取平台账号
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == publish_data.account_id,
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在或未激活")
    
    try:
        # 获取平台发布器
        publisher = get_platform(account.platform)
        
        # 检查Cookie有效性
        publisher.check_cookies_or_raise(account)
        
        # 创建草稿
        result = await publisher.create_draft(
            account=account,
            content=publish_data.content,
            title=publish_data.title,
            cover_image=publish_data.cover_image,
            images=publish_data.images,
            video_url=publish_data.video_url,
            tags=publish_data.tags,
            location=publish_data.location
        )
        
        # 保存发布历史
        history = PublishRecord(
            user_id=current_user.id,
            account_id=account.id,
            creation_id=publish_data.creation_id,
            platform=account.platform,
            content_type=publish_data.content_type,
            title=publish_data.title,
            status="draft",
            platform_post_id=result.get("draft_id"),
            platform_url=result.get("draft_url")
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return PublishStatusResponse(
            id=history.id,
            platform=history.platform,
            status=history.status,
            platform_post_id=history.platform_post_id,
            platform_url=history.platform_url,
            message=result.get("message", "草稿创建成功"),
            published_at=history.published_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建草稿失败: {str(e)}"
        )


@router.get("/history", response_model=List[PublishRecordResponse])
async def get_publish_history(
    platform: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发布历史"""
    query = db.query(PublishRecord).filter(
        PublishRecord.user_id == current_user.id
    )
    
    if platform:
        query = query.filter(PublishRecord.platform == platform)
    if status:
        query = query.filter(PublishRecord.status == status)
    
    histories = query.order_by(
        PublishRecord.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        PublishRecordResponse(
            id=h.id,
            platform=h.platform,
            account_name=h.account.account_name if h.account else None,
            content_type=h.content_type,
            title=h.title,
            status=h.status,
            platform_post_id=h.platform_post_id,
            platform_url=h.platform_url,
            error_message=h.error_message,
            published_at=h.published_at,
            created_at=h.created_at
        )
        for h in histories
    ]


@router.get("/history/{history_id}", response_model=PublishRecordResponse)
async def get_publish_history_detail(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发布历史详情"""
    history = db.query(PublishRecord).filter(
        PublishRecord.id == history_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="发布历史不存在")
    
    return PublishRecordResponse(
        id=history.id,
        platform=history.platform,
        account_name=history.account.account_name if history.account else None,
        content_type=history.content_type,
        title=history.title,
        status=history.status,
        platform_post_id=history.platform_post_id,
        platform_url=history.platform_url,
        error_message=history.error_message,
        published_at=history.published_at,
        created_at=history.created_at
    )


@router.delete("/history/{history_id}")
async def delete_publish_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除发布历史"""
    history = db.query(PublishRecord).filter(
        PublishRecord.id == history_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="发布历史不存在")
    
    db.delete(history)
    db.commit()
    
    return {"message": "删除成功"}
