"""
OpenAI服务实现
"""
from typing import Optional
import httpx

from .base import AIServiceBase


class OpenAIService(AIServiceBase):
    """OpenAI服务"""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        super().__init__(api_key, config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1") if config else "https://api.openai.com/v1"
        self.model = config.get("model", "gpt-4") if config else "gpt-4"
        self.image_model = config.get("image_model", "dall-e-3") if config else "dall-e-3"
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": kwargs.get("model", self.model),
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens or 2000,
                    "temperature": temperature or 0.7,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成图片"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": kwargs.get("model", self.image_model),
                    "prompt": prompt,
                    "size": size or "1024x1024",
                    "quality": quality or "standard",
                    "n": 1,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["url"]
    
    async def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False
