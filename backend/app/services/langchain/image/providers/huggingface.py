"""
Hugging Face 图片生成

通过 Hugging Face Inference Endpoints (OpenAI兼容) 调用开源图片生成模型。

支持模型：
- stabilityai/stable-diffusion-xl-base-1.0
- stabilityai/stable-diffusion-2-1
- runwayml/stable-diffusion-v1-5
- stabilityai/sdxl-turbo

API文档: https://huggingface.co/docs/api-inference/
"""

import logging
from typing import List, Optional

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)





class HuggingFaceImageGenerator(ImageGeneratorBase):
    """
    Hugging Face 图片生成器
    
    使用 Hugging Face Inference API 调用开源图片生成模型。
    免费使用，有速率限制（约30请求/分钟）。
    
    特点：
    - 完全免费
    - 支持多种开源模型
    - 返回图片URL或base64
    """
    
    provider_name = "huggingface"
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "stabilityai/stable-diffusion-2-1",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
        "stabilityai/sdxl-turbo",
    ]
    
    # 模型对应的推荐尺寸
    MODEL_SIZES = {
        "stabilityai/stable-diffusion-xl-base-1.0": ["1024x1024", "1024x768", "768x1024"],
        "stabilityai/sdxl-turbo": ["1024x1024", "512x512"],
        "stabilityai/stable-diffusion-2-1": ["768x768", "512x512"],
        "runwayml/stable-diffusion-v1-5": ["512x512", "512x768", "768x512"],
        "CompVis/stable-diffusion-v1-4": ["512x512", "256x256"],
    }
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "stabilityai/stable-diffusion-xl-base-1.0",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        # 使用 HuggingFace Router (OpenAI兼容接口)
        self.base_url = "https://router.huggingface.co/v1"
    
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
        生成图片 - 使用 OpenAI 兼容接口
        
        Args:
            prompt: 图片描述
            negative_prompt: 负面提示词
            size: 图片尺寸
            quality: 图片质量
            style: 风格提示词
            n: 生成数量
            model: 模型名称
        """
        from openai import AsyncOpenAI
        
        model = model or self.default_model
        
        logger.info(f"HuggingFace image generation: model={model}, size={size}")
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        # 构建提示词
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        try:
            # 使用 OpenAI 兼容接口
            client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=180.0,
                max_retries=2,
            )
            
            images = []
            
            # HF API 一次只能生成一张图片
            for i in range(min(n, 4)):
                try:
                    response = await client.images.generate(
                        model=model,
                        prompt=full_prompt,
                        size=size,
                        quality=quality if quality != "hd" else "standard",
                        n=1,
                    )
                    
                    if response.data and len(response.data) > 0:
                        img_url = response.data[0].url
                        if img_url:
                            images.append(img_url)
                            
                except Exception as e:
                    logger.warning(f"第 {i+1} 次尝试失败: {e}")
                    continue
            
            if images:
                return ImageGenerationResult.ok(
                    images=images,
                    model=model or self.default_model,
                    provider=self.provider_name,
                    is_base64=False
                )
            else:
                return ImageGenerationResult.fail(
                    f"未能生成图片，可能是因为模型 {model} 不支持图片生成或API调用失败",
                    self.provider_name
                )
                
        except Exception as e:
            logger.error(f"Hugging Face image generation error: {e}")
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["512x512", "768x768", "1024x1024", "1024x768", "768x1024"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
