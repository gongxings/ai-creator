"""
API Key管理服务
"""
import secrets
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import APIKey, APIKeyUsageLog, User
from app.schemas.api_key import (
    APIKeyCreate, APIKeyResponse, APIKeyCreateResponse,
    APIKeyUpdate, APIKeyUsageLogResponse, APIKeyStatsResponse
)
from app.core.exceptions import BusinessException


class APIKeyService:
    """API Key管理服务"""
    
    @staticmethod
    def generate_api_key() -> str:
        """生成API Key（sk-开头的32位随机字符）"""
        random_part = secrets.token_urlsafe(24)  # 生成32个字符
        return f"sk-{random_part}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """计算API Key的SHA256哈希"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        遮罩API Key，只显示前后几位
        例如：sk-abc...xyz1234
        """
        if len(api_key) <= 12:
            return api_key
        return f"{api_key[:6]}...{api_key[-4:]}"
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: int,
        key_data: APIKeyCreate
    ) -> APIKeyCreateResponse:
        """
        创建新的API Key
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            key_data: API Key创建数据
        
        Returns:
            创建的API Key信息（包含完整Key）
        """
        # 生成API Key
        api_key = APIKeyService.generate_api_key()
        key_hash = APIKeyService.hash_api_key(api_key)
        
        # 提取前缀和后缀用于显示
        # API Key格式: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # 前缀: sk-xxxx (前8位)
        # 后缀: 最后4位
        key_prefix = api_key[:8] if len(api_key) >= 8 else api_key
        key_suffix = api_key[-4:] if len(api_key) >= 4 else api_key
        
        # 计算过期时间
        expires_at = None
        if key_data.expires_days:
            expires_at = datetime.now() + timedelta(days=key_data.expires_days)
        
        # 创建数据库记录
        db_key = APIKey(
            user_id=user_id,
            key_name=key_data.key_name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            key_suffix=key_suffix,
            is_active=True,
            rate_limit=key_data.rate_limit,
            allowed_models=key_data.allowed_models,
            expires_at=expires_at
        )
        
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        
        # 返回响应（包含完整Key）
        return APIKeyCreateResponse(
            id=db_key.id,
            key_name=db_key.key_name,
            api_key=api_key,  # 完整Key，仅此一次返回
            key_display=APIKeyService.mask_api_key(api_key),
            is_active=db_key.is_active,
            rate_limit=db_key.rate_limit,
            allowed_models=db_key.allowed_models,
            expires_at=db_key.expires_at,
            created_at=db_key.created_at
        )
    
    @staticmethod
    def get_user_api_keys(
        db: Session,
        user_id: int
    ) -> List[APIKeyResponse]:
        """
        获取用户的所有API Key
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            API Key列表
        """
        keys = db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc()).all()
        
        result = []
        for key in keys:
            # 使用存储的前缀和后缀生成显示用的Key
            key_display = f"{key.key_prefix}...{key.key_suffix}"
            
            result.append(APIKeyResponse(
                id=key.id,
                key_name=key.key_name,
                key_display=key_display,
                is_active=key.is_active,
                rate_limit=key.rate_limit,
                allowed_models=key.allowed_models,
                total_requests=key.total_requests,
                total_tokens=key.total_tokens,
                last_used_at=key.last_used_at,
                expires_at=key.expires_at,
                created_at=key.created_at
            ))
        
        return result
    
    @staticmethod
    def get_api_key_by_id(
        db: Session,
        key_id: int,
        user_id: int
    ) -> Optional[APIKey]:
        """
        根据ID获取API Key
        
        Args:
            db: 数据库会话
            key_id: Key ID
            user_id: 用户ID
        
        Returns:
            API Key对象或None
        """
        return db.query(APIKey).filter(
            and_(
                APIKey.id == key_id,
                APIKey.user_id == user_id
            )
        ).first()
    
    @staticmethod
    def update_api_key(
        db: Session,
        key_id: int,
        user_id: int,
        update_data: APIKeyUpdate
    ) -> APIKeyResponse:
        """
        更新API Key
        
        Args:
            db: 数据库会话
            key_id: Key ID
            user_id: 用户ID
            update_data: 更新数据
        
        Returns:
            更新后的API Key信息
        """
        db_key = APIKeyService.get_api_key_by_id(db, key_id, user_id)
        if not db_key:
            raise BusinessException("API Key不存在")
        
        # 更新字段
        if update_data.key_name is not None:
            db_key.key_name = update_data.key_name
        if update_data.is_active is not None:
            db_key.is_active = update_data.is_active
        if update_data.rate_limit is not None:
            db_key.rate_limit = update_data.rate_limit
        if update_data.allowed_models is not None:
            db_key.allowed_models = update_data.allowed_models
        
        db.commit()
        db.refresh(db_key)
        
        # 使用存储的前缀和后缀生成显示用的Key
        key_display = f"{db_key.key_prefix}...{db_key.key_suffix}"
        
        return APIKeyResponse(
            id=db_key.id,
            key_name=db_key.key_name,
            key_display=key_display,
            is_active=db_key.is_active,
            rate_limit=db_key.rate_limit,
            allowed_models=db_key.allowed_models,
            total_requests=db_key.total_requests,
            total_tokens=db_key.total_tokens,
            last_used_at=db_key.last_used_at,
            expires_at=db_key.expires_at,
            created_at=db_key.created_at
        )
    
    @staticmethod
    def delete_api_key(
        db: Session,
        key_id: int,
        user_id: int
    ) -> bool:
        """
        删除API Key
        
        Args:
            db: 数据库会话
            key_id: Key ID
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        db_key = APIKeyService.get_api_key_by_id(db, key_id, user_id)
        if not db_key:
            raise BusinessException("API Key不存在")
        
        db.delete(db_key)
        db.commit()
        return True
    
    @staticmethod
    def verify_api_key(
        db: Session,
        api_key: str
    ) -> Optional[APIKey]:
        """
        验证API Key并返回对应的记录
        
        Args:
            db: 数据库会话
            api_key: API Key字符串
        
        Returns:
            API Key对象或None
        """
        key_hash = APIKeyService.hash_api_key(api_key)
        
        db_key = db.query(APIKey).filter(
            APIKey.key_hash == key_hash
        ).first()
        
        if not db_key:
            return None
        
        # 检查是否激活
        if not db_key.is_active:
            return None
        
        # 检查是否过期
        if db_key.expires_at and db_key.expires_at < datetime.now():
            return None
        
        return db_key
    
    @staticmethod
    def log_api_key_usage(
        db: Session,
        api_key_id: int,
        model_id: Optional[str],
        model_name: Optional[str],
        endpoint: Optional[str],
        method: Optional[str],
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time: Optional[int] = None,
        status_code: Optional[int] = None
    ) -> APIKeyUsageLog:
        """
        记录API Key使用日志
        
        Args:
            db: 数据库会话
            api_key_id: API Key ID
            model_id: 模型ID
            model_name: 模型名称
            endpoint: 端点
            method: 请求方法
            prompt_tokens: 提示Token数
            completion_tokens: 完成Token数
            total_tokens: 总Token数
            request_data: 请求数据
            response_data: 响应数据
            error_message: 错误信息
            ip_address: IP地址
            user_agent: User Agent
            response_time: 响应时间（毫秒）
            status_code: 状态码
        
        Returns:
            使用日志对象
        """
        # 创建日志记录
        log = APIKeyUsageLog(
            api_key_id=api_key_id,
            model_id=model_id,
            model_name=model_name,
            endpoint=endpoint,
            method=method,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            response_time=response_time,
            status_code=status_code
        )
        
        db.add(log)
        
        # 更新API Key统计
        db_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if db_key:
            db_key.total_requests += 1
            db_key.total_tokens += total_tokens
            db_key.last_used_at = datetime.now()
        
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def get_api_key_stats(
        db: Session,
        key_id: int,
        user_id: int,
        limit: int = 10
    ) -> APIKeyStatsResponse:
        """
        获取API Key使用统计
        
        Args:
            db: 数据库会话
            key_id: Key ID
            user_id: 用户ID
            limit: 最近日志数量
        
        Returns:
            统计信息
        """
        db_key = APIKeyService.get_api_key_by_id(db, key_id, user_id)
        if not db_key:
            raise BusinessException("API Key不存在")
        
        # 统计成功和失败的请求
        success_count = db.query(func.count(APIKeyUsageLog.id)).filter(
            and_(
                APIKeyUsageLog.api_key_id == key_id,
                APIKeyUsageLog.error_message.is_(None)
            )
        ).scalar() or 0
        
        failed_count = db.query(func.count(APIKeyUsageLog.id)).filter(
            and_(
                APIKeyUsageLog.api_key_id == key_id,
                APIKeyUsageLog.error_message.isnot(None)
            )
        ).scalar() or 0
        
        # 计算平均响应时间
        avg_response_time = db.query(func.avg(APIKeyUsageLog.response_time)).filter(
            and_(
                APIKeyUsageLog.api_key_id == key_id,
                APIKeyUsageLog.response_time.isnot(None)
            )
        ).scalar()
        
        # 获取最近的日志
        recent_logs = db.query(APIKeyUsageLog).filter(
            APIKeyUsageLog.api_key_id == key_id
        ).order_by(APIKeyUsageLog.created_at.desc()).limit(limit).all()
        
        recent_logs_response = [
            APIKeyUsageLogResponse(
                id=log.id,
                model_id=log.model_id,
                model_name=log.model_name,
                endpoint=log.endpoint,
                method=log.method,
                prompt_tokens=log.prompt_tokens,
                completion_tokens=log.completion_tokens,
                total_tokens=log.total_tokens,
                error_message=log.error_message,
                ip_address=log.ip_address,
                response_time=log.response_time,
                status_code=log.status_code,
                created_at=log.created_at
            )
            for log in recent_logs
        ]
        
        return APIKeyStatsResponse(
            total_requests=db_key.total_requests,
            total_tokens=db_key.total_tokens,
            success_requests=success_count,
            failed_requests=failed_count,
            avg_response_time=float(avg_response_time) if avg_response_time else None,
            last_used_at=db_key.last_used_at,
            recent_logs=recent_logs_response
        )
