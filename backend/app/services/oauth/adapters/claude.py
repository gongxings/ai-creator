"""
Claude网页版适配器
"""
from typing import Dict, Any
from app.services.oauth.adapters.base import PlatformAdapter


class ClaudeAdapter(PlatformAdapter):
    """Claude网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://claude.ai/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/claude.ai/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "sessionKey",
            "__cf_bm",
            "_cfuvid",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".claude.ai"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://claude.ai/api/organizations"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        Claude网页版使用sessionKey认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "claude_web/claude-3-sonnet",
            "api_base": "https://claude.ai/api",
            "custom_llm_provider": "claude_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://claude.ai/",
                "Origin": "https://claude.ai",
            },
            # Claude网页版的免费模型
            "available_models": [
                "claude-3-opus",  # 需要Pro订阅
                "claude-3-sonnet",
                "claude-3-haiku",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（Claude网页版免费额度）"""
        # 网页版免费额度
        return 500000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 50,
            "tokens_per_minute": 80000,
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, organization_id: str = None) -> Dict[str, Any]:
        """
        发送消息到Claude网页版
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            organization_id: 组织ID（必需）
            
        Returns:
            响应数据
        """
        import httpx
        import uuid
        
        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://claude.ai/",
            "Origin": "https://claude.ai",
            "Content-Type": "application/json",
        }
        
        # 如果没有conversation_id，先创建会话
        if not conversation_id:
            async with httpx.AsyncClient() as client:
                create_response = await client.post(
                    f"https://claude.ai/api/organizations/{organization_id}/chat_conversations",
                    headers=headers,
                    json={"name": ""},
                    timeout=30.0,
                )
                create_response.raise_for_status()
                conversation_data = create_response.json()
                conversation_id = conversation_data.get("uuid")
        
        # 构建请求体
        payload = {
            "prompt": message,
            "timezone": "Asia/Shanghai",
            "attachments": [],
            "files": [],
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://claude.ai/api/organizations/{organization_id}/chat_conversations/{conversation_id}/completion",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            
            # Claude返回的是SSE流，需要解析
            lines = response.text.strip().split("\n")
            result = {"conversation_id": conversation_id}
            
            for line in lines:
                if line.startswith("data: "):
                    data = line[6:]
                    if data:
                        import json
                        try:
                            parsed = json.loads(data)
                            if "completion" in parsed:
                                result["completion"] = parsed["completion"]
                            if "stop_reason" in parsed:
                                result["stop_reason"] = parsed["stop_reason"]
                        except:
                            continue
            
            return result
