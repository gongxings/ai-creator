"""
基于Cookie的AI服务管理器
负责从OAuth账号获取Cookie并调用相应的AI服务
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials
from app.services.ai.doubao_service import DoubaoService
from app.services.ai.cookie_based_service import CookieBasedAIService
from app.services.ai.video_service import create_doubao_video_service
from app.services.ai.ppt_service import create_ppt_service

logger = logging.getLogger(__name__)


class CookieAIServiceManager:
    """Cookie-based AI服务管理器"""
    
    def __init__(self, db: Session):
        """初始化服务管理器"""
        self.db = db
    
    def get_user_oauth_accounts(self, user_id: int, platform: Optional[str] = None) -> list:
        """
        获取用户的OAuth账号列表
        
        Args:
            user_id: 用户ID
            platform: 平台名称（可选）
            
        Returns:
            OAuth账号列表
        """
        query = self.db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user_id,
            OAuthAccount.is_active == True,
            OAuthAccount.is_expired == False,
        )
        
        if platform:
            query = query.filter(OAuthAccount.platform == platform)
        
        return query.all()
    
    def get_service_for_platform(self, user_id: int, platform: str) -> Optional[CookieBasedAIService]:
        """
        获取指定平台的AI服务实例
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            
        Returns:
            AI服务实例或None
        """
        accounts = self.get_user_oauth_accounts(user_id, platform)
        if not accounts:
            logger.warning(f"No active {platform} account found for user {user_id}")
            return None
        
        # 使用第一个可用的账号
        account = accounts[0]
        
        try:
            # 解密凭证
            credentials = decrypt_credentials(account.credentials)
            cookies = credentials.get("cookies", {})
            user_agent = credentials.get("user_agent")
            
            # 根据平台创建相应的服务实例
            if platform == "doubao":
                service = DoubaoService(cookies=cookies, user_agent=user_agent)
                return service
            
            # 未来支持更多平台
            # elif platform == "qwen":
            #     return QwenService(cookies=cookies, user_agent=user_agent)
            # elif platform == "claude":
            #     return ClaudeService(cookies=cookies, user_agent=user_agent)
            
            logger.error(f"Unsupported platform: {platform}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create service for platform {platform}: {e}")
            return None
    
    async def generate_text_with_cookie(
        self,
        user_id: int,
        platform: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        使用Cookie调用AI生成文本
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        service = self.get_service_for_platform(user_id, platform)
        if not service:
            raise ValueError(f"No available {platform} account for user {user_id}")
        
        # 验证Cookie是否有效
        is_valid = await service.validate_cookies()
        if not is_valid:
            logger.warning(f"Cookie validation failed for {platform}")
            raise ValueError(f"{platform} Cookie已过期，请重新授权")
        
        # 调用生成文本
        return await service.generate_text(prompt, **kwargs)
    
    async def generate_text_stream_with_cookie(
        self,
        user_id: int,
        platform: str,
        prompt: str,
        **kwargs
    ):
        """
        使用Cookie调用AI生成文本（流式）
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            prompt: 提示词
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        service = self.get_service_for_platform(user_id, platform)
        if not service:
            raise ValueError(f"No available {platform} account for user {user_id}")
        
        # 验证Cookie是否有效
        is_valid = await service.validate_cookies()
        if not is_valid:
            logger.warning(f"Cookie validation failed for {platform}")
            raise ValueError(f"{platform} Cookie已过期，请重新授权")
        
        # 检查是否支持流式生成
        if hasattr(service, 'generate_text_stream'):
            async for chunk in service.generate_text_stream(prompt, **kwargs):
                yield chunk
        else:
            # 不支持流式，一次性返回
            result = await service.generate_text(prompt, **kwargs)
            yield result
    
    async def generate_image_with_cookie(
        self,
        user_id: int,
        platform: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Cookie调用AI生成图片
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            prompt: 图片描述
            **kwargs: 其他参数
            
        Returns:
            {
                "images": [...],  # 图片URL列表
                "error": "错误信息"（可选）
            }
        """
        service = self.get_service_for_platform(user_id, platform)
        if not service:
            return {
                "images": [],
                "error": f"No available {platform} account for user {user_id}"
            }
        
        # 验证Cookie是否有效
        is_valid = await service.validate_cookies()
        if not is_valid:
            logger.warning(f"Cookie validation failed for {platform}")
            return {
                "images": [],
                "error": f"{platform} Cookie已过期，请重新授权"
            }
        
        # 调用生成图片
        return await service.generate_image(prompt, **kwargs)
    
    async def generate_video_with_cookie(
        self,
        user_id: int,
        platform: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Cookie调用AI生成视频
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            prompt: 视频描述
            **kwargs: 其他参数
            
        Returns:
            {
                "video_url": "视频URL",
                "error": "错误信息"（可选）
            }
        """
        service = self.get_service_for_platform(user_id, platform)
        if not service:
            return {
                "video_url": None,
                "error": f"No available {platform} account for user {user_id}"
            }
        
        # 验证Cookie是否有效
        is_valid = await service.validate_cookies()
        if not is_valid:
            logger.warning(f"Cookie validation failed for {platform}")
            return {
                "video_url": None,
                "error": f"{platform} Cookie已过期，请重新授权"
            }
        
        # 调用生成视频
        return await service.generate_video(prompt, **kwargs)


# 全局实例创建器
def create_cookie_service_manager(db: Session) -> CookieAIServiceManager:
    """创建Cookie AI服务管理器"""
    return CookieAIServiceManager(db)
