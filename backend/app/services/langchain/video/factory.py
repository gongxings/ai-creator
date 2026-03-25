"""
视频生成工厂

统一创建各厂商的视频生成器实例。
支持 6 个厂商：智谱, 通义, 豆包, MiniMax, Stability, Replicate
"""

import logging
from typing import Dict, List, Optional, Type

from ..config import get_provider_config, Capability, get_video_providers
from .base import VideoGeneratorBase, VideoGenerationResult

logger = logging.getLogger(__name__)


class VideoGeneratorFactory:
    """
    视频生成器工厂
    
    统一创建各厂商的视频生成器实例。
    
    Example:
        >>> generator = VideoGeneratorFactory.create(
        ...     provider="zhipu",
        ...     api_key="xxx",
        ...     model="cogvideox"
        ... )
        >>> result = await generator.generate("一只猫在花园里奔跑")
    """
    
    # 厂商到生成器类的映射（延迟导入）
    _provider_mapping: Dict[str, str] = {
        "zhipu": ".providers.zhipu.ZhipuVideoGenerator",
        "qwen": ".providers.qwen.QwenVideoGenerator",
        "doubao": ".providers.doubao.DoubaoVideoGenerator",
        "minimax": ".providers.minimax.MiniMaxVideoGenerator",
        "stability": ".providers.stability.StabilityVideoGenerator",
        "replicate": ".providers.replicate.ReplicateVideoGenerator",
        "huggingface": ".providers.huggingface.HuggingFaceVideoGenerator",
        "modelscope": ".providers.modelscope.ModelScopeVideoGenerator",
    }
    
    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ) -> VideoGeneratorBase:
        """
        创建视频生成器实例
        
        Args:
            provider: 厂商标识 (zhipu, qwen, doubao, minimax, stability, replicate)
            api_key: API 密钥
            model: 模型名称（可选，使用厂商默认）
            api_base: 自定义 API 地址
            **kwargs: 其他参数（如 secret_key, group_id 等）
            
        Returns:
            VideoGeneratorBase 实例
            
        Raises:
            ValueError: 不支持的厂商或厂商不支持视频生成
        """
        provider_lower = provider.lower()
        
        # 检查厂商是否支持视频生成
        config = get_provider_config(provider_lower)
        if not config:
            raise ValueError(f"不支持的厂商: {provider}")
        
        if Capability.VIDEO not in config.capabilities:
            raise ValueError(f"厂商 {provider} 不支持视频生成")
        
        # 获取生成器类路径
        class_path = cls._provider_mapping.get(provider_lower)
        if not class_path:
            raise ValueError(f"未实现的视频生成厂商: {provider}")
        
        # 动态导入生成器类
        generator_class = cls._import_class(class_path)
        
        # 确定默认模型
        if not model and config.models.get("video"):
            model = config.models["video"][0]
        
        # 确定 API 地址
        if not api_base:
            api_base = config.base_url
        
        logger.info(f"Creating video generator: {provider}/{model}")
        
        return generator_class(
            api_key=api_key,
            api_base=api_base,
            default_model=model,
            **kwargs
        )
    
    @classmethod
    def _import_class(cls, class_path: str) -> Type[VideoGeneratorBase]:
        """动态导入生成器类"""
        try:
            # class_path 格式: ".providers.zhipu.ZhipuVideoGenerator"
            module_path, class_name = class_path.rsplit(".", 1)
            
            # 相对于当前包导入
            from importlib import import_module
            full_module = f"app.services.langchain.video{module_path}"
            module = import_module(full_module)
            
            return getattr(module, class_name)
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import {class_path}: {e}")
            raise ImportError(f"无法导入视频生成器: {class_path}") from e
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持视频生成的厂商列表"""
        return get_video_providers()
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """检查厂商是否支持视频生成"""
        provider_lower = provider.lower()
        config = get_provider_config(provider_lower)
        return config is not None and Capability.VIDEO in config.capabilities
    
    @classmethod
    def get_provider_models(cls, provider: str) -> List[str]:
        """获取厂商支持的视频模型列表"""
        config = get_provider_config(provider.lower())
        if config and "video" in config.models:
            return config.models["video"]
        return []


# ============================================================================
# 便捷函数
# ============================================================================

async def generate_video(
    provider: str,
    api_key: str,
    prompt: str,
    model: Optional[str] = None,
    size: str = "1280x720",
    duration: float = 4.0,
    **kwargs
) -> VideoGenerationResult:
    """
    快速生成视频（一次性调用）
    
    Args:
        provider: 厂商标识
        api_key: API 密钥
        prompt: 视频描述
        model: 模型名称
        size: 视频尺寸
        duration: 视频时长（秒）
        **kwargs: 其他参数
        
    Returns:
        VideoGenerationResult
        
    Example:
        >>> result = await generate_video(
        ...     "zhipu", "xxx",
        ...     "一只金毛犬在海滩上奔跑",
        ...     size="1280x720",
        ...     duration=4.0
        ... )
        >>> if result.success:
        ...     print(result.videos[0])
    """
    generator = VideoGeneratorFactory.create(
        provider=provider,
        api_key=api_key,
        model=model,
        **kwargs
    )
    return await generator.generate(
        prompt=prompt,
        size=size,
        duration=duration,
        **kwargs
    )


async def generate_video_from_image(
    provider: str,
    api_key: str,
    prompt: str,
    image_url: str,
    model: Optional[str] = None,
    size: str = "1280x720",
    duration: float = 4.0,
    **kwargs
) -> VideoGenerationResult:
    """
    从图片生成视频（图生视频）
    
    Args:
        provider: 厂商标识
        api_key: API 密钥
        prompt: 视频描述
        image_url: 参考图片 URL
        model: 模型名称
        size: 视频尺寸
        duration: 视频时长（秒）
        **kwargs: 其他参数
        
    Returns:
        VideoGenerationResult
        
    Example:
        >>> result = await generate_video_from_image(
        ...     "zhipu", "xxx",
        ...     "让图片中的人物微笑并挥手",
        ...     "https://example.com/photo.jpg",
        ... )
    """
    generator = VideoGeneratorFactory.create(
        provider=provider,
        api_key=api_key,
        model=model,
        **kwargs
    )
    
    if not generator.supports_image_to_video():
        return VideoGenerationResult.fail(
            f"厂商 {provider} 不支持图生视频功能",
            provider
        )
    
    return await generator.generate(
        prompt=prompt,
        image_url=image_url,
        size=size,
        duration=duration,
        **kwargs
    )
