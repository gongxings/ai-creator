"""
配图功能相关 Schema
支持图库搜索（Unsplash/Pexels）和 AI 生成
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ImageSource(str, Enum):
    """图片来源"""
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    AI_GENERATED = "ai_generated"


class ImageOrientation(str, Enum):
    """图片方向"""
    LANDSCAPE = "landscape"  # 横向
    PORTRAIT = "portrait"    # 纵向
    SQUARE = "square"        # 正方形


class ImageSearchRequest(BaseModel):
    """图库搜索请求"""
    query: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    source: Optional[ImageSource] = Field(None, description="指定图库来源，不指定则搜索全部")
    orientation: Optional[ImageOrientation] = Field(None, description="图片方向")
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=30)
    color: Optional[str] = Field(None, description="主色调（仅 Unsplash 支持）")


class ImageItem(BaseModel):
    """图片项"""
    id: str = Field(..., description="图片ID")
    source: ImageSource = Field(..., description="图片来源")
    url: str = Field(..., description="图片URL")
    thumb_url: str = Field(..., description="缩略图URL")
    width: int = Field(..., description="图片宽度")
    height: int = Field(..., description="图片高度")
    alt: Optional[str] = Field(None, description="图片描述")
    photographer: Optional[str] = Field(None, description="摄影师")
    photographer_url: Optional[str] = Field(None, description="摄影师主页")
    download_url: Optional[str] = Field(None, description="下载链接")
    color: Optional[str] = Field(None, description="主色调")


class ImageSearchResponse(BaseModel):
    """图库搜索响应"""
    query: str = Field(..., description="搜索关键词")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页数量")
    images: List[ImageItem] = Field(default_factory=list, description="图片列表")


class KeywordSuggestRequest(BaseModel):
    """关键词建议请求"""
    content: str = Field(..., description="文章内容或主题", min_length=2, max_length=1000)
    count: int = Field(5, description="建议数量", ge=1, le=10)


class KeywordSuggestResponse(BaseModel):
    """关键词建议响应"""
    keywords: List[str] = Field(..., description="建议的搜索关键词")
    keywords_en: List[str] = Field(..., description="英文关键词（图库搜索更准确）")
