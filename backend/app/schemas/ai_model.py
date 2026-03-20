"""
AI模型配置的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AIModelBase(BaseModel):
    """AI模型基础模型"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    model_name: str = Field(..., description="模型标识")
    base_url: Optional[str] = Field(None, description="API基础URL")
    is_active: bool = Field(True, description="是否启用")
    is_system_builtin: bool = Field(False, description="是否系统内置模型")
    description: Optional[str] = Field(None, description="模型描述")
    capabilities: List[str] = Field(default=["text"], description="模型能力列表(text/image/video/audio)")


class AIModelCreate(AIModelBase):
    """创建AI模型"""
    api_key: str = Field(..., description="API密钥")


class AIModelUpdate(BaseModel):
    """更新AI模型"""
    name: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    model_name: Optional[str] = Field(None, description="模型标识")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    is_active: Optional[bool] = Field(None, description="是否启用")
    is_system_builtin: Optional[bool] = Field(None, description="是否系统内置模型")
    description: Optional[str] = Field(None, description="模型描述")
    capabilities: Optional[List[str]] = Field(None, description="模型能力列表(text/image/video/audio)")


class AIModelResponse(AIModelBase):
    """AI模型响应"""
    id: int
    user_id: int
    is_default: bool
    capabilities: List[str] = Field(default=["text"], description="模型能力列表")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIModelTestRequest(BaseModel):
    """测试AI模型请求"""
    prompt: Optional[str] = Field(None, description="测试提示词")


class AIModelTestResponse(BaseModel):
    """测试AI模型响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    response: Optional[str] = Field(None, description="AI响应内容")


class AIModelListResponse(BaseModel):
    """AI模型列表响应"""
    items: list[AIModelResponse] = Field(..., description="模型列表")
    total: int = Field(..., description="总数")


class ModelInfo(BaseModel):
    """统一模型信息（用于模型选择）"""
    model_id: str = Field(..., description="模型ID（oauth_{account_id}_{model_name} 或 ai_model_{model_id}）")
    model_name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    provider: str = Field(..., description="提供商")
    source_type: str = Field(..., description="来源类型（oauth/api_key）")
    source_id: int = Field(..., description="来源ID")
    is_free: bool = Field(False, description="是否免费")
    is_preferred: bool = Field(False, description="是否偏好模型")
    status: str = Field("active", description="状态")
    quota_info: Optional[Dict[str, Any]] = Field(None, description="配额信息")


class AvailableModelsResponse(BaseModel):
    """可用模型列表响应"""
    models: List[ModelInfo] = Field(..., description="可用模型列表")
    total: int = Field(..., description="总数")
