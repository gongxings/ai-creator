"""
爆款模仿相关 Schema
分析爆款文章风格并生成类似内容
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ContentCategory(str, Enum):
    """内容类别"""
    EMOTION = "emotion"           # 情感共鸣
    KNOWLEDGE = "knowledge"       # 知识干货
    STORY = "story"               # 故事叙事
    NEWS = "news"                 # 新闻热点
    TUTORIAL = "tutorial"         # 教程攻略
    REVIEW = "review"             # 测评种草
    OPINION = "opinion"           # 观点输出


class ViralElement(BaseModel):
    """爆款元素"""
    name: str = Field(..., description="元素名称")
    description: str = Field(..., description="元素说明")
    score: int = Field(..., description="该元素的运用得分 (0-100)")
    examples: List[str] = Field(default_factory=list, description="文中示例")


class StructureAnalysis(BaseModel):
    """结构分析"""
    sections: List[str] = Field(..., description="段落结构")
    opening_hook: str = Field(..., description="开头钩子")
    closing_cta: str = Field(..., description="结尾行动召唤")
    transition_style: str = Field(..., description="过渡风格")


class AnalyzeRequest(BaseModel):
    """爆款分析请求"""
    content: str = Field(..., description="要分析的爆款内容", min_length=50, max_length=20000)
    title: Optional[str] = Field(None, description="文章标题")
    platform: Optional[str] = Field(None, description="来源平台")


class AnalyzeResponse(BaseModel):
    """爆款分析响应"""
    title: str = Field(..., description="文章标题")
    category: ContentCategory = Field(..., description="内容类别")
    viral_score: int = Field(..., description="爆款指数 (0-100)")
    
    # 风格分析
    tone: str = Field(..., description="语气风格")
    target_audience: str = Field(..., description="目标受众")
    emotional_triggers: List[str] = Field(..., description="情感触发点")
    
    # 爆款元素
    viral_elements: List[ViralElement] = Field(..., description="爆款元素分析")
    
    # 结构分析
    structure: StructureAnalysis = Field(..., description="结构分析")
    
    # 写作技巧
    writing_techniques: List[str] = Field(..., description="写作技巧")
    
    # 关键词
    keywords: List[str] = Field(..., description="核心关键词")
    
    # 改进建议
    improvement_suggestions: List[str] = Field(default_factory=list, description="可改进的点")


class ImitateRequest(BaseModel):
    """爆款模仿请求"""
    reference_content: str = Field(..., description="参考的爆款内容", min_length=50, max_length=20000)
    reference_title: Optional[str] = Field(None, description="参考文章标题")
    new_topic: str = Field(..., description="新的主题/话题", min_length=2, max_length=200)
    platform: Optional[str] = Field(None, description="目标平台")
    style_strength: int = Field(80, description="风格模仿强度 (0-100)", ge=0, le=100)
    keep_structure: bool = Field(True, description="是否保持相同结构")
    additional_requirements: Optional[str] = Field(None, description="额外要求")


class ImitateResponse(BaseModel):
    """爆款模仿响应"""
    title: str = Field(..., description="生成的标题")
    content: str = Field(..., description="生成的内容")
    
    # 模仿说明
    imitation_notes: List[str] = Field(..., description="模仿说明")
    elements_applied: List[str] = Field(..., description="应用的爆款元素")
    
    # 统计信息
    word_count: int = Field(..., description="字数")
    estimated_viral_score: int = Field(..., description="预估爆款指数")
    
    # 创作记录ID
    creation_id: Optional[int] = Field(None, description="创作记录ID")


class StyleTemplateRequest(BaseModel):
    """风格模板提取请求"""
    contents: List[str] = Field(..., description="多篇同风格的内容", min_items=2, max_items=5)
    template_name: str = Field(..., description="模板名称")


class StyleTemplate(BaseModel):
    """风格模板"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    
    # 风格特征
    tone: str = Field(..., description="语气风格")
    sentence_style: str = Field(..., description="句式特点")
    vocabulary_style: str = Field(..., description="用词风格")
    structure_pattern: str = Field(..., description="结构模式")
    
    # 爆款元素配比
    element_weights: dict = Field(..., description="元素权重配置")
    
    # 示例句式
    example_sentences: List[str] = Field(..., description="示例句式")


class QuickImitateRequest(BaseModel):
    """快速模仿请求（基于模板）"""
    template_id: int = Field(..., description="风格模板ID")
    topic: str = Field(..., description="新主题")
    word_count: int = Field(800, description="目标字数", ge=100, le=5000)
