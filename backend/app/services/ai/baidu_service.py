"""
百度文心一言服务
"""
from typing import Dict, Any, Optional
import httpx
from .base import BaseAIService


class BaiduService(BaseAIService):
    """百度文心一言服务"""
    
    def __init__(self, api_key: str, secret_key: str, model: str = "ernie-bot-4"):
        super().__init__(api_key, model)
        self.secret_key = secret_key
        self.access_token = None
        self.base_url = "https://aip.baidubce.com"
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token:
            return self.access_token
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/2.0/token",
                    params={
                        "grant_type": "client_credentials",
                        "client_id": self.api_key,
                        "client_secret": self.secret_key
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                self.access_token = data["access_token"]
                return self.access_token
        except Exception as e:
            raise Exception(f"获取百度访问令牌失败: {str(e)}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        try:
            access_token = await self._get_access_token()
            
            # 根据模型选择端点
            endpoint_map = {
                "ernie-bot-4": "completions_pro",
                "ernie-bot": "completions",
                "ernie-bot-turbo": "eb-instant"
            }
            endpoint = endpoint_map.get(self.model, "completions_pro")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{endpoint}",
                    params={"access_token": access_token},
                    json={
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        **kwargs
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["result"]
        except Exception as e:
            raise Exception(f"百度文心一言API调用失败: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """生成图片"""
        try:
            access_token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl",
                    params={"access_token": access_token},
                    json={
                        "prompt": prompt,
                        "size": size,
                        **kwargs
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                return data["data"]["img_urls"][0]
        except Exception as e:
            raise Exception(f"百度图片生成失败: {str(e)}")
    
    async def generate_video(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """生成视频（暂不支持）"""
        raise NotImplementedError("百度暂不支持视频生成功能")
