"""
通义千问网页版适配器
"""
from typing import Dict, Any
from app.services.oauth.adapters.base import PlatformAdapter


class QwenAdapter(PlatformAdapter):
    """通义千问网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://tongyi.aliyun.com/qianwen/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/tongyi.aliyun.com/qianwen/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "login_aliyunid_ticket",
            "cna",
            "isg",
            "aliyun_choice",
            "aliyun_lang",
            "login_aliyunid_csrf",
            "login_aliyunid_pk",
            "tfstk",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".aliyun.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://tongyi.aliyun.com/qianwen/"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        通义千问网页版使用Cookie认证，需要构建特殊的配置
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "qwen_web/qwen-turbo",
            "api_base": "https://qianwen.biz.aliyun.com/dialog/conversation",
            "custom_llm_provider": "qwen_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://tongyi.aliyun.com/",
                "Origin": "https://tongyi.aliyun.com",
            },
            # 通义千问网页版的免费模型
            "available_models": [
                "qwen-turbo",
                "qwen-plus",
                "qwen-max",
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
        发送消息到通义千问网页版
        
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
            "Referer": "https://tongyi.aliyun.com/qianwen/",
            "Origin": "https://tongyi.aliyun.com",
            "Content-Type": "application/json",
        }
        
        # 构建请求体
        payload = {
            "model": "",
            "action": "next",
            "mode": "chat",
            "userAction": "chat",
            "requestId": "",
            "sessionId": conversation_id or "",
            "sessionType": "text_chat",
            "params": {
                "content": message,
            },
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://qianwen.biz.aliyun.com/dialog/conversation",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
