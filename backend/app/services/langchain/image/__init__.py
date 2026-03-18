"""
图片生成模块

支持 9 个厂商的图片生成：
- 国外：OpenAI (DALL-E), Stability AI, Google Imagen, Replicate
- 国内：智谱 (CogView), 通义 (Wanx), 百度, 豆包 (Seedream), 混元
"""

from .base import (
    ImageGeneratorBase,
    ImageGenerationResult,
    ImageGenerationTool,
    ImageSize,
    ImageQuality,
    ImageStyle,
    create_image_tool,
)

from .factory import (
    ImageGeneratorFactory,
    generate_image,
)

__all__ = [
    # 基类
    "ImageGeneratorBase",
    "ImageGenerationResult",
    "ImageGenerationTool",
    "ImageSize",
    "ImageQuality", 
    "ImageStyle",
    "create_image_tool",
    
    # 工厂
    "ImageGeneratorFactory",
    "generate_image",
]
