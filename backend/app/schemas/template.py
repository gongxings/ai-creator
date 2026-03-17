"""
文章模板 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# ============ 样式配置相关 ============

class CSSProperties(BaseModel):
    """CSS 属性配置"""
    fontSize: Optional[str] = None
    fontWeight: Optional[str] = None
    color: Optional[str] = None
    backgroundColor: Optional[str] = None
    lineHeight: Optional[str] = None
    marginTop: Optional[str] = None
    marginBottom: Optional[str] = None
    marginLeft: Optional[str] = None
    marginRight: Optional[str] = None
    paddingTop: Optional[str] = None
    paddingBottom: Optional[str] = None
    paddingLeft: Optional[str] = None
    paddingRight: Optional[str] = None
    padding: Optional[str] = None
    margin: Optional[str] = None
    borderLeft: Optional[str] = None
    borderBottom: Optional[str] = None
    borderRadius: Optional[str] = None
    textAlign: Optional[str] = None
    textIndent: Optional[str] = None
    textDecoration: Optional[str] = None
    fontFamily: Optional[str] = None
    maxWidth: Optional[str] = None
    display: Optional[str] = None
    overflow: Optional[str] = None
    border: Optional[str] = None
    borderTop: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外的 CSS 属性


class TemplateStyles(BaseModel):
    """模板样式配置"""
    container: Optional[CSSProperties] = None
    h1: Optional[CSSProperties] = None
    h2: Optional[CSSProperties] = None
    h3: Optional[CSSProperties] = None
    p: Optional[CSSProperties] = None
    blockquote: Optional[CSSProperties] = None
    ul: Optional[CSSProperties] = None
    ol: Optional[CSSProperties] = None
    li: Optional[CSSProperties] = None
    code: Optional[CSSProperties] = None
    pre: Optional[CSSProperties] = None
    img: Optional[CSSProperties] = None
    a: Optional[CSSProperties] = None
    hr: Optional[CSSProperties] = None
    strong: Optional[CSSProperties] = None
    em: Optional[CSSProperties] = None
    
    class Config:
        extra = "allow"  # 允许额外的元素样式


# ============ 模板 CRUD 相关 ============

class TemplateBase(BaseModel):
    """模板基础模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    styles: Dict[str, Any] = Field(..., description="样式配置")
    is_public: bool = Field(False, description="是否公开")


class TemplateCreate(TemplateBase):
    """创建模板"""
    pass


class TemplateUpdate(BaseModel):
    """更新模板"""
    name: Optional[str] = Field(None, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    styles: Optional[Dict[str, Any]] = Field(None, description="样式配置")
    is_public: Optional[bool] = Field(None, description="是否公开")


class TemplateResponse(TemplateBase):
    """模板响应"""
    id: int
    is_system: bool
    user_id: Optional[int] = None
    use_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    total: int
    items: list[TemplateResponse]


class TemplateCloneRequest(BaseModel):
    """克隆模板请求"""
    name: Optional[str] = Field(None, max_length=100, description="新模板名称（可选，默认在原名称后加'-副本'）")
