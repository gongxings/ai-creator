"""
阶跃星辰 Step 跃问 StepChat 多模态大模型适配器 - 基于 step-free-api 优化
"""
from typing import Dict, Any, Optional
import uuid
import logging
import time
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class StepAdapter(PlatformAdapter):
    """阶跃星辰 Step 跃问 StepChat 适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://yuewen.cn"
    CHAT_ENDPOINT = "/api/v1/chat/completions"
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        return "https://yuewen.cn/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/yuewen.cn/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "deviceId",      # 设备ID（从 LocalStorage 获取）
            "Oasis-Token",   # 主要凭证
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return []
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".yuewen.cn"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return f"{self.API_BASE}/api/v1/user/info"
    
    def build_request_headers(self, device_id: str, oasis_token: str) -> Dict[str, str]:
        """
        构建请求头（参考 step-free-api）
        
        Args:
            device_id: 设备ID
            oasis_token: Oasis Token
            
        Returns:
            请求头字典
        """
        return {
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {device_id}@{oasis_token}",
            "Content-Type": "application/json",
            "Device-Id": device_id,
            "Origin": "https://yuewen.cn",
            "Referer": "https://yuewen.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Device-Id": device_id,
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于多模态对话
        
        Step 使用 deviceId + Oasis-Token 认证
        """
        cookies = credentials.get("cookies", {})
        device_id = cookies.get("deviceId")
        oasis_token = cookies.get("Oasis-Token")
        
        if not device_id or not oasis_token:
            raise ValueError("缺少 deviceId 或 Oasis-Token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(device_id, oasis_token)
        
        return {
            "model": "step_web/step-1-8k",
            "api_base": f"{self.API_BASE}{self.CHAT_ENDPOINT}",
            "custom_llm_provider": "step_web",
            "extra_headers": headers,
            # Step 支持的模型
            "available_models": [
                "step-1-8k",
                "step-1-32k",
                "step-1-128k",
                "step-1-256k",
            ],
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
        model: str = "step-1-8k"
    ) -> Dict[str, Any]:
        """
        发送消息到 Step（优化版 - 基于 step-free-api）
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            model: 模型名称
            
        Returns:
            响应数据
        """
        import httpx
        
        # 获取凭证
        device_id = cookies.get("deviceId")
        oasis_token = cookies.get("Oasis-Token")
        
        if not device_id or not oasis_token:
            raise ValueError("缺少 deviceId 或 Oasis-Token")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(device_id, oasis_token)
        
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
        生成图片（Step 主要用于文本和多模态对话）
        """
        return {
            "error": "Step 主要用于文本和多模态对话，图像生成请使用即梦 AI",
            "images": [],
        }
