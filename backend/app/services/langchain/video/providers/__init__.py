"""
视频生成 Providers

各厂商的视频生成实现
"""

from .zhipu import ZhipuVideoGenerator
from .qwen import QwenVideoGenerator
from .doubao import DoubaoVideoGenerator
from .minimax import MiniMaxVideoGenerator
from .stability import StabilityVideoGenerator
from .replicate import ReplicateVideoGenerator

__all__ = [
    "ZhipuVideoGenerator",
    "QwenVideoGenerator",
    "DoubaoVideoGenerator",
    "MiniMaxVideoGenerator",
    "StabilityVideoGenerator",
    "ReplicateVideoGenerator",
]
