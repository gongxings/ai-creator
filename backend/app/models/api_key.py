"""
API Key管理模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, DateTime, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship, foreign
from app.core.database import Base
from app.models.user import User

class APIKey(Base):
    """API Key管理表"""
    __tablename__ = "api_keys"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="API Key ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    key_name = Column(String(100), nullable=False, comment="Key名称")
    key_hash = Column(String(64), nullable=False, unique=True, comment="Key的SHA256哈希值")
    key_prefix = Column(String(20), nullable=False, comment="Key前缀（用于显示）")
    key_suffix = Column(String(10), nullable=False, comment="Key后缀（用于显示）")

    is_active = Column(Boolean, default=True, comment="是否启用")

    # 系统默认标识
    is_system_default = Column(Boolean, default=False, index=True, comment="是否系统默认 Key")
    system_default_order = Column(Integer, default=99, comment="系统默认排序（数字越小越优先）")
    
    # AI Provider 信息
    provider = Column(String(50), comment="AI 提供商（openai/anthropic/zhipu 等）")
    model_name = Column(String(100), comment="模型名称")
    base_url = Column(String(255), nullable=True, comment="API 基础 URL")
    
    # 加密存储的原始 Key（用于解密后调用 API）
    encrypted_key = Column(Text, nullable=True, comment="加密存储的原始 APIKey")
    
    # 统计信息
    total_assigned_users = Column(Integer, default=0, comment="已分配用户数")

    # 权限控制
    allowed_models = Column(JSON, comment="允许使用的模型列表（为空表示全部）")
    rate_limit = Column(Integer, default=60, comment="速率限制（次/分钟）")

    # 使用统计
    total_requests = Column(BigInteger, default=0, comment="总请求次数")
    total_tokens = Column(BigInteger, default=0, comment="总Token使用量")
    last_used_at = Column(DateTime, comment="最后使用时间")

    # 时间管理
    expires_at = Column(DateTime, comment="过期时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系 - 使用 primaryjoin 替代外键
    user = relationship(
        "User",
        back_populates="api_keys",
        primaryjoin="APIKey.user_id == foreign(User.id)",
        remote_side="User.id"
    )
    usage_logs = relationship(
        "APIKeyUsageLog",
        back_populates="api_key",
        cascade="all, delete-orphan",
        primaryjoin="APIKey.id == APIKeyUsageLog.api_key_id"
    )

    # 索引
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_key_hash", "key_hash"),
    )

    def __repr__(self):
        return f"<APIKey(id={self.id}, user_id={self.user_id}, name={self.key_name})>"


class APIKeyUsageLog(Base):
    """API Key 使用日志表"""
    __tablename__ = "api_key_usage_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志 ID")
    api_key_id = Column(BigInteger, nullable=False, comment="API Key ID")
    used_by_user_id = Column(BigInteger, index=True, comment="实际使用用户 ID（用于统计）")

    # 模型信息
    model_id = Column(String(100), comment="模型ID")
    model_name = Column(String(100), comment="模型名称")

    # 请求信息
    endpoint = Column(String(100), comment="请求端点")
    method = Column(String(10), comment="请求方法")

    # Token统计
    prompt_tokens = Column(Integer, default=0, comment="输入Token数")
    completion_tokens = Column(Integer, default=0, comment="输出Token数")
    total_tokens = Column(Integer, default=0, comment="总Token数")

    # 详细数据
    request_data = Column(JSON, comment="请求数据（可选）")
    response_data = Column(JSON, comment="响应数据（可选）")
    error_message = Column(Text, comment="错误信息")

    # 追踪信息
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="User-Agent")

    # 性能指标
    response_time = Column(Integer, comment="响应时间（毫秒）")
    status_code = Column(Integer, comment="HTTP状态码")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系 - 使用 primaryjoin 替代外键
    api_key = relationship(
        "APIKey",
        back_populates="usage_logs",
        primaryjoin="APIKeyUsageLog.api_key_id == foreign(APIKey.id)",
        remote_side="APIKey.id"
    )

    def __repr__(self):
        return f"<APIKeyUsageLog(id={self.id}, api_key_id={self.api_key_id}, model={self.model_name})>"


# 索引
__table_args__ = (
    Index("idx_api_key_id", "api_key_id"),
    Index("idx_created_at", "created_at"),
)
