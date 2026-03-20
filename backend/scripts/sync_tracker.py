"""
独立脚本：同步埋点数据
可用于手动触发数据同步或调试

用法：
    python scripts/sync_tracker.py [--force] [--aggregate]

参数：
    --force      强制同步所有缓存数据（默认会分批处理）
    --aggregate  同时执行每日统计汇总
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import get_sync_database_url
from app.services.tracker_service import tracker_service
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timedelta
import time


def sync_page_views(db, batch_size: int = 1000) -> int:
    """同步页面访问记录"""
    from app.models.traffic import PageView
    
    records = tracker_service.get_cached_page_views(limit=batch_size)
    if not records:
        return 0
    
    count = 0
    for record in records:
        try:
            created_at = record.get("created_at")
            if isinstance(created_at, str):
                try:
                    from datetime import timezone
                    dt_str = created_at.rstrip('Z').replace('+00:00', '')
                    created_at = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                    created_at = created_at.replace(tzinfo=None)
                except (ValueError, AttributeError):
                    created_at = datetime.utcnow()
            
            page_view = PageView(
                path=record.get("path", ""),
                session_id=record.get("session_id", ""),
                user_id=record.get("user_id"),
                ip_address=record.get("ip_address"),
                user_agent=record.get("user_agent"),
                referer=record.get("referer"),
                screen_width=record.get("screen_width"),
                screen_height=record.get("screen_height"),
                stay_duration=record.get("stay_duration", 0),
                max_scroll_depth=record.get("max_scroll_depth", 0),
                is_bounce=record.get("is_bounce", True),
                created_at=created_at
            )
            db.add(page_view)
            count += 1
        except Exception as e:
            print(f"  [Error] PageView: {e}")
            continue
    
    if count > 0:
        db.commit()
    
    return count


def sync_user_events(db, batch_size: int = 1000) -> int:
    """同步用户行为事件"""
    from app.models.traffic import UserEvent
    
    events = tracker_service.get_cached_user_events(limit=batch_size)
    if not events:
        return 0
    
    count = 0
    for event in events:
        try:
            created_at = event.get("created_at")
            if isinstance(created_at, str):
                try:
                    from datetime import timezone
                    dt_str = created_at.rstrip('Z').replace('+00:00', '')
                    created_at = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                    created_at = created_at.replace(tzinfo=None)
                except (ValueError, AttributeError):
                    created_at = datetime.utcnow()
            
            user_event = UserEvent(
                session_id=event.get("session_id", ""),
                user_id=event.get("user_id"),
                page_path=event.get("page_path", ""),
                event_type=event.get("event_type", "custom"),
                event_name=event.get("event_name"),
                event_target=event.get("event_target"),
                event_data=event.get("event_data"),
                page_view_id=event.get("page_view_id"),
                created_at=created_at
            )
            db.add(user_event)
            count += 1
        except Exception as e:
            print(f"  [Error] UserEvent: {e}")
            continue
    
    if count > 0:
        db.commit()
    
    return count


def sync_all_data(force: bool = False) -> dict:
    """
    同步所有缓存数据
    
    Args:
        force: 强制同步（忽略队列限制）
    
    Returns:
        同步统计
    """
    print("=" * 50)
    print("开始同步埋点数据")
    print("=" * 50)
    
    db_url = get_sync_database_url(settings.DATABASE_URL)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 检查缓存统计
        stats = tracker_service.get_stats()
        print(f"\n缓存状态:")
        print(f"  PageViews: {stats['page_views']}")
        print(f"  Events: {stats['events']}")
        print(f"  Updates: {stats['updates']}")
        
        if stats['page_views'] == 0 and stats['events'] == 0:
            print("\n无待同步数据，跳过")
            return {"page_views": 0, "events": 0}
        
        # 同步页面访问
        print("\n[1] 同步页面访问记录...")
        pv_total = 0
        while True:
            pv_count = sync_page_views(db, batch_size=1000)
            pv_total += pv_count
            print(f"  本轮同步: {pv_count} 条")
            
            if pv_count < 1000 and not force:
                break
            if force and pv_count == 0:
                break
            time.sleep(0.1)
        
        # 同步用户事件
        print("\n[2] 同步用户行为事件...")
        event_total = 0
        while True:
            event_count = sync_user_events(db, batch_size=1000)
            event_total += event_count
            print(f"  本轮同步: {event_count} 条")
            
            if event_count < 1000 and not force:
                break
            if force and event_count == 0:
                break
            time.sleep(0.1)
        
        print(f"\n同步完成！总计: {pv_total} 页面访问, {event_total} 事件")
        return {"page_views": pv_total, "events": event_total}
        
    finally:
        db.close()


def aggregate_daily_stats(target_date: date = None) -> dict:
    """
    汇总每日统计
    
    Args:
        target_date: 汇总的日期，默认为昨天
    
    Returns:
        汇总结果
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    
    print("=" * 50)
    print(f"汇总每日统计: {target_date}")
    print("=" * 50)
    
    db_url = get_sync_database_url(settings.DATABASE_URL)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        from app.models.traffic import PageView, DailyStats
        from app.models.user import User
        
        # 检查是否已汇总
        existing = db.query(DailyStats).filter(DailyStats.date == target_date).first()
        if existing:
            print(f"  日期 {target_date} 已汇总，跳过")
            return {"status": "skipped", "date": str(target_date)}
        
        # 统计页面访问
        pv = db.query(func.count(PageView.id)).filter(
            func.date(PageView.created_at) == target_date
        ).scalar() or 0
        
        uv = db.query(func.count(func.distinct(PageView.session_id))).filter(
            func.date(PageView.created_at) == target_date
        ).scalar() or 0
        
        # 平均停留时长
        avg_duration = db.query(func.avg(PageView.stay_duration)).filter(
            func.date(PageView.created_at) == target_date,
            PageView.stay_duration > 0
        ).scalar() or 0
        
        # 平均滚动深度
        avg_scroll = db.query(func.avg(PageView.max_scroll_depth)).filter(
            func.date(PageView.created_at) == target_date,
            PageView.max_scroll_depth > 0
        ).scalar() or 0
        
        # 跳出率
        bounce_count = db.query(func.count(PageView.id)).filter(
            func.date(PageView.created_at) == target_date,
            PageView.is_bounce == True
        ).scalar() or 0
        bounce_rate = round(bounce_count / pv * 100) if pv > 0 else 0
        
        # 新用户数
        new_users = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == target_date
        ).scalar() or 0
        
        # 活跃用户数
        active_users = db.query(func.count(func.distinct(PageView.user_id))).filter(
            func.date(PageView.created_at) == target_date,
            PageView.user_id.isnot(None)
        ).scalar() or 0
        
        # 写入 daily_stats
        daily_stat = DailyStats(
            date=target_date,
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
        
        print(f"  汇总结果: PV={pv}, UV={uv}, 新用户={new_users}")
        
        return {
            "date": str(target_date),
            "pv": pv,
            "uv": uv,
            "new_users": new_users,
            "active_users": active_users,
            "avg_stay_duration": round(avg_duration),
            "avg_scroll_depth": round(avg_scroll),
            "bounce_rate": bounce_rate
        }
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="同步埋点数据")
    parser.add_argument("--force", action="store_true", help="强制同步所有数据")
    parser.add_argument("--aggregate", action="store_true", help="同时执行每日统计汇总")
    args = parser.parse_args()
    
    try:
        # 同步数据
        result = sync_all_data(force=args.force)
        
        # 如果需要，同时汇总统计
        if args.aggregate:
            print("\n" + "=" * 50)
            agg_result = aggregate_daily_stats()
            print(f"汇总完成: {agg_result}")
        
        print("\n" + "=" * 50)
        print("任务完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
