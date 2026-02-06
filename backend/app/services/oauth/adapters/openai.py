"""
ChatGPT网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


class OpenAIAdapter(PlatformAdapter):
    """ChatGPT网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://chatgpt.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/chatgpt.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "__Secure-next-auth.session-token",
            "__Secure-next-auth.callback-url",
            "__Host-next-auth.csrf-token",
            "_cfuvid",
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return []
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".chatgpt.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://chatgpt.com/api/auth/session"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        ChatGPT网页版使用session token认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "chatgpt_web/gpt-3.5-turbo",
            "api_base": "https://chatgpt.com/backend-api/conversation",
            "custom_llm_provider": "chatgpt_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://chatgpt.com/",
                "Origin": "https://chatgpt.com",
            },
            # ChatGPT网页版的免费模型
            "available_models": [
                "gpt-3.5-turbo",
                "gpt-4",  # 需要Plus订阅
                "gpt-4-turbo",  # 需要Plus订阅
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（ChatGPT网页版免费额度）"""
        # 网页版免费额度
        return 500000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 90000,
        }

    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, parent_message_id: str = None) -> Dict[str, Any]:
        """
        发送消息到ChatGPT网页版

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            parent_message_id: 父消息ID（可选）

        Returns:
            响应数据
        """
        import httpx
        import uuid

        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://chatgpt.com/",
            "Origin": "https://chatgpt.com",
            "Content-Type": "application/json",
        }

        # 构建请求体
        payload = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "author": {"role": "user"},
                    "content": {"content_type": "text", "parts": [message]},
                }
            ],
            "parent_message_id": parent_message_id or str(uuid.uuid4()),
            "model": "text-davinci-002-render-sha",
            "timezone_offset_min": -480,
            "suggestions": [],
            "history_and_training_disabled": False,
            "conversation_mode": {"kind": "primary_assistant"},
            "force_paragen": False,
            "force_rate_limit": False,
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://chatgpt.com/backend-api/conversation",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # ChatGPT返回的是SSE流，需要解析
            lines = response.text.strip().split("\n")
            for line in lines:
                if line.startswith("data: "):
                    data = line[6:]
                    if data != "[DONE]":
                        import json
                        try:
                            return json.loads(data)
                        except:
                            continue

            return {}

    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        生成图片（ChatGPT暂不支持Cookie方式）
        """
        return {
            "error": "ChatGPT图片生成需要使用 API Key，不支持Cookie方式",
            "images": [],
        }
