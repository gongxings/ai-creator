"""
Stability AI 图片生成

支持 Stable Diffusion 3 等模型
"""

import base64
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class StabilityImageGenerator(ImageGeneratorBase):
    """
    Stability AI 图片生成器
    
    支持模型：
    - sd3-large: Stable Diffusion 3 Large
    - sd3-medium: Stable Diffusion 3 Medium
    - sd3-large-turbo: 快速版本
    """
    
    provider_name = "stability"
    
    SUPPORTED_SIZES = [
        "1024x1024", "1152x896", "896x1152",
        "1216x832", "832x1216", "1344x768",
        "768x1344", "1536x640", "640x1536"
    ]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "sd3-large",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.stability.ai/v2beta"
    
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
        
        # 确定输出格式
        output_format = kwargs.get("output_format", "png")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            }
            
            # SD3 使用 multipart/form-data
            form_data = {
                "prompt": prompt,
                "model": model,
                "output_format": output_format,
            }
            
            if negative_prompt:
                form_data["negative_prompt"] = negative_prompt
            
            # 设置宽高（需要是 64 的倍数）
            form_data["width"] = (width // 64) * 64
            form_data["height"] = (height // 64) * 64
            
            # 风格预设
            if style:
                form_data["style_preset"] = style
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.base_url}/stable-image/generate/sd3",
                    headers=headers,
                    data=form_data
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return ImageGenerationResult.fail(f"Stability API 错误: {error_msg}", self.provider_name)
                
                # 响应是二进制图片数据
                image_data = base64.b64encode(response.content).decode("utf-8")
                
                return ImageGenerationResult.ok(
                    images=[image_data],
                    model=model,
                    provider=self.provider_name,
                    is_base64=True
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Stability image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["sd3-large", "sd3-medium", "sd3-large-turbo", "stable-diffusion-xl-1024-v1-0"]
