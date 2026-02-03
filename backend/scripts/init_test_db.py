"""
测试数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pymysql
from app.core.config import settings


def create_test_database():
    """创建测试数据库"""
    # 从配置中提取数据库连接信息
    db_url = settings.DATABASE_URL
    # mysql+pymysql://root:password@localhost:3306/ai_creator
    parts = db_url.split('/')
    db_name = parts[-1]
    base_url = '/'.join(parts[:-1]) + '/'
    
    # 测试数据库名称
    test_db_name = db_name + "_test"
    
    connection = None
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password',
            port=3306
        )
        
        with connection.cursor() as cursor:
            # 删除可能存在的测试数据库
            cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
            # 创建新的测试数据库
            cursor.execute(f"CREATE DATABASE {test_db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
        connection.commit()
        print(f"✓ 测试数据库 '{test_db_name}' 创建成功")
        
        # 更新测试环境变量
        test_db_url = base_url + test_db_name
        os.environ['TEST_DATABASE_URL'] = test_db_url
        print(f"✓ 测试数据库URL设置为: {test_db_url}")
        
    except Exception as e:
        print(f"✗ 创建测试数据库失败: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_test_database()