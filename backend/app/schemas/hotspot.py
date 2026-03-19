"""
热点追踪相关 Schema
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class HotspotItem(BaseModel):
    """热点条目"""
    title: str = Field(..., description="热点标题")
    url: Optional[str] = Field(None, description="热点链接")
    hot: Optional[int] = Field(None, description="热度值")
    index: Optional[int] = Field(None, description="排名")
    mobile_url: Optional[str] = Field(None, description="移动端链接")


class HotspotListResponse(BaseModel):
    """热点列表响应"""
    platform: str = Field(..., description="平台名称")
    platform_name: str = Field(..., description="平台中文名")
    update_time: Optional[str] = Field(None, description="更新时间")
    items: List[HotspotItem] = Field(default_factory=list, description="热点列表")


class CategoryInfo(BaseModel):
    """分类信息"""
    code: str = Field(..., description="分类代码")
    name: str = Field(..., description="分类中文名")
    order: int = Field(..., description="排序顺序")


class CategoryListResponse(BaseModel):
    """分类列表响应"""
    categories: List[CategoryInfo] = Field(..., description="分类列表")


class PlatformInfo(BaseModel):
    """平台信息"""
    code: str = Field(..., description="平台代码")
    name: str = Field(..., description="平台中文名")
    category: str = Field(..., description="所属分类")
    icon: Optional[str] = Field(None, description="平台图标")
    color: Optional[str] = Field(None, description="平台主题色")
    subtypes: Optional[Dict[str, str]] = Field(None, description="子类型（如百度的热搜/汽车/游戏等）")


class PlatformListResponse(BaseModel):
    """平台列表响应"""
    platforms: List[PlatformInfo] = Field(..., description="支持的平台列表")


class TopicSuggestRequest(BaseModel):
    """选题建议请求"""
    hot_title: str = Field(..., description="热点标题")
    user_domain: Optional[str] = Field(None, description="用户领域（如：科技、娱乐、职场等）")
    target_platforms: Optional[List[str]] = Field(None, description="目标平台列表")


class WritingAngle(BaseModel):
    """创作角度"""
    angle: str = Field(..., description="创作角度描述")
    title_suggestion: str = Field(..., description="标题建议")
    content_direction: str = Field(..., description="内容方向")
    recommended_tools: List[str] = Field(..., description="推荐的写作工具类型")
    target_audience: str = Field(..., description="目标受众")


class TopicSuggestResponse(BaseModel):
    """选题建议响应"""
    hot_title: str = Field(..., description="原热点标题")
    background: str = Field(..., description="热点背景分析")
    angles: List[WritingAngle] = Field(..., description="创作角度列表")
    keywords: List[str] = Field(..., description="相关关键词")


class ExtractKeywordsRequest(BaseModel):
    """提取关键词请求"""
    title: str = Field(..., description="热点标题")


class ExtractKeywordsResponse(BaseModel):
    """提取关键词响应"""
    title: str = Field(..., description="原标题")
    keywords: List[str] = Field(..., description="提取的关键词列表")
