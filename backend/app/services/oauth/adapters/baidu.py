"""
百度文心一言网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


class BaiduAdapter(PlatformAdapter):
    """百度文心一言网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://yiyan.baidu.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/yiyan.baidu.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "BAIDUID",
            "BDUSS",
            "BDUSS_BFESS",
            "STOKEN",
            "PTOKEN",
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return []
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".baidu.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://yiyan.baidu.com/eb/user/info"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        文心一言网页版使用BDUSS认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "yiyan_web/ernie-bot-turbo",
            "api_base": "https://yiyan.baidu.com/eb/chat/new",
            "custom_llm_provider": "yiyan_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://yiyan.baidu.com/",
                "Origin": "https://yiyan.baidu.com",
            },
            # 文心一言网页版的免费模型
            "available_models": [
                "ernie-bot-turbo",
                "ernie-bot",
                "ernie-bot-4",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（文心一言网页版免费额度）"""
        # 网页版免费额度
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, parent_chat_id: str = None) -> Dict[str, Any]:
        """
        发送消息到文心一言网页版

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            parent_chat_id: 父聊天ID（可选）

        Returns:
            响应数据
        """
        import httpx

        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://yiyan.baidu.com/",
            "Origin": "https://yiyan.baidu.com",
            "Content-Type": "application/json",
        }

        # 构建请求体
        payload = {
            "text": message,
            "parentChatId": parent_chat_id or 0,
            "conversationId": conversation_id or "",
            "model": "eb-turbo-pro-v1",
            "timestamp": int(__import__("time").time() * 1000),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://yiyan.baidu.com/eb/chat/new",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # 文心一言返回JSON格式
            data = response.json()
            return {
                "conversation_id": data.get("conversationId"),
                "chat_id": data.get("chatId"),
                "content": data.get("content"),
                "is_end": data.get("isEnd", True),
            }

    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        生成图片（文心一言暂不支持Cookie方式）
        """
        return {
            "error": "文心一言图片生成需要使用 API Key，不支持Cookie方式",
            "images": [],
        }
