"""
豆包网页版AI服务 - 基于Cookie调用
支持文本生成、图片生成、视频生成
"""
import httpx
import json
import re
import logging
import random
import base64
import secrets
import time
from typing import Dict, Any, Optional, List, AsyncGenerator

from app.services.ai.cookie_based_service import CookieBasedAIService

logger = logging.getLogger(__name__)


class DoubaoService(CookieBasedAIService):
    """豆包网页版AI服务"""
    
    # 豆包网页版API端点
    BASE_URL = "https://www.doubao.com"
    CHAT_COMPLETIONS_API = f"{BASE_URL}/samantha/chat/completion"
    IMAGE_API = f"{BASE_URL}/samantha/image/gen_image"
    VIDEO_API = f"{BASE_URL}/samantha/video/gen_video"  # 视频生成API
    
    # 默认Bot ID
    DEFAULT_BOT_ID = "7358044466096914465"
    DEFAULT_ASSISTANT_ID = "497858"
    VERSION_CODE = "20800"
    
    def __init__(self, cookies: Dict[str, str], user_agent: Optional[str] = None):
        super().__init__(cookies, user_agent)
        # 生成设备ID
        self.device_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        self.web_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        # 生成用户ID
        import uuid
        self.user_id = str(uuid.uuid4()).replace('-', '')
    
    def build_complete_cookie(self, ms_token: str) -> str:
        """
        构建完整的 Cookie 字符串
        参考 doubao-free-api 的实现
        """
        sessionid = self.cookies.get("sessionid", "")
        sessionid_ss = self.cookies.get("sessionid_ss", sessionid)
        
        current_timestamp = int(time.time())
        
        cookie_parts = [
            "is_staff_user=false",
            "store-region=cn-gd",
            "store-region-src=uid",
            f"sid_guard={sessionid}%7C{current_timestamp}%7C5184000%7CSun%2C+02-Feb-2025+04%3A17%3A20+GMT",
            f"uid_tt={self.user_id}",
            f"uid_tt_ss={self.user_id}",
            f"sid_tt={sessionid}",
            f"sessionid={sessionid}",
            f"sessionid_ss={sessionid_ss}",
            f"msToken={ms_token}",
        ]
        
        # 添加其他可选的 Cookie
        if "s_v_web_id" in self.cookies:
            cookie_parts.append(f"s_v_web_id={self.cookies['s_v_web_id']}")
        if "tt_webid" in self.cookies:
            cookie_parts.append(f"tt_webid={self.cookies['tt_webid']}")
        
        return "; ".join(cookie_parts)
    
    @staticmethod
    def generate_fake_ms_token() -> str:
        """生成伪造的 msToken (128字符)"""
        random_bytes = secrets.token_bytes(96)
        ms_token = base64.b64encode(random_bytes).decode('utf-8')
        ms_token = ms_token.replace('+', '-').replace('/', '_').replace('=', '')
        return ms_token
    
    @staticmethod
    def generate_fake_a_bogus() -> str:
        """生成伪造的 a_bogus 签名"""
        import string
        charset = string.ascii_letters + string.digits
        part1 = ''.join(secrets.choice(charset) for _ in range(34))
        part2 = ''.join(secrets.choice(charset) for _ in range(6))
        return f"mf-{part1}-{part2}"
    
    @staticmethod
    def generate_local_ids():
        """生成本地会话ID和消息ID"""
        local_conv_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        local_msg_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        return local_conv_id, local_msg_id
    
    def get_platform_name(self) -> str:
        return "doubao"
    
    def get_check_url(self) -> str:
        return self.BASE_URL
    
    def get_headers(self, referer: Optional[str] = None, content_type: str = "application/json", ms_token: Optional[str] = None) -> Dict[str, str]:
        """
        构建豆包请求头
        """
        # 如果提供了 ms_token，使用完整的 Cookie 构建
        if ms_token:
            cookie_str = self.build_complete_cookie(ms_token)
        else:
            # 否则使用简单拼接（用于验证等场景）
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
        # 生成本地ID - 参考 doubao-free-api 的格式
        local_conv_id = f"local_16{''.join(str(random.randint(0, 9)) for _ in range(14))}"
        local_msg_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        
        # 构建消息负载 - 使用 doubao-free-api 的格式
        payload = {
            "messages": [
                {
                    "content": json.dumps({"text": prompt}),
                    "content_type": 2001,
                    "attachments": [],
                    "references": [],
                }
            ],
            "completion_option": {
                "is_regen": False,
                "with_suggest": True,
                "need_create_conversation": True,
                "launch_stage": 1,
                "is_replace": False,
                "is_delete": False,
                "message_from": 0,
                "event_id": "0"
            },
            "conversation_id": "0",
            "local_conversation_id": local_conv_id,
            "local_message_id": local_msg_id
        }
        
        # 生成查询参数
        ms_token = self.generate_fake_ms_token()
        a_bogus = self.generate_fake_a_bogus()
        
        params = {
            "aid": self.DEFAULT_ASSISTANT_ID,
            "device_id": self.device_id,
            "device_platform": "web",
            "language": "zh",
            "pkg_type": "release_version",
            "real_aid": self.DEFAULT_ASSISTANT_ID,
            "region": "CN",
            "samantha_web": 1,
            "sys_region": "CN",
            "tea_uuid": self.web_id,
            "use_olympus_account": 1,
            "version_code": self.VERSION_CODE,
            "web_id": self.web_id,
            "msToken": ms_token,
            "a_bogus": a_bogus,
        }
        
        # 使用完整的 Cookie 构建请求头
        headers = self.get_headers(ms_token=ms_token)
        # 添加必需的请求头
        headers["Referer"] = "https://www.doubao.com/chat/"
        headers["Agw-Js-Conv"] = "str"
        headers["X-Flow-Trace"] = f"04-{str(int(random.random() * 999999999999999999))}-{str(int(random.random() * 999999999999))}-01"
        
        logger.info(f"Doubao text generation - prompt length: {len(prompt)}")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            response = await client.post(
                self.CHAT_COMPLETIONS_API,
                params=params,
                headers=headers,
                json=payload,
            )
            
            logger.info(f"Doubao response status: {response.status_code}")
            logger.info(f"Doubao response content-type: {response.headers.get('content-type')}")
            
            if response.status_code == 401:
                logger.error("Doubao API returned 401 - Cookie may be expired")
                raise ValueError("Cookie已过期，请重新登录授权")
            
            if response.status_code == 400:
                # 记录详细的错误信息
                response_text = response.text
                logger.error(f"Doubao API returned 400")
                logger.error(f"Response text length: {len(response_text)}")
                logger.error(f"Response text: {response_text[:1000] if response_text else '(empty)'}")
                
                try:
                    error_data = response.json()
                    logger.error(f"Response JSON: {error_data}")
                    error_msg = error_data.get("message") or error_data.get("error") or error_data.get("msg") or str(error_data)
                    raise ValueError(f"豆包API请求错误: {error_msg}")
                except Exception as parse_error:
                    logger.error(f"Failed to parse error response as JSON: {parse_error}")
                    if response_text:
                        raise ValueError(f"豆包API请求错误 (400): {response_text[:200]}")
                    else:
                        raise ValueError(f"豆包API请求错误 (400): 未返回错误详情，请检查Cookie是否有效")
            
            response.raise_for_status()
            
            # 检查响应类型
            content_type = response.headers.get('content-type', '')
            if 'text/event-stream' not in content_type:
                logger.error(f"Invalid response content-type: {content_type}")
                raise ValueError(f"豆包API返回了错误的内容类型: {content_type}")
            
            # 流式解析 SSE 响应
            result_text = ""
            event_count = 0
            buffer = ""
            
            logger.info("Starting to process SSE stream...")
            
            # 逐块读取流式响应
            async for chunk in response.aiter_text():
                buffer += chunk
                
                # 按行处理
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                raw_result = json.loads(data_str)
                                event_count += 1
                                
                                # 记录前几个事件用于调试
                                if event_count <= 3:
                                    logger.info(f"Event {event_count}: event_type={raw_result.get('event_type')}")
                                    # 记录完整的事件数据用于调试未知事件类型
                                    if raw_result.get('event_type') not in [2001, 2003]:
                                        logger.info(f"  Unknown event_type, full data: {json.dumps(raw_result, ensure_ascii=False)[:500]}")
                                
                                # 检查错误
                                if raw_result.get("code"):
                                    error_msg = f"豆包API错误: {raw_result.get('code')}-{raw_result.get('message')}"
                                    logger.error(error_msg)
                                    raise ValueError(error_msg)
                                
                                # event_type == 2005 表示错误/警告
                                if raw_result.get("event_type") == 2005:
                                    event_data_str = raw_result.get("event_data", "{}")
                                    try:
                                        event_data = json.loads(event_data_str)
                                        error_code = event_data.get("code")
                                        error_message = event_data.get("message", "")
                                        error_detail = event_data.get("error_detail", {})
                                        detail_message = error_detail.get("message", "")
                                        
                                        error_msg = f"豆包API返回错误 (event_type=2005, code={error_code}): {error_message}"
                                        if detail_message:
                                            error_msg += f" - {detail_message}"
                                        
                                        logger.error(error_msg)
                                        raise ValueError(error_msg)
                                    except json.JSONDecodeError:
                                        logger.error(f"Failed to parse error event_data: {event_data_str}")
                                        raise ValueError("豆包API返回了错误事件但无法解析详情")
                                
                                # event_type == 2001 表示消息内容
                                if raw_result.get("event_type") == 2001:
                                    event_data_str = raw_result.get("event_data", "{}")
                                    try:
                                        event_data = json.loads(event_data_str)
                                        message_data = event_data.get("message", {})
                                        content_type = message_data.get("content_type")
                                        
                                        if content_type in [2001, 2008]:
                                            content_str = message_data.get("content", "{}")
                                            content_obj = json.loads(content_str)
                                            if "text" in content_obj:
                                                text_chunk = content_obj["text"]
                                                result_text += text_chunk
                                                if event_count <= 3:
                                                    logger.info(f"  → Text chunk: {text_chunk[:50]}")
                                    except json.JSONDecodeError as e:
                                        logger.error(f"Failed to parse event_data: {e}")
                                
                                # event_type == 2003 表示结束
                                elif raw_result.get("event_type") == 2003:
                                    logger.info(f"Stream ended at event {event_count}")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse SSE data: {e}")
                                continue
            
            logger.info(f"Total events processed: {event_count}")
            logger.info(f"Result text length: {len(result_text)}")
            
            if result_text:
                return result_text
            
            logger.warning("No text content found in response")
            raise ValueError("豆包API返回的响应中没有文本内容")
    
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
        生成视频（优先使用直接API）
        """
        # 先尝试直接API
        result = await self.generate_video_direct(prompt, duration, **kwargs)
        
        # 如果直接API失败，回退到聊天方式
        if result.get("error") and "404" in str(result.get("error")):
            return await self.generate_video_via_chat(prompt, duration, **kwargs)
        
        return result
    
    async def generate_video_direct(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        直接调用视频生成API
        """
        headers = self.get_headers()
        
        payload = {
            "prompt": prompt,
            "duration": duration or 5,  # 默认5秒
        }
        
        logger.info(f"Doubao direct video generation - prompt: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=300.0) as client:
                response = await client.post(
                    self.VIDEO_API,
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 401:
                    return {
                        "video_url": None,
                        "prompt": prompt,
                        "error": "Cookie已过期，请重新登录授权"
                    }
                
                if response.status_code == 404:
                    # API不存在，回退到聊天方式
                    logger.warning("Direct video API not available, falling back to chat method")
                    return await self.generate_video_via_chat(prompt, duration)
                
                response.raise_for_status()
                data = response.json()
                
                video_url = None
                if "video_url" in data:
                    video_url = data["video_url"]
                elif "data" in data and len(data["data"]) > 0:
                    video_url = data["data"][0].get("url")
                
                return {
                    "video_url": video_url,
                    "prompt": prompt,
                    "status": data.get("status", "completed"),
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return await self.generate_video_via_chat(prompt, duration)
            logger.error(f"Doubao direct video generation failed: {e}")
            return {
                "video_url": None,
                "prompt": prompt,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Doubao direct video generation failed: {e}")
            return {
                "video_url": None,
                "prompt": prompt,
                "error": str(e)
            }
    
    async def generate_video_via_chat(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通过聊天方式生成视频
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
        
        logger.info(f"Doubao video generation via chat - prompt: {prompt[:100]}...")
        
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
                content = ""
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
            logger.error(f"Doubao video generation via chat failed: {e}")
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
