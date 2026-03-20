"""
后台埋点数据同步任务
使用独立线程运行，不依赖 Celery
"""
import asyncio
import threading
import time
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.services.tracker_service import tracker_service
from app.core.database import get_sync_database_url
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session
from app.models.traffic import PageView, UserEvent, DailyStats
from app.models.user import User


class TrackerBackgroundTask:
    """埋点数据后台同步任务"""

    def __init__(self, sync_interval: int = 60):
        """
        初始化后台任务
        
        Args:
            sync_interval: 同步间隔（秒），默认60秒
        """
        self.sync_interval = sync_interval
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self):
        """启动后台任务"""
        if self._thread and self._thread.is_alive():
            print("[Tracker] Background task already running")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run_async_loop,
            daemon=True,
            name="TrackerBackgroundTask"
        )
        self._thread.start()
        print("[Tracker] Background task started")

    def stop(self):
        """停止后台任务"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            print("[Tracker] Background task stopped")

    def _run_async_loop(self):
        """在新线程中运行 asyncio 事件循环"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._sync_loop())
        except Exception as e:
            print(f"[Tracker] Background task error: {e}")
        finally:
            self._loop.close()

    async def _sync_loop(self):
        """同步循环"""
        # 首次启动后等待一段时间再执行
        await asyncio.sleep(10)
        
        while self._running:
            try:
                await self._sync_tracking_data()
            except Exception as e:
                print(f"[Tracker] Sync error: {e}")
            
            # 等待下一次同步
            await asyncio.sleep(self.sync_interval)

    async def _sync_tracking_data(self):
        """同步埋点数据：Redis → MySQL"""
        db_url = get_sync_database_url(settings.DATABASE_URL)
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        db = SessionLocal()
        try:
            # 1. 同步页面访问记录
            pv_count = self._sync_page_views(db)
            
            # 2. 同步用户行为事件
            event_count = self._sync_user_events(db)
            
            if pv_count > 0 or event_count > 0:
                print(f"[Tracker] Synced: {pv_count} page views, {event_count} events")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def _sync_page_views(self, db: Session) -> int:
        """同步页面访问记录"""
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
                        # 处理 ISO 格式时间
                        from datetime import timezone
                        # 移除 'Z' 并添加时区信息
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
                print(f"[Tracker] PageView insert error: {e}")
                continue

        if count > 0:
            db.commit()

        return count

    def _sync_user_events(self, db: Session) -> int:
        """同步用户行为事件"""
        events = tracker_service.get_cached_user_events(limit=1000)
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
                print(f"[Tracker] Event insert error: {e}")
                continue

        if count > 0:
            db.commit()

        return count


# 全局后台任务实例
tracker_background_task = TrackerBackgroundTask(sync_interval=60)


def start_tracker_background():
    """启动埋点后台任务（在 FastAPI startup 事件中调用）"""
    tracker_background_task.start()


def stop_tracker_background():
    """停止埋点后台任务"""
    tracker_background_task.stop()


# 独立运行（调试用）
if __name__ == "__main__":
    print("Starting tracker background task...")
    start_tracker_background()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_tracker_background()
