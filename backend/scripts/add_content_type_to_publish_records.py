"""
为 publish_records 表添加 content_type 字段的迁移脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    print("开始迁移数据库...")
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'publish_records' 
            AND COLUMN_NAME = 'content_type'
        """))
        exists = result.fetchone()[0] > 0
        
        if exists:
            print("字段 'content_type' 已存在于 publish_records 表中")
            return
        
        # 添加 content_type 字段
        print("正在添加 content_type 字段...")
        conn.execute(text("""
            ALTER TABLE publish_records 
            ADD COLUMN content_type VARCHAR(50) NULL COMMENT '内容类型'
            AFTER status
        """))
        conn.commit()
        
        print("[SUCCESS] 成功添加 content_type 字段到 publish_records 表")
    
    print("\n[SUCCESS] 数据库迁移完成！")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"[ERROR] 迁移失败: {str(e)}")
        sys.exit(1)
