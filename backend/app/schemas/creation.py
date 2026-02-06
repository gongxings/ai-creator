"""
创作记录的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WritingToolInfo(BaseModel):
    """写作工具信息"""
    tool_type: str = Field(..., description="工具类型")
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    category: str = Field(..., description="工具分类")
    icon: Optional[str] = Field(None, description="图标")


class CreationGenerate(BaseModel):
    """生成创作请求"""
    tool_type: str = Field(..., description="工具类型")
    prompt: str = Field(..., description="提示词")
    parameters: Optional[Dict[str, Any]] = Field(None, description="生成参数")
    model_id: Optional[int] = Field(None, description="使用的AI模型ID")
    platform: Optional[str] = Field(None, description="使用的平台（doubao等），为空则使用API Key模式")


class CreationRegenerate(BaseModel):
    """重新生成创作请求"""
    prompt: Optional[str] = Field(None, description="新的提示词")
    parameters: Optional[Dict[str, Any]] = Field(None, description="生成参数")


class CreationOptimize(BaseModel):
    """优化创作请求"""
    optimization_type: str = Field(..., description="优化类型: seo, readability, grammar等")
    parameters: Optional[Dict[str, Any]] = Field(None, description="优化参数")


class CreationBase(BaseModel):
    """创作记录基础模型"""
    title: str = Field(..., description="标题")
    content: Optional[str] = Field(None, description="内容")
    creation_type: Optional[str] = Field(None, description="创作类型")
    tool_type: Optional[str] = Field(None, description="工具类型（已弃用，保留用于兼容）")


class CreationCreate(CreationBase):
    """创建创作记录"""
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class CreationUpdate(BaseModel):
    """更新创作记录"""
    title: Optional[str] = Field(None, description="标题")
    content: Optional[str] = Field(None, description="内容")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class CreationResponse(BaseModel):
    """创作记录响应"""
    id: int
    user_id: int
    title: Optional[str] = None
    content: Optional[str] = None
    creation_type: Optional[str] = None
    tool_type: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None
    output_content: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    version_history: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreationListResponse(BaseModel):
    """创作列表响应"""
    total: int = Field(..., description="总数")
    items: List[CreationResponse] = Field(..., description="创作列表")


class CreationListItem(BaseModel):
    """创作列表项"""
    id: int
    title: Optional[str] = None
    creation_type: Optional[str] = None
    tool_type: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreationVersion(BaseModel):
    """创作版本"""
    version: int = Field(..., description="版本号")
    content: str = Field(..., description="内容")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class CreationVersionResponse(BaseModel):
    """创作版本响应"""
    version: int = Field(..., description="版本号")
    content: str = Field(..., description="内容")
    updated_at: str = Field(..., description="更新时间")
