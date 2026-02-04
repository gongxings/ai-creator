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
        if is_active is not None:
            query = query.filter(Coupon.is_active == is_active)
        
        total = query.count()
        coupons = query.order_by(Coupon.created_at.desc()).offset(skip).limit(limit).all()
        
        return coupons, total
    
    @staticmethod
    def receive_coupon(db: Session, coupon_id: int, user_id: int) -> UserCoupon:
        """领取优惠券"""
        coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            raise BusinessException("优惠券不存在")
        
        if not coupon.is_active:
            raise BusinessException("优惠券已失效")
        
        # 检查是否已领取
        existing = db.query(UserCoupon).filter(
            UserCoupon.coupon_id == coupon_id,
            UserCoupon.user_id == user_id
        ).first()
        if existing:
            raise BusinessException("已领取过该优惠券")
        
        # 检查领取数量限制
        if coupon.total_quantity:
            if coupon.received_quantity >= coupon.total_quantity:
                raise BusinessException("优惠券已被领完")
        
        # 创建用户优惠券
        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon_id,
            status=CouponStatus.UNUSED,
            expire_time=coupon.expire_time
        )
        db.add(user_coupon)
        
        # 更新优惠券领取数量
        coupon.received_quantity += 1
        
        db.commit()
        db.refresh(user_coupon)
        
        return user_coupon
    
    @staticmethod
    def use_coupon(db: Session, user_coupon_id: int, order_amount: Decimal) -> Dict[str, Any]:
        """使用优惠券"""
        user_coupon = db.query(UserCoupon).filter(UserCoupon.id == user_coupon_id).first()
        if not user_coupon:
            raise BusinessException("优惠券不存在")
        
        if user_coupon.status != CouponStatus.UNUSED:
            raise BusinessException("优惠券已使用或已过期")
        
        if user_coupon.expire_time and datetime.now() > user_coupon.expire_time:
            user_coupon.status = CouponStatus.EXPIRED
            db.commit()
            raise BusinessException("优惠券已过期")
        
        coupon = user_coupon.coupon
        
        # 检查使用条件
        if coupon.min_amount and order_amount < coupon.min_amount:
            raise BusinessException(f"订单金额需满{coupon.min_amount}元才能使用")
        
        # 计算折扣金额
        discount_amount = Decimal('0')
        if coupon.coupon_type == CouponType.DISCOUNT:
            discount_amount = order_amount * (Decimal('1') - coupon.discount_rate / Decimal('100'))
        elif coupon.coupon_type == CouponType.CASH:
            discount_amount = min(coupon.discount_amount, order_amount)
        
        # 更新优惠券状态
        user_coupon.status = CouponStatus.USED
        user_coupon.used_time = datetime.now()
        
        db.commit()
        
        return {
            "discount_amount": float(discount_amount),
            "final_amount": float(order_amount - discount_amount)
        }


