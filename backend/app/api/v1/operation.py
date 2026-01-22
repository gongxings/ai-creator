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
    ActivityParticipate, ParticipationResponse,
    CouponCreate, CouponUpdate, CouponResponse,
    CouponReceive, CouponUse, UserCouponResponse, CouponCalculateResponse,
    ReferralCodeGenerate, ReferralCodeResponse,
    ReferralRecordResponse, ReferralStatisticsResponse,
    StatisticsQuery, StatisticsResponse
)
from app.schemas.common import Response, PaginatedResponse
from app.services.operation_service import OperationService

router = APIRouter(prefix="/operation", tags=["运营管理"])


# ==================== 活动管理 ====================

@router.post("/activities", response_model=Response[ActivityResponse])
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建运营活动（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.create_activity(activity)
    return Response(data=result)


@router.get("/activities", response_model=Response[PaginatedResponse[ActivityResponse]])
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
    return Response(data=PaginatedResponse(
        items=activities,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/activities/{activity_id}", response_model=Response[ActivityResponse])
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
    return Response(data=activity)


@router.put("/activities/{activity_id}", response_model=Response[ActivityResponse])
async def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新活动（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.update_activity(activity_id, activity)
    if not result:
        raise HTTPException(status_code=404, detail="活动不存在")
    return Response(data=result)


@router.delete("/activities/{activity_id}", response_model=Response[dict])
async def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除活动（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    success = await service.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="活动不存在")
    return Response(data={"message": "删除成功"})


@router.post("/activities/{activity_id}/participate", response_model=Response[ParticipationResponse])
async def participate_activity(
    activity_id: int,
    participate: ActivityParticipate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """参与活动"""
    service = OperationService(db)
    result = await service.participate_activity(activity_id, current_user.id, participate)
    return Response(data=result)


@router.get("/activities/{activity_id}/participations", response_model=Response[PaginatedResponse[ParticipationResponse]])
async def get_activity_participations(
    activity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取活动参与记录（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    participations, total = await service.get_activity_participations(
        activity_id=activity_id,
        skip=skip,
        limit=limit
    )
    return Response(data=PaginatedResponse(
        items=participations,
        total=total,
        skip=skip,
        limit=limit
    ))


# ==================== 优惠券管理 ====================

@router.post("/coupons", response_model=Response[CouponResponse])
async def create_coupon(
    coupon: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建优惠券（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.create_coupon(coupon)
    return Response(data=result)


@router.get("/coupons", response_model=Response[PaginatedResponse[CouponResponse]])
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
    return Response(data=PaginatedResponse(
        items=coupons,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/coupons/{coupon_id}", response_model=Response[CouponResponse])
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
    return Response(data=coupon)


@router.put("/coupons/{coupon_id}", response_model=Response[CouponResponse])
async def update_coupon(
    coupon_id: int,
    coupon: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新优惠券（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    result = await service.update_coupon(coupon_id, coupon)
    if not result:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return Response(data=result)


@router.delete("/coupons/{coupon_id}", response_model=Response[dict])
async def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除优惠券（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    success = await service.delete_coupon(coupon_id)
    if not success:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return Response(data={"message": "删除成功"})


@router.post("/coupons/{coupon_id}/receive", response_model=Response[UserCouponResponse])
async def receive_coupon(
    coupon_id: int,
    receive: CouponReceive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """领取优惠券"""
    service = OperationService(db)
    result = await service.receive_coupon(coupon_id, current_user.id, receive)
    return Response(data=result)


@router.get("/my-coupons", response_model=Response[PaginatedResponse[UserCouponResponse]])
async def get_my_coupons(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的优惠券"""
    service = OperationService(db)
    coupons, total = await service.get_user_coupons(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    return Response(data=PaginatedResponse(
        items=coupons,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.post("/coupons/calculate", response_model=Response[CouponCalculateResponse])
async def calculate_coupon_discount(
    use: CouponUse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """计算优惠券折扣"""
    service = OperationService(db)
    result = await service.calculate_coupon_discount(use.user_coupon_id, use.original_amount)
    return Response(data=result)


# ==================== 推广返利 ====================

@router.post("/referral/generate-code", response_model=Response[ReferralCodeResponse])
async def generate_referral_code(
    generate: ReferralCodeGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成推荐码"""
    service = OperationService(db)
    result = await service.generate_referral_code(current_user.id, generate)
    return Response(data=result)


@router.get("/referral/my-code", response_model=Response[ReferralCodeResponse])
async def get_my_referral_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的推荐码"""
    if not current_user.referral_code:
        raise HTTPException(status_code=404, detail="尚未生成推荐码")
    
    return Response(data=ReferralCodeResponse(
        referral_code=current_user.referral_code,
        referral_url=f"https://your-domain.com/register?ref={current_user.referral_code}"
    ))


@router.get("/referral/records", response_model=Response[PaginatedResponse[ReferralRecordResponse]])
async def get_referral_records(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取推广记录"""
    service = OperationService(db)
    records, total = await service.get_referral_records(
        referrer_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    return Response(data=PaginatedResponse(
        items=records,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.get("/referral/statistics", response_model=Response[ReferralStatisticsResponse])
async def get_referral_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取推广统计"""
    service = OperationService(db)
    stats = await service.get_referral_statistics(current_user.id)
    return Response(data=stats)


# ==================== 数据统计 ====================

@router.get("/statistics", response_model=Response[StatisticsResponse])
async def get_statistics(
    query: StatisticsQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取运营统计数据（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = OperationService(db)
    stats = await service.get_statistics(query)
    return Response(data=stats)


@router.get("/statistics/user/{user_id}", response_model=Response[dict])
async def get_user_statistics(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户统计数据"""
    # 只能查看自己的统计或管理员可以查看所有
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限查看")
    
    service = OperationService(db)
    stats = await service.get_user_statistics(user_id, start_date, end_date)
    return Response(data=stats)
