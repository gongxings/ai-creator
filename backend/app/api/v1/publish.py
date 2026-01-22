"""
发布管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.publish import PlatformAccount, PublishRecord, PlatformType, PublishStatus
from app.models.creation import Creation
from app.schemas.publish import (
    PlatformAccountCreate,
    PlatformAccountUpdate,
    PlatformAccountResponse,
    PlatformAccountListResponse,
    PublishCreate,
    PublishUpdate,
    PublishRecordResponse,
    PublishRecordListResponse,
    PublishStatusResponse,
    BatchPublishResponse,
    PlatformInfo,
    PlatformListResponse
)
from app.services.publish.publisher_factory import PublisherFactory
from app.core.security import encrypt_data, decrypt_data

router = APIRouter()


# ============ 平台信息相关 ============

@router.get("/platforms", response_model=PlatformListResponse)
async def get_supported_platforms():
    """获取支持的平台列表"""
    platforms = [
        PlatformInfo(
            platform=PlatformType.WECHAT,
            name="微信公众号",
            description="发布文章到微信公众号",
            icon="wechat",
            supported_content_types=["article"],
            max_title_length=64,
            max_content_length=20000,
            supports_scheduling=True,
            auth_type="oauth"
        ),
        PlatformInfo(
            platform=PlatformType.XIAOHONGSHU,
            name="小红书",
            description="发布笔记到小红书",
            icon="xiaohongshu",
            supported_content_types=["note", "image"],
            max_title_length=20,
            max_content_length=1000,
            supports_scheduling=False,
            auth_type="cookie"
        ),
        PlatformInfo(
            platform=PlatformType.DOUYIN,
            name="抖音",
            description="发布视频到抖音",
            icon="douyin",
            supported_content_types=["video"],
            max_title_length=55,
            supports_scheduling=True,
            auth_type="oauth"
        ),
        PlatformInfo(
            platform=PlatformType.KUAISHOU,
            name="快手",
            description="发布视频到快手",
            icon="kuaishou",
            supported_content_types=["video"],
            max_title_length=50,
            supports_scheduling=True,
            auth_type="oauth"
        ),
        PlatformInfo(
            platform=PlatformType.TOUTIAO,
            name="今日头条",
            description="发布文章到今日头条",
            icon="toutiao",
            supported_content_types=["article"],
            max_title_length=30,
            supports_scheduling=True,
            auth_type="oauth"
        ),
        PlatformInfo(
            platform=PlatformType.BAIJIAHAO,
            name="百家号",
            description="发布文章到百家号",
            icon="baijiahao",
            supported_content_types=["article", "video"],
            max_title_length=40,
            supports_scheduling=True,
            auth_type="oauth"
        ),
        PlatformInfo(
            platform=PlatformType.ZHIHU,
            name="知乎",
            description="发布文章到知乎",
            icon="zhihu",
            supported_content_types=["article"],
            max_title_length=100,
            supports_scheduling=False,
            auth_type="cookie"
        ),
        PlatformInfo(
            platform=PlatformType.JIANSHU,
            name="简书",
            description="发布文章到简书",
            icon="jianshu",
            supported_content_types=["article"],
            max_title_length=100,
            supports_scheduling=False,
            auth_type="cookie"
        )
    ]
    
    return PlatformListResponse(platforms=platforms)


# ============ 平台账号管理 ============

@router.post("/platforms/bind", response_model=PlatformAccountResponse, status_code=status.HTTP_201_CREATED)
async def bind_platform_account(
    account_data: PlatformAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """绑定平台账号"""
    # 检查是否已绑定相同平台的账号
    existing = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.platform == account_data.platform,
        PlatformAccount.account_name == account_data.account_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该平台账号已绑定"
        )
    
    # 加密敏感信息
    encrypted_access_token = None
    encrypted_refresh_token = None
    encrypted_credentials = None
    
    if account_data.access_token:
        encrypted_access_token = encrypt_data(account_data.access_token)
    if account_data.refresh_token:
        encrypted_refresh_token = encrypt_data(account_data.refresh_token)
    if account_data.credentials:
        encrypted_credentials = account_data.credentials
    
    # 创建平台账号
    platform_account = PlatformAccount(
        user_id=current_user.id,
        platform=account_data.platform,
        account_name=account_data.account_name,
        account_id=account_data.account_id,
        access_token=encrypted_access_token,
        refresh_token=encrypted_refresh_token,
        expires_at=account_data.expires_at,
        credentials=encrypted_credentials,
        config=account_data.config or {}
    )
    
    db.add(platform_account)
    db.commit()
    db.refresh(platform_account)
    
    return platform_account


@router.get("/platforms/accounts", response_model=PlatformAccountListResponse)
async def get_platform_accounts(
    platform: Optional[PlatformType] = Query(None),
    is_active: Optional[str] = Query(None, pattern="^(active|inactive)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的平台账号列表"""
    query = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id
    )
    
    if platform:
        query = query.filter(PlatformAccount.platform == platform)
    if is_active:
        query = query.filter(PlatformAccount.is_active == is_active)
    
    accounts = query.order_by(PlatformAccount.created_at.desc()).all()
    
    return PlatformAccountListResponse(
        total=len(accounts),
        items=accounts
    )


@router.get("/platforms/accounts/{account_id}", response_model=PlatformAccountResponse)
async def get_platform_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取平台账号详情"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="平台账号不存在"
        )
    
    return account


