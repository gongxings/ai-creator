"""
数据库初始化脚本
创建数据库表并插入初始数据
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import engine, Base
from app.models.user import User
from app.models.ai_model import AIModel
from app.models.creation import Creation, CreationVersion
from app.models.publish import PlatformAccount, PublishRecord
from app.core.security import get_password_hash


def init_database():
    """初始化数据库"""
    print("开始创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库表创建完成！")
    print("\n数据库初始化成功！")
    print("您可以开始使用系统了。")
    print("\n提示：请通过管理后台添加AI模型配置和平台账号。")


if __name__ == "__main__":
    init_database()
