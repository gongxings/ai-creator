"""
OpenAI DALL-E 图片生成

支持 DALL-E 2 和 DALL-E 3 模型
"""

import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class OpenAIImageGenerator(ImageGeneratorBase):
    """
    OpenAI DALL-E 图片生成器
    
    支持模型：
    - dall-e-3: 更高质量，支持 1024x1024, 1024x1792, 1792x1024
    - dall-e-2: 支持 256x256, 512x512, 1024x1024
    """
    
    provider_name = "openai"
    
    # DALL-E 3 支持的尺寸
    DALLE3_SIZES = ["1024x1024", "1024x1792", "1792x1024"]
    # DALL-E 2 支持的尺寸
    DALLE2_SIZES = ["256x256", "512x512", "1024x1024"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "dall-e-3",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.openai.com/v1"
    
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
            prompt: 图片描述
            negative_prompt: 负面提示词（DALL-E 不直接支持，会合并到 prompt）
            size: 图片尺寸
            quality: 图片质量 (standard/hd)，仅 DALL-E 3 支持 hd
            style: 风格 (vivid/natural)，仅 DALL-E 3 支持
            n: 生成数量，DALL-E 3 只支持 n=1
            model: 模型名称
        """
        model = model or self.default_model
        
        # 验证参数
        if model == "dall-e-3":
            if size not in self.DALLE3_SIZES:
                size = "1024x1024"
            n = 1  # DALL-E 3 只支持 n=1
        else:
            if size not in self.DALLE2_SIZES:
                size = "1024x1024"
            quality = "standard"  # DALL-E 2 不支持 hd
            style = None
        
        # 处理负面提示词
        full_prompt = prompt
        if negative_prompt:
            full_prompt = f"{prompt}. Avoid: {negative_prompt}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "n": n,
                "size": size,
                "quality": quality,
            }
            
            if style and model == "dall-e-3":
                payload["style"] = style
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", str(response.status_code))
                    return ImageGenerationResult.fail(f"OpenAI API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                
                images = []
                revised_prompt = None
                
                for item in data.get("data", []):
                    if "url" in item:
                        images.append(item["url"])
                    elif "b64_json" in item:
                        images.append(item["b64_json"])
                    
                    # DALL-E 3 会返回优化后的提示词
                    if "revised_prompt" in item and not revised_prompt:
                        revised_prompt = item["revised_prompt"]
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name,
                    revised_prompt=revised_prompt
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"OpenAI image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return list(set(self.DALLE3_SIZES + self.DALLE2_SIZES))
    
    def get_supported_models(self) -> List[str]:
        return ["dall-e-3", "dall-e-2"]
