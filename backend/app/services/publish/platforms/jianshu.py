"""
简书平台发布服务
"""
from typing import Dict, Any, Optional, List

from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class JianshuPublisher(BasePlatformPublisher):
    """简书平台发布实现（草稿占位版本）"""

    def get_platform_name(self) -> str:
        return "简书"

    def get_login_url(self) -> str:
        return "https://www.jianshu.com/sign_in"

    async def validate_cookies(self, account: PlatformAccount) -> bool:
        cookies = self.get_cookies(account)
        return bool(cookies)

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
        await self.check_cookies_or_raise(account)
        return {
            "draft_id": None,
            "draft_url": "https://www.jianshu.com/writer",
            "message": "简书草稿创建已排队（待接入实际API调用）"
        }
