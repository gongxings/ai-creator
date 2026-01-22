"""
AI模型配置的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AIModelBase(BaseModel):
    """AI模型基础模型"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    model_name: str = Field(..., description="模型标识")
    base_url: Optional[str] = Field(None, description="API基础URL")
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="模型描述")


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
    description: Optional[str] = Field(None, description="模型描述")


class AIModelResponse(AIModelBase):
    """AI模型响应"""
    id: int
    user_id: int
    is_default: bool
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
