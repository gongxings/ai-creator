"""
AI模型配置数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AIProvider(str, enum.Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"
    BAIDU = "baidu"
    ALI = "ali"
    TENCENT = "tencent"


class ModelType(str, enum.Enum):
    """模型类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True, comment="模型ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(100), nullable=False, comment="模型名称")
    provider = Column(String(50), nullable=False, comment="提供商(openai/anthropic/zhipu/baidu/ali/tencent)")
    model_name = Column(String(100), nullable=False, comment="模型标识")
    api_key = Column(Text, nullable=False, comment="API密钥(加密存储)")
    base_url = Column(String(255), nullable=True, comment="API基础URL")
    is_default = Column(Boolean, default=False, comment="是否为默认模型")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="模型描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="ai_models")
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', provider='{self.provider}')>"
