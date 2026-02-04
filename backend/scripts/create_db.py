"""
创建数据库脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings


def create_database():
    """创建数据库"""
    print("开始创建数据库...")
    
    # 从DATABASE_URL中提取数据库名称
    db_url = settings.DATABASE_URL
    db_name = db_url.split('/')[-1]
    
    # 创建不带数据库名的连接URL
    base_url = db_url.rsplit('/', 1)[0]
    
    print(f"连接到MySQL服务器: {base_url}")
    
    # 连接到MySQL服务器（不指定数据库）
    engine = create_engine(base_url)
    
    try:
        with engine.connect() as conn:
            # 创建数据库
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            print(f"[SUCCESS] Database '{db_name}' created successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    create_database()
