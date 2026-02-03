"""
智谱AI (GLM) 服务
"""
from typing import Dict, Any, Optional
import httpx
from .base import AIServiceBase


class ZhipuService(AIServiceBase):
    """智谱AI服务"""
    
    def __init__(self, api_key: str, model: str = "glm-4", base_url: str = "https://open.bigmodel.cn/api/paas/v4"):
        super().__init__(api_key, model)
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        **kwargs
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """生成图片"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers=self.headers,
                    json={
                        "model": "cogview-3",
                        "prompt": prompt,
                        "size": size,
                        **kwargs
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["url"]
        except Exception as e:
            raise Exception(f"智谱AI图片生成失败: {str(e)}")
    
    async def generate_video(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """生成视频"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/videos/generations",
                    headers=self.headers,
                    json={
                        "model": "cogvideox",
                        "prompt": prompt,
                        **kwargs
                    },
                    timeout=300.0
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["url"]
        except Exception as e:
            raise Exception(f"智谱AI视频生成失败: {str(e)}")
