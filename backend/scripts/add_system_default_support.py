"""
数据库迁移脚本 - 添加系统默认APIKey支持
运行方式：python scripts/add_system_default_support.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, engine
from sqlalchemy import text


def add_api_key_columns():
    """为 api_keys 表添加新字段"""
    print("正在为 api_keys 表添加字段...")
    
    with engine.connect() as conn:
        # 添加系统默认标识字段
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN is_system_default BOOLEAN DEFAULT FALSE COMMENT '是否系统默认 Key'
            """))
            print("✓ 添加 is_system_default 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ is_system_default 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN system_default_order INTEGER DEFAULT 99 COMMENT '系统默认排序'
            """))
            print("✓ 添加 system_default_order 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ system_default_order 字段已存在")
            else:
                raise
        
        # 添加 AI Provider 信息
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN provider VARCHAR(50) COMMENT 'AI 提供商'
            """))
            print("✓ 添加 provider 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ provider 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN model_name VARCHAR(100) COMMENT '模型名称'
            """))
            print("✓ 添加 model_name 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ model_name 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN base_url VARCHAR(255) COMMENT 'API 基础 URL'
            """))
            print("✓ 添加 base_url 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ base_url 字段已存在")
            else:
                raise
        
        # 添加加密存储字段
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN encrypted_key TEXT COMMENT '加密存储的原始 APIKey'
            """))
            print("✓ 添加 encrypted_key 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ encrypted_key 字段已存在")
            else:
                raise
        
        # 添加统计字段
        try:
            conn.execute(text("""
                ALTER TABLE api_keys 
                ADD COLUMN total_assigned_users INTEGER DEFAULT 0 COMMENT '已分配用户数'
            """))
            print("✓ 添加 total_assigned_users 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ total_assigned_users 字段已存在")
            else:
                raise
        
        # 添加索引
        try:
            conn.execute(text("""
                CREATE INDEX idx_system_default ON api_keys(is_system_default, system_default_order)
            """))
            print("✓ 添加 idx_system_default 索引")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("⚠ idx_system_default 索引已存在")
            else:
                raise
        
        conn.commit()
        print("✅ api_keys 表迁移完成\n")


def add_ai_model_columns():
    """为 ai_models 表添加新字段"""
    print("正在为 ai_models 表添加字段...")
    
    with engine.connect() as conn:
        # 添加系统默认来源标识
        try:
            conn.execute(text("""
                ALTER TABLE ai_models 
                ADD COLUMN system_default_source BOOLEAN DEFAULT FALSE COMMENT '是否来源于系统默认APIKey'
            """))
            print("✓ 添加 system_default_source 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ system_default_source 字段已存在")
            else:
                raise
        
        try:
            conn.execute(text("""
                ALTER TABLE ai_models 
                ADD COLUMN source_api_key_id BIGINT COMMENT '来源的 APIKey ID'
            """))
            print("✓ 添加 source_api_key_id 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ source_api_key_id 字段已存在")
            else:
                raise
        
        # 添加索引
        try:
            conn.execute(text("""
                CREATE INDEX idx_system_default_user ON ai_models(system_default_source, user_id)
            """))
            print("✓ 添加 idx_system_default_user 索引")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("⚠ idx_system_default_user 索引已存在")
            else:
                raise
        
        conn.commit()
        print("✅ ai_models 表迁移完成\n")


def add_usage_log_columns():
    """为 api_key_usage_logs 表添加新字段"""
    print("正在为 api_key_usage_logs 表添加字段...")
    
    with engine.connect() as conn:
        # 添加 used_by_user_id 字段
        try:
            conn.execute(text("""
                ALTER TABLE api_key_usage_logs 
                ADD COLUMN used_by_user_id BIGINT COMMENT '实际使用用户 ID'
            """))
            print("✓ 添加 used_by_user_id 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ used_by_user_id 字段已存在")
            else:
                raise
        
        # 添加索引
        try:
            conn.execute(text("""
                CREATE INDEX idx_used_by_user ON api_key_usage_logs(used_by_user_id)
            """))
            print("✓ 添加 idx_used_by_user 索引")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("⚠ idx_used_by_user 索引已存在")
            else:
                raise
        
        conn.commit()
        print("✅ api_key_usage_logs 表迁移完成\n")


def main():
    """主函数"""
    print("=" * 60)
    print("开始数据库迁移 - 系统默认APIKey支持")
    print("=" * 60)
    print()
    
    try:
        # 执行迁移
        add_api_key_columns()
        add_ai_model_columns()
        add_usage_log_columns()
        
        print("=" * 60)
        print("✅ 所有迁移成功完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 迁移失败：{str(e)}")
        print("\n请检查：")
        print("1. 数据库连接配置是否正确")
        print("2. 数据库用户是否有 ALTER TABLE 权限")
        print("3. 表是否已经存在（如果是，需要先删除或跳过）")
        sys.exit(1)


if __name__ == "__main__":
    main()
