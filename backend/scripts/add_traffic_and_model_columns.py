"""
数据库迁移脚本：
1. 添加 is_system_builtin 字段到 ai_models 表
2. 创建流量统计相关表（page_views, daily_stats）
3. 删除 api_keys 和 api_key_usage_logs 表（如果存在）

运行方式：
    cd backend
    python -m scripts.add_traffic_and_model_columns
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


def add_is_system_builtin():
    """添加 is_system_builtin 字段到 ai_models 表"""
    print("[1/4] 添加 is_system_builtin 字段...")
    
    try:
        with engine.connect() as conn:
            # 检查字段是否存在
            result = conn.execute(text("SHOW COLUMNS FROM ai_models LIKE 'is_system_builtin'"))
            if result.fetchone():
                print("  - is_system_builtin 字段已存在，跳过")
                return
            
            # 添加字段
            conn.execute(text("""
                ALTER TABLE ai_models 
                ADD COLUMN is_system_builtin TINYINT(1) DEFAULT 0 COMMENT '是否系统内置模型'
            """))
            
            # 添加索引
            try:
                conn.execute(text("""
                    CREATE INDEX idx_system_builtin_user 
                    ON ai_models (is_system_builtin, user_id)
                """))
            except Exception as e:
                if "Duplicate key name" not in str(e):
                    print(f"  - 创建索引时出错（可能已存在）: {e}")
            
            # 删除旧索引（如果存在）
            try:
                conn.execute(text("DROP INDEX idx_system_default_user ON ai_models"))
            except Exception:
                pass
            
            # 删除旧字段（如果存在）
            for col in ['system_default_source', 'source_api_key_id']:
                try:
                    conn.execute(text(f"ALTER TABLE ai_models DROP COLUMN {col}"))
                except Exception:
                    pass
            
            conn.commit()
            print("  - is_system_builtin 字段添加成功")
    except Exception as e:
        print(f"  - 错误: {e}")


def create_traffic_tables():
    """创建流量统计相关表"""
    print("[2/4] 创建流量统计表...")
    
    with engine.connect() as conn:
        # 创建 page_views 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS page_views (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                path VARCHAR(500) NOT NULL COMMENT '访问路径',
                user_id BIGINT COMMENT '用户ID',
                ip_address VARCHAR(50) COMMENT 'IP地址',
                user_agent VARCHAR(500) COMMENT 'User-Agent',
                referer VARCHAR(500) COMMENT '来源页面',
                session_id VARCHAR(100) COMMENT '会话ID',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
                INDEX idx_path (path),
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='页面访问记录表'
        """))
        
        # 创建 daily_stats 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL COMMENT '统计日期',
                pv INT DEFAULT 0 COMMENT '页面访问量',
                uv INT DEFAULT 0 COMMENT '独立访客数',
                new_users INT DEFAULT 0 COMMENT '新注册用户数',
                active_users INT DEFAULT 0 COMMENT '活跃用户数',
                total_requests INT DEFAULT 0 COMMENT 'AI请求总数',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                UNIQUE INDEX idx_date (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日统计表'
        """))
        
        conn.commit()
        print("  - 流量统计表创建成功")


def drop_api_key_tables():
    """删除 API Key 相关表"""
    print("[3/4] 删除 API Key 相关表...")
    
    tables = ['api_key_usage_logs', 'api_keys']
    
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"  - 已删除表 {table}")
            except Exception as e:
                print(f"  - 删除表 {table} 时出错: {e}")
        
        conn.commit()


def update_indexes():
    """更新索引"""
    print("[4/4] 更新索引...")
    
    with engine.connect() as conn:
        # 删除旧的 system_default 索引
        try:
            conn.execute(text("DROP INDEX idx_system_default ON api_keys"))
        except Exception:
            pass
        
        conn.commit()
        print("  - 索引更新完成")


def main():
    print("=" * 50)
    print("数据库迁移：添加流量统计和系统内置模型支持")
    print("=" * 50)
    
    try:
        add_is_system_builtin()
        create_traffic_tables()
        drop_api_key_tables()
        update_indexes()
        
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
