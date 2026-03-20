"""
流量统计 Celery 任务
1. 定时将 Redis 缓存的埋点数据同步到 MySQL
2. 每日汇总统计
"""
from celery import shared_task
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import get_sync_database_url
from app.services.tracker_service import tracker_service


@shared_task(name="app.tasks.traffic_tasks.sync_tracking_data")
def sync_tracking_data():
    """
    同步埋点数据：Redis → MySQL

    每分钟执行一次，批量处理：
    1. 页面访问记录
    2. 页面更新记录（停留时长、滚动深度）
    3. 用户行为事件
    """
    try:
        db_url = get_sync_database_url(settings.DATABASE_URL)
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        # 1. 同步页面访问记录
        pv_count = _sync_page_views(db)

        # 2. 同步页面更新记录
        update_count = _sync_page_view_updates(db)

        # 3. 同步用户行为事件
        event_count = _sync_user_events(db)

        db.close()

        if pv_count > 0 or update_count > 0 or event_count > 0:
            print(f"[Tracker] Synced: {pv_count} page views, {update_count} updates, {event_count} events")

        return {
            "page_views": pv_count,
            "updates": update_count,
            "events": event_count
        }
    except Exception as e:
        print(f"[Tracker] Sync failed: {e}")
        return {"error": str(e)}


def _sync_page_views(db) -> int:
    """同步页面访问记录"""
    from app.models.traffic import PageView

    records = tracker_service.get_cached_page_views(limit=1000)
    if not records:
        return 0

    count = 0
    for record in records:
        try:
            # 解析时间
            created_at = record.get("created_at")
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    created_at = datetime.utcnow()

            page_view = PageView(
                path=record.get("path"),
                session_id=record.get("session_id"),
                user_id=record.get("user_id"),
                ip_address=record.get("ip_address"),
                user_agent=record.get("user_agent"),
                referer=record.get("referer"),
                screen_width=record.get("screen_width"),
                screen_height=record.get("screen_height"),
                created_at=created_at
            )
            db.add(page_view)
            count += 1
        except Exception as e:
            print(f"[Tracker] PageView insert error: {e}")
            continue

    if count > 0:
        db.commit()

    return count


def _sync_page_view_updates(db) -> int:
    """同步页面更新记录（停留时长、滚动深度）"""
    from app.models.traffic import PageView

    updates = tracker_service.get_cached_page_view_updates(limit=1000)
    if not updates:
        return 0

    count = 0
    for update in updates:
        try:
            pv_id = update.get("page_view_id")
            stay_duration = update.get("stay_duration", 0)
            max_scroll_depth = update.get("max_scroll_depth", 0)

            # 根据 session_id + path 查找最近的记录
            # 或者根据前端传入的 page_view_id（如果有）
            # 这里简化处理：按 session_id 查找最近未完成的记录
            # 实际应该按业务逻辑优化

            # 标记为非跳出
            if stay_duration > 0 or max_scroll_depth > 0:
                # 更新所有满足条件的记录
                db.query(PageView).filter(
                    PageView.session_id == pv_id  # 使用 page_view_id 作为 session_id
                ).update({
                    PageView.stay_duration: stay_duration,
                    PageView.max_scroll_depth: max_scroll_depth,
                    PageView.is_bounce: False,
                    PageView.updated_at: datetime.utcnow()
                })
                count += 1
        except Exception as e:
            print(f"[Tracker] Update error: {e}")
            continue

    if count > 0:
        db.commit()

    return count


def _sync_user_events(db) -> int:
    """同步用户行为事件"""
    from app.models.traffic import UserEvent

    events = tracker_service.get_cached_user_events(limit=1000)
    if not events:
        return 0

    count = 0
    for event in events:
        try:
            created_at = event.get("created_at")
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    created_at = datetime.utcnow()

            user_event = UserEvent(
                session_id=event.get("session_id"),
                user_id=event.get("user_id"),
                page_path=event.get("page_path"),
                event_type=event.get("event_type"),
                event_name=event.get("event_name"),
                event_target=event.get("event_target"),
                event_data=event.get("event_data"),
                page_view_id=event.get("page_view_id"),
                created_at=created_at
            )
            db.add(user_event)
            count += 1
        except Exception as e:
            print(f"[Tracker] Event insert error: {e}")
            continue

    if count > 0:
        db.commit()

    return count


@shared_task(name="app.tasks.traffic_tasks.aggregate_daily_stats")
def aggregate_daily_stats():
    """
    每日统计汇总

    每天凌晨2点执行，汇总前一天的数据到 daily_stats 表
    """
    try:
        db_url = get_sync_database_url(settings.DATABASE_URL)
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        from app.models.traffic import PageView, DailyStats
        from app.models.user import User

        # 汇总昨天的数据
        yesterday = date.today() - timedelta(days=1)

        # 检查是否已汇总
        existing = db.query(DailyStats).filter(DailyStats.date == yesterday).first()
        if existing:
            print(f"[Stats] Already aggregated for {yesterday}")
            db.close()
            return {"status": "already_aggregated", "date": str(yesterday)}

        # 统计页面访问
        pv = db.query(func.count(PageView.id)).filter(
            func.date(PageView.created_at) == yesterday
        ).scalar() or 0

        uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
            func.date(PageView.created_at) == yesterday
        ).scalar() or 0

        # 平均停留时长
        avg_duration = db.query(func.avg(PageView.stay_duration)).filter(
            func.date(PageView.created_at) == yesterday,
            PageView.stay_duration > 0
        ).scalar() or 0

        # 平均滚动深度
        avg_scroll = db.query(func.avg(PageView.max_scroll_depth)).filter(
            func.date(PageView.created_at) == yesterday,
            PageView.max_scroll_depth > 0
        ).scalar() or 0

        # 跳出率
        bounce_count = db.query(func.count(PageView.id)).filter(
            func.date(PageView.created_at) == yesterday,
            PageView.is_bounce == True
        ).scalar() or 0
        bounce_rate = round(bounce_count / pv * 100) if pv > 0 else 0

        # 新用户数
        new_users = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == yesterday
        ).scalar() or 0

        # 活跃用户数（有访问记录的用户）
        active_users = db.query(func.count(func.distinct(PageView.user_id))).filter(
            func.date(PageView.created_at) == yesterday,
            PageView.user_id.isnot(None)
        ).scalar() or 0

        # 写入 daily_stats 表
        daily_stat = DailyStats(
            date=yesterday,
            pv=pv,
            uv=uv,
            new_users=new_users,
            active_users=active_users,
            avg_stay_duration=round(avg_duration),
            avg_scroll_depth=round(avg_scroll),
            bounce_rate=bounce_rate
        )
        db.add(daily_stat)
        db.commit()

        print(f"[Stats] Aggregated for {yesterday}: PV={pv}, UV={uv}")

        db.close()

        return {
            "date": str(yesterday),
            "pv": pv,
            "uv": uv,
            "new_users": new_users,
            "active_users": active_users,
            "avg_stay_duration": round(avg_duration),
            "avg_scroll_depth": round(avg_scroll),
            "bounce_rate": bounce_rate
        }
    except Exception as e:
        print(f"[Stats] Aggregation failed: {e}")
        return {"error": str(e)}
