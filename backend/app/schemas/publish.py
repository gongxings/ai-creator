"""
发布管理Pydantic模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """平台类型"""
    WECHAT = "wechat"
    XIAOHONGSHU = "xiaohongshu"
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"
    TOUTIAO = "toutiao"
    BAIJIAHAO = "baijiahao"
    ZHIHU = "zhihu"
    JIANSHU = "jianshu"


class PublishStatus(str, Enum):
    """发布状态"""
    PENDING = "pending"
    PUBLISHING = "publishing"
    SUCCESS = "success"
    FAILED = "failed"
    SCHEDULED = "scheduled"


# ============ 平台账号相关 ============

class PlatformAccountBase(BaseModel):
    """平台账号基础模型"""
    platform: PlatformType
    account_name: str = Field(..., max_length=100)
    account_id: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = None


class PlatformAccountCreate(PlatformAccountBase):
    """创建平台账号"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    credentials: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, str]] = None  # Cookie字典


class PlatformAccountUpdate(BaseModel):
    """更新平台账号"""
    account_name: Optional[str] = Field(None, max_length=100)
    account_id: Optional[str] = Field(None, max_length=100)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    credentials: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[str] = Field(None, pattern="^(active|inactive)$")
    cookies: Optional[Dict[str, str]] = None  # Cookie字典


class PlatformAccountResponse(PlatformAccountBase):
    """平台账号响应"""
    id: int
    user_id: int
    is_active: str
    expires_at: Optional[datetime] = None
    cookies_valid: Optional[str] = None  # Cookie有效性状态
    cookies_updated_at: Optional[datetime] = None  # Cookie更新时间
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlatformAccountListResponse(BaseModel):
    """平台账号列表响应"""
    total: int
    items: List[PlatformAccountResponse]


# ============ 发布记录相关 ============

class PublishContentBase(BaseModel):
    """发布内容基础模型"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    media_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class PublishCreate(BaseModel):
    """创建发布任务"""
    account_id: int
    creation_id: int
    content_type: str
    scheduled_at: Optional[datetime] = None
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    location: Optional[str] = None


class PublishUpdate(BaseModel):
    """更新发布记录"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=500)
    media_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None


class PublishRecordResponse(PublishContentBase):
    """发布记录响应"""
    id: int
    platform: PlatformType
    status: PublishStatus
    account_name: Optional[str] = None
    content_type: Optional[str] = None
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PublishRecordListResponse(BaseModel):
    """发布记录列表响应"""
    total: int
    items: List[PublishRecordResponse]


class PublishStatusResponse(BaseModel):
    """发布状态响应"""
    id: int
    platform: PlatformType
    status: PublishStatus
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None


class BatchPublishResponse(BaseModel):
    """批量发布响应"""
    success_count: int
    failed_count: int
    records: List[PublishRecordResponse]


# ============ 平台信息相关 ============

class PlatformInfo(BaseModel):
    """平台信息"""
    platform: PlatformType
    name: str
    login_url: str
    supported_types: List[str]


class PlatformListResponse(BaseModel):
    """支持的平台列表"""
    platforms: List[PlatformInfo]


# ============ Cookie管理相关 ============

class CookieUpdateRequest(BaseModel):
    """更新Cookie请求"""
    cookies: Dict[str, str] = Field(..., description="Cookie字典")


class CookieValidationResponse(BaseModel):
    """Cookie验证响应"""
    valid: bool
    message: str
    login_url: Optional[str] = None  # 如果Cookie无效，返回登录URL
    cookies_updated_at: Optional[datetime] = None


class PlatformLoginInfo(BaseModel):
    """平台登录信息"""
    platform: PlatformType
    name: str
    login_url: str
    instructions: str  # 登录说明