class ReferralService:
    """推荐返利服务"""
    
    @staticmethod
    def generate_referral_code(db: Session, user_id: int) -> str:
        """生成推荐码"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        if user.referral_code:
            return user.referral_code
        
        # 生成唯一推荐码
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            existing = db.query(User).filter(User.referral_code == code).first()
            if not existing:
                break
        
        user.referral_code = code
        db.commit()
        
        return code
    
    @staticmethod
    def process_referral(db: Session, referee_id: int, referral_code: str) -> ReferralRecord:
        """处理推荐关系"""
        # 查找推荐人
        referrer = db.query(User).filter(User.referral_code == referral_code).first()
        if not referrer:
            raise BusinessException("推荐码无效")
        
        if referrer.id == referee_id:
            raise BusinessException("不能使用自己的推荐码")
        
        # 检查是否已被推荐
        existing = db.query(ReferralRecord).filter(ReferralRecord.referee_id == referee_id).first()
        if existing:
            raise BusinessException("已使用过推荐码")
        
        # 创建推荐记录
        record = ReferralRecord(
            referrer_id=referrer.id,
            referee_id=referee_id,
            status=ReferralStatus.PENDING
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
    
    @staticmethod
    def complete_referral(db: Session, record_id: int, reward_amount: Decimal) -> ReferralRecord:
        """完成推荐返利"""
        record = db.query(ReferralRecord).filter(ReferralRecord.id == record_id).first()
        if not record:
            raise BusinessException("推荐记录不存在")
        
        if record.status != ReferralStatus.PENDING:
            raise BusinessException("推荐记录状态异常")
        
        # 发放返利
        referrer = db.query(User).filter(User.id == record.referrer_id).first()
        referrer.credits += int(reward_amount * 100)  # 转换为积分
        
        # 记录积分交易
        transaction = CreditTransaction(
            user_id=record.referrer_id,
            transaction_type=TransactionType.REFERRAL,
            amount=int(reward_amount * 100),
            balance_before=referrer.credits - int(reward_amount * 100),
            balance_after=referrer.credits,
            description=f"推荐返利",
            related_id=record_id,
            related_type="referral"
        )
        db.add(transaction)
        
        # 更新推荐记录
        record.status = ReferralStatus.COMPLETED
        record.reward_amount = reward_amount
        record.completed_at = datetime.now()
        
        db.commit()
        db.refresh(record)
        
        return record


class OperationService:
    """运营服务统一入口"""
    
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService()
        self.coupon_service = CouponService()
        self.referral_service = ReferralService()
    
    # Activity methods
    async def create_activity(self, activity_data: ActivityCreate, creator_id: int) -> Activity:
        return self.activity_service.create_activity(self.db, activity_data, creator_id)
    
    async def update_activity(self, activity_id: int, activity_data: ActivityUpdate) -> Activity:
        return self.activity_service.update_activity(self.db, activity_id, activity_data)
    
    async def get_activity(self, activity_id: int) -> Optional[Activity]:
        return self.activity_service.get_activity(self.db, activity_id)
    
    async def get_activities(self, status: Optional[str] = None, activity_type: Optional[str] = None, 
                            skip: int = 0, limit: int = 20) -> tuple[List[Activity], int]:
        return self.activity_service.list_activities(self.db, status, activity_type, skip, limit)
    
    async def delete_activity(self, activity_id: int) -> bool:
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            self.db.delete(activity)
            self.db.commit()
            return True
        return False
    
    async def participate_activity(self, activity_id: int, user_id: int, participate: Any) -> ActivityParticipation:
        return self.activity_service.participate_activity(self.db, activity_id, user_id)
    
    async def get_activity_participations(self, activity_id: int, skip: int = 0, limit: int = 20) -> tuple[List[ActivityParticipation], int]:
        query = self.db.query(ActivityParticipation).filter(ActivityParticipation.activity_id == activity_id)
        total = query.count()
        participations = query.offset(skip).limit(limit).all()
        return participations, total
    
    # Coupon methods
    async def create_coupon(self, coupon_data: CouponCreate) -> Coupon:
        return self.coupon_service.create_coupon(self.db, coupon_data)
    
    async def update_coupon(self, coupon_id: int, coupon_data: CouponUpdate) -> Coupon:
        return self.coupon_service.update_coupon(self.db, coupon_id, coupon_data)
    
    async def get_coupon(self, coupon_id: int) -> Optional[Coupon]:
        return self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    async def get_coupons(self, coupon_type: Optional[str] = None, is_active: Optional[bool] = None,
                         skip: int = 0, limit: int = 20) -> tuple[List[Coupon], int]:
        return self.coupon_service.list_coupons(self.db, coupon_type, is_active, skip, limit)
    
    async def delete_coupon(self, coupon_id: int) -> bool:
        coupon = self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if coupon:
            self.db.delete(coupon)
            self.db.commit()
            return True
        return False
    
    async def receive_coupon(self, coupon_id: int, user_id: int, receive: Any) -> UserCoupon:
        return self.coupon_service.receive_coupon(self.db, coupon_id, user_id)
    
    async def get_user_coupons(self, user_id: int, status: Optional[str] = None,
                              skip: int = 0, limit: int = 20) -> tuple[List[UserCoupon], int]:
        query = self.db.query(UserCoupon).filter(UserCoupon.user_id == user_id)
        if status:
            query = query.filter(UserCoupon.status == status)
        total = query.count()
        coupons = query.offset(skip).limit(limit).all()
        return coupons, total
    
    async def calculate_coupon_discount(self, user_coupon_id: int, original_amount: Decimal) -> Dict[str, Any]:
        return self.coupon_service.use_coupon(self.db, user_coupon_id, original_amount)
    
    # Referral methods
    async def generate_referral_code(self, user_id: int, generate: Any) -> Dict[str, str]:
        code = self.referral_service.generate_referral_code(self.db, user_id)
        return {"referral_code": code, "referral_url": f"https://your-domain.com/register?ref={code}"}
    
    async def get_referral_records(self, referrer_id: int, status: Optional[str] = None,
                                  skip: int = 0, limit: int = 20) -> tuple[List[ReferralRecord], int]:
        query = self.db.query(ReferralRecord).filter(ReferralRecord.referrer_id == referrer_id)
        if status:
            query = query.filter(ReferralRecord.status == status)
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total
    
    async def get_referral_statistics(self, user_id: int) -> Dict[str, Any]:
        total_referrals = self.db.query(ReferralRecord).filter(ReferralRecord.referrer_id == user_id).count()
        completed_referrals = self.db.query(ReferralRecord).filter(
            ReferralRecord.referrer_id == user_id,
            ReferralRecord.status == ReferralStatus.COMPLETED
        ).count()
        total_rewards = self.db.query(func.sum(ReferralRecord.reward_amount)).filter(
            ReferralRecord.referrer_id == user_id,
            ReferralRecord.status == ReferralStatus.COMPLETED
        ).scalar() or Decimal('0')
        
        return {
            "total_referrals": total_referrals,
            "completed_referrals": completed_referrals,
            "pending_referrals": total_referrals - completed_referrals,
            "total_rewards": float(total_rewards)
        }
    
    # Statistics methods
    async def get_statistics(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取运营统计数据"""
        from app.models.creation import Creation
        from app.models.credit import RechargeOrder, MembershipOrder
        
        # 设置默认时间范围（最近30天）
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 用户统计
        new_users = self.db.query(User).filter(
            User.created_at >= start_date,
            User.created_at <= end_date
        ).count()
        
        active_users = self.db.query(func.count(func.distinct(Creation.user_id))).filter(
            Creation.created_at >= start_date,
            Creation.created_at <= end_date
        ).scalar() or 0
        
        # 充值统计
        recharge_stats = self.db.query(
            func.count(RechargeOrder.id).label('count'),
            func.sum(RechargeOrder.amount).label('amount')
        ).filter(
            RechargeOrder.created_at >= start_date,
            RechargeOrder.created_at <= end_date,
            RechargeOrder.status == 'paid'
        ).first()
        
        # 会员统计
        membership_stats = self.db.query(
            func.count(MembershipOrder.id).label('count'),
            func.sum(MembershipOrder.amount).label('amount')
        ).filter(
            MembershipOrder.created_at >= start_date,
            MembershipOrder.created_at <= end_date,
            MembershipOrder.status == 'paid'
        ).first()
        
        # 积分消耗统计
        credit_consume = self.db.query(func.sum(CreditTransaction.amount)).filter(
            CreditTransaction.created_at >= start_date,
            CreditTransaction.created_at <= end_date,
            CreditTransaction.transaction_type == TransactionType.CONSUME
        ).scalar() or 0
        
        # 创作统计
        generation_count = self.db.query(Creation).filter(
            Creation.created_at >= start_date,
            Creation.created_at <= end_date
        ).count()
        
        # 活动统计
        activity_participants = self.db.query(ActivityParticipation).filter(
            ActivityParticipation.participated_at >= start_date,
            ActivityParticipation.participated_at <= end_date
        ).count()
        
        # 优惠券统计
        coupon_used = self.db.query(UserCoupon).filter(
            UserCoupon.used_time >= start_date,
            UserCoupon.used_time <= end_date,
            UserCoupon.status == CouponStatus.USED
        ).count()
        
        # 推荐统计
        referral_count = self.db.query(ReferralRecord).filter(
            ReferralRecord.created_at >= start_date,
            ReferralRecord.created_at <= end_date
        ).count()
        
        referral_rewards = self.db.query(func.sum(ReferralRecord.reward_amount)).filter(
            ReferralRecord.completed_at >= start_date,
            ReferralRecord.completed_at <= end_date,
            ReferralRecord.status == ReferralStatus.COMPLETED
        ).scalar() or Decimal('0')
        
        return {
            "new_users": new_users,
            "active_users": active_users,
            "recharge_amount": float(recharge_stats.amount or 0),
            "recharge_count": recharge_stats.count or 0,
            "membership_amount": float(membership_stats.amount or 0),
            "membership_count": membership_stats.count or 0,
            "credit_consume": abs(credit_consume),
            "generation_count": generation_count,
            "activity_participants": activity_participants,
            "coupon_used": coupon_used,
            "referral_count": referral_count,
            "referral_rewards": float(referral_rewards)
        }
    
    async def get_user_statistics(self, user_id: int, start_date: Optional[datetime] = None, 
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取用户运营统计数据"""
        from app.models.creation import Creation
        
        # 设置默认时间范围（最近30天）
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 创作统计
        total_creations = self.db.query(Creation).filter(
            Creation.user_id == user_id,
            Creation.created_at >= start_date,
            Creation.created_at <= end_date
        ).count()
        
        # 活动参与统计
        activities_participated = self.db.query(ActivityParticipation).filter(
            ActivityParticipation.user_id == user_id,
            ActivityParticipation.participated_at >= start_date,
            ActivityParticipation.participated_at <= end_date
        ).count()
        
        activity_rewards = self.db.query(func.sum(ActivityParticipation.reward_amount)).filter(
            ActivityParticipation.user_id == user_id,
            ActivityParticipation.participated_at >= start_date,
            ActivityParticipation.participated_at <= end_date
        ).scalar() or 0
        
        # 优惠券统计
        coupons_received = self.db.query(UserCoupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.received_at >= start_date,
            UserCoupon.received_at <= end_date
        ).count()
        
        coupons_used = self.db.query(UserCoupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.used_time >= start_date,
            UserCoupon.used_time <= end_date,
            UserCoupon.status == CouponStatus.USED
        ).count()
        
        # 推荐统计
        referrals_made = self.db.query(ReferralRecord).filter(
            ReferralRecord.referrer_id == user_id,
            ReferralRecord.created_at >= start_date,
            ReferralRecord.created_at <= end_date
        ).count()
        
        referral_rewards = self.db.query(func.sum(ReferralRecord.reward_amount)).filter(
            ReferralRecord.referrer_id == user_id,
            ReferralRecord.completed_at >= start_date,
            ReferralRecord.completed_at <= end_date,
            ReferralRecord.status == ReferralStatus.COMPLETED
        ).scalar() or Decimal('0')
        
        return {
            "total_creations": total_creations,
            "activities_participated": activities_participated,
            "activity_rewards": float(activity_rewards),
            "coupons_received": coupons_received,
            "coupons_used": coupons_used,
            "referrals_made": referrals_made,
            "referral_rewards": float(referral_rewards)
        }
