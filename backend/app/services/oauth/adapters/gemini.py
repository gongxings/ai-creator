"""
Google Gemini网页版适配器
"""
from typing import Dict, Any
from app.services.oauth.adapters.base import PlatformAdapter


class GeminiAdapter(PlatformAdapter):
    """Google Gemini网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://gemini.google.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/gemini.google.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "SID",
            "HSID",
            "SSID",
            "APISID",
            "SAPISID",
            "__Secure-1PSID",
            "__Secure-3PSID",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".google.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://gemini.google.com/"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        Gemini网页版使用Google账号Cookie认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "gemini_web/gemini-pro",
            "api_base": "https://gemini.google.com/app",
            "custom_llm_provider": "gemini_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://gemini.google.com/",
                "Origin": "https://gemini.google.com",
            },
            # Gemini网页版的免费模型
            "available_models": [
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（Gemini网页版免费额度）"""
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, message_id: str = None) -> Dict[str, Any]:
        """
        发送消息到Gemini网页版
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            message_id: 消息ID（可选）
            
        Returns:
            响应数据
        """
        import httpx
        
        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://gemini.google.com/",
            "Origin": "https://gemini.google.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        # 构建请求体
        payload = {
            "f.req": f'[[null,"[\\"{message}\\"]"]]',
            "at": cookies.get("__Secure-1PSID", ""),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
                headers=headers,
                data=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            
            # Gemini返回特殊格式，需要解析
            text = response.text
            import json
            try:
                # 提取JSON数据
                lines = text.strip().split("\n")
                for line in lines:
                    if line.startswith("["):
                        data = json.loads(line)
                        if len(data) > 0 and len(data[0]) > 2:
                            content = data[0][2]
                            if content:
                                parsed_content = json.loads(content)
                                if len(parsed_content) > 4:
                                    return {
                                        "content": parsed_content[4][0][1][0],
                                        "conversation_id": parsed_content[1][0],
                                        "message_id": parsed_content[1][1],
                                    }
            except:
                pass
            
            return {}
