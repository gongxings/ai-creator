"""
积分和会员模型
"""
from sqlalchemy import Column, BigInteger, Integer, String, Enum, DateTime, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TransactionType(str, enum.Enum):
    """交易类型枚举"""
    RECHARGE = "recharge"  # 充值
    CONSUME = "consume"    # 消费
    REFUND = "refund"      # 退款
    REWARD = "reward"      # 奖励
    EXPIRE = "expire"      # 过期


class MembershipType(str, enum.Enum):
    """会员类型枚举"""
    MONTHLY = "monthly"    # 月度会员
    QUARTERLY = "quarterly"  # 季度会员
    YEARLY = "yearly"      # 年度会员


class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"    # 待支付
    PAID = "paid"          # 已支付
    FAILED = "failed"      # 支付失败
    REFUNDED = "refunded"  # 已退款
    CANCELLED = "cancelled"  # 已取消


class CreditTransaction(Base):
    """积分交易记录表"""
    __tablename__ = "credit_transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="交易ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    transaction_type = Column(
        Enum(TransactionType),
        nullable=False,
        comment="交易类型: recharge-充值, consume-消费, refund-退款, reward-奖励, expire-过期"
    )
    
    amount = Column(Integer, nullable=False, comment="积分数量（正数为增加，负数为减少）")
    balance_before = Column(Integer, nullable=False, comment="交易前余额")
    balance_after = Column(Integer, nullable=False, comment="交易后余额")
    
    description = Column(String(255), comment="交易描述")
    related_id = Column(BigInteger, comment="关联ID（如创作ID、订单ID等）")
    related_type = Column(String(50), comment="关联类型（如creation、order等）")
    
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    
    # 关系
    user = relationship("User", back_populates="credit_transactions")
    
    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"


class MembershipOrder(Base):
    """会员订单表"""
    __tablename__ = "membership_orders"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(64), unique=True, nullable=False, index=True, comment="订单号")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    membership_type = Column(
        Enum(MembershipType),
        nullable=False,
        comment="会员类型: monthly-月度, quarterly-季度, yearly-年度"
    )
    
    amount = Column(Numeric(10, 2), nullable=False, comment="订单金额")
    original_amount = Column(Numeric(10, 2), comment="原价")
    discount_amount = Column(Numeric(10, 2), default=0, comment="优惠金额")
    
    payment_method = Column(String(50), comment="支付方式（如alipay、wechat等）")
    payment_status = Column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        comment="支付状态: pending-待支付, paid-已支付, failed-失败, refunded-已退款, cancelled-已取消"
    )
    
    paid_at = Column(DateTime, comment="支付时间")
    expired_at = Column(DateTime, comment="会员到期时间")
    
    transaction_id = Column(String(128), comment="第三方交易ID")
    remark = Column(Text, comment="备注")
    
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
    
    # 关系
    user = relationship("User", back_populates="membership_orders")
    
    def __repr__(self):
        return f"<MembershipOrder(id={self.id}, order_no={self.order_no}, user_id={self.user_id}, status={self.payment_status})>"


class RechargeOrder(Base):
    """充值订单表"""
    __tablename__ = "recharge_orders"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(64), unique=True, nullable=False, index=True, comment="订单号")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    amount = Column(Numeric(10, 2), nullable=False, comment="充值金额")
    credits = Column(Integer, nullable=False, comment="获得积分数")
    bonus_credits = Column(Integer, default=0, comment="赠送积分数")
    
    payment_method = Column(String(50), comment="支付方式（如alipay、wechat等）")
    payment_status = Column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        comment="支付状态: pending-待支付, paid-已支付, failed-失败, refunded-已退款, cancelled-已取消"
    )
    
    paid_at = Column(DateTime, comment="支付时间")
    transaction_id = Column(String(128), comment="第三方交易ID")
    remark = Column(Text, comment="备注")
    
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
    
    # 关系
    user = relationship("User", back_populates="recharge_orders")
    
    def __repr__(self):
        return f"<RechargeOrder(id={self.id}, order_no={self.order_no}, user_id={self.user_id}, status={self.payment_status})>"


class CreditPrice(Base):
    """积分价格配置表"""
    __tablename__ = "credit_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="配置ID")
    name = Column(String(100), nullable=False, comment="套餐名称")
    amount = Column(Numeric(10, 2), nullable=False, comment="金额")
    credits = Column(Integer, nullable=False, comment="积分数")
    bonus_credits = Column(Integer, default=0, comment="赠送积分数")
    
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    description = Column(String(255), comment="描述")
    
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
    
    def __repr__(self):
        return f"<CreditPrice(id={self.id}, name={self.name}, amount={self.amount}, credits={self.credits})>"


class MembershipPrice(Base):
    """会员价格配置表"""
    __tablename__ = "membership_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="配置ID")
    name = Column(String(100), nullable=False, comment="套餐名称")
    membership_type = Column(
        Enum(MembershipType),
        nullable=False,
        comment="会员类型: monthly-月度, quarterly-季度, yearly-年度"
    )
    
    amount = Column(Numeric(10, 2), nullable=False, comment="金额")
    original_amount = Column(Numeric(10, 2), comment="原价")
    duration_days = Column(Integer, nullable=False, comment="有效天数")
    
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    description = Column(String(255), comment="描述")
    features = Column(Text, comment="会员特权（JSON格式）")
    
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
    
    def __repr__(self):
        return f"<MembershipPrice(id={self.id}, name={self.name}, type={self.membership_type}, amount={self.amount})>"
