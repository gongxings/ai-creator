"""
图片生成 Providers
"""

from .openai import OpenAIImageGenerator
from .stability import StabilityImageGenerator
from .zhipu import ZhipuImageGenerator
from .qwen import QwenImageGenerator
from .baidu import BaiduImageGenerator
from .doubao import DoubaoImageGenerator
from .hunyuan import HunyuanImageGenerator
from .google import GoogleImageGenerator
from .replicate import ReplicateImageGenerator

__all__ = [
    "OpenAIImageGenerator",
    "StabilityImageGenerator",
    "ZhipuImageGenerator",
    "QwenImageGenerator",
    "BaiduImageGenerator",
    "DoubaoImageGenerator",
    "HunyuanImageGenerator",
    "GoogleImageGenerator",
    "ReplicateImageGenerator",
]
