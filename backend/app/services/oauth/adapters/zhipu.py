"""
智谱清言网页版适配器
"""
from typing import Dict, Any, Optional
from app.services.oauth.adapters.base import PlatformAdapter


class ZhipuAdapter(PlatformAdapter):
    """智谱清言网页版适配器"""
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://chatglm.cn/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/chatglm.cn/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "chatglm_token",
            "chatglm_refresh_token",
            "chatglm_user_id",
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return []
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".chatglm.cn"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://chatglm.cn/chatglm/backend-api/v1/user/info"
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        智谱清言网页版使用token认证
        """
        cookies = credentials.get("cookies", {})
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "model": "chatglm_web/glm-4-flash",
            "api_base": "https://chatglm.cn/chatglm/backend-api/assistant/stream",
            "custom_llm_provider": "chatglm_web",
            "extra_headers": {
                "Cookie": cookie_str,
                "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                "Referer": "https://chatglm.cn/",
                "Origin": "https://chatglm.cn",
            },
            # 智谱清言网页版的免费模型
            "available_models": [
                "glm-4-flash",
                "glm-4",
                "glm-4v",
            ],
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（智谱清言网页版免费额度）"""
        return 1000000
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000,
        }

    async def send_message(self, message: str, cookies: Dict[str, str], conversation_id: str = None, assistant_id: str = None) -> Dict[str, Any]:
        """
        发送消息到智谱清言网页版

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            assistant_id: 助手ID（可选）

        Returns:
            响应数据
        """
        import httpx

        # 构建请求头
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://chatglm.cn/",
            "Origin": "https://chatglm.cn",
            "Content-Type": "application/json",
        }

        # 构建请求体
        payload = {
            "assistant_id": assistant_id or "65940acff94777010aa6b796",
            "conversation_id": conversation_id or "",
            "messages": [{"role": "user", "content": [{"type": "text", "text": message}]}],
            "meta_data": {
                "channel": "",
                "draft_id": "",
                "input_question_type": "xxxx",
                "is_test": False,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://chatglm.cn/chatglm/backend-api/assistant/stream",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # 智谱清言返回SSE流
            lines = response.text.strip().split("\n")
            result = {"conversation_id": conversation_id}

            for line in lines:
                if line.startswith("data: "):
                    data = line[6:]
                    if data and data != "[DONE]":
                        import json
                        try:
                            parsed = json.loads(data)
                            if "parts" in parsed:
                                for part in parsed["parts"]:
                                    if part.get("status") == "finish":
                                        result["content"] = part.get("content", [""])[0].get("text", "")
                                        result["conversation_id"] = parsed.get("conversation_id")
                        except:
                            continue

            return result

    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        生成图片（智谱清言暂不支持Cookie方式，需要API Key）
        """
        return {
            "error": "智谱清言图片生成需要使用 API Key，不支持Cookie方式",
            "images": [],
        }
