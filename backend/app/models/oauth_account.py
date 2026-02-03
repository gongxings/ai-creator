"""
OAuth账号模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthAccount(Base):
    """OAuth账号表"""
    __tablename__ = "oauth_accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False, comment="平台ID(qwen/doubao/zhipu/chatgpt/gemini/codex)")
    account_name = Column(String(100), comment="账号名称（用户自定义）")
    credentials = Column(Text, nullable=False, comment="加密的凭证（Cookie/Token）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_expired = Column(Boolean, default=False, comment="是否过期")
    quota_used = Column(Integer, default=0, comment="已使用次数")
    quota_limit = Column(Integer, comment="额度限制")
    last_used_at = Column(DateTime, comment="最后使用时间")
    expired_at = Column(DateTime, comment="过期时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="oauth_accounts")
    usage_logs = relationship("OAuthUsageLog", back_populates="account", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_user_platform", "user_id", "platform"),
    )

    def __repr__(self):
        return f"<OAuthAccount(id={self.id}, user_id={self.user_id}, platform={self.platform})>"
