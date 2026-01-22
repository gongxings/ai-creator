"""
运营功能模型
"""
from sqlalchemy import Column, BigInteger, Integer, String, Enum, DateTime, Numeric, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ActivityType(str, enum.Enum):
    """活动类型枚举"""
    CREDIT_GIFT = "credit_gift"  # 积分赠送
    RECHARGE_BONUS = "recharge_bonus"  # 充值优惠
    COUPON = "coupon"  # 优惠券
    REFERRAL = "referral"  # 推广返利


class ActivityStatus(str, enum.Enum):
    """活动状态枚举"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 已暂停
    ENDED = "ended"  # 已结束


class CouponType(str, enum.Enum):
    """优惠券类型枚举"""
    RECHARGE_DISCOUNT = "recharge_discount"  # 充值折扣
    RECHARGE_BONUS = "recharge_bonus"  # 充值赠送
    MEMBERSHIP_DISCOUNT = "membership_discount"  # 会员折扣


class CouponStatus(str, enum.Enum):
    """优惠券状态枚举"""
    UNUSED = "unused"  # 未使用
    USED = "used"  # 已使用
    EXPIRED = "expired"  # 已过期


class ReferralStatus(str, enum.Enum):
    """推广状态枚举"""
    PENDING = "pending"  # 待结算
    SETTLED = "settled"  # 已结算
    CANCELLED = "cancelled"  # 已取消


class Activity(Base):
    """运营活动表"""
    __tablename__ = "activities"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="活动ID")
    title = Column(String(200), nullable=False, comment="活动标题")
    activity_type = Column(
        Enum(ActivityType),
        nullable=False,
        comment="活动类型: credit_gift-积分赠送, recharge_bonus-充值优惠, coupon-优惠券, referral-推广返利"
    )
    
    status = Column(
        Enum(ActivityStatus),
        nullable=False,
        default=ActivityStatus.DRAFT,
        comment="活动状态: draft-草稿, active-进行中, paused-已暂停, ended-已结束"
    )
    
    description = Column(Text, comment="活动描述")
    rules = Column(JSON, comment="活动规则（JSON格式）")
    
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    
    target_users = Column(JSON, comment="目标用户条件（JSON格式）")
    max_participants = Column(Integer, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前参与人数")
    
    budget = Column(Numeric(10, 2), comment="活动预算")
    cost = Column(Numeric(10, 2), default=0, comment="已花费金额")
    
    created_by = Column(BigInteger, comment="创建人ID")
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
    participations = relationship("ActivityParticipation", back_populates="activity")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, title={self.title}, type={self.activity_type}, status={self.status})>"


class ActivityParticipation(Base):
    """活动参与记录表"""
    __tablename__ = "activity_participations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    activity_id = Column(BigInteger, ForeignKey("activities.id"), nullable=False, index=True, comment="活动ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    reward_type = Column(String(50), comment="奖励类型（credits、coupon等）")
    reward_amount = Column(Integer, comment="奖励数量")
    reward_data = Column(JSON, comment="奖励详情（JSON格式）")
    
    participated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="参与时间"
    )
    
    # 关系
    activity = relationship("Activity", back_populates="participations")
    user = relationship("User", back_populates="activity_participations")
    
    def __repr__(self):
        return f"<ActivityParticipation(id={self.id}, activity_id={self.activity_id}, user_id={self.user_id})>"


class Coupon(Base):
    """优惠券表"""
    __tablename__ = "coupons"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="优惠券ID")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="优惠券码")
    name = Column(String(200), nullable=False, comment="优惠券名称")
    
    coupon_type = Column(
        Enum(CouponType),
        nullable=False,
        comment="优惠券类型: recharge_discount-充值折扣, recharge_bonus-充值赠送, membership_discount-会员折扣"
    )
    
    discount_type = Column(String(20), comment="折扣类型（percent-百分比, fixed-固定金额）")
    discount_value = Column(Numeric(10, 2), comment="折扣值")
    
    min_amount = Column(Numeric(10, 2), comment="最低消费金额")
    max_discount = Column(Numeric(10, 2), comment="最大优惠金额")
    
    total_quantity = Column(Integer, comment="总发行量（null表示不限量）")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    
    valid_from = Column(DateTime, nullable=False, comment="有效期开始")
    valid_until = Column(DateTime, nullable=False, comment="有效期结束")
    
    description = Column(Text, comment="使用说明")
    activity_id = Column(BigInteger, ForeignKey("activities.id"), comment="关联活动ID")
    
    is_active = Column(Boolean, default=True, comment="是否启用")
    
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
    user_coupons = relationship("UserCoupon", back_populates="coupon")
    
    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, name={self.name}, type={self.coupon_type})>"


class UserCoupon(Base):
    """用户优惠券表"""
    __tablename__ = "user_coupons"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    coupon_id = Column(BigInteger, ForeignKey("coupons.id"), nullable=False, index=True, comment="优惠券ID")
    
    status = Column(
        Enum(CouponStatus),
        nullable=False,
        default=CouponStatus.UNUSED,
        comment="状态: unused-未使用, used-已使用, expired-已过期"
    )
    
    used_at = Column(DateTime, comment="使用时间")
    order_id = Column(BigInteger, comment="使用订单ID")
    
    received_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="领取时间"
    )
    
    # 关系
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")
    
    def __repr__(self):
        return f"<UserCoupon(id={self.id}, user_id={self.user_id}, coupon_id={self.coupon_id}, status={self.status})>"


class ReferralRecord(Base):
    """推广返利记录表"""
    __tablename__ = "referral_records"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    referrer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="推荐人ID")
    referee_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="被推荐人ID")
    
    referral_code = Column(String(50), index=True, comment="推荐码")
    
    # 返利信息
    reward_type = Column(String(50), comment="奖励类型（credits、cash等）")
    reward_amount = Column(Numeric(10, 2), comment="奖励金额")
    reward_credits = Column(Integer, comment="奖励积分")
    
    status = Column(
        Enum(ReferralStatus),
        nullable=False,
        default=ReferralStatus.PENDING,
        comment="状态: pending-待结算, settled-已结算, cancelled-已取消"
    )
    
    # 触发条件
    trigger_event = Column(String(50), comment="触发事件（register-注册, first_recharge-首充, membership-购买会员等）")
    trigger_amount = Column(Numeric(10, 2), comment="触发金额")
    
    settled_at = Column(DateTime, comment="结算时间")
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
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    referee = relationship("User", foreign_keys=[referee_id], back_populates="referrals_received")
    
    def __repr__(self):
        return f"<ReferralRecord(id={self.id}, referrer_id={self.referrer_id}, referee_id={self.referee_id}, status={self.status})>"


class OperationStatistics(Base):
    """运营统计表"""
    __tablename__ = "operation_statistics"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="统计ID")
    stat_date = Column(DateTime, nullable=False, index=True, comment="统计日期")
    stat_type = Column(String(50), nullable=False, index=True, comment="统计类型（daily-日, weekly-周, monthly-月）")
    
    # 用户统计
    new_users = Column(Integer, default=0, comment="新增用户数")
    active_users = Column(Integer, default=0, comment="活跃用户数")
    paying_users = Column(Integer, default=0, comment="付费用户数")
    
    # 收入统计
    recharge_amount = Column(Numeric(10, 2), default=0, comment="充值金额")
    recharge_count = Column(Integer, default=0, comment="充值次数")
    membership_amount = Column(Numeric(10, 2), default=0, comment="会员收入")
    membership_count = Column(Integer, default=0, comment="会员购买次数")
    
    # 积分统计
    credits_consumed = Column(Integer, default=0, comment="消耗积分")
    credits_recharged = Column(Integer, default=0, comment="充值积分")
    credits_rewarded = Column(Integer, default=0, comment="奖励积分")
    
    # 创作统计
    total_creations = Column(Integer, default=0, comment="总创作数")
    writing_count = Column(Integer, default=0, comment="写作次数")
    image_count = Column(Integer, default=0, comment="图片生成次数")
    video_count = Column(Integer, default=0, comment="视频生成次数")
    ppt_count = Column(Integer, default=0, comment="PPT生成次数")
    
    # 推广统计
    referral_count = Column(Integer, default=0, comment="推广人数")
    referral_reward = Column(Numeric(10, 2), default=0, comment="推广奖励")
    
    # 活动统计
    activity_participants = Column(Integer, default=0, comment="活动参与人数")
    activity_cost = Column(Numeric(10, 2), default=0, comment="活动成本")
    
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    
    def __repr__(self):
        return f"<OperationStatistics(id={self.id}, date={self.stat_date}, type={self.stat_type})>"
