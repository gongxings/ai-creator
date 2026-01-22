"""
积分和会员相关Schema
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ 积分交易相关 ============

class CreditTransactionBase(BaseModel):
    """积分交易基础Schema"""
    transaction_type: str
    amount: int
    description: Optional[str] = None


class CreditTransactionCreate(CreditTransactionBase):
    """创建积分交易"""
    pass


class CreditTransactionResponse(CreditTransactionBase):
    """积分交易响应"""
    id: int
    user_id: int
    balance_before: int
    balance_after: int
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditBalanceResponse(BaseModel):
    """积分余额响应"""
    credits: int
    is_member: bool
    member_expired_at: Optional[datetime] = None


# ============ 充值订单相关 ============

class RechargeOrderCreate(BaseModel):
    """创建充值订单"""
    price_id: int = Field(..., description="价格套餐ID")
    payment_method: str = Field(..., description="支付方式: alipay, wechat")


class RechargeOrderResponse(BaseModel):
    """充值订单响应"""
    id: int
    order_no: str
    amount: Decimal
    credits: int
    bonus_credits: int
    payment_status: str
    payment_method: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ 会员订单相关 ============

class MembershipOrderCreate(BaseModel):
    """创建会员订单"""
    price_id: int = Field(..., description="价格套餐ID")
    payment_method: str = Field(..., description="支付方式: alipay, wechat")


class MembershipOrderResponse(BaseModel):
    """会员订单响应"""
    id: int
    order_no: str
    membership_type: str
    amount: Decimal
    original_amount: Optional[Decimal] = None
    discount_amount: Decimal
    payment_status: str
    payment_method: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ 价格配置相关 ============

class CreditPriceResponse(BaseModel):
    """积分价格响应"""
    id: int
    name: str
    amount: Decimal
    credits: int
    bonus_credits: int
    description: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class MembershipPriceResponse(BaseModel):
    """会员价格响应"""
    id: int
    name: str
    membership_type: str
    amount: Decimal
    original_amount: Optional[Decimal] = None
    duration_days: int
    description: Optional[str] = None
    features: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class CreditPriceCreate(BaseModel):
    """创建积分价格"""
    name: str = Field(..., max_length=100)
    amount: Decimal = Field(..., gt=0)
    credits: int = Field(..., gt=0)
    bonus_credits: int = Field(default=0, ge=0)
    description: Optional[str] = Field(None, max_length=255)
    sort_order: int = Field(default=0)


class MembershipPriceCreate(BaseModel):
    """创建会员价格"""
    name: str = Field(..., max_length=100)
    membership_type: str = Field(..., description="monthly, quarterly, yearly")
    amount: Decimal = Field(..., gt=0)
    original_amount: Optional[Decimal] = Field(None, gt=0)
    duration_days: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=255)
    features: Optional[str] = None
    sort_order: int = Field(default=0)
    
    @validator('membership_type')
    def validate_membership_type(cls, v):
        if v not in ['monthly', 'quarterly', 'yearly']:
            raise ValueError('会员类型必须是 monthly, quarterly 或 yearly')
        return v


# ============ 支付相关 ============

class PaymentCallbackRequest(BaseModel):
    """支付回调请求"""
    order_no: str
    transaction_id: str
    payment_method: str
    amount: Decimal
    status: str


class PaymentStatusResponse(BaseModel):
    """支付状态响应"""
    order_no: str
    payment_status: str
    paid_at: Optional[datetime] = None


# ============ 消费记录相关 ============

class ConsumeCreditsRequest(BaseModel):
    """消费积分请求"""
    amount: int = Field(..., gt=0, description="消费积分数")
    description: str = Field(..., description="消费描述")
    related_id: Optional[int] = None
    related_type: Optional[str] = None


class CreditStatisticsResponse(BaseModel):
    """积分统计响应"""
    total_recharge: int = Field(description="总充值积分")
    total_consume: int = Field(description="总消费积分")
    total_reward: int = Field(description="总奖励积分")
    current_balance: int = Field(description="当前余额")
    recharge_amount: Decimal = Field(description="总充值金额")
    recharge_count: int = Field(description="充值次数")


class MembershipStatisticsResponse(BaseModel):
    """会员统计响应"""
    is_member: bool = Field(description="是否会员")
    member_expired_at: Optional[datetime] = Field(description="会员到期时间")
    total_orders: int = Field(description="总订单数")
    total_amount: Decimal = Field(description="总消费金额")
    days_remaining: Optional[int] = Field(description="剩余天数")
