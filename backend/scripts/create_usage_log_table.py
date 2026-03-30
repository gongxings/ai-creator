"""
手动创建 ai_model_usage_logs 表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.model_usage_log import AIModelUsageLog
from sqlalchemy import text

print("开始创建 ai_model_usage_logs 表...")

try:
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()
    
    # 只创建这一个表
    AIModelUsageLog.__table__.create(bind=engine, checkfirst=True)
    
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    
    print("ai_model_usage_logs 表创建成功!")
    
    # 验证表是否存在
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES LIKE 'ai_model_usage_logs'"))
        if result.fetchone():
            print("验证通过: 表已存在")
        else:
            print("警告: 表可能未创建成功")
            
except Exception as e:
    print(f"创建表失败: {e}")
    import traceback
    traceback.print_exc()
