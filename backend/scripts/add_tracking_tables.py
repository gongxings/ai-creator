"""
数据库迁移脚本：
1. 扩展 page_views 表（添加停留时长、滚动深度字段）
2. 创建 user_events 表（用户行为事件）

运行方式：
    cd backend
    python -m scripts.add_tracking_tables
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text, create_engine
from app.core.config import settings
from app.core.database import get_sync_database_url

db_url = get_sync_database_url(settings.DATABASE_URL)
engine = create_engine(db_url)


def extend_page_views_table():
    """扩展 page_views 表"""
    print("[1/2] 扩展 page_views 表...")

    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("SHOW COLUMNS FROM page_views LIKE 'stay_duration'"))
            if result.fetchone():
                print("  - page_views 表已是最新，跳过")
                return

            # 添加新字段
            conn.execute(text("""
                ALTER TABLE page_views
                ADD COLUMN stay_duration INT DEFAULT 0 COMMENT '停留时长（秒）',
                ADD COLUMN max_scroll_depth INT DEFAULT 0 COMMENT '最大滚动深度（百分比0-100）',
                ADD COLUMN is_bounce TINYINT(1) DEFAULT 1 COMMENT '是否跳出（单页访问）',
                ADD COLUMN screen_width INT COMMENT '屏幕宽度',
                ADD COLUMN screen_height INT COMMENT '屏幕高度',
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            """))

            # 添加索引
            try:
                conn.execute(text("CREATE INDEX idx_page_views_is_bounce ON page_views (is_bounce)"))
            except Exception:
                pass  # 索引可能已存在

            conn.commit()
            print("  - page_views 表扩展完成")
    except Exception as e:
        print(f"  - 扩展 page_views 表时出错: {e}")


def create_user_events_table():
    """创建 user_events 表"""
    print("[2/2] 创建 user_events 表...")

    try:
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("SHOW TABLES LIKE 'user_events'"))
            if result.fetchone():
                print("  - user_events 表已存在，跳过")
                return

            # 创建表
            conn.execute(text("""
                CREATE TABLE user_events (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
                    session_id VARCHAR(100) NOT NULL COMMENT '会话ID',
                    user_id BIGINT COMMENT '用户ID',
                    page_path VARCHAR(500) COMMENT '所在页面路径',
                    event_type VARCHAR(50) NOT NULL COMMENT '事件类型: click/scroll/custom',
                    event_name VARCHAR(100) COMMENT '事件名称',
                    event_target VARCHAR(200) COMMENT '目标元素',
                    event_data JSON COMMENT '附加数据',
                    page_view_id BIGINT COMMENT '关联的PageView ID',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '事件时间',
                    INDEX idx_session_id (session_id),
                    INDEX idx_user_id (user_id),
                    INDEX idx_page_path (page_path),
                    INDEX idx_event_type (event_type),
                    INDEX idx_page_view_id (page_view_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户行为事件表'
            """))

            conn.commit()
            print("  - user_events 表创建完成")
    except Exception as e:
        print(f"  - 创建 user_events 表时出错: {e}")


def update_daily_stats_table():
    """更新 daily_stats 表（添加新字段）"""
    print("[3/3] 更新 daily_stats 表...")

    try:
        with engine.connect() as conn:
            # 检查字段是否存在
            result = conn.execute(text("SHOW COLUMNS FROM daily_stats LIKE 'avg_stay_duration'"))
            if result.fetchone():
                print("  - daily_stats 表已是最新，跳过")
                return

            # 添加新字段
            conn.execute(text("""
                ALTER TABLE daily_stats
                ADD COLUMN avg_stay_duration INT DEFAULT 0 COMMENT '平均停留时长（秒）',
                ADD COLUMN avg_scroll_depth INT DEFAULT 0 COMMENT '平均滚动深度（百分比）',
                ADD COLUMN bounce_rate INT DEFAULT 0 COMMENT '跳出率（百分比）'
            """))

            conn.commit()
            print("  - daily_stats 表更新完成")
    except Exception as e:
        print(f"  - 更新 daily_stats 表时出错: {e}")


def main():
    print("=" * 50)
    print("数据库迁移：全埋点表结构")
    print("=" * 50)

    try:
        extend_page_views_table()
        create_user_events_table()
        update_daily_stats_table()

        print("\n" + "=" * 50)
        print("数据库迁移完成！")
        print("=" * 50)
    except Exception as e:
        print(f"\n迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
