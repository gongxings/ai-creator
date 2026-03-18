"""
图片生成基类

定义图片生成的统一接口，所有厂商的实现都继承此基类。
同时提供 LangChain Tool 包装，便于 Agent 调用图片生成能力。
"""

import base64
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ImageSize(str, Enum):
    """标准图片尺寸"""
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    LANDSCAPE_1024_768 = "1024x768"
    LANDSCAPE_1280_720 = "1280x720"
    LANDSCAPE_1920_1080 = "1920x1080"
    PORTRAIT_768_1024 = "768x1024"
    PORTRAIT_720_1280 = "720x1280"
    PORTRAIT_1080_1920 = "1080x1920"


class ImageQuality(str, Enum):
    """图片质量"""
    STANDARD = "standard"
    HD = "hd"
    ULTRA = "ultra"


class ImageStyle(str, Enum):
    """图片风格"""
    NATURAL = "natural"           # 自然/写实
    VIVID = "vivid"               # 鲜艳
    ANIME = "anime"               # 动漫
    ARTISTIC = "artistic"         # 艺术
    PHOTOGRAPHIC = "photographic" # 摄影
    DIGITAL_ART = "digital_art"   # 数字艺术
    CINEMATIC = "cinematic"       # 电影感


@dataclass
class ImageGenerationResult:
    """图片生成结果"""
    success: bool
    images: List[str] = field(default_factory=list)  # URL 或 base64 列表
    is_base64: bool = False                           # 是否为 base64 编码
    model: str = ""                                   # 使用的模型
    provider: str = ""                                # 厂商
    revised_prompt: Optional[str] = None              # 优化后的提示词
    error: Optional[str] = None                       # 错误信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "images": self.images,
            "is_base64": self.is_base64,
            "model": self.model,
            "provider": self.provider,
            "revised_prompt": self.revised_prompt,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def ok(
        cls,
        images: List[str],
        model: str = "",
        provider: str = "",
        is_base64: bool = False,
        revised_prompt: str = None,
        **metadata
    ) -> "ImageGenerationResult":
        """成功结果"""
        return cls(
            success=True,
            images=images,
            is_base64=is_base64,
            model=model,
            provider=provider,
            revised_prompt=revised_prompt,
            metadata=metadata
        )
    
    @classmethod
    def fail(cls, error: str, provider: str = "") -> "ImageGenerationResult":
        """失败结果"""
        return cls(success=False, error=error, provider=provider)


class ImageGeneratorBase(ABC):
    """
    图片生成器基类
    
    所有厂商的图片生成实现都需要继承此类。
    
    Example:
        >>> class OpenAIImageGenerator(ImageGeneratorBase):
        ...     provider_name = "openai"
        ...     
        ...     async def generate(self, prompt, **kwargs):
        ...         # 调用 OpenAI DALL-E API
        ...         pass
    """
    
    # 子类必须定义
    provider_name: str = ""
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs
    ):
        """
        初始化生成器
        
        Args:
            api_key: API 密钥
            api_base: 自定义 API 地址
            default_model: 默认模型
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.api_base = api_base
        self.default_model = default_model
        self.extra_config = kwargs
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        n: int = 1,
        model: Optional[str] = None,
        **kwargs
    ) -> ImageGenerationResult:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            negative_prompt: 负面提示词（不希望出现的内容）
            size: 图片尺寸 (如 "1024x1024")
            quality: 图片质量 (standard/hd)
            style: 图片风格
            n: 生成数量
            model: 模型名称（覆盖默认）
            **kwargs: 厂商特定参数
            
        Returns:
            ImageGenerationResult
        """
        pass
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的图片尺寸"""
        return ["1024x1024"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return []
    
    def validate_size(self, size: str) -> bool:
        """验证尺寸是否支持"""
        return size in self.get_supported_sizes()
    
    def parse_size(self, size: str) -> tuple:
        """解析尺寸字符串为 (width, height)"""
        try:
            parts = size.lower().split("x")
            return int(parts[0]), int(parts[1])
        except:
            return 1024, 1024


# ============================================================================
# LangChain Tool 包装
# ============================================================================

class ImageGenerationInput(BaseModel):
    """图片生成工具输入参数"""
    prompt: str = Field(description="图片描述，详细描述想要生成的图片内容")
    negative_prompt: Optional[str] = Field(
        default=None,
        description="负面提示词，描述不希望在图片中出现的内容"
    )
    size: str = Field(
        default="1024x1024",
        description="图片尺寸，如 1024x1024, 1280x720 等"
    )
    style: Optional[str] = Field(
        default=None,
        description="图片风格，如 natural, vivid, anime, photographic 等"
    )
    n: int = Field(
        default=1,
        description="生成图片数量（1-4）",
        ge=1,
        le=4
    )


class ImageGenerationTool(BaseTool):
    """
    图片生成 LangChain Tool
    
    将图片生成器包装为 LangChain Tool，便于 Agent 调用。
    
    Example:
        >>> generator = OpenAIImageGenerator(api_key="sk-xxx")
        >>> tool = ImageGenerationTool(generator=generator)
        >>> result = await tool.ainvoke({"prompt": "一只可爱的猫咪"})
    """
    
    name: str = "image_generation"
    description: str = """生成图片。根据文字描述生成对应的图片。
适合用于：创建插图、生成配图、可视化概念等场景。
输入详细的图片描述，可以指定风格和尺寸。"""
    
    args_schema: type = ImageGenerationInput
    
    generator: ImageGeneratorBase = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, generator: ImageGeneratorBase, **kwargs):
        super().__init__(generator=generator, **kwargs)
        # 更新 tool 名称以包含厂商信息
        self.name = f"image_generation_{generator.provider_name}"
        self.description = f"使用 {generator.provider_name} 生成图片。{self.description}"
    
    def _run(self, **kwargs) -> str:
        """同步执行"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._arun(**kwargs)
                    )
                    return future.result()
            return asyncio.run(self._arun(**kwargs))
        except RuntimeError:
            return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """异步执行"""
        try:
            result = await self.generator.generate(**kwargs)
            
            if result.success:
                # 返回图片信息
                images_info = []
                for i, img in enumerate(result.images):
                    if result.is_base64:
                        images_info.append(f"图片 {i+1}: [Base64 数据，长度 {len(img)} 字符]")
                    else:
                        images_info.append(f"图片 {i+1}: {img}")
                
                output = f"成功生成 {len(result.images)} 张图片\n"
                output += "\n".join(images_info)
                if result.revised_prompt:
                    output += f"\n优化后的提示词: {result.revised_prompt}"
                return output
            else:
                return f"图片生成失败: {result.error}"
                
        except Exception as e:
            logger.error(f"Image generation error: {e}", exc_info=True)
            return f"图片生成错误: {str(e)}"


def create_image_tool(generator: ImageGeneratorBase) -> ImageGenerationTool:
    """
    从图片生成器创建 LangChain Tool
    
    Args:
        generator: 图片生成器实例
        
    Returns:
        ImageGenerationTool
    """
    return ImageGenerationTool(generator=generator)
