"""
聆心智能 Emohaa 情感陪伴大模型适配器 - 基于 emohaa-free-api 优化
"""
from typing import Dict, Any, Optional
import uuid
import logging
import time
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class EmohaaAdapter(PlatformAdapter):
    """聆心智能 Emohaa 适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://echo.turing-world.com"
    CHAT_ENDPOINT = "/api/v2/chat/completions"
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        return "https://echo.turing-world.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/echo.turing-world.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "Token",  # 主要凭证（从 LocalStorage 获取）
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return []
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".turing-world.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return f"{self.API_BASE}/api/v1/user/info"
    
    def build_request_headers(self, token: str) -> Dict[str, str]:
        """
        构建请求头（参考 emohaa-free-api）
        
        Args:
            token: Token
            
        Returns:
            请求头字典
        """
        return {
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Origin": "https://echo.turing-world.com",
            "Referer": "https://echo.turing-world.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于情感陪伴对话
        
        Emohaa 使用 Token 认证
        """
        cookies = credentials.get("cookies", {})
        token = cookies.get("Token")
        
        if not token:
            raise ValueError("缺少 Token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(token)
        
        return {
            "model": "emohaa_web/emohaa",
            "api_base": f"{self.API_BASE}{self.CHAT_ENDPOINT}",
            "custom_llm_provider": "emohaa_web",
            "extra_headers": headers,
            # Emohaa 只有一个情感陪伴模型
            "available_models": ["emohaa"],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制"""
        return 1000000  # 免费版
    
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
        conversation_id: str = ""
    ) -> Dict[str, Any]:
        """
        发送消息到 Emohaa（优化版 - 基于 emohaa-free-api）
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            
        Returns:
            响应数据
        """
        import httpx
        
        # 获取 Token
        token = cookies.get("Token")
        if not token:
            raise ValueError("缺少 Token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(token)
        
        # 构建请求体
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": False
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}{self.CHAT_ENDPOINT}",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        生成图片（Emohaa 不支持图像生成）
        """
        return {
            "error": "Emohaa 是情感陪伴模型，不支持图像生成",
            "images": [],
        }
