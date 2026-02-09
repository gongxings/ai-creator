"""
深度求索 DeepSeek 大模型适配器 - 基于 deepseek-free-api 优化
"""
from typing import Dict, Any, Optional
import uuid
import logging
import time
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class DeepSeekAdapter(PlatformAdapter):
    """深度求索 DeepSeek 适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://chat.deepseek.com"
    CHAT_ENDPOINT = "/api/v0/chat/completions"
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        return "https://chat.deepseek.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/chat.deepseek.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "token",  # 主要凭证
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "user_id",
            "session_id",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".deepseek.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return f"{self.API_BASE}/api/v0/user/info"
    
    def build_request_headers(self, token: str) -> Dict[str, str]:
        """
        构建请求头（参考 deepseek-free-api）
        
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
            "Origin": "https://chat.deepseek.com",
            "Referer": "https://chat.deepseek.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-App-Version": "20240101",
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置
        
        DeepSeek 使用 token 认证
        """
        cookies = credentials.get("cookies", {})
        token = cookies.get("token")
        
        if not token:
            raise ValueError("缺少 token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(token)
        
        return {
            "model": "deepseek_web/deepseek-chat",
            "api_base": f"{self.API_BASE}{self.CHAT_ENDPOINT}",
            "custom_llm_provider": "deepseek_web",
            "extra_headers": headers,
            # DeepSeek 支持的模型
            "available_models": [
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-v3",
                "deepseek-r1",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制"""
        return 10000000  # DeepSeek 免费版额度较高
    
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
        model: str = "deepseek-chat"
    ) -> Dict[str, Any]:
        """
        发送消息到 DeepSeek（优化版 - 基于 deepseek-free-api）
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            model: 模型名称
            
        Returns:
            响应数据
        """
        import httpx
        
        # 获取 token
        token = cookies.get("token")
        if not token:
            raise ValueError("缺少 token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(token)
        
        # 构建请求体
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": False
        }
        
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
        生成图片（DeepSeek 不支持图像生成）
        """
        return {
            "error": "DeepSeek 专注于文本和代码生成，不支持图像生成",
            "images": [],
        }