@router.put("/platforms/accounts/{account_id}", response_model=PlatformAccountResponse)
async def update_platform_account(
    account_id: int,
    account_data: PlatformAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="平台账号不存在"
        )
    
    # 更新字段
    update_data = account_data.dict(exclude_unset=True)
    
    # 加密敏感信息
    if "access_token" in update_data and update_data["access_token"]:
        update_data["access_token"] = encrypt_data(update_data["access_token"])
    if "refresh_token" in update_data and update_data["refresh_token"]:
        update_data["refresh_token"] = encrypt_data(update_data["refresh_token"])
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/platforms/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="平台账号不存在"
        )
    
    db.delete(account)
    db.commit()


# ============ 发布管理 ============

@router.post("", response_model=BatchPublishResponse, status_code=status.HTTP_201_CREATED)
async def publish_content(
    publish_data: PublishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发布内容到多个平台"""
    # 验证创作是否存在
    creation = db.query(Creation).filter(
        Creation.id == publish_data.creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在"
        )
    
    # 验证平台账号
    platform_accounts = db.query(PlatformAccount).filter(
        PlatformAccount.id.in_(publish_data.platform_account_ids),
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.is_active == "active"
    ).all()
    
    if len(platform_accounts) != len(publish_data.platform_account_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分平台账号不存在或未激活"
        )
    
    # 创建发布记录
    records = []
    success_count = 0
    failed_count = 0
    
    for account in platform_accounts:
        # 准备发布内容
        title = publish_data.title or creation.title
        content = publish_data.content or creation.content
        
        # 创建发布记录
        record = PublishRecord(
            user_id=current_user.id,
            creation_id=creation.id,
            platform_account_id=account.id,
            platform=account.platform,
            status=PublishStatus.SCHEDULED if publish_data.scheduled_at else PublishStatus.PENDING,
            title=title,
            content=content,
            cover_image=publish_data.cover_image,
            media_urls=publish_data.media_urls,
            tags=publish_data.tags,
            scheduled_at=publish_data.scheduled_at
        )
        
        db.add(record)
        db.flush()
        
        # 如果不是定时发布，立即发布
        if not publish_data.scheduled_at:
            try:
                # 获取发布器
                publisher = PublisherFactory.get_publisher(account.platform)
                
                # 解密认证信息
                access_token = decrypt_data(account.access_token) if account.access_token else None
                
                # 发布内容
                record.status = PublishStatus.PUBLISHING
                db.commit()
                
                result = await publisher.publish(
                    title=title,
                    content=content,
                    cover_image=publish_data.cover_image,
                    media_urls=publish_data.media_urls,
                    tags=publish_data.tags,
                    access_token=access_token,
                    credentials=account.credentials
                )
                
                # 更新发布记录
                record.status = PublishStatus.SUCCESS
                record.platform_post_id = result.get("post_id")
                record.platform_url = result.get("url")
                record.platform_response = result
                record.published_at = datetime.utcnow()
                success_count += 1
                
            except Exception as e:
                record.status = PublishStatus.FAILED
                record.error_message = str(e)
                failed_count += 1
            
            db.commit()
        
        db.refresh(record)
        records.append(record)
    
    db.commit()
    
    return BatchPublishResponse(
        success_count=success_count,
        failed_count=failed_count,
        records=records
    )


@router.get("/history", response_model=PublishRecordListResponse)
async def get_publish_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[PlatformType] = Query(None),
    status: Optional[PublishStatus] = Query(None),
    creation_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取发布历史"""
    query = db.query(PublishRecord).filter(
        PublishRecord.user_id == current_user.id
    )
    
    if platform:
        query = query.filter(PublishRecord.platform == platform)
    if status:
        query = query.filter(PublishRecord.status == status)
    if creation_id:
        query = query.filter(PublishRecord.creation_id == creation_id)
    
    total = query.count()
    records = query.order_by(PublishRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return PublishRecordListResponse(
        total=total,
        items=records
    )


@router.get("/{record_id}", response_model=PublishRecordResponse)
async def get_publish_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取发布记录详情"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == record_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    return record


@router.get("/{record_id}/status", response_model=PublishStatusResponse)
async def get_publish_status(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取发布状态"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == record_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    return PublishStatusResponse(
        id=record.id,
        platform=record.platform,
        status=record.status,
        platform_url=record.platform_url,
        error_message=record.error_message,
        published_at=record.published_at
    )


@router.put("/{record_id}", response_model=PublishRecordResponse)
async def update_publish_record(
    record_id: int,
    update_data: PublishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新发布记录（仅限未发布的记录）"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == record_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    if record.status not in [PublishStatus.PENDING, PublishStatus.SCHEDULED, PublishStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能更新待发布、已定时或失败的记录"
        )
    
    # 更新字段
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.post("/{record_id}/retry", response_model=PublishRecordResponse)
async def retry_publish(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重试发布"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == record_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    if record.status != PublishStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能重试失败的发布"
        )
    
    # 获取平台账号
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == record.platform_account_id
    ).first()
    
    if not account or account.is_active != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="平台账号不可用"
        )
    
    try:
        # 获取发布器
        publisher = PublisherFactory.get_publisher(account.platform)
        
        # 解密认证信息
        access_token = decrypt_data(account.access_token) if account.access_token else None
        
        # 发布内容
        record.status = PublishStatus.PUBLISHING
        record.retry_count += 1
        db.commit()
        
        result = await publisher.publish(
            title=record.title,
            content=record.content,
            cover_image=record.cover_image,
            media_urls=record.media_urls,
            tags=record.tags,
            access_token=access_token,
            credentials=account.credentials
        )
        
        # 更新发布记录
        record.status = PublishStatus.SUCCESS
        record.platform_post_id = result.get("post_id")
        record.platform_url = result.get("url")
        record.platform_response = result
        record.published_at = datetime.utcnow()
        record.error_message = None
        
    except Exception as e:
        record.status = PublishStatus.FAILED
        record.error_message = str(e)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publish_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除发布记录"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == record_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    db.delete(record)
    db.commit()
