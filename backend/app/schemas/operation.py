"""
运营功能Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============ 活动相关 ============

class ActivityCreate(BaseModel):
    """创建活动"""
    title: str = Field(..., description="活动标题")
    activity_type: str = Field(..., description="活动类型")
    description: Optional[str] = Field(None, description="活动描述")
    rules: Optional[Dict[str, Any]] = Field(None, description="活动规则")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    target_users: Optional[Dict[str, Any]] = Field(None, description="目标用户条件")
    max_participants: Optional[int] = Field(None, description="最大参与人数")
    budget: Optional[Decimal] = Field(None, description="活动预算")


class ActivityUpdate(BaseModel):
    """更新活动"""
    title: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    target_users: Optional[Dict[str, Any]] = None
    max_participants: Optional[int] = None
    budget: Optional[Decimal] = None


class ActivityResponse(BaseModel):
    """活动响应"""
    id: int
    title: str
    activity_type: str
    status: str
    description: Optional[str]
    rules: Optional[Dict[str, Any]]
    start_time: datetime
    end_time: datetime
    target_users: Optional[Dict[str, Any]]
    max_participants: Optional[int]
    current_participants: int
    budget: Optional[Decimal]
    cost: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityParticipate(BaseModel):
    """参与活动"""
    activity_id: int = Field(..., description="活动ID")


class ActivityParticipationResponse(BaseModel):
    """活动参与响应"""
    id: int
    activity_id: int
    user_id: int
    reward_type: Optional[str]
    reward_amount: Optional[int]
    reward_data: Optional[Dict[str, Any]]
    participated_at: datetime

    class Config:
        from_attributes = True


# ============ 优惠券相关 ============

class CouponCreate(BaseModel):
    """创建优惠券"""
    code: str = Field(..., description="优惠券码")
    name: str = Field(..., description="优惠券名称")
    coupon_type: str = Field(..., description="优惠券类型")
    discount_type: str = Field(..., description="折扣类型")
    discount_value: Decimal = Field(..., description="折扣值")
    min_amount: Optional[Decimal] = Field(None, description="最低消费金额")
    max_discount: Optional[Decimal] = Field(None, description="最大优惠金额")
    total_quantity: Optional[int] = Field(None, description="总发行量")
    valid_from: datetime = Field(..., description="有效期开始")
    valid_until: datetime = Field(..., description="有效期结束")
    description: Optional[str] = Field(None, description="使用说明")
    activity_id: Optional[int] = Field(None, description="关联活动ID")


class CouponUpdate(BaseModel):
    """更新优惠券"""
    name: Optional[str] = None
    discount_value: Optional[Decimal] = None
    min_amount: Optional[Decimal] = None
    max_discount: Optional[Decimal] = None
    total_quantity: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    """优惠券响应"""
    id: int
    code: str
    name: str
    coupon_type: str
    discount_type: str
    discount_value: Decimal
    min_amount: Optional[Decimal]
    max_discount: Optional[Decimal]
    total_quantity: Optional[int]
    used_quantity: int
    valid_from: datetime
    valid_until: datetime
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CouponReceive(BaseModel):
    """领取优惠券"""
    coupon_code: str = Field(..., description="优惠券码")


class CouponUse(BaseModel):
    """使用优惠券"""
    coupon_code: str = Field(..., description="优惠券码")
    order_type: str = Field(..., description="订单类型: recharge-充值, membership-会员")
    amount: Decimal = Field(..., description="订单金额")


class UserCouponResponse(BaseModel):
    """用户优惠券响应"""
    id: int
    coupon_id: int
    status: str
    used_at: Optional[datetime]
    received_at: datetime
    coupon: CouponResponse

    class Config:
        from_attributes = True


class CouponCalculateResponse(BaseModel):
    """优惠券计算响应"""
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    coupon_info: Dict[str, Any]


# ============ 推广返利相关 ============

class ReferralCodeGenerate(BaseModel):
    """生成推荐码"""
    pass


class ReferralCodeResponse(BaseModel):
    """推荐码响应"""
    referral_code: str
    referral_url: str


class ReferralRecordResponse(BaseModel):
    """推广记录响应"""
    id: int
    referrer_id: int
    referee_id: int
    referral_code: Optional[str]
    reward_type: Optional[str]
    reward_amount: Optional[Decimal]
    reward_credits: Optional[int]
    status: str
    trigger_event: Optional[str]
    trigger_amount: Optional[Decimal]
    settled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralStatisticsResponse(BaseModel):
    """推广统计响应"""
    total_referrals: int
    pending_referrals: int
    settled_referrals: int
    total_reward_amount: Decimal
    total_reward_credits: int
    referral_list: List[ReferralRecordResponse]


# ============ 统计相关 ============

class StatisticsQuery(BaseModel):
    """统计查询"""
    stat_type: str = Field(..., description="统计类型: daily-日, weekly-周, monthly-月")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")


class OperationStatisticsResponse(BaseModel):
    """运营统计响应"""
    id: int
    stat_date: datetime
    stat_type: str
    new_users: int
    active_users: int
    paying_users: int
    recharge_amount: Decimal
    recharge_count: int
    membership_amount: Decimal
    membership_count: int
    credits_consumed: int
    credits_recharged: int
    credits_rewarded: int
    total_creations: int
    writing_count: int
    image_count: int
    video_count: int
    ppt_count: int
    referral_count: int
    referral_reward: Decimal
    activity_participants: int
    activity_cost: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStatisticsResponse(BaseModel):
    """仪表盘统计响应"""
    # 今日数据
    today_new_users: int
    today_active_users: int
    today_recharge_amount: Decimal
    today_creations: int
    
    # 累计数据
    total_users: int
    total_members: int
    total_recharge_amount: Decimal
    total_creations: int
    
    # 趋势数据
    user_trend: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    creation_trend: List[Dict[str, Any]]
    
    # 排行榜
    top_creators: List[Dict[str, Any]]
    top_referrers: List[Dict[str, Any]]
