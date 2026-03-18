"""
热点追踪相关 Schema
"""
from typing import List, Optional
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


class PlatformInfo(BaseModel):
    """平台信息"""
    code: str = Field(..., description="平台代码")
    name: str = Field(..., description="平台中文名")
    icon: Optional[str] = Field(None, description="平台图标")
    color: Optional[str] = Field(None, description="平台主题色")


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
