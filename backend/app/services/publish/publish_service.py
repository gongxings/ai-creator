"""
发布服务
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.publish import PublishRecord, PlatformAccount
from app.schemas.publish import PublishCreate, PublishStatus
from app.services.publish.platforms import get_platform
from app.core.exceptions import BusinessException


class PublishService:
    """发布服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def publish_content(
        self,
        user_id: int,
        publish_data: PublishCreate
    ) -> List[PublishRecord]:
        """
        发布内容到多个平台
        
        Args:
            user_id: 用户ID
            publish_data: 发布数据
            
        Returns:
            List[PublishRecord]: 发布记录列表
        """
        records = []
        
        for platform_name in publish_data.platforms:
            # 获取平台账号
            account = self.db.query(PlatformAccount).filter(
                and_(
                    PlatformAccount.user_id == user_id,
                    PlatformAccount.platform == platform_name,
                    PlatformAccount.is_active == True
                )
            ).first()
            
            if not account:
                raise BusinessException(f"未找到{platform_name}平台的有效账号")
            
            # 创建发布记录
            record = PublishRecord(
                user_id=user_id,
                creation_id=publish_data.creation_id,
                platform=platform_name,
                platform_account_id=account.id,
                title=publish_data.title,
                content=publish_data.content,
                cover_image=publish_data.cover_image,
                tags=publish_data.tags,
                status=PublishStatus.PENDING,
                scheduled_at=publish_data.scheduled_at
            )
            self.db.add(record)
            self.db.flush()
            
            # 如果是立即发布，执行发布操作
            if not publish_data.scheduled_at:
                try:
                    await self._execute_publish(record, account)
                except Exception as e:
                    record.status = PublishStatus.FAILED
                    record.error_message = str(e)
            
            records.append(record)
        
        self.db.commit()
        return records
    
    async def _execute_publish(
        self,
        record: PublishRecord,
        account: PlatformAccount
    ) -> None:
        """
        执行发布操作
        
        Args:
            record: 发布记录
            account: 平台账号
        """
        try:
            # 获取平台实例
            platform = get_platform(record.platform)
            
            # 准备发布数据
            publish_data = {
                "title": record.title,
                "content": record.content,
                "cover_image": record.cover_image,
                "tags": record.tags,
            }
            
            # 执行发布
            record.status = PublishStatus.PUBLISHING
            self.db.commit()
            
            result = await platform.publish(
                credentials=account.credentials,
                content=publish_data
            )
            
            # 更新发布记录
            record.status = PublishStatus.SUCCESS
            record.platform_post_id = result.get("post_id")
            record.platform_url = result.get("url")
            record.published_at = datetime.utcnow()
            
        except Exception as e:
            record.status = PublishStatus.FAILED
            record.error_message = str(e)
            raise
        finally:
            self.db.commit()
    
    async def retry_publish(self, record_id: int, user_id: int) -> PublishRecord:
        """
        重试发布
        
        Args:
            record_id: 发布记录ID
            user_id: 用户ID
            
        Returns:
            PublishRecord: 发布记录
        """
        record = self.db.query(PublishRecord).filter(
            and_(
                PublishRecord.id == record_id,
                PublishRecord.user_id == user_id
            )
        ).first()
        
        if not record:
            raise BusinessException("发布记录不存在")
        
        if record.status == PublishStatus.SUCCESS:
            raise BusinessException("该内容已成功发布，无需重试")
        
        # 获取平台账号
        account = self.db.query(PlatformAccount).filter(
            PlatformAccount.id == record.platform_account_id
        ).first()
        
        if not account:
            raise BusinessException("平台账号不存在")
        
        # 执行发布
        await self._execute_publish(record, account)
        
        return record
    
    def get_publish_history(
        self,
        user_id: int,
        platform: Optional[str] = None,
        status: Optional[PublishStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[PublishRecord], int]:
        """
        获取发布历史
        
        Args:
            user_id: 用户ID
            platform: 平台名称（可选）
            status: 发布状态（可选）
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            tuple: (发布记录列表, 总数)
        """
        query = self.db.query(PublishRecord).filter(
            PublishRecord.user_id == user_id
        )
        
        if platform:
            query = query.filter(PublishRecord.platform == platform)
        
        if status:
            query = query.filter(PublishRecord.status == status)
        
        total = query.count()
        records = query.order_by(
            PublishRecord.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return records, total
    
    def get_publish_status(self, record_id: int, user_id: int) -> PublishRecord:
        """
        获取发布状态
        
        Args:
            record_id: 发布记录ID
            user_id: 用户ID
            
        Returns:
            PublishRecord: 发布记录
        """
        record = self.db.query(PublishRecord).filter(
            and_(
                PublishRecord.id == record_id,
                PublishRecord.user_id == user_id
            )
        ).first()
        
        if not record:
            raise BusinessException("发布记录不存在")
        
        return record
    
    def bind_platform_account(
        self,
        user_id: int,
        platform: str,
        credentials: Dict
    ) -> PlatformAccount:
        """
        绑定平台账号
        
        Args:
            user_id: 用户ID
            platform: 平台名称
            credentials: 平台凭证
            
        Returns:
            PlatformAccount: 平台账号
        """
        # 检查是否已存在
        existing = self.db.query(PlatformAccount).filter(
            and_(
                PlatformAccount.user_id == user_id,
                PlatformAccount.platform == platform
            )
        ).first()
        
        if existing:
            # 更新凭证
            existing.credentials = credentials
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        
        # 创建新账号
        account = PlatformAccount(
            user_id=user_id,
            platform=platform,
            credentials=credentials,
            is_active=True
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def unbind_platform_account(
        self,
        user_id: int,
        platform: str
    ) -> None:
        """
        解绑平台账号
        
        Args:
            user_id: 用户ID
            platform: 平台名称
        """
        account = self.db.query(PlatformAccount).filter(
            and_(
                PlatformAccount.user_id == user_id,
                PlatformAccount.platform == platform
            )
        ).first()
        
        if account:
            account.is_active = False
            self.db.commit()
    
    def get_platform_accounts(self, user_id: int) -> List[PlatformAccount]:
        """
        获取用户的平台账号列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[PlatformAccount]: 平台账号列表
        """
        return self.db.query(PlatformAccount).filter(
            and_(
                PlatformAccount.user_id == user_id,
                PlatformAccount.is_active == True
            )
        ).all()
