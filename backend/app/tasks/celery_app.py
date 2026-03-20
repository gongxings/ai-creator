"""
Celery 应用配置
"""
from celery import Celery
from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "ai_creator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.traffic_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    # 序列化
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务结果过期时间（秒）
    result_expires=3600,

    # 任务超时时间（秒）
    task_soft_time_limit=300,
    task_time_limit=600,

    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # 定时任务
    beat_schedule={
        # 每分钟同步埋点数据
        "sync-tracking-data": {
            "task": "app.tasks.traffic_tasks.sync_tracking_data",
            "schedule": 60.0,  # 每60秒
        },
        # 每天凌晨2点汇总统计
        "daily-stats-aggregation": {
            "task": "app.tasks.traffic_tasks.aggregate_daily_stats",
            "schedule": {
                "hour": 2,
                "minute": 0,
            },
        },
    },
)

if __name__ == "__main__":
    celery_app.start()
