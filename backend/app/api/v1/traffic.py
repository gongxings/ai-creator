"""
流量统计 API
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.traffic import PageView, DailyStats
from app.utils.deps import get_admin_user
from app.schemas.common import success_response

router = APIRouter()


@router.post("/record")
def record_page_view(
    path: str = Query(..., description="访问路径"),
    session_id: Optional[str] = Query(None, description="会话ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    ip_address: Optional[str] = Query(None, description="IP地址"),
    user_agent: Optional[str] = Query(None, description="User-Agent"),
    referer: Optional[str] = Query(None, description="来源页面"),
    db: Session = Depends(get_db)
) -> Any:
    """记录页面访问"""
    page_view = PageView(
        path=path,
        session_id=session_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        created_at=datetime.utcnow()
    )
    db.add(page_view)
    db.commit()
    
    return success_response(message="访问已记录")


@router.get("/overview")
def get_traffic_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取流量概览（管理员）
    
    **权限要求**: 管理员
    
    **返回**:
    - 今日PV/UV、总用户数、总创作数、周/月统计
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # 今日PV
    today_pv = db.query(func.count(PageView.id)).filter(
        func.date(PageView.created_at) == today
    ).scalar() or 0
    
    # 今日UV（独立会话数）
    today_uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
        func.date(PageView.created_at) == today
    ).scalar() or 0
    
    # 今日新用户
    today_new_users = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar() or 0
    
    # 总用户数
    total_users = db.query(func.count(User.id)).filter(
        User.deleted_at.is_(None)
    ).scalar() or 0
    
    # 总创作数
    total_creations = db.query(func.count(User.id)).filter(
        User.total_creations > 0
    ).scalar() or 0
    
    # 本周PV
    week_pv = db.query(func.count(PageView.id)).filter(
        func.date(PageView.created_at) >= week_start
    ).scalar() or 0
    
    # 本周UV
    week_uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
        func.date(PageView.created_at) >= week_start
    ).scalar() or 0
    
    # 本月PV
    month_pv = db.query(func.count(PageView.id)).filter(
        func.date(PageView.created_at) >= month_start
    ).scalar() or 0
    
    # 本月UV
    month_uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
        func.date(PageView.created_at) >= month_start
    ).scalar() or 0
    
    return success_response(
        data={
            "today_pv": today_pv,
            "today_uv": today_uv,
            "today_new_users": today_new_users,
            "total_users": total_users,
            "total_creations": total_creations,
            "week_pv": week_pv,
            "week_uv": week_uv,
            "month_pv": month_pv,
            "month_uv": month_uv
        }
    )


@router.get("/daily")
def get_daily_stats(
    days: int = Query(default=30, ge=1, le=90, description="查询天数"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取每日统计列表（管理员）
    
    **权限要求**: 管理员
    
    **参数**:
    - days: 查询天数（默认30天，最大90天）
    
    **返回**:
    - 每日PV/UV/新用户/活跃用户统计
    """
    start_date = date.today() - timedelta(days=days)
    
    # 从 daily_stats 表获取数据
    stats = db.query(DailyStats).filter(
        DailyStats.date >= start_date
    ).order_by(DailyStats.date.asc()).all()
    
    # 如果没有预聚合数据，从 page_views 实时计算
    if not stats:
        # 按日期分组统计
        daily_data = []
        current = start_date
        end_date = date.today()
        
        while current <= end_date:
            day_pv = db.query(func.count(PageView.id)).filter(
                func.date(PageView.created_at) == current
            ).scalar() or 0
            
            day_uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
                func.date(PageView.created_at) == current
            ).scalar() or 0
            
            day_new_users = db.query(func.count(User.id)).filter(
                func.date(User.created_at) == current
            ).scalar() or 0
            
            daily_data.append({
                "date": current.strftime("%Y-%m-%d"),
                "pv": day_pv,
                "uv": day_uv,
                "new_users": day_new_users,
                "active_users": 0,
                "total_requests": 0
            })
            
            current += timedelta(days=1)
    else:
        daily_data = [{
            "date": s.date.strftime("%Y-%m-%d"),
            "pv": s.pv,
            "uv": s.uv,
            "new_users": s.new_users,
            "active_users": s.active_users,
            "total_requests": s.total_requests
        } for s in stats]
    
    return success_response(data=daily_data)
