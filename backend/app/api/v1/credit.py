"""
积分和会员API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.common import Response, PaginatedResponse
from app.schemas.credit import (
    CreditTransactionResponse,
    RechargeOrderCreate, RechargeOrderResponse,
    MembershipOrderCreate, MembershipOrderResponse,
    CreditPriceResponse, MembershipPriceResponse,
    CreditPriceCreate, MembershipPriceCreate,
    PaymentCallbackRequest,
    CreditStatisticsResponse, MembershipStatisticsResponse
)
from app.services.credit_service import (
    CreditService, RechargeService, MembershipService, PriceService
)

router = APIRouter(prefix="/credit", tags=["积分和会员"])


# ==================== 积分相关 ====================

@router.get("/balance", response_model=Response)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户积分余额和会员状态"""
    balance = CreditService.get_user_balance(db, current_user.id)
    return Response(data=balance)


@router.get("/transactions", response_model=Response[PaginatedResponse[CreditTransactionResponse]])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取积分交易记录"""
    transactions, total = CreditService.get_transactions(
        db, current_user.id, skip, limit
    )
    return Response(data=PaginatedResponse(
        items=[CreditTransactionResponse.from_orm(t) for t in transactions],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    ))


@router.get("/statistics", response_model=Response[CreditStatisticsResponse])
async def get_credit_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取积分统计"""
    statistics = CreditService.get_credit_statistics(db, current_user.id)
    return Response(data=statistics)


# ==================== 充值相关 ====================

@router.post("/recharge/order", response_model=Response[RechargeOrderResponse])
async def create_recharge_order(
    order_data: RechargeOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建充值订单"""
    order = RechargeService.create_recharge_order(db, current_user.id, order_data)
    return Response(data=RechargeOrderResponse.from_orm(order))


@router.get("/recharge/orders", response_model=Response[PaginatedResponse[RechargeOrderResponse]])
async def get_recharge_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取充值订单列表"""
    orders, total = RechargeService.get_user_orders(
        db, current_user.id, skip, limit
    )
    return Response(data=PaginatedResponse(
        items=[RechargeOrderResponse.from_orm(o) for o in orders],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    ))


@router.post("/recharge/callback", response_model=Response)
async def recharge_payment_callback(
    callback_data: PaymentCallbackRequest,
    db: Session = Depends(get_db)
):
    """充值支付回调（由支付平台调用）"""
    success = RechargeService.process_payment_callback(
        db,
        callback_data.order_no,
        callback_data.transaction_id,
        callback_data.status
    )
    return Response(data={"success": success})


# ==================== 会员相关 ====================

@router.post("/membership/order", response_model=Response[MembershipOrderResponse])
async def create_membership_order(
    order_data: MembershipOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建会员订单"""
    order = MembershipService.create_membership_order(db, current_user.id, order_data)
    return Response(data=MembershipOrderResponse.from_orm(order))


@router.get("/membership/orders", response_model=Response[PaginatedResponse[MembershipOrderResponse]])
async def get_membership_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会员订单列表"""
    orders, total = MembershipService.get_user_orders(
        db, current_user.id, skip, limit
    )
    return Response(data=PaginatedResponse(
        items=[MembershipOrderResponse.from_orm(o) for o in orders],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    ))


@router.post("/membership/callback", response_model=Response)
async def membership_payment_callback(
    callback_data: PaymentCallbackRequest,
    db: Session = Depends(get_db)
):
    """会员支付回调（由支付平台调用）"""
    success = MembershipService.process_payment_callback(
        db,
        callback_data.order_no,
        callback_data.transaction_id,
        callback_data.status
    )
    return Response(data={"success": success})


@router.get("/membership/statistics", response_model=Response[MembershipStatisticsResponse])
async def get_membership_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会员统计"""
    statistics = MembershipService.get_membership_statistics(db, current_user.id)
    return Response(data=statistics)


# ==================== 价格配置相关 ====================

@router.get("/prices/credits", response_model=Response[List[CreditPriceResponse]])
async def get_credit_prices(db: Session = Depends(get_db)):
    """获取积分价格列表（公开接口）"""
    prices = PriceService.get_credit_prices(db)
    return Response(data=[CreditPriceResponse.from_orm(p) for p in prices])


@router.get("/prices/membership", response_model=Response[List[MembershipPriceResponse]])
async def get_membership_prices(db: Session = Depends(get_db)):
    """获取会员价格列表（公开接口）"""
    prices = PriceService.get_membership_prices(db)
    return Response(data=[MembershipPriceResponse.from_orm(p) for p in prices])


# ==================== 管理员接口 ====================

@router.post("/admin/prices/credits", response_model=Response[CreditPriceResponse])
async def create_credit_price(
    price_data: CreditPriceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建积分价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    price = PriceService.create_credit_price(db, price_data.dict())
    return Response(data=CreditPriceResponse.from_orm(price))


@router.put("/admin/prices/credits/{price_id}", response_model=Response[CreditPriceResponse])
async def update_credit_price(
    price_id: int,
    price_data: CreditPriceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新积分价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    price = PriceService.update_credit_price(db, price_id, price_data.dict(exclude_unset=True))
    return Response(data=CreditPriceResponse.from_orm(price))


@router.delete("/admin/prices/credits/{price_id}", response_model=Response)
async def delete_credit_price(
    price_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除积分价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    success = PriceService.delete_credit_price(db, price_id)
    return Response(data={"success": success})


@router.post("/admin/prices/membership", response_model=Response[MembershipPriceResponse])
async def create_membership_price(
    price_data: MembershipPriceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建会员价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    price = PriceService.create_membership_price(db, price_data.dict())
    return Response(data=MembershipPriceResponse.from_orm(price))


@router.put("/admin/prices/membership/{price_id}", response_model=Response[MembershipPriceResponse])
async def update_membership_price(
    price_id: int,
    price_data: MembershipPriceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新会员价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    price = PriceService.update_membership_price(db, price_id, price_data.dict(exclude_unset=True))
    return Response(data=MembershipPriceResponse.from_orm(price))


@router.delete("/admin/prices/membership/{price_id}", response_model=Response)
async def delete_membership_price(
    price_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除会员价格配置（管理员）"""
    # TODO: 添加管理员权限检查
    success = PriceService.delete_membership_price(db, price_id)
    return Response(data={"success": success})
