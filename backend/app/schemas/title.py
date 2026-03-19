"""
爆款标题生成相关 Schema
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TitleStyle(str, Enum):
    """标题风格"""
    CURIOSITY = "curiosity"           # 好奇心驱动
    BENEFIT = "benefit"               # 利益驱动
    EMOTIONAL = "emotional"           # 情感驱动
    TRENDING = "trending"             # 热点借势
    LISTICLE = "listicle"             # 数字清单
    QUESTION = "question"             # 提问式
    HOW_TO = "how_to"                 # 教程式
    CONTRAST = "contrast"             # 对比反差


class PlatformType(str, Enum):
    """目标平台"""
    WECHAT = "wechat"                 # 微信公众号
    XIAOHONGSHU = "xiaohongshu"       # 小红书
    DOUYIN = "douyin"                 # 抖音
    ZHIHU = "zhihu"                   # 知乎
    WEIBO = "weibo"                   # 微博
    TOUTIAO = "toutiao"               # 今日头条
    BILIBILI = "bilibili"             # B站


class TitleGenerateRequest(BaseModel):
    """标题生成请求"""
    content: str = Field(..., description="内容摘要或主题关键词", min_length=2, max_length=500)
    platform: Optional[PlatformType] = Field(None, description="目标平台")
    style: Optional[TitleStyle] = Field(None, description="标题风格")
    count: int = Field(5, description="生成数量", ge=1, le=10)
    keywords: Optional[List[str]] = Field(None, description="必须包含的关键词")
    tone: Optional[str] = Field(None, description="语气（如：专业、轻松、幽默、严肃）")


class TitleItem(BaseModel):
    """生成的标题项"""
    title: str = Field(..., description="标题文本")
    style: TitleStyle = Field(..., description="标题风格")
    score: int = Field(..., description="爆款指数 (0-100)", ge=0, le=100)
    hooks: List[str] = Field(default_factory=list, description="使用的钩子技巧")
    explanation: str = Field("", description="标题解析")


class TitleGenerateResponse(BaseModel):
    """标题生成响应"""
    titles: List[TitleItem] = Field(..., description="生成的标题列表")
    analysis: str = Field("", description="整体分析建议")


class TitleOptimizeRequest(BaseModel):
    """标题优化请求"""
    original_title: str = Field(..., description="原标题", min_length=2, max_length=200)
    platform: Optional[PlatformType] = Field(None, description="目标平台")
    optimization_goals: Optional[List[str]] = Field(
        None,
        description="优化目标（如：增加点击率、更吸引眼球、更专业等）"
    )


class TitleOptimizeResponse(BaseModel):
    """标题优化响应"""
    original_title: str = Field(..., description="原标题")
    original_score: int = Field(..., description="原标题爆款指数")
    original_issues: List[str] = Field(..., description="原标题问题分析")
    optimized_titles: List[TitleItem] = Field(..., description="优化后的标题列表")
    improvement_tips: List[str] = Field(..., description="改进建议")


class TitleAnalyzeRequest(BaseModel):
    """标题分析请求"""
    title: str = Field(..., description="要分析的标题", min_length=2, max_length=200)
    platform: Optional[PlatformType] = Field(None, description="目标平台")


class TitleAnalyzeResponse(BaseModel):
    """标题分析响应"""
    title: str = Field(..., description="分析的标题")
    score: int = Field(..., description="爆款指数 (0-100)")
    style: TitleStyle = Field(..., description="识别的标题风格")
    strengths: List[str] = Field(..., description="标题优点")
    weaknesses: List[str] = Field(..., description="标题缺点")
    hooks_used: List[str] = Field(..., description="使用的钩子技巧")
    improvement_suggestions: List[str] = Field(..., description="改进建议")
    platform_fit: Optional[str] = Field(None, description="平台适配度分析")
