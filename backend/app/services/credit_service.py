"""
积分和会员服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from decimal import Decimal
import uuid

from app.models.user import User
from app.models.credit import (
    CreditTransaction, TransactionType,
    RechargeOrder, MembershipOrder, PaymentStatus,
    CreditPrice, MembershipPrice, MembershipType
)
from app.schemas.credit import (
    CreditTransactionResponse,
    RechargeOrderCreate, RechargeOrderResponse,
    MembershipOrderCreate, MembershipOrderResponse,
    CreditStatisticsResponse, MembershipStatisticsResponse
)
from app.core.exceptions import BusinessException


class CreditService:
    """积分服务"""
    
    @staticmethod
    def get_user_balance(db: Session, user_id: int) -> dict:
        """
        获取用户积分余额和会员状态
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户余额信息
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        # 检查会员是否过期
        is_member = False
        if user.is_member and user.member_expired_at:
            if user.member_expired_at > datetime.now():
                is_member = True
            else:
                # 会员已过期，更新状态
                user.is_member = 0
                db.commit()
        
        return {
            "credits": user.credits,
            "is_member": is_member,
            "member_expired_at": user.member_expired_at if is_member else None
        }
    
    @staticmethod
    def check_and_consume_credits(
        db: Session,
        user_id: int,
        amount: int,
        description: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None
    ) -> bool:
        """
        检查并消费积分（会员不扣积分）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 消费积分数
            description: 消费描述
            related_id: 关联ID
            related_type: 关联类型
            
        Returns:
            是否成功
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        # 检查是否是会员
        is_member = False
        if user.is_member and user.member_expired_at:
            if user.member_expired_at > datetime.now():
                is_member = True
            else:
                # 会员已过期
                user.is_member = 0
                db.commit()
        
        # 会员不扣积分
        if is_member:
            return True
        
        # 非会员检查积分余额
        if user.credits < amount:
            raise BusinessException(f"积分不足，当前余额: {user.credits}，需要: {amount}")
        
        # 扣减积分
        balance_before = user.credits
        user.credits -= amount
        balance_after = user.credits
        
        # 记录交易
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=TransactionType.CONSUME,
            amount=-amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            related_id=related_id,
            related_type=related_type
        )
        db.add(transaction)
        db.commit()
        
        return True
    
    @staticmethod
    def add_credits(
        db: Session,
        user_id: int,
        amount: int,
        transaction_type: TransactionType,
        description: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None
    ) -> CreditTransaction:
        """
        增加积分
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 积分数
            transaction_type: 交易类型
            description: 描述
            related_id: 关联ID
            related_type: 关联类型
            
        Returns:
            交易记录
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        balance_before = user.credits
        user.credits += amount
        balance_after = user.credits
        
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            related_id=related_id,
            related_type=related_type
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def get_transactions(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[CreditTransaction], int]:
        """
        获取积分交易记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            交易记录列表和总数
        """
        query = db.query(CreditTransaction).filter(
            CreditTransaction.user_id == user_id
        )
        
        total = query.count()
        transactions = query.order_by(
            CreditTransaction.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return transactions, total
    
    @staticmethod
    def get_credit_statistics(db: Session, user_id: int) -> CreditStatisticsResponse:
        """
        获取积分统计
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            积分统计
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        # 统计各类型积分
        stats = db.query(
            CreditTransaction.transaction_type,
            func.sum(CreditTransaction.amount).label('total')
        ).filter(
            CreditTransaction.user_id == user_id
        ).group_by(CreditTransaction.transaction_type).all()
        
        total_recharge = 0
        total_consume = 0
        total_reward = 0
        
        for stat in stats:
            if stat.transaction_type == TransactionType.RECHARGE:
                total_recharge = abs(stat.total or 0)
            elif stat.transaction_type == TransactionType.CONSUME:
                total_consume = abs(stat.total or 0)
            elif stat.transaction_type == TransactionType.REWARD:
                total_reward = abs(stat.total or 0)
        
        # 统计充值金额和次数
        recharge_stats = db.query(
            func.sum(RechargeOrder.amount).label('total_amount'),
            func.count(RechargeOrder.id).label('count')
        ).filter(
            and_(
                RechargeOrder.user_id == user_id,
                RechargeOrder.payment_status == PaymentStatus.PAID
            )
        ).first()
        
        return CreditStatisticsResponse(
            total_recharge=total_recharge,
            total_consume=total_consume,
            total_reward=total_reward,
            current_balance=user.credits,
            recharge_amount=recharge_stats.total_amount or Decimal(0),
            recharge_count=recharge_stats.count or 0
        )


class RechargeService:
    """充值服务"""
    
    @staticmethod
    def create_recharge_order(
        db: Session,
        user_id: int,
        order_data: RechargeOrderCreate
    ) -> RechargeOrder:
        """
        创建充值订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            order_data: 订单数据
            
        Returns:
            充值订单
        """
        # 获取价格配置
        price = db.query(CreditPrice).filter(
            CreditPrice.id == order_data.price_id,
            CreditPrice.is_active == True
        ).first()
        
        if not price:
            raise BusinessException("价格套餐不存在或已下架")
        
        # 生成订单号
        order_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        
        # 创建订单
        order = RechargeOrder(
            order_no=order_no,
            user_id=user_id,
            amount=price.amount,
            credits=price.credits,
            bonus_credits=price.bonus_credits,
            payment_method=order_data.payment_method,
            payment_status=PaymentStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def process_payment_callback(
        db: Session,
        order_no: str,
        transaction_id: str,
        status: str
    ) -> bool:
        """
        处理支付回调
        
        Args:
            db: 数据库会话
            order_no: 订单号
            transaction_id: 第三方交易ID
            status: 支付状态
            
        Returns:
            是否成功
        """
        order = db.query(RechargeOrder).filter(
            RechargeOrder.order_no == order_no
        ).first()
        
        if not order:
            raise BusinessException("订单不存在")
        
        if order.payment_status == PaymentStatus.PAID:
            return True  # 已支付，避免重复处理
        
        if status == "paid":
            # 更新订单状态
            order.payment_status = PaymentStatus.PAID
            order.paid_at = datetime.now()
            order.transaction_id = transaction_id
            
            # 增加用户积分
            total_credits = order.credits + order.bonus_credits
            CreditService.add_credits(
                db=db,
                user_id=order.user_id,
                amount=total_credits,
                transaction_type=TransactionType.RECHARGE,
                description=f"充值 {order.credits} 积分（赠送 {order.bonus_credits} 积分）",
                related_id=order.id,
                related_type="recharge_order"
            )
            
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[RechargeOrder], int]:
        """
        获取用户充值订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            订单列表和总数
        """
        query = db.query(RechargeOrder).filter(
            RechargeOrder.user_id == user_id
        )
        
        total = query.count()
        orders = query.order_by(
            RechargeOrder.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return orders, total


class MembershipService:
    """会员服务"""
    
    @staticmethod
    def create_membership_order(
        db: Session,
        user_id: int,
        order_data: MembershipOrderCreate
    ) -> MembershipOrder:
        """
        创建会员订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            order_data: 订单数据
            
        Returns:
            会员订单
        """
        # 获取价格配置
        price = db.query(MembershipPrice).filter(
            MembershipPrice.id == order_data.price_id,
            MembershipPrice.is_active == True
        ).first()
        
        if not price:
            raise BusinessException("会员套餐不存在或已下架")
        
        # 生成订单号
        order_no = f"M{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        
        # 创建订单
        order = MembershipOrder(
            order_no=order_no,
            user_id=user_id,
            membership_type=price.membership_type,
            amount=price.amount,
            original_amount=price.original_amount,
            discount_amount=(price.original_amount or price.amount) - price.amount,
            payment_method=order_data.payment_method,
            payment_status=PaymentStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def process_payment_callback(
        db: Session,
        order_no: str,
        transaction_id: str,
        status: str
    ) -> bool:
        """
        处理支付回调
        
        Args:
            db: 数据库会话
            order_no: 订单号
            transaction_id: 第三方交易ID
            status: 支付状态
            
        Returns:
            是否成功
        """
        order = db.query(MembershipOrder).filter(
            MembershipOrder.order_no == order_no
        ).first()
        
        if not order:
            raise BusinessException("订单不存在")
        
        if order.payment_status == PaymentStatus.PAID:
            return True  # 已支付，避免重复处理
        
        if status == "paid":
            # 获取价格配置以获取有效期
            price = db.query(MembershipPrice).filter(
                MembershipPrice.membership_type == order.membership_type,
                MembershipPrice.is_active == True
            ).first()
            
            if not price:
                raise BusinessException("会员套餐配置不存在")
            
            # 更新订单状态
            order.payment_status = PaymentStatus.PAID
            order.paid_at = datetime.now()
            order.transaction_id = transaction_id
            
            # 更新用户会员状态
            user = db.query(User).filter(User.id == order.user_id).first()
            if not user:
                raise BusinessException("用户不存在")
            
            # 计算会员到期时间
            now = datetime.now()
            if user.is_member and user.member_expired_at and user.member_expired_at > now:
                # 如果当前是会员且未过期，在原有基础上延长
                start_time = user.member_expired_at
            else:
                # 否则从现在开始计算
                start_time = now
            
            # 根据会员类型计算到期时间
            if price.membership_type == MembershipType.MONTHLY:
                expired_at = start_time + timedelta(days=price.duration_days)
            elif price.membership_type == MembershipType.QUARTERLY:
                expired_at = start_time + timedelta(days=price.duration_days)
            elif price.membership_type == MembershipType.YEARLY:
                expired_at = start_time + timedelta(days=price.duration_days)
            else:
                expired_at = start_time + timedelta(days=price.duration_days)
            
            user.is_member = 1
            user.member_expired_at = expired_at
            order.expired_at = expired_at
            
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[MembershipOrder], int]:
        """
        获取用户会员订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            订单列表和总数
        """
        query = db.query(MembershipOrder).filter(
            MembershipOrder.user_id == user_id
        )
        
        total = query.count()
        orders = query.order_by(
            MembershipOrder.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def get_membership_statistics(
        db: Session,
        user_id: int
    ) -> MembershipStatisticsResponse:
        """
        获取会员统计
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            会员统计
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException("用户不存在")
        
        # 检查会员状态
        is_member = False
        if user.is_member and user.member_expired_at:
            if user.member_expired_at > datetime.now():
                is_member = True
            else:
                user.is_member = 0
                db.commit()
        
        # 统计购买次数和金额
        purchase_stats = db.query(
            func.sum(MembershipOrder.amount).label('total_amount'),
            func.count(MembershipOrder.id).label('count')
        ).filter(
            and_(
                MembershipOrder.user_id == user_id,
                MembershipOrder.payment_status == PaymentStatus.PAID
            )
        ).first()
        
        # 获取最近一次购买记录
        last_order = db.query(MembershipOrder).filter(
            and_(
                MembershipOrder.user_id == user_id,
                MembershipOrder.payment_status == PaymentStatus.PAID
            )
        ).order_by(MembershipOrder.paid_at.desc()).first()
        
        return MembershipStatisticsResponse(
            is_member=is_member,
            member_expired_at=user.member_expired_at if is_member else None,
            total_purchase_amount=purchase_stats.total_amount or Decimal(0),
            total_purchase_count=purchase_stats.count or 0,
            last_purchase_at=last_order.paid_at if last_order else None,
            last_membership_type=last_order.membership_type if last_order else None
        )


class PriceService:
    """价格配置服务"""
    
    @staticmethod
    def get_credit_prices(db: Session) -> List[CreditPrice]:
        """
        获取积分价格列表
        
        Args:
            db: 数据库会话
            
        Returns:
            价格列表
        """
        return db.query(CreditPrice).filter(
            CreditPrice.is_active == True
        ).order_by(CreditPrice.sort_order).all()
    
    @staticmethod
    def get_membership_prices(db: Session) -> List[MembershipPrice]:
        """
        获取会员价格列表
        
        Args:
            db: 数据库会话
            
        Returns:
            价格列表
        """
        return db.query(MembershipPrice).filter(
            MembershipPrice.is_active == True
        ).order_by(MembershipPrice.sort_order).all()
    
    @staticmethod
    def create_credit_price(
        db: Session,
        price_data: dict
    ) -> CreditPrice:
        """
        创建积分价格配置
        
        Args:
            db: 数据库会话
            price_data: 价格数据
            
        Returns:
            价格配置
        """
        price = CreditPrice(**price_data)
        db.add(price)
        db.commit()
        db.refresh(price)
        return price
    
    @staticmethod
    def create_membership_price(
        db: Session,
        price_data: dict
    ) -> MembershipPrice:
        """
        创建会员价格配置
        
        Args:
            db: 数据库会话
            price_data: 价格数据
            
        Returns:
            价格配置
        """
        price = MembershipPrice(**price_data)
        db.add(price)
        db.commit()
        db.refresh(price)
        return price
    
    @staticmethod
    def update_credit_price(
        db: Session,
        price_id: int,
        price_data: dict
    ) -> CreditPrice:
        """
        更新积分价格配置
        
        Args:
            db: 数据库会话
            price_id: 价格ID
            price_data: 价格数据
            
        Returns:
            价格配置
        """
        price = db.query(CreditPrice).filter(CreditPrice.id == price_id).first()
        if not price:
            raise BusinessException("价格配置不存在")
        
        for key, value in price_data.items():
            setattr(price, key, value)
        
        db.commit()
        db.refresh(price)
        return price
    
    @staticmethod
    def update_membership_price(
        db: Session,
        price_id: int,
        price_data: dict
    ) -> MembershipPrice:
        """
        更新会员价格配置
        
        Args:
            db: 数据库会话
            price_id: 价格ID
            price_data: 价格数据
            
        Returns:
            价格配置
        """
        price = db.query(MembershipPrice).filter(MembershipPrice.id == price_id).first()
        if not price:
            raise BusinessException("价格配置不存在")
        
        for key, value in price_data.items():
            setattr(price, key, value)
        
        db.commit()
        db.refresh(price)
        return price
    
    @staticmethod
    def delete_credit_price(db: Session, price_id: int) -> bool:
        """
        删除积分价格配置（软删除）
        
        Args:
            db: 数据库会话
            price_id: 价格ID
            
        Returns:
            是否成功
        """
        price = db.query(CreditPrice).filter(CreditPrice.id == price_id).first()
        if not price:
            raise BusinessException("价格配置不存在")
        
        price.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def delete_membership_price(db: Session, price_id: int) -> bool:
        """
        删除会员价格配置（软删除）
        
        Args:
            db: 数据库会话
            price_id: 价格ID
            
        Returns:
            是否成功
        """
        price = db.query(MembershipPrice).filter(MembershipPrice.id == price_id).first()
        if not price:
            raise BusinessException("价格配置不存在")
        
        price.is_active = False
        db.commit()
        return True
