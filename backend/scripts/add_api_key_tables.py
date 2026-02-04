# -*- coding: utf-8 -*-
"""
添加API Key相关表的数据库迁移脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models.api_key import APIKey, APIKeyUsageLog

def create_tables():
    """创建API Key相关表"""
    print("开始创建API Key相关表...")
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[
            APIKey.__table__,
            APIKeyUsageLog.__table__
        ])
        print("[OK] 表创建成功")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_name IN ('api_keys', 'api_key_usage_logs')"
            ))
            tables = [row[0] for row in result]
            
            if 'api_keys' in tables:
                print("[OK] api_keys 表已创建")
            else:
                print("[ERROR] api_keys 表创建失败")
                
            if 'api_key_usage_logs' in tables:
                print("[OK] api_key_usage_logs 表已创建")
            else:
                print("[ERROR] api_key_usage_logs 表创建失败")
        
        print("\n数据库迁移完成！")
        
    except Exception as e:
        print("[ERROR] 创建表失败: {}".format(str(e)))
        raise

if __name__ == "__main__":
    create_tables()
