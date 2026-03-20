"""
埋点数据 Redis 缓存服务
将埋点数据先存入 Redis，再定时批量写入 MySQL
"""
import json
import redis
from typing import Dict, List, Optional
from datetime import datetime

from app.core.config import settings


class TrackerService:
    """埋点数据缓存服务"""

    PAGE_VIEW_KEY = "tracker:page_views"
    USER_EVENT_KEY = "tracker:user_events"
    PAGE_VIEW_UPDATE_KEY = "tracker:page_view_updates"

    def __init__(self):
        self.redis_client = None
        self._connect()

    def _connect(self):
        """连接 Redis"""
        try:
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}. Using memory cache.")
            self.redis_client = None

    def cache_page_view(self, data: Dict) -> Optional[str]:
        """
        缓存页面访问记录

        Args:
            data: {
                "id": str,  # 前端生成的唯一ID
                "path": str,
                "session_id": str,
                "user_id": int | None,
                "ip_address": str | None,
                "user_agent": str | None,
                "referer": str | None,
                "screen_width": int | None,
                "screen_height": int | None,
                "created_at": str
            }

        Returns:
            缓存的记录ID，失败返回 None
        """
        if not self.redis_client:
            return self._fallback_db_store(data)

        try:
            record_id = data.get("id") or f"pv_{int(datetime.utcnow().timestamp())}_{hash(data['session_id'])}"
            data["id"] = record_id

            # 存入 Redis List（按时间顺序）
            self.redis_client.lpush(self.PAGE_VIEW_KEY, json.dumps(data, ensure_ascii=False))

            # 限制 List 大小，防止内存溢出
            self.redis_client.ltrim(self.PAGE_VIEW_KEY, 0, 99999)

            return record_id
        except Exception as e:
            print(f"Redis cache failed: {e}")
            return self._fallback_db_store(data)

    def update_page_view(self, page_view_id: str, stay_duration: int, max_scroll_depth: int):
        """
        更新页面访问记录（停留时长、滚动深度）

        Args:
            page_view_id: PageView记录ID
            stay_duration: 停留时长（秒）
            max_scroll_depth: 最大滚动深度（百分比）
        """
        if not self.redis_client:
            return False

        try:
            update_data = {
                "page_view_id": page_view_id,
                "stay_duration": stay_duration,
                "max_scroll_depth": max_scroll_depth,
                "updated_at": datetime.utcnow().isoformat()
            }
            self.redis_client.lpush(self.PAGE_VIEW_UPDATE_KEY, json.dumps(update_data))
            self.redis_client.ltrim(self.PAGE_VIEW_UPDATE_KEY, 0, 99999)
            return True
        except Exception as e:
            print(f"Redis update failed: {e}")
            return False

    def cache_user_events(self, events: List[Dict]) -> int:
        """
        批量缓存用户行为事件

        Args:
            events: [{
                "session_id": str,
                "user_id": int | None,
                "page_path": str,
                "event_type": str,
                "event_name": str,
                "event_target": str | None,
                "event_data": dict | None,
                "page_view_id": str | None,
                "created_at": str
            }, ...]

        Returns:
            成功缓存的事件数量
        """
        if not self.redis_client:
            return 0

        success_count = 0
        try:
            pipeline = self.redis_client.pipeline()
            for event in events:
                event["created_at"] = event.get("created_at") or datetime.utcnow().isoformat()
                pipeline.lpush(self.USER_EVENT_KEY, json.dumps(event, ensure_ascii=False))
            pipeline.ltrim(self.USER_EVENT_KEY, 0, 99999)
            pipeline.execute()
            success_count = len(events)
        except Exception as e:
            print(f"Redis batch cache failed: {e}")

        return success_count

    def get_cached_page_views(self, limit: int = 1000) -> List[Dict]:
        """
        获取缓存的页面访问记录

        Args:
            limit: 最大获取数量

        Returns:
            页面访问记录列表
        """
        if not self.redis_client:
            return []

        try:
            # 原子性获取并删除（RPOP 从尾部取，配合 pipeline）
            pipeline = self.redis_client.pipeline()
            for _ in range(min(limit, 10000)):
                pipeline.rpop(self.PAGE_VIEW_KEY)
            results = pipeline.execute()

            # 过滤 None 并解析 JSON
            records = []
            for item in results:
                if item:
                    try:
                        records.append(json.loads(item))
                    except json.JSONDecodeError:
                        continue

            return records
        except Exception as e:
            print(f"Redis get failed: {e}")
            return []

    def get_cached_page_view_updates(self, limit: int = 1000) -> List[Dict]:
        """
        获取缓存的页面更新记录（停留时长、滚动深度）

        Args:
            limit: 最大获取数量

        Returns:
            页面更新记录列表
        """
        if not self.redis_client:
            return []

        try:
            pipeline = self.redis_client.pipeline()
            for _ in range(min(limit, 10000)):
                pipeline.rpop(self.PAGE_VIEW_UPDATE_KEY)
            results = pipeline.execute()

            records = []
            for item in results:
                if item:
                    try:
                        records.append(json.loads(item))
                    except json.JSONDecodeError:
                        continue

            return records
        except Exception as e:
            print(f"Redis get updates failed: {e}")
            return []

    def get_cached_user_events(self, limit: int = 1000) -> List[Dict]:
        """
        获取缓存的用户行为事件

        Args:
            limit: 最大获取数量

        Returns:
            用户事件列表
        """
        if not self.redis_client:
            return []

        try:
            pipeline = self.redis_client.pipeline()
            for _ in range(min(limit, 10000)):
                pipeline.rpop(self.USER_EVENT_KEY)
            results = pipeline.execute()

            records = []
            for item in results:
                if item:
                    try:
                        records.append(json.loads(item))
                    except json.JSONDecodeError:
                        continue

            return records
        except Exception as e:
            print(f"Redis get events failed: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        if not self.redis_client:
            return {"status": "redis_unavailable", "page_views": 0, "events": 0, "updates": 0}

        try:
            return {
                "status": "ok",
                "page_views": self.redis_client.llen(self.PAGE_VIEW_KEY),
                "events": self.redis_client.llen(self.USER_EVENT_KEY),
                "updates": self.redis_client.llen(self.PAGE_VIEW_UPDATE_KEY)
            }
        except Exception:
            return {"status": "error", "page_views": 0, "events": 0, "updates": 0}

    def _fallback_db_store(self, data: Dict) -> Optional[str]:
        """Redis 不可用时，直接存储到数据库"""
        try:
            from app.core.database import get_sync_database_url
            from sqlalchemy import create_engine, text

            db_url = get_sync_database_url(settings.DATABASE_URL)
            engine = create_engine(db_url)

            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO page_views (path, session_id, user_id, ip_address, user_agent, referer, created_at)
                    VALUES (:path, :session_id, :user_id, :ip_address, :user_agent, :referer, :created_at)
                """), {
                    "path": data.get("path"),
                    "session_id": data.get("session_id"),
                    "user_id": data.get("user_id"),
                    "ip_address": data.get("ip_address"),
                    "user_agent": data.get("user_agent"),
                    "referer": data.get("referer"),
                    "created_at": data.get("created_at") or datetime.utcnow()
                })
                conn.commit()

            return "db_stored"
        except Exception as e:
            print(f"Fallback DB store failed: {e}")
            return None


# 全局实例
tracker_service = TrackerService()
