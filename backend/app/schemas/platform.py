"""
平台Schema模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.platform import PlatformType, PlatformStatus, PublishStatus


class PlatformBind(BaseModel):
    """绑定平台账号请求"""
    platform_type: PlatformType = Field(..., description="平台类型")
    account_name: str = Field(..., max_length=100, description="账号名称")
    credentials: dict = Field(..., description="认证凭证")
    config: Optional[dict] = Field(None, description="平台配置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_type": "wechat",
                "account_name": "我的公众号",
                "credentials": {
                    "app_id": "wx1234567890",
                    "app_secret": "secret123",
                    "access_token": "token123"
                },
                "config": {
                    "auto_publish": False,
                    "default_tags": ["科技", "互联网"]
                }
            }
        }


class PlatformUpdate(BaseModel):
    """更新平台账号请求"""
    account_name: Optional[str] = Field(None, max_length=100, description="账号名称")
    credentials: Optional[dict] = Field(None, description="认证凭证")
    config: Optional[dict] = Field(None, description="平台配置")
    status: Optional[PlatformStatus] = Field(None, description="状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_name": "新账号名称",
                "config": {
                    "auto_publish": True
                }
            }
        }


class PlatformResponse(BaseModel):
    """平台账号响应"""
    id: int
    user_id: int
    platform_type: PlatformType
    account_name: str
    config: Optional[dict]
    status: PlatformStatus
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "platform_type": "wechat",
                "account_name": "我的公众号",
                "config": {
                    "auto_publish": False
                },
                "status": "active",
                "last_sync_at": "2024-01-01T00:00:00",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class PublishRequest(BaseModel):
    """发布内容请求"""
    creation_id: int = Field(..., description="创作内容ID")
    platform_ids: list[int] = Field(..., min_length=1, description="目标平台ID列表")
    scheduled_at: Optional[datetime] = Field(None, description="定时发布时间")
    platform_config: Optional[dict] = Field(None, description="平台特定配置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "creation_id": 1,
                "platform_ids": [1, 2, 3],
                "scheduled_at": "2024-01-02T10:00:00",
                "platform_config": {
                    "wechat": {
                        "thumb_media_id": "media123",
                        "need_open_comment": True
                    },
                    "xiaohongshu": {
                        "cover_image": "https://example.com/cover.jpg",
                        "tags": ["生活", "分享"]
                    }
                }
            }
        }


class PublishResponse(BaseModel):
    """发布记录响应"""
    id: int
    user_id: int
    creation_id: int
    platform_id: int
    platform_type: PlatformType
    platform_account: str
    status: PublishStatus
    platform_url: Optional[str]
    platform_id_str: Optional[str]
    error_message: Optional[str]
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "creation_id": 1,
                "platform_id": 1,
                "platform_type": "wechat",
                "platform_account": "我的公众号",
                "status": "published",
                "platform_url": "https://mp.weixin.qq.com/s/xxx",
                "platform_id_str": "article123",
                "error_message": None,
                "scheduled_at": None,
                "published_at": "2024-01-01T10:00:00",
                "created_at": "2024-01-01T09:55:00"
            }
        }


class PublishListItem(BaseModel):
    """发布记录列表项"""
    id: int
    creation_id: int
    creation_title: Optional[str]
    platform_type: PlatformType
    platform_account: str
    status: PublishStatus
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlatformInfo(BaseModel):
    """平台信息"""
    type: PlatformType
    name: str
    description: str
    icon: str
    features: list[str]
    auth_type: str
    required_credentials: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "wechat",
                "name": "微信公众号",
                "description": "发布文章到微信公众号",
                "icon": "💬",
                "features": ["文章发布", "定时发布", "评论管理"],
                "auth_type": "oauth",
                "required_credentials": ["app_id", "app_secret"]
            }
        }
