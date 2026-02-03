"""
讯飞星火网页版适配器
"""
from typing import Dict, Any
from app.services.oauth.adapters.base import PlatformAdapter


class SparkAdapter(PlatformAdapter):
    """讯飞星火网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://xinghuo.xfyun.cn/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/xinghuo.xfyun.cn/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "ssoSessionId",
            "refreshToken",
            "accessToken",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".xfyun.cn"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://xinghuo.xfyun.cn/iflygpt/u/user/info"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        讯飞星火网页版使用token认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "spark_web/spark-lite",
            "api_base": "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat",
            "custom_llm_provider": "spark_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://xinghuo.xfyun.cn/",
                "Origin": "https://xinghuo.xfyun.cn",
            },
            # 讯飞星火网页版的免费模型
            "available_models": [
                "spark-lite",
                "spark-pro",
                "spark-max",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（讯飞星火网页版免费额度）"""
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], chat_id: str = None) -> Dict[str, Any]:
        """
        发送消息到讯飞星火网页版
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            chat_id: 聊天ID（可选）
            
        Returns:
            响应数据
        """
        import httpx
        
        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://xinghuo.xfyun.cn/",
            "Origin": "https://xinghuo.xfyun.cn",
            "Content-Type": "application/json",
        }
        
        # 构建请求体
        payload = {
            "chatId": chat_id or "",
            "text": message,
            "clientType": "1",
            "model": "general",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            
            # 讯飞星火返回SSE流
            lines = response.text.strip().split("\n")
            result = {"chat_id": chat_id}
            
            for line in lines:
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data and data != "[DONE]":
                        import json
                        try:
                            parsed = json.loads(data)
                            if "content" in parsed:
                                result["content"] = parsed["content"]
                            if "chatId" in parsed:
                                result["chat_id"] = parsed["chatId"]
                        except:
                            continue
            
            return result
