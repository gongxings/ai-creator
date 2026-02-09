"""
即梦 AI 图像生成适配器 - 基于 jimeng-free-api 优化
"""
from typing import Dict, Any, Optional, List
import uuid
import logging
import time
from app.services.oauth.adapters.base import PlatformAdapter

logger = logging.getLogger(__name__)


class JimengAdapter(PlatformAdapter):
    """即梦 AI 图像生成适配器 - 优化版"""
    
    # API 端点
    API_BASE = "https://jimeng.jianying.com"
    IMAGE_GEN_ENDPOINT = "/ai_tool/api/v1/public/multimodal/sync_text2image"
    CHAT_ENDPOINT = "/ai_tool/api/v1/public/multimodal/sync_text2image"  # 即梦主要用于图像生成
    
    # 支持的模型列表
    SUPPORTED_MODELS = [
        "jimeng-3.0",       # 默认最新模型
        "jimeng-2.1",       # 2.1 版本
        "jimeng-2.0-pro",   # 2.0 专业版
        "jimeng-2.0",       # 2.0 版本
        "jimeng-1.4",       # 1.4 版本
        "jimeng-xl-pro",    # XL 专业版
    ]
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        super().__init__(platform_id, config)
    
    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        return "https://jimeng.jianying.com/"
    
    def get_success_pattern(self) -> str:
        """获取登录成功的URL模式"""
        return "**/jimeng.jianying.com/**"
    
    def get_cookie_names(self) -> list:
        """获取需要提取的Cookie名称"""
        return [
            "sessionid",  # 主要凭证
        ]
    
    def get_optional_cookie_names(self) -> list:
        """获取可选的Cookie名称"""
        return [
            "sid_guard",
            "uid_tt",
            "uid_tt_ss",
            "sid_tt",
            "ssid_ucp_v1",
            "passport_csrf_token",
            "passport_csrf_token_default",
            "odin_tt",
            "store-region",
            "store-region-src",
        ]
    
    def get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".jianying.com"
    
    def get_check_url(self) -> str:
        """获取凭证验证URL"""
        return f"{self.API_BASE}/ai_tool/api/v1/user/info"
    
    def build_request_headers(self, sessionid: str) -> Dict[str, str]:
        """
        构建请求头（参考 jimeng-free-api）
        
        Args:
            sessionid: 会话ID
            
        Returns:
            请求头字典
        """
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": f"sessionid={sessionid}",
            "Origin": "https://jimeng.jianying.com",
            "Pragma": "no-cache",
            "Referer": "https://jimeng.jianying.com/ai-tool/image/generate",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Secsdk-Csrf-Token": str(uuid.uuid4()),
        }
    
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置 - 用于图像生成API调用
        
        即梦主要用于图像生成，使用sessionid认证
        """
        cookies = credentials.get("cookies", {})
        sessionid = cookies.get("sessionid")
        
        if not sessionid:
            raise ValueError("缺少 sessionid")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(sessionid)
        
        return {
            "model": "jimeng_web/jimeng-3.0",
            "api_base": f"{self.API_BASE}{self.IMAGE_GEN_ENDPOINT}",
            "custom_llm_provider": "jimeng_web",
            "extra_headers": headers,
            # 即梦支持的模型
            "available_models": self.SUPPORTED_MODELS,
        }
    
    def get_quota_limit(self) -> int:
        """获取配额限制（即梦每日免费 66 积分）"""
        # 每日 66 积分，每次生成消耗 1 积分
        return 66
    
    def get_rate_limit(self) -> Dict[str, int]:
        """获取速率限制"""
        return {
            "requests_per_minute": 10,
            "images_per_day": 66,
        }
    
    def build_image_request_body(
        self, 
        prompt: str, 
        model: str = "jimeng-3.0",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        sample_strength: float = 0.5
    ) -> Dict[str, Any]:
        """
        构建图像生成请求体（参考 jimeng-free-api）
        
        Args:
            prompt: 提示词
            model: 模型名称
            negative_prompt: 反向提示词
            width: 图像宽度
            height: 图像高度
            sample_strength: 精细度 (0-1)
            
        Returns:
            请求体字典
        """
        return {
            "model_version": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "sample_strength": sample_strength,
            "task_type": "text2image",
            "batch_size": 4,  # 默认生成 4 张图片
        }
    
    async def generate_image(
        self,
        prompt: str,
        cookies: Dict[str, str],
        model: str = "jimeng-3.0",
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        sample_strength: float = 0.5
    ) -> Dict[str, Any]:
        """
        生成图片（优化版 - 基于 jimeng-free-api）
        
        Args:
            prompt: 提示词
            cookies: Cookie字典
            model: 模型名称
            negative_prompt: 反向提示词
            width: 图像宽度
            height: 图像高度
            sample_strength: 精细度
            
        Returns:
            图像生成结果
        """
        import httpx
        
        # 获取 sessionid
        sessionid = cookies.get("sessionid")
        if not sessionid:
            raise ValueError("缺少 sessionid")
        
        # 使用优化后的请求头
        headers = self.build_request_headers(sessionid)
        
        # 构建请求体
        payload = self.build_image_request_body(
            prompt=prompt,
            model=model,
            negative_prompt=negative_prompt or "",
            width=width,
            height=height,
            sample_strength=sample_strength
        )
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.API_BASE}{self.IMAGE_GEN_ENDPOINT}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if result.get("status_code") == 0 and result.get("data"):
                images = result["data"].get("images", [])
                return {
                    "created": int(time.time()),
                    "data": [{"url": img.get("url")} for img in images],
                    "model": model,
                }
            else:
                error_msg = result.get("status_msg", "图像生成失败")
                logger.error(f"即梦图像生成失败: {error_msg}")
                return {
                    "error": error_msg,
                    "images": [],
                }
    
    async def send_message(
        self, 
        message: str, 
        cookies: Dict[str, str], 
        model: str = "jimeng-3.0"
    ) -> Dict[str, Any]:
        """
        发送消息（即梦主要用于图像生成，此方法将提示词转换为图像）
        
        Args:
            message: 提示词
            cookies: Cookie字典
            model: 模型名称
            
        Returns:
            响应数据（包含生成的图像链接）
        """
        # 将文本消息转换为图像生成请求
        result = await self.generate_image(
            prompt=message,
            cookies=cookies,
            model=model
        )
        
        if "error" not in result:
            # 格式化为聊天响应格式
            image_urls = [img["url"] for img in result.get("data", [])]
            content = "\n".join([f"![image_{i}]({url})" for i, url in enumerate(image_urls)])
            
            return {
                "id": str(uuid.uuid4()),
                "model": model,
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2
                },
                "created": result.get("created", int(time.time()))
            }
        else:
            return result
