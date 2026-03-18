"""
火山引擎豆包 Seedream 图片生成

支持即梦系列模型
"""

import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class DoubaoImageGenerator(ImageGeneratorBase):
    """
    火山引擎豆包图片生成器
    
    支持模型：
    - seedream-5.0-lite: 轻量版
    - seedream-4.5: 高质量版
    - seedream-4.0
    - seedream-3.0
    """
    
    provider_name = "doubao"
    
    SUPPORTED_SIZES = ["1024x1024", "512x512", "768x768", "1280x720", "720x1280"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "seedream-5.0-lite",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://ark.cn-beijing.volces.com/api/v3"
    
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
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": prompt,
                "width": width,
                "height": height,
                "n": min(n, 4),
            }
            
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
            
            # 豆包支持的风格参数
            if style:
                payload["style"] = style
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return ImageGenerationResult.fail(f"豆包 API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                
                images = []
                for item in data.get("data", []):
                    if "url" in item:
                        images.append(item["url"])
                    elif "b64_json" in item:
                        images.append(item["b64_json"])
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Doubao image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["seedream-5.0-lite", "seedream-4.5", "seedream-4.0", "seedream-3.0"]
