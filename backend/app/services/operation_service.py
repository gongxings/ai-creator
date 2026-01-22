"""
运营功能服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
import string

from app.models.operation import (
    Activity, ActivityParticipation, Coupon, UserCoupon, ReferralRecord, OperationStatistics,
    ActivityType, ActivityStatus, CouponType, CouponStatus, ReferralStatus
)
from app.models.user import User
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.operation import (
    ActivityCreate, ActivityUpdate, CouponCreate, CouponUpdate
)
from app.core.exceptions import BusinessException


class ActivityService:
    """活动服务"""
    
    @staticmethod
    def create_activity(db: Session, activity_data: ActivityCreate, creator_id: int) -> Activity:
        """创建活动"""
        activity = Activity(
            **activity_data.model_dump(),
            created_by=creator_id,
            status=ActivityStatus.DRAFT
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def update_activity(db: Session, activity_id: int, activity_data: ActivityUpdate) -> Activity:
        """更新活动"""
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise BusinessException("活动不存在")
        
        update_data = activity_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(activity, key, value)
        
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_activity(db: Session, activity_id: int) -> Optional[Activity]:
        """获取活动详情"""
        return db.query(Activity).filter(Activity.id == activity_id).first()
    
    @staticmethod
    def list_activities(
        db: Session,
        status: Optional[str] = None,
        activity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Activity], int]:
        """获取活动列表"""
        query = db.query(Activity)
        
        if status:
            query = query.filter(Activity.status == status)
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        total = query.count()
        activities = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()
        
        return activities, total
    
    @staticmethod
    def participate_activity(db: Session, activity_id: int, user_id: int) -> ActivityParticipation:
        """参与活动"""
        # 检查活动是否存在且有效
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise BusinessException("活动不存在")
        
        if activity.status != ActivityStatus.ACTIVE:
            raise BusinessException("活动未开始或已结束")
        
        now = datetime.now()
        if now < activity.start_time or now > activity.end_time:
            raise BusinessException("不在活动时间范围内")
        
        # 检查是否已参与
        existing = db.query(ActivityParticipation).filter(
            ActivityParticipation.activity_id == activity_id,
            ActivityParticipation.user_id == user_id
        ).first()
        if existing:
            raise BusinessException("已参与过该活动")
        
        # 检查参与人数限制
        if activity.max_participants:
            if activity.current_participants >= activity.max_participants:
                raise BusinessException("活动参与人数已满")
        
        # 根据活动类型发放奖励
        reward_type = None
        reward_amount = None
        reward_data = None
        
        if activity.activity_type == ActivityType.CREDIT_GIFT:
            # 积分赠送
            reward_type = "credits"
            reward_amount = activity.rules.get("credits", 0) if activity.rules else 0
            
            # 增加用户积分
            user = db.query(User).filter(User.id == user_id).first()
            user.credits += reward_amount
            
            # 记录积分交易
            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type=TransactionType.REWARD,
                amount=reward_amount,
                balance_before=user.credits - reward_amount,
                balance_after=user.credits,
                description=f"参与活动：{activity.title}",
                related_id=activity_id,
                related_type="activity"
            )
            db.add(transaction)
        
        # 创建参与记录
        participation = ActivityParticipation(
            activity_id=activity_id,
            user_id=user_id,
            reward_type=reward_type,
            reward_amount=reward_amount,
            reward_data=reward_data
        )
        db.add(participation)
        
        # 更新活动参与人数和成本
        activity.current_participants += 1
        if reward_amount:
            activity.cost += Decimal(str(reward_amount * 0.01))  # 假设1积分=0.01元
        
        db.commit()
        db.refresh(participation)
        
        return participation


class CouponService:
    """优惠券服务"""
    
    @staticmethod
    def create_coupon(db: Session, coupon_data: CouponCreate) -> Coupon:
        """创建优惠券"""
        # 检查优惠券码是否已存在
        existing = db.query(Coupon).filter(Coupon.code == coupon_data.code).first()
        if existing:
            raise BusinessException("优惠券码已存在")
        
        coupon = Coupon(**coupon_data.model_dump())
        db.add(coupon)
        db.commit()
        db.refresh(coupon)
        return coupon
    
    @staticmethod
    def update_coupon(db: Session, coupon_id: int, coupon_data: CouponUpdate) -> Coupon:
        """更新优惠券"""
        coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            raise BusinessException("优惠券不存在")
        
        update_data = coupon_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(coupon, key, value)
        
        db.commit()
        db.refresh(coupon)
        return coupon
    
    @staticmethod
    def get_coupon_by_code(db: Session, code: str) -> Optional[Coupon]:
        """根据优惠券码获取优惠券"""
        return db.query(Coupon).filter(Coupon.code == code).first()
    
    @staticmethod
    def list_coupons(
        db: Session,
        coupon_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Coupon], int]:
        """获取优惠券列表"""
        query = db.query(Coupon)
        
        if coupon_type:
            query = query.filter(Coupon.coupon_type == coupon_type)
        if is
