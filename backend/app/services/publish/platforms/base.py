"""
平台发布器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List\nfrom urllib.parse import urlparse
from datetime import datetime
import json
import logging
from cryptography.fernet import Fernet

from app.models.publish import PlatformAccount
from app.core.config import settings


class BasePlatformPublisher(ABC):
    """平台发布器基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # 使用配置中的加密密钥
        self.cipher = Fernet(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
    
    @abstractmethod
    async def create_draft(
        self,
        account: PlatformAccount,
        title: str,
        content: str,
        cover_image: Optional[str] = None,
        media_urls: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建草稿（不直接发布）
        
        Args:
            account: 平台账号
            title: 标题
            content: 内容
            cover_image: 封面图片URL
            media_urls: 媒体文件URLs
            tags: 标签列表
            **kwargs: 其他平台特定参数
            
        Returns:
            Dict: 草稿信息，包含draft_id和draft_url
        """
        pass
    
    @abstractmethod
    async def validate_cookies(
        self,
        account: PlatformAccount
    ) -> bool:
        """
        验证Cookie有效性
        
        Args:
            account: 平台账号
            
        Returns:
            bool: Cookie是否有效
        """
        pass
    
    def get_cookies(self, account: PlatformAccount) -> Optional[Dict[str, str]]:
        """
        获取解密后的Cookie
        
        Args:
            account: 平台账号
            
        Returns:
            Dict: Cookie字典，如果没有Cookie返回None
        """
        if not account.cookies:
            return None
        
        try:
            # 解密Cookie
            decrypted = self.cipher.decrypt(account.cookies.encode()).decode()
            return json.loads(decrypted)
        except Exception as e:
            self.logger.error(f"解密Cookie失败: {str(e)}")
            return None
    
    def set_cookies(
        self,
        account: PlatformAccount,
        cookies: Dict[str, str]
    ) -> None:
        """
        保存加密的Cookie
        
        Args:
            account: 平台账号
            cookies: Cookie字典
        """
        try:
            # 加密Cookie
            cookie_json = json.dumps(cookies)
            encrypted = self.cipher.encrypt(cookie_json.encode()).decode()
            
            # 保存到账号
            account.cookies = encrypted
            account.cookies_updated_at = datetime.utcnow()
            account.cookies_valid = "unknown"  # 需要验证
        except Exception as e:
            self.logger.error(f"加密Cookie失败: {str(e)}")
            raise
    
    async def check_cookies_or_raise(
        self,
        account: PlatformAccount
    ) -> Dict[str, str]:
        """
        检查Cookie是否存在且有效，如果无效则抛出异常
        
        Args:
            account: 平台账号
            
        Returns:
            Dict: Cookie字典
            
        Raises:
            ValueError: Cookie不存在或无效
        """
        cookies = self.get_cookies(account)
        
        if not cookies:
            raise ValueError(
                f"请先登录{self.get_platform_name()}平台并上传Cookie。"
                f"登录地址：{self.get_login_url()}"
            )
        
        # 验证Cookie有效性
        try:
            is_valid = await self.validate_cookies(account)
        except TypeError:
            cookie_list = self._build_cookie_list(self.get_login_url(), cookies)
            is_valid = await self.validate_cookies(cookie_list)
        
        if not is_valid:
            # 更新Cookie状态
            account.cookies_valid = "invalid"
            raise ValueError(
                f"{self.get_platform_name()}平台Cookie已失效，请重新登录并上传Cookie。"
                f"登录地址：{self.get_login_url()}"
            )
        
        # 更新Cookie状态
        account.cookies_valid = "valid"
        return cookies
    
        def _build_cookie_list(self, login_url: str, cookies: Dict[str, str]) -> List[Dict[str, Any]]:
        parsed = urlparse(login_url)
        host = parsed.netloc
        parts = host.split(".")
        root = ".".join(parts[-2:]) if len(parts) >= 2 else host
        domain = f".{root}"
        return [
            {"name": name, "value": value, "domain": domain, "path": "/"}
            for name, value in cookies.items()
        ]

\1(self) -> str:
        """获取平台名称"""
        pass
    
    @abstractmethod
    def get_login_url(self) -> str:
        """获取平台登录URL"""
        pass
    
    async def upload_image(
        self,
        image_url: str,
        cookies: Dict[str, str]
    ) -> Optional[str]:
        """
        上传图片到平台（可选实现）
        
        Args:
            image_url: 图片URL
            cookies: Cookie字典
            
        Returns:
            str: 平台图片ID或URL
        """
        return image_url
    
    async def upload_video(
        self,
        video_url: str,
        cookies: Dict[str, str]
    ) -> Optional[str]:
        """
        上传视频到平台（可选实现）
        
        Args:
            video_url: 视频URL
            cookies: Cookie字典
            
        Returns:
            str: 平台视频ID或URL
        """
        return video_url
