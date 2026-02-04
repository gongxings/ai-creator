"""
API Key相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class APIKeyCreate(BaseModel):
    """创建API Key请求"""
    key_name: str = Field(..., min_length=1, max_length=100, description="Key名称")
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="过期天数（1-365天）")
    rate_limit: int = Field(60, ge=1, le=1000, description="速率限制（次/分钟）")
    allowed_models: Optional[List[str]] = Field(None, description="允许使用的模型列表（为空表示全部）")


class APIKeyResponse(BaseModel):
    """API Key响应（列表）"""
    id: int
    key_name: str
    key_display: str = Field(..., description="显示用的Key（sk-****...****1234）")
    is_active: bool
    rate_limit: int
    allowed_models: Optional[List[str]]
    total_requests: int
    total_tokens: int
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    """创建API Key响应（包含完整Key）"""
    id: int
    key_name: str
    api_key: str = Field(..., description="完整的API Key（仅在创建时返回一次）")
    key_display: str
    is_active: bool
    rate_limit: int
    allowed_models: Optional[List[str]]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyUpdate(BaseModel):
    """更新API Key请求"""
    key_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=1000)
    allowed_models: Optional[List[str]] = None


class APIKeyUsageLogResponse(BaseModel):
    """API Key使用日志响应"""
    id: int
    model_id: Optional[str]
    model_name: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    error_message: Optional[str]
    ip_address: Optional[str]
    response_time: Optional[int]
    status_code: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyStatsResponse(BaseModel):
    """API Key统计响应"""
    total_requests: int
    total_tokens: int
    success_requests: int
    failed_requests: int
    avg_response_time: Optional[float]
    last_used_at: Optional[datetime]
    recent_logs: List[APIKeyUsageLogResponse]


class ModelInfo(BaseModel):
    """模型信息"""
    model_id: str = Field(..., description="统一的模型标识符")
    model_name: str = Field(..., description="实际的模型名称")
    display_name: str = Field(..., description="显示名称")
    provider: str = Field(..., description="提供商")
    source_type: str = Field(..., description="来源类型（oauth/api_key）")
    source_id: int = Field(..., description="来源ID")
    is_free: bool = Field(..., description="是否免费")
    is_preferred: bool = Field(False, description="是否为用户偏好")
    status: str = Field(..., description="状态（active/expired/quota_exceeded）")
    quota_info: Optional[dict] = Field(None, description="配额信息")


class AvailableModelsResponse(BaseModel):
    """可用模型列表响应"""
    models: List[ModelInfo]
    total: int


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色（system/user/assistant）")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """统一聊天请求"""
    model_id: str = Field(..., description="模型ID")
    messages: List[ChatMessage] = Field(..., description="消息列表")
    scene_type: Optional[str] = Field(None, description="场景类型（writing/image/video）")
    stream: bool = Field(False, description="是否流式响应")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大Token数")


class ChatResponse(BaseModel):
    """统一聊天响应"""
    content: str = Field(..., description="生成的内容")
    model_id: str = Field(..., description="使用的模型ID")
    model_name: str = Field(..., description="模型名称")
    usage: dict = Field(..., description="Token使用情况")
    finish_reason: Optional[str] = Field(None, description="完成原因")


# OpenAI兼容格式
class OpenAIChatMessage(BaseModel):
    """OpenAI聊天消息格式"""
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    """OpenAI聊天请求格式"""
    model: str
    messages: List[OpenAIChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


class OpenAIUsage(BaseModel):
    """OpenAI使用情况"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIChoice(BaseModel):
    """OpenAI选择"""
    index: int
    message: OpenAIChatMessage
    finish_reason: Optional[str] = None


class OpenAIChatResponse(BaseModel):
    """OpenAI聊天响应格式"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: OpenAIUsage


class OpenAIModel(BaseModel):
    """OpenAI模型格式"""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "user"


class OpenAIModelsResponse(BaseModel):
    """OpenAI模型列表响应"""
    object: str = "list"
    data: List[OpenAIModel]
