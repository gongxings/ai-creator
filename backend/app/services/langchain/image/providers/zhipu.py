"""
智谱 AI CogView 图片生成

支持 CogView-3 系列模型
"""

import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class ZhipuImageGenerator(ImageGeneratorBase):
    """
    智谱 AI CogView 图片生成器
    
    支持模型：
    - cogview-3-plus: 高质量版本
    - cogview-3: 标准版本
    """
    
    provider_name = "zhipu"
    
    SUPPORTED_SIZES = ["1024x1024", "768x1344", "864x1152", "1344x768", "1152x864", "1440x720", "720x1440"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "cogview-3-plus",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://open.bigmodel.cn/api/paas/v4"
    
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
        
        # 验证尺寸
        if size not in self.SUPPORTED_SIZES:
            size = "1024x1024"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": prompt,
                "size": size,
            }
            
            # 智谱支持用户ID用于内容审核追踪
            if kwargs.get("user_id"):
                payload["user_id"] = kwargs["user_id"]
            
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
                    return ImageGenerationResult.fail(f"智谱 API 错误: {error_msg}", self.provider_name)
                
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
            logger.error(f"Zhipu image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["cogview-3-plus", "cogview-3"]
