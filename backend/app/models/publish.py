"""
发布管理数据模型
"""
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class PlatformType(str, enum.Enum):
    """平台类型枚举"""
    WECHAT = "wechat"  # 微信公众号
    XIAOHONGSHU = "xiaohongshu"  # 小红书
    DOUYIN = "douyin"  # 抖音
    KUAISHOU = "kuaishou"  # 快手
    TOUTIAO = "toutiao"  # 今日头条
    BAIJIAHAO = "baijiahao"  # 百家号
    ZHIHU = "zhihu"  # 知乎
    JIANSHU = "jianshu"  # 简书


class PublishStatus(str, enum.Enum):
    """发布状态枚举"""
    PENDING = "pending"  # 待发布
    PUBLISHING = "publishing"  # 发布中
    SUCCESS = "success"  # 发布成功
    FAILED = "failed"  # 发布失败
    SCHEDULED = "scheduled"  # 已定时


class CookieStatus(str, enum.Enum):
    """Cookie状态枚举"""
    VALID = "valid"  # 有效
    INVALID = "invalid"  # 无效
    UNKNOWN = "unknown"  # 未知


class PlatformStatus(str, enum.Enum):
    """平台账号状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 未激活


class PlatformAccount(Base):
    """平台账号表"""
    __tablename__ = "platform_accounts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(SQLEnum(PlatformType), nullable=False, comment="平台类型")
    account_name = Column(String(100), nullable=False, comment="账号名称")
    account_id = Column(String(100), comment="平台账号ID")
    
    # 认证信息（加密存储）
    access_token = Column(Text, comment="访问令牌")
    refresh_token = Column(Text, comment="刷新令牌")
    expires_at = Column(DateTime, comment="令牌过期时间")
    credentials = Column(JSON, comment="其他认证信息")
    
    # Cookie认证（加密存储）
    cookies = Column(Text, comment="平台登录Cookie（加密）")
    cookies_updated_at = Column(DateTime, comment="Cookie更新时间")
    cookies_valid = Column(SQLEnum(CookieStatus), 
                          default=CookieStatus.UNKNOWN, comment="Cookie有效性")
    
    # 账号配置
    config = Column(JSON, comment="平台特定配置")
    is_active = Column(SQLEnum(PlatformStatus), 
                      default=PlatformStatus.ACTIVE, nullable=False, comment="账号状态")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="platform_accounts")
    publish_records = relationship("PublishRecord", back_populates="platform_account", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_platform", "user_id", "platform"),
        {"comment": "平台账号表"}
    )


class PublishRecord(Base):
    """发布记录表"""
    __tablename__ = "publish_records"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    creation_id = Column(BigInteger, ForeignKey("creations.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_account_id = Column(BigInteger, ForeignKey("platform_accounts.id", ondelete="CASCADE"), 
                                nullable=False, index=True)
    
    # 发布信息
    platform = Column(SQLEnum(PlatformType), nullable=False, comment="发布平台")
    status = Column(SQLEnum(PublishStatus), default=PublishStatus.PENDING, 
                   nullable=False, index=True, comment="发布状态")
    
    # 发布内容（可能经过平台适配）
    content_type = Column(String(50), comment="内容类型")
    title = Column(String(200), comment="标题")
    content = Column(Text, comment="内容")
    cover_image = Column(String(500), comment="封面图片URL")
    media_urls = Column(JSON, comment="媒体文件URLs")
    tags = Column(JSON, comment="标签")
    
    # 平台返回信息
    platform_post_id = Column(String(100), comment="平台文章ID")
    platform_url = Column(String(500), comment="平台文章URL")
    platform_response = Column(JSON, comment="平台返回的完整响应")
    
    # 定时发布
    scheduled_at = Column(DateTime, comment="定时发布时间")
    published_at = Column(DateTime, comment="实际发布时间")
    
    # 错误信息
    error_message = Column(Text, comment="错误信息")
    retry_count = Column(BigInteger, default=0, comment="重试次数")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="publish_records")
    creation = relationship("Creation", back_populates="publish_records")
    platform_account = relationship("PlatformAccount", back_populates="publish_records")
    
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_scheduled", "scheduled_at", "status"),
        {"comment": "发布记录表"}
    )
