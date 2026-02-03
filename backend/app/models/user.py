"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, Enum, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"
    VIP = "vip"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), comment="昵称")
    avatar = Column(String(255), comment="头像URL")
    phone = Column(String(20), comment="手机号")
    
    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER,
        comment="用户角色: user-普通用户, vip-VIP用户, admin-管理员"
    )
    
    status = Column(
        Enum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE,
        comment="用户状态: active-正常, inactive-未激活, banned-已封禁"
    )
    
    daily_quota = Column(Integer, nullable=False, default=100, comment="每日配额")
    used_quota = Column(Integer, nullable=False, default=0, comment="已使用配额")
    total_creations = Column(Integer, nullable=False, default=0, comment="总创作数")
    
    # 积分和会员相关
    credits = Column(Integer, nullable=False, default=0, comment="积分余额")
    is_member = Column(Integer, nullable=False, default=0, comment="是否会员: 0-否, 1-是")
    member_expired_at = Column(DateTime, comment="会员到期时间")
    
    last_login_at = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    deleted_at = Column(DateTime, comment="删除时间（软删除）")
    
    # 推广相关
    referral_code = Column(String(50), unique=True, index=True, comment="推荐码")
    referred_by = Column(BigInteger, comment="推荐人ID")
    
    # 关系
    creations = relationship("Creation", back_populates="user")
    ai_models = relationship("AIModel", back_populates="user")
    publish_records = relationship("PublishRecord", back_populates="user")
    platform_accounts = relationship("PlatformAccount", back_populates="user")
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    membership_orders = relationship("MembershipOrder", back_populates="user")
    recharge_orders = relationship("RechargeOrder", back_populates="user")
    
    # 运营相关关系
    activity_participations = relationship("ActivityParticipation", back_populates="user")
    user_coupons = relationship("UserCoupon", back_populates="user")
    referrals_made = relationship("ReferralRecord", foreign_keys="ReferralRecord.referrer_id", back_populates="referrer")
    referrals_received = relationship("ReferralRecord", foreign_keys="ReferralRecord.referee_id", back_populates="referee")
    
    # OAuth相关关系
    oauth_accounts = relationship("OAuthAccount", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
