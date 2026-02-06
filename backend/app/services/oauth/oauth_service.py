"""
OAuth账号管理服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger

from app.models.oauth_account import OAuthAccount
from app.models.oauth_usage_log import OAuthUsageLog
from app.models.platform_config import PlatformConfig
from app.services.oauth.encryption import encrypt_credentials, decrypt_credentials
from app.services.oauth.playwright_service import playwright_service
from app.services.oauth.adapters import (
    QwenAdapter, ChatQwenAdapter, QianwenAdapter, OpenAIAdapter, BaiduAdapter, ZhipuAdapter,
    SparkAdapter, ClaudeAdapter, GeminiAdapter, DoubaoAdapter
)


# 平台适配器映射
PLATFORM_ADAPTERS = {
    'qwen': QwenAdapter,
    'chatqwen': ChatQwenAdapter,
    'qianwen': QianwenAdapter,
    'openai': OpenAIAdapter,
    'baidu': BaiduAdapter,
    'zhipu': ZhipuAdapter,
    'spark': SparkAdapter,
    'claude': ClaudeAdapter,
    'gemini': GeminiAdapter,
    'doubao': DoubaoAdapter,
}


def get_adapter(platform: str, config: Dict[str, Any]):
    """获取平台适配器实例"""
    adapter_class = PLATFORM_ADAPTERS.get(platform)
    if not adapter_class:
        return None
    return adapter_class(platform, config)


class OAuthService:
    """OAuth账号管理服务"""
    
    async def authorize_account(
        self,
        db: Session,
        user_id: int,
        platform: str,
        account_name: Optional[str] = None,
    ) -> OAuthAccount:
        """
        授权OAuth账号
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            platform: 平台ID
            account_name: 账号名称
            
        Returns:
            OAuth账号对象
        """
        # 获取平台配置
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == platform
        ).first()
        
        if not platform_config:
            raise ValueError(f"Platform {platform} not found")
        
        if not platform_config.is_enabled:
            raise ValueError(f"Platform {platform} is disabled")
        
        # 获取适配器
        adapter = get_adapter(platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })
        
        if not adapter:
            raise ValueError(f"Adapter for platform {platform} not found")
        
        # 执行授权流程
        logger.info(f"Starting OAuth authorization for user {user_id}, platform {platform}")
        
        credentials = await playwright_service.authorize_platform(
            adapter.get_platform_config()
        )
        
        logger.info(f"Credentials received: {credentials.keys()}")
        logger.info(f"Cookies count: {len(credentials.get('cookies', {}))}")
        
        # 验证凭证
        if not adapter.validate_credentials(credentials):
            logger.error("Credentials validation failed")
            raise ValueError("Invalid credentials")
        
        logger.info("Credentials validated successfully")
        
        # 加密凭证
        logger.info("Encrypting credentials...")
        encrypted_credentials = encrypt_credentials(credentials)
        logger.info(f"Credentials encrypted, length: {len(encrypted_credentials)}")
        
        # 检查是否已存在账号
        existing_account = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == user_id,
                OAuthAccount.platform == platform
            )
        ).first()
        
        if existing_account:
            # 更新现有账号
            existing_account.credentials = encrypted_credentials
            existing_account.account_name = account_name or existing_account.account_name
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_account)
            logger.info(f"Updated OAuth account {existing_account.id}")
            return existing_account
        
        # 创建新账号
        quota_limit = adapter.get_quota_limit()
        
        logger.info(f"Creating new OAuth account: user_id={user_id}, platform={platform}")
        
        account = OAuthAccount(
            user_id=user_id,
            platform=platform,
            account_name=account_name or f"{platform}_account",
            credentials=encrypted_credentials,
            is_active=True,
            is_expired=False,
            quota_used=0,
            quota_limit=quota_limit,
        )
        
        logger.info("Adding account to database session...")
        db.add(account)
        logger.info("Committing database transaction...")
        db.commit()
        logger.info(f"Database commit successful, account ID: {account.id}")
        db.refresh(account)
        
        logger.info(f"Created OAuth account {account.id}")
        return account
    
    def create_or_update_account_with_credentials(
        self,
        db: Session,
        user_id: int,
        platform: str,
        credentials: Dict[str, Any],
        account_name: Optional[str] = None,
    ) -> OAuthAccount:
        """
        Manual cookie/token credential upsert.
        """
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == platform
        ).first()

        if not platform_config:
            raise ValueError(f"Platform {platform} not found")

        if not platform_config.is_enabled:
            raise ValueError(f"Platform {platform} is disabled")

        adapter = get_adapter(platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })

        if not adapter:
            raise ValueError(f"Adapter for platform {platform} not found")

        if not adapter.validate_credentials(credentials):
            raise ValueError("Invalid credentials")

        encrypted_credentials = encrypt_credentials(credentials)

        existing_account = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == user_id,
                OAuthAccount.platform == platform
            )
        ).first()

        if existing_account:
            existing_account.credentials = encrypted_credentials
            existing_account.account_name = account_name or existing_account.account_name
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_account)
            logger.info(f"Updated OAuth account {existing_account.id}")
            return existing_account

        quota_limit = adapter.get_quota_limit()

        account = OAuthAccount(
            user_id=user_id,
            platform=platform,
            account_name=account_name or f"{platform}_account",
            credentials=encrypted_credentials,
            is_active=True,
            is_expired=False,
            quota_used=0,
            quota_limit=quota_limit,
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        logger.info(f"Created OAuth account {account.id}")
        return account

    def get_user_accounts(
        self,
        db: Session,
        user_id: int,
        platform: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[OAuthAccount]:
        """
        获取用户的OAuth账号列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            platform: 平台ID（可选）
            is_active: 是否激活（可选）
            
        Returns:
            OAuth账号列表
        """
        query = db.query(OAuthAccount).filter(OAuthAccount.user_id == user_id)
        
        if platform:
            query = query.filter(OAuthAccount.platform == platform)
        
        if is_active is not None:
            query = query.filter(OAuthAccount.is_active == is_active)
        
        return query.all()
    
    def get_account(
        self,
        db: Session,
        account_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[OAuthAccount]:
        """
        获取OAuth账号
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            user_id: 用户ID（可选，用于权限检查）
            
        Returns:
            OAuth账号对象
        """
        query = db.query(OAuthAccount).filter(OAuthAccount.id == account_id)
        
        if user_id:
            query = query.filter(OAuthAccount.user_id == user_id)
        
        return query.first()
    
    def get_account_credentials(
        self,
        db: Session,
        account_id: int,
    ) -> Dict[str, Any]:
        """
        获取账号凭证（解密）
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            
        Returns:
            凭证字典
        """
        account = db.query(OAuthAccount).filter(OAuthAccount.id == account_id).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if not account.is_active:
            raise ValueError(f"Account {account_id} is not active")
        
        if account.is_expired:
            raise ValueError(f"Account {account_id} is expired")
        
        # 解密凭证
        credentials = decrypt_credentials(account.credentials)
        
        return credentials
    
    def update_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
        **kwargs
    ) -> OAuthAccount:
        """
        更新OAuth账号
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            user_id: 用户ID
            **kwargs: 更新字段
            
        Returns:
            更新后的账号对象
        """
        account = self.get_account(db, account_id, user_id)
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        account.updated_at = datetime.now()
        db.commit()
        db.refresh(account)
        
        logger.info(f"Updated OAuth account {account_id}")
        return account
    
    def delete_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ) -> bool:
        """
        删除OAuth账号
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        account = self.get_account(db, account_id, user_id)
        
        if not account:
            return False
        
        db.delete(account)
        db.commit()
        
        logger.info(f"Deleted OAuth account {account_id}")
        return True
    
    def log_usage(
        self,
        db: Session,
        account_id: int,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> OAuthUsageLog:
        """
        记录使用日志
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            model: 模型名称
            prompt_tokens: 提示词tokens
            completion_tokens: 完成tokens
            total_tokens: 总tokens
            request_data: 请求数据
            response_data: 响应数据
            error_message: 错误信息
            
        Returns:
            使用日志对象
        """
        # 更新账号使用量
        account = db.query(OAuthAccount).filter(OAuthAccount.id == account_id).first()
        if account:
            account.quota_used += total_tokens
            
            # 检查是否超出配额
            if account.quota_limit and account.quota_used >= account.quota_limit:
                account.is_expired = True
                logger.warning(f"Account {account_id} quota exceeded")
        
        # 创建使用日志
        log = OAuthUsageLog(
            account_id=account_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    def get_usage_logs(
        self,
        db: Session,
        account_id: int,
        limit: int = 100,
    ) -> List[OAuthUsageLog]:
        """
        获取使用日志
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            limit: 返回数量限制
            
        Returns:
            使用日志列表
        """
        return db.query(OAuthUsageLog).filter(
            OAuthUsageLog.account_id == account_id
        ).order_by(
            OAuthUsageLog.created_at.desc()
        ).limit(limit).all()
    
    async def check_account_validity(
        self,
        db: Session,
        account_id: int,
    ) -> bool:
        """
        检查账号凭证是否有效
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            
        Returns:
            是否有效
        """
        account = db.query(OAuthAccount).filter(OAuthAccount.id == account_id).first()
        
        if not account:
            return False
        
        # 获取平台配置
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == account.platform
        ).first()
        
        if not platform_config:
            return False
        
        # 获取适配器
        adapter = get_adapter(account.platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })
        
        if not adapter:
            return False
        
        try:
            # 解密凭证
            credentials = decrypt_credentials(account.credentials)
            
            # 如果凭证为空或无效，标记为过期
            if not credentials.get("cookies"):
                account.is_expired = True
                db.commit()
                logger.warning(f"Account {account_id} has invalid credentials, marked as expired")
                return False
            
            # 检查凭证有效性
            is_valid = await playwright_service.check_credentials_validity(
                adapter.get_platform_config(),
                credentials
            )
        except Exception as e:
            logger.error(f"Failed to check account validity: {e}")
            # 解密失败或其他错误，标记为过期
            account.is_expired = True
            db.commit()
            return False
        
        # 更新账号状态
        if not is_valid:
            account.is_expired = True
            db.commit()
            logger.warning(f"Account {account_id} credentials expired")
        
        return is_valid


# 全局OAuth服务实例
oauth_service = OAuthService()
