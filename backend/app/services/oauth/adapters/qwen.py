"""
通义千问网页版适配器 - 基于 qwen-free-api 优化
"""
from typing import Dict, Any, Optional
import uuid
import logging
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class QwenAdapter(PlatformAdapter):
    """通义千问网页版适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://qianwen.biz.aliyun.com"
    CONVERSATION_ENDPOINT = "/dialog/conversation"
    DELETE_SESSION_ENDPOINT = "/dialog/session/delete"
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL - 网页聊天版本"""
        return "https://tongyi.aliyun.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/tongyi.aliyun.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "tongyi_sso_ticket",  # 主要凭证
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "login_aliyunid_ticket",  # 备用凭证
            "aliyun_choice",
            "_samesite_flag_",
            "cna",
            "isg",
            "tfstk",
            "t",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".aliyun.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return "https://tongyi.aliyun.com/"
    
    @staticmethod
    def generate_complete_cookie(ticket: str) -> str:
        """
        生成完整的 Cookie 字符串
        参考 qwen-free-api 实现
        
        Args:
            ticket: tongyi_sso_ticket 或 login_aliyunid_ticket
            
        Returns:
            完整的 Cookie 字符串
        """
        # 判断是哪种 ticket
        cookie_name = 'login_aliyunid_ticket' if len(ticket) > 100 else 'tongyi_sso_ticket'
        
        # 生成随机 UUID
        random_t = str(uuid.uuid4()).replace('-', '')
        
        return "; ".join([
            f"{cookie_name}={ticket}",
            "aliyun_choice=intl",
            "_samesite_flag_=true",
            f"t={random_t}",
        ])
    
    def build_request_headers(self, ticket: str) -> Dict[str, str]:
        """
        构建请求头（参考 qwen-free-api）
        
        Args:
            ticket: tongyi_sso_ticket
            
        Returns:
            请求头字典
        """
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": self.generate_complete_cookie(ticket),
            "Origin": "https://tongyi.aliyun.com",
            "Pragma": "no-cache",
            "Referer": "https://tongyi.aliyun.com/",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Platform": "pc_tongyi",
            "X-Xsrf-Token": str(uuid.uuid4()),
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于网页版API调用
        
        通义千问网页版使用Cookie认证，需要构建特殊的配置
        """
        cookies = credentials.get("cookies", {})
        ticket = cookies.get("tongyi_sso_ticket") or cookies.get("login_aliyunid_ticket")
        
        if not ticket:
            raise ValueError("缺少 tongyi_sso_ticket 或 login_aliyunid_ticket")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(ticket)
        
        return {
            "model": "qwen_web/qwen-turbo",
            "api_base": f"{self.API_BASE}{self.CONVERSATION_ENDPOINT}",
            "custom_llm_provider": "qwen_web",
            "extra_headers": headers,
            # 通义千问网页版的免费模型
            "available_models": [
                "qwen-turbo",
                "qwen-plus",
                "qwen-max",
                "qwen-vl-max",
                "qwen2.5-72b",
                "qwen-max-longcontext",  # 长文本模型
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
    
    def build_request_body(self, message: str, session_id: str = "", model: str = "") -> Dict[str, Any]:
        """
        构建请求体（参考 qwen-free-api）
        
        Args:
            message: 用户消息
            session_id: 会话ID
            model: 模型名称（可选）
            
        Returns:
            请求体字典
        """
        request_id = str(uuid.uuid4()).replace('-', '')
        file_upload_batch_id = str(uuid.uuid4())
        
        return {
            "mode": "chat",
            "model": model,
            "action": "next",
            "userAction": "chat",
            "requestId": request_id,
            "sessionId": session_id,
            "sessionType": "text_chat",
            "parentMsgId": "",
            "params": {
                "fileUploadBatchId": file_upload_batch_id
            },
            "contents": [
                {
                    "content": message,
                    "contentType": "text",
                    "role": "user",
                }
            ],
        }
    
    async def send_message(self, message: str, cookies: Dict[str, str], session_id: str = "", model: str = "") -> Dict[str, Any]:
        """
        发送消息到通义千问网页版（优化版 - 基于 qwen-free-api）
        
        Args:
            message: 用户消息
            cookies: Cookie字典
            session_id: 会话ID（可选）
            model: 模型名称（可选）

        Returns:
            响应数据
        """
        import httpx

        # 获取 ticket
        ticket = cookies.get("tongyi_sso_ticket") or cookies.get("login_aliyunid_ticket")
        if not ticket:
            raise ValueError("缺少 tongyi_sso_ticket 或 login_aliyunid_ticket")

        # 使用优化后的请求头
        headers = self.build_request_headers(ticket)
        
        # 使用优化后的请求体
        payload = self.build_request_body(message, session_id, model)

        async with httpx.AsyncClient(http2=True) as client:
            response = await client.post(
                f"{self.API_BASE}{self.CONVERSATION_ENDPOINT}",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def remove_conversation(self, session_id: str, cookies: Dict[str, str]) -> Dict[str, Any]:
        """
        删除会话（参考 qwen-free-api）
        
        Args:
            session_id: 会话ID
            cookies: Cookie字典
            
        Returns:
            删除结果
        """
        import httpx
        
        # 获取 ticket
        ticket = cookies.get("tongyi_sso_ticket") or cookies.get("login_aliyunid_ticket")
        if not ticket:
            raise ValueError("缺少 tongyi_sso_ticket 或 login_aliyunid_ticket")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(ticket)
        
        # 构建删除请求体
        payload = {
            "sessionId": session_id
        }
        
        async with httpx.AsyncClient(http2=True) as client:
            response = await client.post(
                f"{self.API_BASE}{self.DELETE_SESSION_ENDPOINT}",
                headers=headers,
                json=payload,
                timeout=30.0,
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
