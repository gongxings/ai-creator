"""
豆包网页版适配器 - 基于 doubao-free-api 逆向方案
"""
from typing import Dict, Any, Optional
import random
import time
import base64
import secrets
from app.services.oauth.adapters.base import PlatformAdapter
import logging

logger = logging.getLogger(__name__)


class DoubaoAdapter(PlatformAdapter):
    """豆包网页版适配器 - 基于逆向工程"""
    
    # 默认的 AgentID
    DEFAULT_ASSISTANT_ID = "497858"
    # 版本号
    VERSION_CODE = "20800"
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
        # 生成设备ID
        self.device_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        self.web_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        # 生成用户ID
        import uuid
        self.user_id = str(uuid.uuid4()).replace('-', '')
    
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
        ]

    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "s_v_web_id",
            "tt_webid",
            "is_staff_user",
            "store-region",
        ]
    
    @staticmethod
    def generate_fake_ms_token() -> str:
        """
        生成伪造的 msToken (128字符)
        参考 doubao-free-api 实现
        """
        # 生成96字节的随机数据，base64编码后为128字符
        random_bytes = secrets.token_bytes(96)
        ms_token = base64.b64encode(random_bytes).decode('utf-8')
        # 替换特殊字符
        ms_token = ms_token.replace('+', '-').replace('/', '_').replace('=', '')
        return ms_token
    
    @staticmethod
    def generate_fake_a_bogus() -> str:
        """
        生成伪造的 a_bogus 签名
        参考 doubao-free-api 实现
        """
        import string
        charset = string.ascii_letters + string.digits
        part1 = ''.join(secrets.choice(charset) for _ in range(34))
        part2 = ''.join(secrets.choice(charset) for _ in range(6))
        return f"mf-{part1}-{part2}"
    
    def build_complete_cookie(self, credentials: Dict[str, Any]) -> str:
        """
        构建完整的 Cookie 字符串
        参考 doubao-free-api 的 Cookie 构建方式
        
        Args:
            credentials: 凭证信息
            
        Returns:
            完整的 Cookie 字符串
        """
        cookies = credentials.get("cookies", {})
        sessionid = cookies.get("sessionid", "")
        
        # 生成 msToken
        ms_token = self.generate_fake_ms_token()
        
        # 构建完整 Cookie (参考 doubao-free-api)
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
            f"sessionid_ss={cookies.get('sessionid_ss', sessionid)}",
            f"msToken={ms_token}",
        ]
        
        # 添加其他可选 Cookie
        if "s_v_web_id" in cookies:
            cookie_parts.append(f"s_v_web_id={cookies['s_v_web_id']}")
        if "tt_webid" in cookies:
            cookie_parts.append(f"tt_webid={cookies['tt_webid']}")
        
        return "; ".join(cookie_parts)
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".doubao.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://www.doubao.com/"
    
    def get_supported_features(self) -> list:
        """
        获取豆包支持的功能列表
        
        Returns:
            功能列表
        """
        return [
            'chat',           # 文本对话
            'article',        # 文章生成
            'code',           # 代码辅助
            'image',          # 图像生成 ✅
            'video',          # 视频生成 ✅
        ]
    
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
            # 使用完整的 Cookie 构建
            credentials = {"cookies": cookies}
            complete_cookie = self.build_complete_cookie(credentials)
            
            headers = {
                "Cookie": complete_cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Referer": "https://www.doubao.com/",
                "Origin": "https://www.doubao.com",
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
        # 使用完整的 Cookie 构建
        complete_cookie = self.build_complete_cookie(credentials)
        
        return {
            "model": "doubao_web/doubao-lite-4k",
            "api_base": "https://www.doubao.com/samantha/chat/completion",  # 更新为正确的端点
            "custom_llm_provider": "doubao_web",
            "extra_headers": {
                "Cookie": complete_cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Origin": "https://www.doubao.com",
                "Pragma": "no-cache",
                "Referer": "https://www.doubao.com/chat/",
                "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Agw-Js-Conv": "str",
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
    
    async def send_message(
        self, 
        message: str, 
        cookies: Dict[str, str], 
        conversation_id: Optional[str] = None, 
        bot_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送消息到豆包网页版（使用正确的 API 端点）

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            bot_id: 机器人ID（可选）

        Returns:
            响应数据
        """
        import httpx
        import json as json_module
        import uuid

        # 构建完整 Cookie
        credentials = {"cookies": cookies}
        complete_cookie = self.build_complete_cookie(credentials)
        
        # 生成随机 ID
        local_conv_id = f"local_16{''.join(str(random.randint(0, 9)) for _ in range(14))}"
        local_msg_id = str(uuid.uuid4())
        
        # 生成 msToken 和 a_bogus
        ms_token = self.generate_fake_ms_token()
        a_bogus = self.generate_fake_a_bogus()

        # 构建请求头（参考 doubao-free-api）
        headers = {
            "Cookie": complete_cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Origin": "https://www.doubao.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://www.doubao.com/chat/",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Agw-Js-Conv": "str",
            "X-Flow-Trace": f"04-{uuid.uuid4()}-{str(uuid.uuid4())[:16]}-01",
        }

        # 构建请求体（参考 doubao-free-api 的格式）
        payload = {
            "messages": [
                {
                    "content": json_module.dumps({"text": message}),
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

        # 构建查询参数（参考 doubao-free-api）
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

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.doubao.com/samantha/chat/completion",  # 正确的端点
                    params=params,
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content-type: {response.headers.get('content-type')}")
                
                response.raise_for_status()

                # 解析 SSE 流响应
                result = {
                    "conversation_id": "",
                    "content": ""
                }

                lines = response.text.strip().split("\n")
                for line in lines:
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                raw_result = json_module.loads(data_str)
                                
                                # 检查错误
                                if raw_result.get("code"):
                                    error_msg = f"豆包API错误: {raw_result.get('code')}-{raw_result.get('message')}"
                                    logger.error(error_msg)
                                    return {
                                        "error": error_msg,
                                        "conversation_id": "",
                                        "content": ""
                                    }
                                
                                # event_type == 2001 表示消息内容
                                if raw_result.get("event_type") == 2001:
                                    event_data = json_module.loads(raw_result.get("event_data", "{}"))
                                    if not result["conversation_id"]:
                                        result["conversation_id"] = event_data.get("conversation_id", "")
                                    
                                    message_data = event_data.get("message", {})
                                    if message_data.get("content_type") in [2001, 2008]:
                                        content_obj = json_module.loads(message_data.get("content", "{}"))
                                        if "text" in content_obj:
                                            result["content"] += content_obj["text"]
                                
                                # event_type == 2003 表示结束
                                elif raw_result.get("event_type") == 2003:
                                    break
                                    
                            except json_module.JSONDecodeError:
                                continue

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return {
                "error": f"HTTP {e.response.status_code}",
                "conversation_id": "",
                "content": ""
            }
        except Exception as e:
            logger.error(f"Send message failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "conversation_id": "",
                "content": ""
            }
    
    async def remove_conversation(self, conversation_id: str, cookies: Dict[str, str]) -> bool:
        """
        删除会话（避免污染用户会话列表）
        参考 doubao-free-api 实现
        
        Args:
            conversation_id: 会话ID
            cookies: Cookie字典
            
        Returns:
            是否成功
        """
        import httpx
        import uuid
        
        if not conversation_id or conversation_id == "0":
            return False
        
        try:
            # 构建完整 Cookie
            credentials = {"cookies": cookies}
            complete_cookie = self.build_complete_cookie(credentials)
            
            # 生成 msToken 和 a_bogus
            ms_token = self.generate_fake_ms_token()
            a_bogus = self.generate_fake_a_bogus()
            
            headers = {
                "Cookie": complete_cookie,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Referer": "https://www.doubao.com/chat/",
                "Origin": "https://www.doubao.com",
            }
            
            params = {
                "aid": self.DEFAULT_ASSISTANT_ID,
                "device_id": self.device_id,
                "device_platform": "web",
                "language": "zh",
                "region": "CN",
                "web_id": self.web_id,
                "msToken": ms_token,
                "a_bogus": a_bogus,
            }
            
            payload = {
                "conversation_id": conversation_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.doubao.com/samantha/thread/delete",
                    params=params,
                    headers=headers,
                    json=payload,
                    timeout=15.0,
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully removed conversation: {conversation_id}")
                    return True
                else:
                    logger.warning(f"Failed to remove conversation: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove conversation: {e}")
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
        注意：图片生成可能需要特殊的 bot_id 或权限

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
        import json as json_module
        import re

        logger.info(f"Doubao image generation request:")
        logger.info(f"  Prompt: {prompt}")
        logger.info(f"  Size: {size}")

        # 构建图片生成提示词
        image_prompt = f"画一张图片，{prompt}"
        if style:
            image_prompt += f"，风格：{style}"
        if negative_prompt:
            image_prompt += f"，避免：{negative_prompt}"

        # 使用 send_message 方法发送图片生成请求
        try:
            result = await self.send_message(
                message=image_prompt,
                cookies=cookies
            )
            
            if "error" in result:
                return {
                    "error": result["error"],
                    "images": [],
                }
            
            content = result.get("content", "")
            
            # 提取 Markdown 格式的图片链接 ![image](url)
            image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
            
            logger.info(f"Extracted {len(image_urls)} image URLs")
            
            # 清理会话
            if result.get("conversation_id"):
                await self.remove_conversation(result["conversation_id"], cookies)
            
            return {
                "images": image_urls,
                "prompt": prompt,
                "style": style
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "images": [],
            }
