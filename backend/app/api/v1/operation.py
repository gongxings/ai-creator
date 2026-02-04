"""
运营管理API路由
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.schemas.operation import (
    ActivityCreate, ActivityUpdate, ActivityResponse,
    ActivityParticipate, ActivityParticipationResponse,
    CouponCreate, CouponUpdate, CouponResponse,
    CouponReceive, CouponUse, UserCouponResponse, CouponCalculateResponse,
    ReferralCodeGenerate, ReferralCodeResponse,
    ReferralRecordResponse, ReferralStatisticsResponse,
    StatisticsQuery, OperationStatisticsResponse, DashboardStatisticsResponse
)
from app.schemas.common import success_response, PaginatedResponse
from app.services.operation_service import OperationService

router = APIRouter(prefix="/operation", tags=["运营管理"])


# ==================== 活动管理 ====================

@router.post("/activities")
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建运营活动（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.create_activity(activity)
    return success_response(data=result)


@router.get("/activities")
async def get_activities(
    status: Optional[str] = None,
    activity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取活动列表"""
    service = OperationService(db)
    activities, total = await service.get_activities(
        status=status,
        activity_type=activity_type,
        skip=skip,
        limit=limit
    )
    return success_response(data=PaginatedResponse(
        items=activities,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/activities/{activity_id}")
async def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取活动详情"""
    service = OperationService(db)
    activity = await service.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return success_response(data=activity)


@router.put("/activities/{activity_id}")
async def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新活动（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.update_activity(activity_id, activity)
    if not result:
        raise HTTPException(status_code=404, detail="活动不存在")
    return success_response(data=result)


@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除活动（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    success = await service.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="活动不存在")
    return success_response(data={"message": "删除成功"})


@router.post("/activities/{activity_id}/participate")
async def participate_activity(
    activity_id: int,
    participate: ActivityParticipate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """参与活动"""
    service = OperationService(db)
    result = await service.participate_activity(activity_id, current_user.id, participate)
    return success_response(data=result)


@router.get("/activities/{activity_id}/participations")
async def get_activity_participations(
    activity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取活动参与记录（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    participations, total = await service.get_activity_participations(
        activity_id=activity_id,
        skip=skip,
        limit=limit
    )
    return success_response(data=PaginatedResponse(
        items=participations,
        total=total,
        skip=skip,
        limit=limit
    ))


# ==================== 优惠券管理 ====================

@router.post("/coupons")
async def create_coupon(
    coupon: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建优惠券（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.create_coupon(coupon)
    return success_response(data=result)


@router.get("/coupons")
async def get_coupons(
    coupon_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取优惠券列表"""
    service = OperationService(db)
    coupons, total = await service.get_coupons(
        coupon_type=coupon_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return success_response(data=PaginatedResponse(
        items=coupons,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/coupons/{coupon_id}")
async def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取优惠券详情"""
    service = OperationService(db)
    coupon = await service.get_coupon(coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return success_response(data=coupon)


@router.put("/coupons/{coupon_id}")
async def update_coupon(
    coupon_id: int,
    coupon: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新优惠券（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.update_coupon(coupon_id, coupon)
    if not result:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return success_response(data=result)


@router.delete("/coupons/{coupon_id}")
async def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除优惠券（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    success = await service.delete_coupon(coupon_id)
    if not success:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return success_response(data={"message": "删除成功"})


@router.post("/coupons/{coupon_id}/receive")
async def receive_coupon(
    coupon_id: int,
    receive: CouponReceive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """领取优惠券"""
    service = OperationService(db)
    result = await service.receive_coupon(coupon_id, current_user.id, receive)
    return success_response(data=result)


@router.get("/user/coupons")
async def get_user_coupons(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户优惠券列表"""
    service = OperationService(db)
    coupons, total = await service.get_user_coupons(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    return success_response(data=PaginatedResponse(
        items=coupons,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.post("/coupons/use")
async def use_coupon(
    use: CouponUse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """使用优惠券"""
    service = OperationService(db)
    result = await service.use_coupon(current_user.id, use)
    return success_response(data=result)


@router.post("/coupons/calculate")
async def calculate_coupon_discount(
    calculate: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """计算优惠券折扣"""
    service = OperationService(db)
    result = await service.calculate_coupon_discount(
        user_id=current_user.id,
        coupon_code=calculate.get("coupon_code"),
        original_amount=calculate.get("original_amount")
    )
    return success_response(data=result)


# ==================== 推荐奖励 ====================

@router.post("/referral/generate")
async def generate_referral_code(
    generate: ReferralCodeGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成推荐码"""
    service = OperationService(db)
    result = await service.generate_referral_code(current_user.id, generate)
    return success_response(data=result)


@router.get("/referral/code")
async def get_referral_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的推荐码"""
    service = OperationService(db)
    code = await service.get_user_referral_code(current_user.id)
    if not code:
        raise HTTPException(status_code=404, detail="推荐码不存在")
    return success_response(data=code)


@router.get("/referral/records")
async def get_referral_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取推荐记录"""
    service = OperationService(db)
    records, total = await service.get_referral_records(
        referrer_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return success_response(data=PaginatedResponse(
        items=records,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/referral/statistics")
async def get_referral_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取推荐统计"""
    service = OperationService(db)
    statistics = await service.get_referral_statistics(current_user.id)
    return success_response(data=statistics)


# ==================== 运营统计 ====================

@router.get("/statistics")
async def get_operation_statistics(
    query: StatisticsQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取运营统计（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    statistics = await service.get_operation_statistics(query)
    return success_response(data=statistics)


@router.get("/dashboard")
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取仪表盘统计（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    statistics = await service.get_dashboard_statistics()
    return success_response(data=statistics)
