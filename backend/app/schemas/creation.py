"""
创作记录的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CreationBase(BaseModel):
    """创作记录基础模型"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    content_type: str = Field(..., description="内容类型")
    tool_type: str = Field(..., description="工具类型")


class CreationCreate(CreationBase):
    """创建创作记录"""
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class CreationUpdate(BaseModel):
    """更新创作记录"""
    title: Optional[str] = Field(None, description="标题")
    content: Optional[str] = Field(None, description="内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class CreationResponse(CreationBase):
    """创作记录响应"""
    id: int
    user_id: int
    input_data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    version_history: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreationListResponse(BaseModel):
    """创作列表响应"""
    total: int = Field(..., description="总数")
    items: List[CreationResponse] = Field(..., description="创作列表")


class CreationVersionResponse(BaseModel):
    """创作版本响应"""
    version: int = Field(..., description="版本号")
    content: str = Field(..., description="内容")
    updated_at: str = Field(..., description="更新时间")
