"""
豆包网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter
import logging

logger = logging.getLogger(__name__)


class DoubaoAdapter(PlatformAdapter):
    """豆包网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://www.doubao.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        # 豆包登录后URL不变，使用特殊的 pattern 表示需要等待固定时间
        return "WAIT_FOR_LOGIN"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "sessionid",
            "sessionid_ss",
            "s_v_web_id",
        ]

    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "tt_webid",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".doubao.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://www.doubao.com/"
    
    def get_auto_login_config(self) -> Dict[str, Any]:
        """获取自动登录配置"""
        return {
            # 可以从配置文件或环境变量读取
            "username": self.oauth_config.get("username"),
            "password": self.oauth_config.get("password"),
        }
    
    def get_qr_code_selector(self) -> Optional[str]:
        """获取二维码元素选择器"""
        # 豆包登录页面的二维码元素选择器
        return "img[src*='qrcode'], canvas.qrcode, .qrcode img"
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        验证凭证有效性（重写基类方法）
        
        Args:
            credentials: 凭证信息
            
        Returns:
            是否有效
        """
        # 先检查基础格式
        if not credentials:
            return False
        
        cookies = credentials.get("cookies", {})
        if not cookies:
            return False
        
        # 检查必需的Cookie是否存在
        required_cookies = self.get_cookie_names()
        for cookie_name in required_cookies:
            if cookie_name not in cookies or not cookies[cookie_name]:
                logger.warning(f"Missing required cookie: {cookie_name}")
                return False
        
        logger.info(f"Basic credential validation passed for doubao")
        return True
    
    async def validate_cookies_online(self, cookies: Dict[str, str]) -> bool:
        """
        在线验证Cookie是否有效（实际调用API验证）
        
        Args:
            cookies: Cookie字典
            
        Returns:
            是否有效
        """
        import httpx
        
        try:
            headers = {
                "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.doubao.com/",
            }
            
            # 测试访问豆包首页
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(
                    "https://www.doubao.com/",
                    headers=headers
                )
                
                # 检查是否需要登录
                if response.status_code == 200:
                    content = response.text
                    # 如果页面包含登录相关的元素，说明Cookie无效
                    if "login" in content.lower() and "Please Login" in content:
                        logger.warning("Cookie appears to be expired - login page detected")
                        return False
                    logger.info(f"Cookie validation successful - status code: {response.status_code}")
                    return True
                
                logger.warning(f"Cookie validation failed - status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Cookie validation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        豆包网页版使用sessionid认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "doubao_web/doubao-lite-4k",
            "api_base": "https://www.doubao.com/api/chat/stream",
            "custom_llm_provider": "doubao_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://www.doubao.com/",
                "Origin": "https://www.doubao.com",
            },
            # 豆包网页版的免费模型
            "available_models": [
                "doubao-lite-4k",
                "doubao-lite-32k",
                "doubao-pro-4k",
                "doubao-pro-32k",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（豆包网页版免费额度）"""
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, bot_id: str = None) -> Dict[str, Any]:
        """
        发送消息到豆包网页版

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            bot_id: 机器人ID（可选）

        Returns:
            响应数据
        """
        import httpx

        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.doubao.com/",
            "Origin": "https://www.doubao.com",
            "Content-Type": "application/json",
        }

        # 构建请求体
        payload = {
            "conversation_id": conversation_id or "",
            "bot_id": bot_id or "7358044466096914465",  # 默认豆包助手ID
            "user_input": message,
            "stream": True,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.doubao.com/api/chat/stream",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # 豆包返回SSE流
            lines = response.text.strip().split("\n")
            result = {"conversation_id": conversation_id}

            for line in lines:
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data and data != "[DONE]":
                        import json
                        try:
                            parsed = json.loads(data)
                            if "text" in parsed:
                                result["content"] = parsed["text"]
                            if "conversation_id" in parsed:
                                result["conversation_id"] = parsed["conversation_id"]
                        except:
                            continue 

            return result
    
    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        生成图片（通过豆包网页版）
        Args:
            prompt: 图片描述
            cookies: Cookie字典
            negative_prompt: 负面提示词（可选）
            style: 风格（可选）
            size: 图片尺寸，默认 1024x1024
        Returns:
            生成的图片URL
        """
        import httpx
        import json
        import re
        import asyncio
        import uuid
        import random
        
        MAX_RETRIES = 2
        RETRY_DELAY = 1
        
        # 构建请求头
        merged_cookies = dict(self.oauth_config.get("cookies", {}))
        if cookies:
            merged_cookies.update(cookies)
        cookie_str = self.oauth_config.get("cookie_string")
        if not cookie_str:
            cookie_str = "; ".join([f"{k}={v}" for k, v in merged_cookies.items()])

        headers = {
            "Cookie": cookie_str,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.doubao.com",
            "Referer": "https://www.doubao.com/chat/",
            "Content-Type": "application/json",
            "last-event-id": "undefined",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "agw-js-conv": "str, str",
        }
        # 添加x-flow-trace头（如果存在）
        if self.oauth_config.get("x_flow_trace"):
            headers["x-flow-trace"] = self.oauth_config.get("x_flow_trace")
        if self.oauth_config.get("referer"):
            headers["Referer"] = self.oauth_config.get("referer")
        extra_headers = self.oauth_config.get("extra_headers", {})
        if isinstance(extra_headers, dict):
            headers.update(extra_headers)
        
        # 构建请求体
        def build_prompt_text() -> str:
            txt = prompt
            if style:
                txt += f"，风格：{style}"
            if negative_prompt:
                txt += f"，避免：{negative_prompt}"
            return txt

        def default_payload() -> Dict[str, Any]:
            return {
                "messages": [{
                    "content": json.dumps({
                        "text": build_prompt_text(),
                        "model": "Seedream 4.5",
                        "template_type": "placeholder",
                        "use_creation": False
                    }),
                    "content_type": 2009,
                    "attachments": []
                }],
                "completion_option": {
                    "is_regen": False,
                    "with_suggest": False,
                    "need_create_conversation": False,
                    "launch_stage": 1,
                    "is_replace": False,
                    "is_delete": False,
                    "is_ai_playground": False,
                    "message_from": 0,
                    "action_bar_skill_id": 3,
                    "use_auto_cot": False,
                    "resend_for_regen": False,
                    "enable_commerce_credit": False,
                    "event_id": "0"
                },
                "evaluate_option": {
                    "web_ab_params": ""
                },
                "section_id": str(uuid.uuid4()),
                "conversation_id": str(uuid.uuid4()),
                "local_message_id": str(uuid.uuid4()),
                "stream": False
            }

        captured_body = self.oauth_config.get("captured_body")
        payload: Dict[str, Any] = {}

        if captured_body:
            try:
                payload = json.loads(captured_body)
            except Exception:
                payload = {}

        def ensure_payload(data: Dict[str, Any]) -> Dict[str, Any]:
            if not data.get("messages"):
                data["messages"] = [{
                    "content": json.dumps({
                        "text": build_prompt_text(),
                        "model": "Seedream 4.5",
                        "template_type": "placeholder",
                        "use_creation": False
                    }),
                    "content_type": 2009,
                    "attachments": []
                }]
            else:
                try:
                    content_str = data["messages"][0].get("content", "")
                    content_obj = json.loads(content_str) if isinstance(content_str, str) else {}
                except Exception:
                    content_obj = {}
                content_obj["text"] = build_prompt_text()
                content_obj.setdefault("model", "Seedream 4.5")
                content_obj.setdefault("template_type", "placeholder")
                content_obj.setdefault("use_creation", False)
                data["messages"][0]["content"] = json.dumps(content_obj, ensure_ascii=False)

            completion = data.get("completion_option", {})
            defaults = {
                "is_regen": False,
                "with_suggest": False,
                "need_create_conversation": False,
                "launch_stage": 1,
                "is_replace": False,
                "is_delete": False,
                "is_ai_playground": False,
                "message_from": 0,
                "action_bar_skill_id": 3,
                "use_auto_cot": False,
                "resend_for_regen": False,
                "enable_commerce_credit": False,
                "event_id": "0",
            }
            defaults.update(completion)
            data["completion_option"] = defaults
            data["evaluate_option"] = data.get("evaluate_option", {"web_ab_params": ""})
            data["section_id"] = str(uuid.uuid4().int % 10**17)
            data["local_message_id"] = str(uuid.uuid4())
            data["conversation_id"] = data.get("conversation_id", str(uuid.uuid4()))
            data["stream"] = False
            return data

        if not payload:
            payload = default_payload()
        else:
            payload = ensure_payload(payload)

        # 尝试从referer URL提取conversation_id
        referer_url = self.oauth_config.get("referer", "")
        if referer_url:
            import re
            m = re.search(r"/chat/(\d+)", referer_url)
            if m:
                payload["conversation_id"] = m.group(1)
                logger.info(f"Extracted conversation_id from referer: {payload['conversation_id']}")
        
        params = {
            "aid": "497858",
            "device_id": str(random.randint(7000000000000000000, 7999999999999999999)),
            "device_platform": "web",
            "fp": "verify_mlb4q9tv_mxSPv0i4_o7Ax_41Ga_8cIo_hvMcGZd0o4kg",
            "language": "zh",
            "pc_version": "3.5.0",
            "pkg_type": "release_version",
            "real_aid": "497858",
            "region": "",
            "samantha_web": "1",
            "sys_region": "",
            "tea_uuid": str(random.randint(7000000000000000000, 7999999999999999999)),
            "use-olympus-account": "1",
            "version_code": "20800",
            "web_id": str(random.randint(7000000000000000000, 7999999999999999999)),
            "web_tab_id": str(uuid.uuid4()),
            "msToken": ""
        }
        extra_params = self.oauth_config.get("extra_params", {})
        if isinstance(extra_params, dict):
            params.update(extra_params)
        if "msToken" in self.oauth_config:
            params["msToken"] = self.oauth_config.get("msToken") or params.get("msToken", "")
        if "a_bogus" in self.oauth_config:
            params["a_bogus"] = self.oauth_config.get("a_bogus")
        
        logger.info(f"Doubao image generation: {prompt[:50]}...")
        
        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream(
                        "POST",
                        "https://www.doubao.com/samantha/chat/completion",
                        headers=headers,
                        json=payload,
                        params=params,
                        timeout=120.0,
                    ) as response:
                        logger.info(f"Response status: {response.status_code}")
                        
                        if response.status_code == 401:
                            return {"error": "Cookie已过期，请重新登录", "images": []}
                        if response.status_code != 200:
                            body = (await response.aread()).decode("utf-8", errors="ignore")
                            logger.error(f"Doubao 400 error response: {body}")
                            error_text = body[:500] if body else "Empty response"
                            return {"error": f"HTTP {response.status_code}: {error_text}", "images": []}
                        
                        images = []
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            if line.startswith("data:"):
                                data_str = line[5:].strip()
                            else:
                                data_str = line.strip()
                            if not data_str or data_str == "[DONE]":
                                continue
                            try:
                                data = json.loads(data_str)
                                if isinstance(data, dict):
                                    choices = data.get("choices") or []
                                    if choices:
                                        msg = choices[0].get("message", {})
                                        content = msg.get("content", "")
                                    else:
                                        content = data.get("content", "") or data.get("text", "")
                                else:
                                    content = ""
                            except Exception:
                                content = data_str
                            if content:
                                image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                                plain_urls = re.findall(r'https?://[^\s\)]+\.(?:png|jpg|jpeg|gif|webp)', content)
                                for url in plain_urls:
                                    if url not in image_urls:
                                        image_urls.append(url)
                                if image_urls:
                                    images = image_urls
                        
                        return {"images": images, "prompt": prompt, "style": style}
                    
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
        
        error_msg = str(last_error) if last_error else "Unknown error"
        return {"error": f"Connection failed: {error_msg}", "images": []}
        # 构建请求体 - 使用豆包图片生成接口
        # 注意：这是基于豆包网页版逆向的接口
        payload = {
            "user_input": f"画一张图片，{prompt}",
            "bot_id": "7358044466096914465",
            "stream": False,
        }

        # 添加风格和尺寸参数
        if style:
            payload["user_input"] += f"，风格：{style}"
        
        if negative_prompt:
            payload["user_input"] += f"，避免：{negative_prompt}"

        logger.info(f"Doubao image generation request:")
        logger.info(f"  Prompt: {prompt}")
        logger.info(f"  Cookies: {list(cookies.keys())}")
        logger.info(f"  Size: {size}")

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.post(
                    "https://www.doubao.com/api/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0,
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                
                # 解析响应
                data = response.json()
                logger.info(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")

                # 提取图片URL
                images = []
                if isinstance(data, dict):
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice:
                            message = choice["message"]
                            if "content" in message:
                                content = message["content"]
                                logger.info(f"Response content preview: {content[:200]}...")
                                # 豆包可能返回Markdown格式的图片链接
                                # 提取 ![image](url) 格式的图片链接
                                image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                                images = image_urls
                                logger.info(f"Extracted image URLs: {images}")

                if not images:
                    logger.warning(f"No images extracted from response. Response data: {data}")

                return {
                    "images": images,
                    "prompt": prompt,
                    "style": style
                }

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e}")
                logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
                return {
                    "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    "images": [],
                }
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return {
                    "error": str(e),
                    "images": [],
                }
