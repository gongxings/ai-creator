"""
内容模板 Pydantic 模型 - 支持多平台
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============ 平台和分类定义 ============

# 支持的平台类型
PLATFORM_CHOICES = ["wechat", "xiaohongshu", "toutiao", "ppt", "douyin"]

# 各平台的场景分类
PLATFORM_CATEGORIES = {
    "wechat": ["emotion", "knowledge", "marketing", "news", "story"],
    "xiaohongshu": ["recommend", "guide", "review", "daily"],
    "toutiao": ["news", "entertainment", "tech", "life"],
    "ppt": ["report", "training", "roadshow", "teaching"],
    "douyin": ["talk", "drama", "tutorial", "promotion"]
}

# 平台中文名称
PLATFORM_NAMES = {
    "wechat": "公众号",
    "xiaohongshu": "小红书",
    "toutiao": "头条",
    "ppt": "PPT",
    "douyin": "抖音"
}

# 场景中文名称
CATEGORY_NAMES = {
    "emotion": "情感文",
    "knowledge": "干货文",
    "marketing": "营销文",
    "news": "新闻资讯",
    "story": "故事文",
    "recommend": "种草推荐",
    "guide": "攻略指南",
    "review": "测评体验",
    "daily": "日常分享",
    "entertainment": "娱乐八卦",
    "tech": "科技数码",
    "life": "生活百科",
    "report": "工作汇报",
    "training": "培训课件",
    "roadshow": "路演演示",
    "teaching": "教学课件",
    "talk": "口播脚本",
    "drama": "剧情脚本",
    "tutorial": "教程脚本",
    "promotion": "带货脚本"
}


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


class FormatRules(BaseModel):
    """平台格式规范"""
    # 通用规则
    title_max_length: Optional[int] = None
    paragraph_max_length: Optional[int] = None
    
    # 公众号特有
    subtitle_enabled: Optional[bool] = None
    paragraph_spacing: Optional[str] = None
    heading_style: Optional[str] = None
    quote_style: Optional[str] = None
    
    # 小红书特有
    emoji_required: Optional[bool] = None
    emoji_density: Optional[str] = None
    hashtag_count: Optional[int] = None
    hashtag_position: Optional[str] = None
    bullet_style: Optional[str] = None
    
    # 头条特有
    image_frequency: Optional[str] = None
    summary_enabled: Optional[bool] = None
    summary_length: Optional[int] = None
    
    # PPT特有
    slide_count_range: Optional[List[int]] = None
    max_bullet_points: Optional[int] = None
    
    class Config:
        extra = "allow"


# ============ 模板 CRUD 相关 ============

class TemplateBase(BaseModel):
    """模板基础模型"""
    name: str = Field(..., max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    platform: str = Field(..., description="平台类型：wechat/xiaohongshu/toutiao/ppt/douyin")
    category: Optional[str] = Field(None, description="场景分类")
    style: Optional[str] = Field(None, description="风格类型")
    styles: Dict[str, Any] = Field(..., description="样式配置")
    format_rules: Optional[Dict[str, Any]] = Field(None, description="平台格式规范")
    ai_prompt: Optional[str] = Field(None, description="AI生成提示词")
    content_structure: Optional[Dict[str, Any]] = Field(None, description="内容结构定义")
    is_public: bool = Field(False, description="是否公开")


class TemplateCreate(TemplateBase):
    """创建模板"""
    pass


class TemplateUpdate(BaseModel):
    """更新模板"""
    name: Optional[str] = Field(None, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, max_length=500, description="模板描述")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    platform: Optional[str] = Field(None, description="平台类型")
    category: Optional[str] = Field(None, description="场景分类")
    style: Optional[str] = Field(None, description="风格类型")
    styles: Optional[Dict[str, Any]] = Field(None, description="样式配置")
    format_rules: Optional[Dict[str, Any]] = Field(None, description="平台格式规范")
    ai_prompt: Optional[str] = Field(None, description="AI生成提示词")
    content_structure: Optional[Dict[str, Any]] = Field(None, description="内容结构定义")
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


class PlatformInfo(BaseModel):
    """平台信息"""
    id: str
    name: str
    categories: List[Dict[str, str]]


class PlatformsResponse(BaseModel):
    """平台列表响应"""
    platforms: List[PlatformInfo]
