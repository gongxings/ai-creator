"""
OAuth相关Schema
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ 平台配置相关 ============
class PlatformConfigBase(BaseModel):
    """平台配置基础Schema"""
    platform_id: str = Field(..., description="平台ID")
    platform_name: str = Field(..., description="平台名称")
    platform_icon: Optional[str] = Field(None, description="平台图标URL")
    priority: int = Field(99, description="优先级")
    is_enabled: bool = Field(True, description="是否启用")
    oauth_config: Optional[Dict[str, Any]] = Field(None, description="OAuth配置")
    litellm_config: Optional[Dict[str, Any]] = Field(None, description="LiteLLM配置")
    quota_config: Optional[Dict[str, Any]] = Field(None, description="额度配置")


class PlatformConfigCreate(PlatformConfigBase):
    """创建平台配置"""
    pass


class PlatformConfigUpdate(BaseModel):
    """更新平台配置"""
    platform_name: Optional[str] = None
    platform_icon: Optional[str] = None
    priority: Optional[int] = None
    is_enabled: Optional[bool] = None
    oauth_config: Optional[Dict[str, Any]] = None
    litellm_config: Optional[Dict[str, Any]] = None
    quota_config: Optional[Dict[str, Any]] = None


class PlatformConfigResponse(PlatformConfigBase):
    """平台配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ OAuth账号相关 ============
class OAuthAccountBase(BaseModel):
    """OAuth账号基础Schema"""
    platform: str = Field(..., description="平台ID")
    account_name: Optional[str] = Field(None, description="账号名称")


class OAuthAccountCreate(OAuthAccountBase):
    """创建OAuth账号"""
    credentials: str = Field(..., description="加密的凭证")


class OAuthAccountUpdate(BaseModel):
    """更新OAuth账号"""
    account_name: Optional[str] = None
    is_active: Optional[bool] = None


class OAuthAccountResponse(OAuthAccountBase):
    """OAuth账号响应"""
    id: int
    user_id: int
    is_active: bool
    is_expired: bool
    quota_used: int
    quota_limit: Optional[int]
    last_used_at: Optional[datetime]
    expired_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ OAuth授权相关 ============
class OAuthAuthorizeRequest(BaseModel):
    """OAuth授权请求"""
    platform: str = Field(..., description="平台ID")
    account_name: Optional[str] = Field(None, description="账号名称")


class OAuthAuthorizeResponse(BaseModel):
    """OAuth授权响应"""
    success: bool
    message: str
    account_id: Optional[int] = None
    account: Optional[OAuthAccountResponse] = None


# ============ OAuth使用日志相关 ============
class OAuthUsageLogBase(BaseModel):
    """OAuth使用日志基础Schema"""
    platform: str
    model: Optional[str] = None
    request_type: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    response_time: Optional[int] = None


class OAuthUsageLogCreate(OAuthUsageLogBase):
    """创建OAuth使用日志"""
    user_id: int
    account_id: int


class OAuthUsageLogResponse(OAuthUsageLogBase):
    """OAuth使用日志响应"""
    id: int
    user_id: int
    account_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ OAuth统计相关 ============
class OAuthUsageStats(BaseModel):
    """OAuth使用统计"""
    total_requests: int = Field(0, description="总请求数")
    success_requests: int = Field(0, description="成功请求数")
    failed_requests: int = Field(0, description="失败请求数")
    total_tokens: int = Field(0, description="总tokens")
    platform_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="各平台统计")


class OAuthAccountStatus(BaseModel):
    """OAuth账号状态"""
    account_id: int
    platform: str
    is_active: bool
    is_expired: bool
    is_available: bool
    quota_used: int
    quota_limit: Optional[int]
    quota_remaining: Optional[int]
    last_check_at: datetime


# ============ AI生成请求（扩展）============
class AIGenerateWithOAuth(BaseModel):
    """使用OAuth的AI生成请求"""
    content: str = Field(..., description="生成内容")
    use_oauth: bool = Field(False, description="是否使用OAuth")
    oauth_account_id: Optional[int] = Field(None, description="OAuth账号ID")
    oauth_platform: Optional[str] = Field(None, description="OAuth平台（自动选择）")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(2000, description="最大tokens")
