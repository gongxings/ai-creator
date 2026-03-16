"""
OpenAI服务实现
"""
from typing import Optional, AsyncGenerator
import httpx
import json
import asyncio
import logging

from .base import AIServiceBase

logger = logging.getLogger(__name__)


class OpenAIService(AIServiceBase):
    """OpenAI服务"""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        super().__init__(api_key, config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1") if config else "https://api.openai.com/v1"
        self.model = config.get("model", "gpt-4") if config else "gpt-4"
        self.image_model = config.get("image_model", "dall-e-3") if config else "dall-e-3"
        self.max_retries = 3
        self.retry_delay = 5  # 重试间隔秒数
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本，支持429限流重试"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # OpenRouter 需要额外的 headers
        if "openrouter" in self.base_url.lower():
            headers["HTTP-Referer"] = "http://localhost:3001"
            headers["X-Title"] = "AI Creator"
        
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens or 2000,
            "temperature": temperature or 0.7,
        }
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=request_data,
                        timeout=120.0,
                    )
                    
                    # 如果是429限流错误，进行重试
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                        logger.warning(f"Rate limited (429), attempt {attempt + 1}/{self.max_retries}, waiting {retry_after}s...")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            response.raise_for_status()
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # 处理返回内容
                    content = data["choices"][0]["message"].get("content")
                    if content is None:
                        # 某些模型可能在reasoning字段返回内容
                        reasoning = data["choices"][0]["message"].get("reasoning")
                        if reasoning:
                            content = reasoning
                        else:
                            content = ""
                    
                    return content
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429 and attempt < self.max_retries - 1:
                    logger.warning(f"Rate limited (429), attempt {attempt + 1}/{self.max_retries}, retrying...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
            except Exception as e:
                last_error = e
                logger.error(f"API call failed: {e}")
                raise
        
        # 所有重试都失败
        raise last_error or Exception("所有重试都失败")
    
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
    
    async def chat_completion(
        self,
        messages: list,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """聊天完成接口（非流式）"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            return {
                "content": choice["message"]["content"],
                "usage": usage,
                "finish_reason": choice.get("finish_reason", "stop")
            }
    
    async def chat_completion_stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成接口 - 真正的流式响应"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
