"""
图片生成工厂

统一创建各厂商的图片生成器实例。
支持 9 个厂商：OpenAI, Stability, 智谱, 通义, 百度, 豆包, 混元, Google, Replicate
"""

import logging
from typing import Dict, List, Optional, Type

from ..config import get_provider_config, Capability, get_image_providers
from .base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class ImageGeneratorFactory:
    """
    图片生成器工厂
    
    统一创建各厂商的图片生成器实例。
    
    Example:
        >>> generator = ImageGeneratorFactory.create(
        ...     provider="openai",
        ...     api_key="sk-xxx",
        ...     model="dall-e-3"
        ... )
        >>> result = await generator.generate("一只可爱的猫咪")
    """
    
    # 厂商到生成器类的映射（延迟导入）
    _provider_mapping: Dict[str, str] = {
        "openai": ".providers.openai.OpenAIImageGenerator",
        "stability": ".providers.stability.StabilityImageGenerator",
        "zhipu": ".providers.zhipu.ZhipuImageGenerator",
        "qwen": ".providers.qwen.QwenImageGenerator",
        "baidu": ".providers.baidu.BaiduImageGenerator",
        "doubao": ".providers.doubao.DoubaoImageGenerator",
        "hunyuan": ".providers.hunyuan.HunyuanImageGenerator",
        "google": ".providers.google.GoogleImageGenerator",
        "replicate": ".providers.replicate.ReplicateImageGenerator",
    }
    
    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ) -> ImageGeneratorBase:
        """
        创建图片生成器实例
        
        Args:
            provider: 厂商标识 (openai, stability, zhipu, etc.)
            api_key: API 密钥
            model: 模型名称（可选，使用厂商默认）
            api_base: 自定义 API 地址
            **kwargs: 其他参数（如 secret_key）
            
        Returns:
            ImageGeneratorBase 实例
            
        Raises:
            ValueError: 不支持的厂商或厂商不支持图片生成
        """
        provider_lower = provider.lower()
        
        # 检查厂商是否支持图片生成
        config = get_provider_config(provider_lower)
        if not config:
            raise ValueError(f"不支持的厂商: {provider}")
        
        if Capability.IMAGE not in config.capabilities:
            raise ValueError(f"厂商 {provider} 不支持图片生成")
        
        # 获取生成器类路径
        class_path = cls._provider_mapping.get(provider_lower)
        if not class_path:
            raise ValueError(f"未实现的图片生成厂商: {provider}")
        
        # 动态导入生成器类
        generator_class = cls._import_class(class_path)
        
        # 确定默认模型
        if not model and config.models.get("image"):
            model = config.models["image"][0]
        
        # 确定 API 地址
        if not api_base:
            api_base = config.base_url
        
        logger.info(f"Creating image generator: {provider}/{model}")
        
        return generator_class(
            api_key=api_key,
            api_base=api_base,
            default_model=model,
            **kwargs
        )
    
    @classmethod
    def _import_class(cls, class_path: str) -> Type[ImageGeneratorBase]:
        """动态导入生成器类"""
        try:
            # class_path 格式: ".providers.openai.OpenAIImageGenerator"
            module_path, class_name = class_path.rsplit(".", 1)
            
            # 相对于当前包导入
            from importlib import import_module
            full_module = f"app.services.langchain.image{module_path}"
            module = import_module(full_module)
            
            return getattr(module, class_name)
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import {class_path}: {e}")
            raise ImportError(f"无法导入图片生成器: {class_path}") from e
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持图片生成的厂商列表"""
        return get_image_providers()
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """检查厂商是否支持图片生成"""
        provider_lower = provider.lower()
        config = get_provider_config(provider_lower)
        return config is not None and Capability.IMAGE in config.capabilities
    
    @classmethod
    def get_provider_models(cls, provider: str) -> List[str]:
        """获取厂商支持的图片模型列表"""
        config = get_provider_config(provider.lower())
        if config and "image" in config.models:
            return config.models["image"]
        return []


# ============================================================================
# 便捷函数
# ============================================================================

async def generate_image(
    provider: str,
    api_key: str,
    prompt: str,
    model: Optional[str] = None,
    size: str = "1024x1024",
    **kwargs
) -> ImageGenerationResult:
    """
    快速生成图片（一次性调用）
    
    Args:
        provider: 厂商标识
        api_key: API 密钥
        prompt: 图片描述
        model: 模型名称
        size: 图片尺寸
        **kwargs: 其他参数
        
    Returns:
        ImageGenerationResult
        
    Example:
        >>> result = await generate_image(
        ...     "openai", "sk-xxx",
        ...     "一只在阳光下打盹的橘猫",
        ...     size="1024x1024"
        ... )
        >>> if result.success:
        ...     print(result.images[0])
    """
    generator = ImageGeneratorFactory.create(
        provider=provider,
        api_key=api_key,
        model=model,
        **kwargs
    )
    return await generator.generate(prompt=prompt, size=size, **kwargs)
