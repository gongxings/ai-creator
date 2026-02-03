"""
OAuth使用日志模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthUsageLog(Base):
    """OAuth使用日志表"""
    __tablename__ = "oauth_usage_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(BigInteger, ForeignKey("oauth_accounts.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False, comment="平台ID")
    model = Column(String(100), comment="使用的模型")
    request_type = Column(String(50), comment="请求类型")
    prompt_tokens = Column(Integer, comment="提示词tokens")
    completion_tokens = Column(Integer, comment="完成tokens")
    total_tokens = Column(Integer, comment="总tokens")
    status = Column(String(20), comment="状态: success/failed/expired")
    error_message = Column(Text, comment="错误信息")
    response_time = Column(Integer, comment="响应时间(ms)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    user = relationship("User")
    account = relationship("OAuthAccount", back_populates="usage_logs")

    # 索引
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_account_id", "account_id"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<OAuthUsageLog(id={self.id}, platform={self.platform}, status={self.status})>"
