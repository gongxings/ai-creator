"""
Google Imagen 图片生成

支持 Google Cloud Imagen API
"""

import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class GoogleImageGenerator(ImageGeneratorBase):
    """
    Google Imagen 图片生成器
    
    支持模型：
    - imagen-3.0-generate-001
    """
    
    provider_name = "google"
    
    SUPPORTED_SIZES = ["1024x1024", "896x1152", "1152x896"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "imagen-3.0-generate-001",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://generativelanguage.googleapis.com/v1beta"
    
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
        """生成图片"""
        model = model or self.default_model
        
        try:
            # 构建完整的提示词
            full_prompt = prompt
            if negative_prompt:
                full_prompt = f"{prompt}. Do not include: {negative_prompt}"
            
            # 解析尺寸
            width, height = self.parse_size(size)
            aspect_ratio = f"{width}:{height}"
            
            payload = {
                "instances": [
                    {
                        "prompt": full_prompt,
                    }
                ],
                "parameters": {
                    "sampleCount": min(n, 4),
                    "aspectRatio": aspect_ratio,
                }
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{model}:predict",
                    params={"key": self.api_key},
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return ImageGenerationResult.fail(f"Google API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                
                images = []
                for prediction in data.get("predictions", []):
                    if "bytesBase64Encoded" in prediction:
                        images.append(prediction["bytesBase64Encoded"])
                
                if not images:
                    return ImageGenerationResult.fail("未获取到图片", self.provider_name)
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name,
                    is_base64=True
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Google image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["imagen-3.0-generate-001"]
