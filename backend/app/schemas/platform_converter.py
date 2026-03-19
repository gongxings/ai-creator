"""
多平台内容转换相关 Schema
支持将已有内容转换为不同平台格式
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TargetPlatform(str, Enum):
    """目标平台"""
    WECHAT = "wechat_article"           # 微信公众号
    XIAOHONGSHU = "xiaohongshu_note"    # 小红书
    DOUYIN = "video_script"             # 抖音短视频脚本
    ZHIHU = "zhihu_answer"              # 知乎回答
    WEIBO = "weibo_post"                # 微博
    TOUTIAO = "toutiao_article"         # 今日头条
    BILIBILI = "bilibili_dynamic"       # B站动态


class PlatformInfo(BaseModel):
    """平台信息"""
    code: str = Field(..., description="平台代码")
    name: str = Field(..., description="平台中文名")
    icon: Optional[str] = Field(None, description="平台图标")
    max_length: Optional[int] = Field(None, description="内容长度限制")
    features: List[str] = Field(default_factory=list, description="平台特点")
    tips: List[str] = Field(default_factory=list, description="写作技巧")


class ConvertRequest(BaseModel):
    """转换请求"""
    creation_id: int = Field(..., description="原创作记录ID")
    target_platform: TargetPlatform = Field(..., description="目标平台")
    style_adjustment: Optional[str] = Field(None, description="风格调整说明")
    keep_structure: bool = Field(True, description="是否保留原文结构")
    add_emojis: bool = Field(False, description="是否添加表情符号（小红书等）")
    generate_tags: bool = Field(True, description="是否生成平台标签")


class ConvertResult(BaseModel):
    """转换结果"""
    original_platform: str = Field(..., description="原始平台")
    target_platform: str = Field(..., description="目标平台")
    original_title: str = Field(..., description="原标题")
    converted_title: str = Field(..., description="转换后标题")
    converted_content: str = Field(..., description="转换后内容")
    tags: List[str] = Field(default_factory=list, description="推荐标签")
    word_count: int = Field(..., description="字数统计")
    conversion_notes: List[str] = Field(default_factory=list, description="转换说明")
    creation_id: Optional[int] = Field(None, description="新创作记录ID")


class BatchConvertRequest(BaseModel):
    """批量转换请求"""
    creation_id: int = Field(..., description="原创作记录ID")
    target_platforms: List[TargetPlatform] = Field(..., description="目标平台列表")
    style_adjustment: Optional[str] = Field(None, description="风格调整说明")


class BatchConvertResult(BaseModel):
    """批量转换结果"""
    original_creation_id: int = Field(..., description="原创作记录ID")
    results: List[ConvertResult] = Field(..., description="转换结果列表")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")


class PlatformPreviewRequest(BaseModel):
    """平台预览请求"""
    content: str = Field(..., description="内容文本")
    target_platform: TargetPlatform = Field(..., description="目标平台")


class PlatformPreviewResult(BaseModel):
    """平台预览结果"""
    platform: str = Field(..., description="平台名称")
    preview_html: str = Field(..., description="预览HTML")
    word_count: int = Field(..., description="字数")
    estimated_read_time: int = Field(..., description="预计阅读时间（秒）")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
