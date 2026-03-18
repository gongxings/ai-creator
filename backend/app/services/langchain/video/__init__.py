"""
视频生成模块

提供统一的视频生成接口，支持 6 个厂商：
- 智谱 (CogVideoX)
- 通义 (Wanx Video)
- 火山豆包 (Seedance)
- MiniMax (video-01)
- Stability (Stable Video Diffusion)
- Replicate (Zeroscope 等)
"""

from .base import (
    VideoSize,
    VideoQuality,
    VideoStyle,
    VideoGenerationMode,
    VideoGenerationResult,
    VideoGeneratorBase,
    VideoGenerationInput,
    VideoGenerationTool,
    VideoTaskCheckTool,
    create_video_tool,
    create_video_tools,
)
from .factory import (
    VideoGeneratorFactory,
    generate_video,
    generate_video_from_image,
)

__all__ = [
    # 枚举类型
    "VideoSize",
    "VideoQuality",
    "VideoStyle",
    "VideoGenerationMode",
    # 结果类
    "VideoGenerationResult",
    # 基类
    "VideoGeneratorBase",
    # 工厂
    "VideoGeneratorFactory",
    # LangChain Tool
    "VideoGenerationInput",
    "VideoGenerationTool",
    "VideoTaskCheckTool",
    "create_video_tool",
    "create_video_tools",
    # 便捷函数
    "generate_video",
    "generate_video_from_image",
]
