"""
豆包网页版AI服务 - 基于Cookie调用
支持文本生成、图片生成、视频生成
"""
import httpx
import json
import re
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator

from app.services.ai.cookie_based_service import CookieBasedAIService

logger = logging.getLogger(__name__)


class DoubaoService(CookieBasedAIService):
    """豆包网页版AI服务"""
    
    # 豆包网页版API端点
    BASE_URL = "https://www.doubao.com"
    CHAT_API = f"{BASE_URL}/api/chat"
    CHAT_STREAM_API = f"{BASE_URL}/api/chat/stream"
    CHAT_COMPLETIONS_API = f"{BASE_URL}/api/chat/completions"
    IMAGE_API = f"{BASE_URL}/samantha/image/gen_image"
    
    # 默认Bot ID
    DEFAULT_BOT_ID = "7358044466096914465"
    
    def get_platform_name(self) -> str:
        return "doubao"
    
    def get_check_url(self) -> str:
        return self.BASE_URL
    
    def get_headers(self, referer: Optional[str] = None, content_type: str = "application/json") -> Dict[str, str]:
        """
        构建豆包请求头
        """
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        headers = {
            "Cookie": cookie_str,
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": referer or self.BASE_URL,
            "Origin": self.BASE_URL,
        }
        
        if content_type:
            headers["Content-Type"] = content_type
        
        return headers
    
    async def validate_cookies(self) -> bool:
        """
        验证Cookie是否有效
        """
        try:
            headers = self.get_headers()
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers=headers
                )
                
                if response.status_code == 200:
                    content = response.text
                    # 检查是否需要登录
                    if "login" in content.lower() and "请登录" in content:
                        logger.warning("Doubao cookie is expired - login required")
                        return False
                    logger.info("Doubao cookie validation successful")
                    return True
                else:
                    logger.warning(f"Doubao cookie validation failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Doubao cookie validation error: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        conversation_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大令牌数（豆包网页版不支持此参数）
            temperature: 温度参数（豆包网页版不支持此参数）
            conversation_id: 会话ID（可选）
            bot_id: 机器人ID（可选）
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        headers = self.get_headers()
        
        payload = {
            "conversation_id": conversation_id or "",
            "bot_id": bot_id or self.DEFAULT_BOT_ID,
            "user_input": prompt,
            "stream": False,
        }
        
        logger.info(f"Doubao text generation - prompt length: {len(prompt)}")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            response = await client.post(
                self.CHAT_COMPLETIONS_API,
                headers=headers,
                json=payload,
            )
            
            if response.status_code == 401:
                logger.error("Doubao API returned 401 - Cookie may be expired")
                raise ValueError("Cookie已过期，请重新登录授权")
            
            response.raise_for_status()
            
            data = response.json()
            
            # 提取返回的文本
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            
            # 尝试其他格式
            if "text" in data:
                return data["text"]
            
            if "content" in data:
                return data["content"]
            
            logger.warning(f"Unexpected response format: {data}")
            return str(data)
    
    async def generate_text_stream(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式生成文本
        
        Args:
            prompt: 提示词
            conversation_id: 会话ID（可选）
            bot_id: 机器人ID（可选）
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        headers = self.get_headers()
        
        payload = {
            "conversation_id": conversation_id or "",
            "bot_id": bot_id or self.DEFAULT_BOT_ID,
            "user_input": prompt,
            "stream": True,
        }
        
        logger.info(f"Doubao stream text generation - prompt length: {len(prompt)}")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            async with client.stream(
                "POST",
                self.CHAT_STREAM_API,
                headers=headers,
                json=payload,
            ) as response:
                
                if response.status_code == 401:
                    logger.error("Doubao API returned 401 - Cookie may be expired")
                    raise ValueError("Cookie已过期，请重新登录授权")
                
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                data = json.loads(data_str)
                                if "text" in data:
                                    yield data["text"]
                                elif "content" in data:
                                    yield data["content"]
                            except json.JSONDecodeError:
                                continue
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图片
        
        Args:
            prompt: 图片描述
            size: 图片尺寸（豆包可能不完全支持所有尺寸）
            style: 风格
            negative_prompt: 负面提示词
            num_images: 生成数量
            **kwargs: 其他参数
            
        Returns:
            {
                "images": [...]  # 图片URL列表
                "prompt": str    # 原始提示词
                "error": str     # 错误信息（可选）
            }
        """
        headers = self.get_headers()
        
        # 方法1：通过聊天API生成图片（让AI画图）
        full_prompt = f"请帮我生成一张图片：{prompt}"
        if style:
            full_prompt += f"，风格：{style}"
        if negative_prompt:
            full_prompt += f"，避免：{negative_prompt}"
        
        payload = {
            "user_input": full_prompt,
            "bot_id": self.DEFAULT_BOT_ID,
            "stream": False,
        }
        
        logger.info(f"Doubao image generation - prompt: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=180.0) as client:
                response = await client.post(
                    self.CHAT_COMPLETIONS_API,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 401:
                    return {
                        "images": [],
                        "prompt": prompt,
                        "error": "Cookie已过期，请重新登录授权"
                    }
                
                response.raise_for_status()
                data = response.json()
                
                # 提取图片URL
                images = []
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        # 提取Markdown格式的图片链接 ![...](url)
                        image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                        images.extend(image_urls)
                        # 也提取纯URL
                        plain_urls = re.findall(r'https?://[^\s\)]+\.(?:png|jpg|jpeg|gif|webp)', content)
                        for url in plain_urls:
                            if url not in images:
                                images.append(url)
                
                return {
                    "images": images,
                    "prompt": prompt,
                }
                
        except Exception as e:
            logger.error(f"Doubao image generation failed: {e}")
            return {
                "images": [],
                "prompt": prompt,
                "error": str(e)
            }
    
    async def generate_image_direct(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        直接调用图片生成API（如果豆包支持）
        
        注意：此方法依赖于豆包的内部API，可能会发生变化
        """
        headers = self.get_headers()
        
        # 尺寸映射
        size_mapping = {
            "1024x1024": {"width": 1024, "height": 1024},
            "512x512": {"width": 512, "height": 512},
            "1024x768": {"width": 1024, "height": 768},
            "768x1024": {"width": 768, "height": 1024},
        }
        
        dimensions = size_mapping.get(size, {"width": 1024, "height": 1024})
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "width": dimensions["width"],
            "height": dimensions["height"],
            "num_images": num_images,
            "style": style or "auto",
        }
        
        logger.info(f"Doubao direct image generation - prompt: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=180.0) as client:
                response = await client.post(
                    self.IMAGE_API,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 401:
                    return {
                        "images": [],
                        "prompt": prompt,
                        "error": "Cookie已过期，请重新登录授权"
                    }
                
                if response.status_code == 404:
                    # API不存在，回退到聊天方式
                    logger.warning("Direct image API not available, falling back to chat method")
                    return await self.generate_image(prompt, size, style, negative_prompt, num_images)
                
                response.raise_for_status()
                data = response.json()
                
                images = data.get("images", [])
                if not images and "data" in data:
                    images = [item.get("url") for item in data["data"] if item.get("url")]
                
                return {
                    "images": images,
                    "prompt": prompt,
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return await self.generate_image(prompt, size, style, negative_prompt, num_images)
            logger.error(f"Doubao direct image generation failed: {e}")
            return {
                "images": [],
                "prompt": prompt,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Doubao direct image generation failed: {e}")
            return {
                "images": [],
                "prompt": prompt,
                "error": str(e)
            }
    
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频
        
        注意：豆包网页版可能不直接支持视频生成
        这里通过聊天方式尝试生成
        """
        headers = self.get_headers()
        
        full_prompt = f"请帮我生成一个视频：{prompt}"
        if duration:
            full_prompt += f"，时长约{duration}秒"
        
        payload = {
            "user_input": full_prompt,
            "bot_id": self.DEFAULT_BOT_ID,
            "stream": False,
        }
        
        logger.info(f"Doubao video generation - prompt: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=300.0) as client:
                response = await client.post(
                    self.CHAT_COMPLETIONS_API,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 401:
                    return {
                        "video_url": None,
                        "prompt": prompt,
                        "error": "Cookie已过期，请重新登录授权"
                    }
                
                response.raise_for_status()
                data = response.json()
                
                # 提取视频URL
                video_url = None
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        # 提取视频链接
                        video_urls = re.findall(r'https?://[^\s\)]+\.(?:mp4|webm|mov|avi)', content)
                        if video_urls:
                            video_url = video_urls[0]
                
                return {
                    "video_url": video_url,
                    "prompt": prompt,
                    "message": content if not video_url else None,
                }
                
        except Exception as e:
            logger.error(f"Doubao video generation failed: {e}")
            return {
                "video_url": None,
                "prompt": prompt,
                "error": str(e)
            }


# 工厂函数
def create_doubao_service(cookies: Dict[str, str], user_agent: Optional[str] = None) -> DoubaoService:
    """
    创建豆包服务实例
    
    Args:
        cookies: Cookie字典
        user_agent: User-Agent（可选）
        
    Returns:
        DoubaoService实例
    """
    return DoubaoService(cookies=cookies, user_agent=user_agent)
