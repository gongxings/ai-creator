"""
豆包网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


class DoubaoAdapter(PlatformAdapter):
    """豆包网页版适配器"""
    
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
            "s_v_web_id",
        ]

    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "tt_webid",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".doubao.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://www.doubao.com/"
    
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
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        豆包网页版使用sessionid认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "doubao_web/doubao-lite-4k",
            "api_base": "https://www.doubao.com/api/chat/stream",
            "custom_llm_provider": "doubao_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://www.doubao.com/",
                "Origin": "https://www.doubao.com",
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
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, bot_id: str = None) -> Dict[str, Any]:
        """
        发送消息到豆包网页版
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            bot_id: 机器人ID（可选）
            
        Returns:
            响应数据
        """
        import httpx
        
        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.doubao.com/",
            "Origin": "https://www.doubao.com",
            "Content-Type": "application/json",
        }
        
        # 构建请求体
        payload = {
            "conversation_id": conversation_id or "",
            "bot_id": bot_id or "7358044466096914465",  # 默认豆包助手ID
            "user_input": message,
            "stream": True,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.doubao.com/api/chat/stream",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            
            # 豆包返回SSE流
            lines = response.text.strip().split("\n")
            result = {"conversation_id": conversation_id}
            
            for line in lines:
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data and data != "[DONE]":
                        import json
                        try:
                            parsed = json.loads(data)
                            if "text" in parsed:
                                result["content"] = parsed["text"]
                            if "conversation_id" in parsed:
                                result["conversation_id"] = parsed["conversation_id"]
                        except:
                            continue
            
            return result
