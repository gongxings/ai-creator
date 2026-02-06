"""
豆包网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


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
                return False
        
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
                        return False
                    return True
                
                return False
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Cookie validation failed: {e}")
            return False
    
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
        import logging

        logger = logging.getLogger(__name__)

        # 构建请求头
        # 添加更多豆包所需的请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.doubao.com/",
            "Origin": "https://www.doubao.com",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

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
                                import re
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
        
        # 豆包图片生成 API 端点（使用网页版接口）
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.doubao.com/api/chat/completions",
                headers=headers,
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            # 提取图片URL
            images = []
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    message = choice["message"]
                    if "content" in message:
                        content = message["content"]
                        # 豆包可能返回Markdown格式的图片链接
                        # 提取 ![image](url) 格式的图片链接
                        import re
                        image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                        images = image_urls
            
            return {
                "images": images,
                "prompt": prompt,
                "style": style
            }
