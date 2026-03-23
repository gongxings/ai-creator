"""
PPT模板 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============ 占位符和布局相关 ============

class PlaceholderBounds(BaseModel):
    """占位符位置和大小"""
    x: float = Field(..., description="X坐标(EMU)")
    y: float = Field(..., description="Y坐标(EMU)")
    width: float = Field(..., description="宽度(EMU)")
    height: float = Field(..., description="高度(EMU)")


class SlidePlaceholder(BaseModel):
    """幻灯片占位符"""
    idx: int = Field(..., description="占位符索引")
    type: str = Field(..., description="占位符类型：title/subtitle/body/object/chart/picture")
    label: str = Field(..., description="占位符标签")
    bounds: Optional[PlaceholderBounds] = Field(None, description="位置和大小")
    supports_bullets: bool = Field(False, description="是否支持项目符号")


class SlideLayout(BaseModel):
    """幻灯片布局信息"""
    index: int = Field(..., description="幻灯片索引")
    type: str = Field(..., description="布局类型：title/content/section/ending/two_content")
    layout_name: str = Field(..., description="布局名称")
    placeholders: List[SlidePlaceholder] = Field(default_factory=list, description="占位符列表")


class LayoutMetadata(BaseModel):
    """布局元数据"""
    slide_count: int = Field(..., description="幻灯片数量")
    slides: List[SlideLayout] = Field(default_factory=list, description="幻灯片布局列表")


# ============ 模板 CRUD 相关 ============

class PPTTemplateBase(BaseModel):
    """PPT模板基础模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    category: Optional[str] = Field(None, description="场景分类：report/training/roadshow/teaching")
    style: Optional[str] = Field(None, description="风格类型")
    is_public: bool = Field(False, description="是否公开")


class PPTTemplateCreate(PPTTemplateBase):
    """创建PPT模板"""
    pass


class PPTTemplateUpdate(BaseModel):
    """更新PPT模板"""
    name: Optional[str] = Field(None, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    category: Optional[str] = Field(None, description="场景分类")
    style: Optional[str] = Field(None, description="风格类型")
    is_public: Optional[bool] = Field(None, description="是否公开")


class PPTTemplateResponse(PPTTemplateBase):
    """PPT模板响应"""
    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    layout_metadata: Optional[Dict[str, Any]] = None
    is_system: bool
    user_id: Optional[int] = None
    use_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PPTTemplateListResponse(BaseModel):
    """PPT模板列表响应"""
    total: int
    items: List[PPTTemplateResponse]


# ============ 大纲相关 ============

class SlideContent(BaseModel):
    """幻灯片内容"""
    slide_type: str = Field("content", description="幻灯片类型：title/content/section/ending")
    title: str = Field(..., description="幻灯片标题")
    bullets: Optional[List[str]] = Field(None, description="要点列表")
    sub_bullets: Optional[Dict[str, List[str]]] = Field(None, description="子要点")
    notes: Optional[str] = Field(None, description="演讲者备注")
    image_placeholder: bool = Field(False, description="是否需要图片占位符")


class PPTOutline(BaseModel):
    """PPT大纲"""
    title: str = Field(..., description="PPT标题")
    subtitle: Optional[str] = Field(None, description="副标题")
    slides: List[SlideContent] = Field(default_factory=list, description="幻灯片内容列表")
    
    @property
    def slide_count(self) -> int:
        return len(self.slides)


# ============ 编辑相关 ============

class TextUpdateRequest(BaseModel):
    """文本更新请求"""
    slide_index: int = Field(..., description="幻灯片索引")
    placeholder_idx: int = Field(..., description="占位符索引")
    text: str = Field(..., description="新文本内容")


class StyleUpdateRequest(BaseModel):
    """样式更新请求"""
    slide_index: int = Field(..., description="幻灯片索引")
    placeholder_idx: int = Field(..., description="占位符索引")
    font_size: Optional[int] = Field(None, description="字体大小")
    font_bold: Optional[bool] = Field(None, description="是否加粗")
    font_color: Optional[str] = Field(None, description="字体颜色(hex)")


class RegeneratePageRequest(BaseModel):
    """重新生成单页请求"""
    slide_index: int = Field(..., description="幻灯片索引")
    content: Optional[str] = Field(None, description="新的内容描述")
