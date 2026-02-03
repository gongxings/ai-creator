"""
平台配置模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, JSON
from app.core.database import Base


class PlatformConfig(Base):
    """平台配置表"""
    __tablename__ = "platform_configs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    platform_id = Column(String(50), unique=True, nullable=False, comment="平台ID")
    platform_name = Column(String(100), nullable=False, comment="平台名称")
    platform_icon = Column(String(255), comment="平台图标URL")
    priority = Column(Integer, default=99, comment="优先级（数字越小越优先）")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    oauth_config = Column(JSON, comment="OAuth配置")
    litellm_config = Column(JSON, comment="LiteLLM配置")
    quota_config = Column(JSON, comment="额度配置")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<PlatformConfig(id={self.id}, platform_id={self.platform_id}, platform_name={self.platform_name})>"
