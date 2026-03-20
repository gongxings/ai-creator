"""
流量统计 API
支持全埋点：页面访问 + 用户行为事件 + 批量上报
"""
from datetime import date, datetime, timedelta
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.traffic import PageView, UserEvent, DailyStats
from app.models.user import User
from app.schemas.common import success_response
from app.services.tracker_service import tracker_service
from app.utils.deps import get_admin_user

router = APIRouter()


# ===== 批量上报 Schema =====

class PageViewEvent(BaseModel):
    """页面访问事件"""
    id: Optional[str] = Field(None, description="前端生成的唯一ID")
    path: str = Field(..., description="访问路径")
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    user_agent: Optional[str] = Field(None, description="User-Agent")
    referer: Optional[str] = Field(None, description="来源页面")
    screen_width: Optional[int] = Field(None, description="屏幕宽度")
    screen_height: Optional[int] = Field(None, description="屏幕高度")
    created_at: Optional[str] = Field(None, description="创建时间")


class PageViewUpdate(BaseModel):
    """页面更新（停留时长、滚动深度）"""
    page_view_id: str = Field(..., description="PageView ID")
    stay_duration: int = Field(0, description="停留时长（秒）")
    max_scroll_depth: int = Field(0, description="最大滚动深度（百分比）")


class UserBehaviorEvent(BaseModel):
    """用户行为事件"""
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    page_path: str = Field(..., description="所在页面路径")
    event_type: str = Field(..., description="事件类型: click/scroll/custom")
    event_name: Optional[str] = Field(None, description="事件名称")
    event_target: Optional[str] = Field(None, description="目标元素")
    event_data: Optional[dict] = Field(None, description="附加数据")
    page_view_id: Optional[str] = Field(None, description="关联的PageView ID")
    created_at: Optional[str] = Field(None, description="事件时间")


class BatchTrackRequest(BaseModel):
    """批量埋点上报"""
    page_views: List[PageViewEvent] = Field(default=[], description="页面访问记录")
    page_view_updates: List[PageViewUpdate] = Field(default=[], description="页面更新记录")
    user_events: List[UserBehaviorEvent] = Field(default=[], description="用户行为事件")


# ===== 埋点上报接口 =====

@router.post("/batch")
async def batch_track(
    request: Request,
    data: BatchTrackRequest
) -> Any:
    """
    批量埋点上报（无需登录）

    前端通过此接口一次性上报多个埋点事件，后端存入 Redis 缓存
    """
    # 获取真实 IP
    ip_address = (
        request.headers.get("X-Real-IP") or
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        (request.client.host if request.client else None)
    )

    # 存入页面访问记录
    pv_count = 0
    page_view_ids = {}
    for pv in data.page_views:
        pv_dict = pv.model_dump()
        pv_dict["ip_address"] = ip_address
        pv_dict["created_at"] = pv_dict.get("created_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if pv_dict["created_at"].endswith("Z"):
            pv_dict["created_at"] = pv_dict["created_at"][:-1].replace("T", " ")

        record_id = tracker_service.cache_page_view(pv_dict)
        if record_id:
            pv_count += 1
            if pv.id:
                page_view_ids[pv.id] = record_id

    # 存入页面更新记录
    update_count = 0
    for update in data.page_view_updates:
        tracker_service.update_page_view(
            update.page_view_id,
            update.stay_duration,
            update.max_scroll_depth
        )
        update_count += 1

    # 存入用户行为事件
    event_count = 0
    if data.user_events:
        events_data = []
        for event in data.user_events:
            event_dict = event.model_dump()
            event_dict["created_at"] = event_dict.get("created_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            if event_dict["created_at"].endswith("Z"):
                event_dict["created_at"] = event_dict["created_at"][:-1].replace("T", " ")
            # 关联 page_view_id
            if event.page_view_id and event.page_view_id in page_view_ids:
                event_dict["page_view_id"] = page_view_ids[event.page_view_id]
            events_data.append(event_dict)

        event_count = tracker_service.cache_user_events(events_data)

    return success_response(
        data={
            "page_views": pv_count,
            "updates": update_count,
            "events": event_count
        },
        message="埋点数据已记录"
    )


@router.get("/stats")
def get_tracker_stats(
    current_user: User = Depends(get_admin_user)
) -> Any:
    """
    获取埋点缓存统计（管理员）

    查看 Redis 中待处理的埋点数据量
    """
    stats = tracker_service.get_stats()
    return success_response(data=stats)


# ===== 管理员查询接口 =====

@router.get("/overview")
def get_traffic_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取流量概览（管理员）

    返回今日PV/UV、总用户数、总创作数、周/月统计
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

    # 今日平均停留时长
    avg_duration = db.query(func.avg(PageView.stay_duration)).filter(
        func.date(PageView.created_at) == today,
        PageView.stay_duration > 0
    ).scalar() or 0

    # 今日跳出率
    total_today = db.query(func.count(PageView.id)).filter(
        func.date(PageView.created_at) == today
    ).scalar() or 1
    bounce_today = db.query(func.count(PageView.id)).filter(
        func.date(PageView.created_at) == today,
        PageView.is_bounce == True
    ).scalar() or 0
    bounce_rate = round(bounce_today / total_today * 100) if total_today > 0 else 0

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
            "month_uv": month_uv,
            "avg_stay_duration": round(avg_duration),
            "bounce_rate": bounce_rate
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

    参数:
    - days: 查询天数（默认30天，最大90天）
    """
    start_date = date.today() - timedelta(days=days)

    # 从 daily_stats 表获取数据
    stats = db.query(DailyStats).filter(
        DailyStats.date >= start_date
    ).order_by(DailyStats.date.asc()).all()

    # 如果没有预聚合数据，从 page_views 实时计算
    if not stats:
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


@router.get("/hot-pages")
def get_hot_pages(
    days: int = Query(default=7, ge=1, le=90, description="查询天数"),
    limit: int = Query(default=10, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取热门页面（管理员）

    返回访问量最高的页面
    """
    start_date = date.today() - timedelta(days=days)

    hot_pages = db.query(
        PageView.path,
        func.count(PageView.id).label('pv'),
        func.count(func.distinct(PageView.session_id)).label('uv'),
        func.avg(PageView.stay_duration).label('avg_duration')
    ).filter(
        func.date(PageView.created_at) >= start_date
    ).group_by(
        PageView.path
    ).order_by(
        func.count(PageView.id).desc()
    ).limit(limit).all()

    return success_response(data=[
        {
            "path": page.path,
            "pv": page.pv,
            "uv": page.uv,
            "avg_duration": round(page.avg_duration or 0)
        }
        for page in hot_pages
    ])


@router.get("/click-events")
def get_click_events(
    days: int = Query(default=7, ge=1, le=90, description="查询天数"),
    limit: int = Query(default=20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取点击事件统计（管理员）

    返回点击最多的元素
    """
    start_date = date.today() - timedelta(days=days)

    click_events = db.query(
        UserEvent.event_name,
        UserEvent.event_target,
        UserEvent.page_path,
        func.count(UserEvent.id).label('click_count')
    ).filter(
        func.date(UserEvent.created_at) >= start_date,
        UserEvent.event_type == 'click'
    ).group_by(
        UserEvent.event_name,
        UserEvent.event_target,
        UserEvent.page_path
    ).order_by(
        func.count(UserEvent.id).desc()
    ).limit(limit).all()

    return success_response(data=[
        {
            "event_name": event.event_name,
            "event_target": event.event_target,
            "page_path": event.page_path,
            "click_count": event.click_count
        }
        for event in click_events
    ])
