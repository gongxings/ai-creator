"""
数据库迁移脚本：为 ai_models 表添加 capabilities 字段
运行方式：python -m scripts.add_capabilities_column
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, SessionLocal


def add_capabilities_column():
    """添加 capabilities 列到 ai_models 表"""
    db = SessionLocal()
    try:
        # 检查列是否已存在
        result = db.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'ai_models' 
            AND column_name = 'capabilities'
        """))
        row = result.fetchone()
        
        if row and row[0] > 0:
            print("列 'capabilities' 已存在，跳过添加")
        else:
            # 添加列（不设默认值，某些 MySQL 版本不支持 JSON 列默认值）
            db.execute(text("""
                ALTER TABLE ai_models 
                ADD COLUMN capabilities JSON NULL 
                COMMENT '模型能力列表(text/image/video/audio)'
            """))
            db.commit()
            print("成功添加 'capabilities' 列到 ai_models 表")
        
        # 更新所有 NULL 值为默认的 ["text"]
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text"]' 
            WHERE capabilities IS NULL
        """))
        db.commit()
        print("已更新 NULL 值为默认 [\"text\"]")
        
        # 更新现有记录，根据 provider 设置默认能力
        # OpenAI 支持 text 和 image
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text", "image"]' 
            WHERE provider = 'openai' AND capabilities = '["text"]'
        """))
        
        # 智谱 AI 支持 text, image, video
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text", "image", "video"]' 
            WHERE provider = 'zhipu' AND capabilities = '["text"]'
        """))
        
        # 阿里通义支持 text, image, video
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text", "image", "video"]' 
            WHERE provider IN ('ali', 'qwen') AND capabilities = '["text"]'
        """))
        
        # 百度文心支持 text, image
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text", "image"]' 
            WHERE provider = 'baidu' AND capabilities = '["text"]'
        """))
        
        # 火山引擎/豆包支持 text, image, video
        db.execute(text("""
            UPDATE ai_models SET capabilities = '["text", "image", "video"]' 
            WHERE provider = 'doubao' AND capabilities = '["text"]'
        """))
        
        db.commit()
        print("已根据 provider 更新模型的 capabilities 字段")
        
    except Exception as e:
        db.rollback()
        print(f"迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("开始数据库迁移...")
    add_capabilities_column()
    print("迁移完成！")
