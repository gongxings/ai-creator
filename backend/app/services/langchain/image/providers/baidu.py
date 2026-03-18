"""
百度文心一格图片生成

支持百度 AI 绘画模型
"""

import asyncio
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class BaiduImageGenerator(ImageGeneratorBase):
    """
    百度文心一格图片生成器
    
    注意：百度需要双密钥认证（API Key + Secret Key）
    """
    
    provider_name = "baidu"
    
    SUPPORTED_SIZES = ["1024x1024", "512x512", "768x768", "1024x768", "768x1024"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "sd_xl",
        secret_key: str = "",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.secret_key = secret_key
        self.base_url = api_base or "https://aip.baidubce.com"
        self._access_token = None
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            return self._access_token
        
        url = f"{self.base_url}/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=params)
            if response.status_code != 200:
                raise Exception(f"获取 access_token 失败: {response.status_code}")
            
            data = response.json()
            self._access_token = data.get("access_token")
            return self._access_token
    
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
            access_token = await self._get_access_token()
            
            url = f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/{model}"
            
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "n": min(n, 4),
            }
            
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    params={"access_token": access_token},
                    json=payload
                )
                
                if response.status_code != 200:
                    return ImageGenerationResult.fail(f"百度 API 错误: {response.status_code}", self.provider_name)
                
                data = response.json()
                
                if "error_code" in data:
                    return ImageGenerationResult.fail(
                        f"百度 API 错误: {data.get('error_msg', data.get('error_code'))}",
                        self.provider_name
                    )
                
                images = []
                for item in data.get("data", []):
                    if "b64_image" in item:
                        images.append(item["b64_image"])
                    elif "image" in item:
                        images.append(item["image"])
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name,
                    is_base64=True
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Baidu image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["sd_xl"]
