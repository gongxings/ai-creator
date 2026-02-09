"""
智谱清言网页版适配器 - 基于 glm-free-api 优化
"""
from typing import Dict, Any, Optional
import uuid
import logging
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class ZhipuAdapter(PlatformAdapter):
    """智谱清言网页版适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://chatglm.cn"
    CHAT_ENDPOINT = "/chatglm/backend-api/assistant/stream"
    USER_INFO_ENDPOINT = "/chatglm/backend-api/v1/user/info"
    
    # 支持的模型列表
    SUPPORTED_MODELS = [
        "glm-4-flash",      # 免费快速模型
        "glm-4",            # 标准模型
        "glm-4v",           # 视觉模型
        "glm-4-plus",       # Plus 模型
        "glm-4-air",        # Air 模型
        "glm-4-flashx",     # FlashX 模型
        "glm-zero",         # 思考模型
    ]
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
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
        return f"{self.API_BASE}{self.USER_INFO_ENDPOINT}"
    
    def build_request_headers(self, cookies: Dict[str, str]) -> Dict[str, str]:
        """
        构建请求头（参考 glm-free-api）
        
        Args:
            cookies: Cookie字典
            
        Returns:
            请求头字典
        """
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": cookie_str,
            "Origin": "https://chatglm.cn",
            "Pragma": "no-cache",
            "Referer": "https://chatglm.cn/main/alltoolsdetail",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-App-Platform": "pc",
            "X-App-Version": "0.0.1",
            "X-Device-Id": str(uuid.uuid4()),
            "X-Request-Id": str(uuid.uuid4()),
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        智谱清言网页版使用token认证
        """
        cookies = credentials.get("cookies", {})
        
        # 使用优化后的请求头
        headers = self.build_request_headers(cookies)
        
        return {
            "model": "chatglm_web/glm-4-flash",
            "api_base": f"{self.API_BASE}{self.CHAT_ENDPOINT}",
            "custom_llm_provider": "chatglm_web",
            "extra_headers": headers,
            # 智谱清言网页版的免费模型
            "available_models": self.SUPPORTED_MODELS,
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

    async def send_message(
        self, 
        message: str, 
        cookies: Dict[str, str], 
        conversation_id: str = "", 
        assistant_id: str = "65940acff94777010aa6b796"
    ) -> Dict[str, Any]:
        """
        发送消息到智谱清言网页版（优化版 - 基于 glm-free-api）

        Args:
            message: 用户消息
            cookies: Cookie字典
            conversation_id: 会话ID（可选）
            assistant_id: 助手ID（默认使用 glm-4-flash）

        Returns:
            响应数据
        """
        import httpx

        # 使用优化后的请求头
        headers = self.build_request_headers(cookies)

        # 构建请求体（参考 glm-free-api）
        payload = {
            "assistant_id": assistant_id,
            "conversation_id": conversation_id,
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
                f"{self.API_BASE}{self.CHAT_ENDPOINT}",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            # 智谱清言返回SSE流
            lines = response.text.strip().split("\n")
            result = {"conversation_id": conversation_id, "content": ""}

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
                                        content_list = part.get("content", [])
                                        if content_list and len(content_list) > 0:
                                            result["content"] = content_list[0].get("text", "")
                                        result["conversation_id"] = parsed.get("conversation_id", conversation_id)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data}")
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
