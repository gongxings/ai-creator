"""
基于Cookie的AI服务基类 - 用于网页版API调用
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import httpx

logger = logging.getLogger(__name__)


class CookieBasedAIService(ABC):
    """基于Cookie的AI服务基类"""
    
    def __init__(self, cookies: Dict[str, str], user_agent: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化Cookie-based AI服务
        
        Args:
            cookies: Cookie字典 {cookie_name: cookie_value}
            user_agent: User-Agent（可选）
            config: 额外配置
        """
        self.cookies = cookies
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.config = config or {}
        self.client = None
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """获取平台名称"""
        pass
    
    @abstractmethod
    def get_check_url(self) -> str:
        """获取Cookie验证URL"""
        pass
    
    def get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        构建请求头
        
        Args:
            referer: Referer头（可选）
            
        Returns:
            请求头字典
        """
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        headers = {
            "Cookie": cookie_str,
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        if referer:
            headers["Referer"] = referer
            headers["Origin"] = referer.split("/")[-1] if "/" in referer else referer
        
        return headers
    
    async def validate_cookies(self) -> bool:
        """
        验证Cookie是否有效
        
        Returns:
            Cookie是否有效
        """
        try:
            headers = self.get_headers(referer=self.get_check_url())
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(
                    self.get_check_url(),
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"{self.get_platform_name()} cookie validation successful")
                    return True
                else:
                    logger.warning(f"{self.get_platform_name()} cookie validation failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"{self.get_platform_name()} cookie validation error: {e}")
            return False
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大令牌数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图片
        
        Args:
            prompt: 提示词
            size: 图片尺寸
            style: 风格（可选）
            negative_prompt: 负面提示词（可选）
            **kwargs: 其他参数
            
        Returns:
            {
                "images": [...],  # 图片URL列表
                "error": "错误信息"（可选）
            }
        """
        pass
    
    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频
        
        Args:
            prompt: 提示词
            duration: 视频时长（秒）
            **kwargs: 其他参数
            
        Returns:
            {
                "video_url": "视频URL",
                "error": "错误信息"（可选）
            }
        """
        pass
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
