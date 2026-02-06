"""
通义千问 qianwen.com 适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


class QianwenAdapter(PlatformAdapter):
    """通义千问 qianwen.com 适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        return "https://www.qianwen.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/qianwen.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称 - qianwen.com 使用 tongyi_sso_ticket"""
        return [
            "tongyi_sso_ticket",
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "cna",
            "isg",
            "tfstk",
            "xlly_s",
            "UM_distinctid",
            "_qk_bx_um_v1",
            "_qk_bx_ck_v1",
            "_ON_EXT_DVIDN",
            "XSRF-TOKEN",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".qianwen.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://www.qianwen.com/"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        qianwen.com 使用 tongyi_sso_ticket 认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "qwen_web/qwen-turbo",
            "api_base": "https://www.qianwen.com/api/chat",
            "custom_llm_provider": "qwen_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://www.qianwen.com/",
                "Origin": "https://www.qianwen.com",
            },
            # 通义千问网页版的免费模型
            "available_models": [
                "qwen-turbo",
                "qwen-plus",
                "qwen-max",
                "qwen-vl-max",
                "qwen2.5-72b",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（通义千问网页版免费额度）"""
        # 网页版免费额度
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None) -> Dict[str, Any]:
        """
        发送消息到通义千问 qianwen.com
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）

        Returns:
            响应数据
        """
        import httpx

        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.qianwen.com/",
            "Origin": "https://www.qianwen.com",
            "Content-Type": "application/json",
        }

        # 构建请求体（根据实际API格式）
        payload = {
            "model": "qwen-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "stream": False,
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.qianwen.com/api/chat",
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
        生成图片（通义千问暂不支持Cookie方式，需要API Key）
        """
        return {
            "error": "通义千问图片生成需要使用 DashScope API Key，不支持Cookie方式",
            "images": [],
        }
