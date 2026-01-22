"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.ai_model import AIModel
from app.models.creation import Creation
from app.models.creation_version import CreationVersion
from app.models.platform import Platform
from app.models.platform_account import PlatformAccount
from app.models.publish_record import PublishRecord
from app.core.security import get_password_hash


def init_database():
    """初始化数据库"""
    print("🔧 开始初始化数据库...")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    # 创建所有表
    print("📝 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")
    
    # 创建默认管理员用户
    from sqlalchemy.orm import Session
    db = Session(engine)
    
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("👤 创建默认管理员用户...")
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                is_superuser=True,
                is_active=True,
                daily_quota=1000,
            )
            db.add(admin)
            db.commit()
            print("✅ 管理员用户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
        else:
            print("ℹ️  管理员用户已存在")
        
        # 创建默认AI模型配置
        print("🤖 创建默认AI模型配置...")
        models_data = [
            {
                "name": "GPT-4",
                "provider": "openai",
                "model_id": "gpt-4",
                "api_endpoint": "https://api.openai.com/v1/chat/completions",
                "description": "OpenAI GPT-4模型",
                "is_active": True,
            },
            {
                "name": "GPT-3.5 Turbo",
                "provider": "openai",
                "model_id": "gpt-3.5-turbo",
                "api_endpoint": "https://api.openai.com/v1/chat/completions",
                "description": "OpenAI GPT-3.5 Turbo模型",
                "is_active": True,
            },
            {
                "name": "Claude 3",
                "provider": "anthropic",
                "model_id": "claude-3-opus-20240229",
                "api_endpoint": "https://api.anthropic.com/v1/messages",
                "description": "Anthropic Claude 3模型",
                "is_active": False,
            },
        ]
        
        for model_data in models_data:
            existing_model = db.query(AIModel).filter(
                AIModel.model_id == model_data["model_id"]
            ).first()
            if not existing_model:
                model = AIModel(**model_data)
                db.add(model)
        
        db.commit()
        print("✅ AI模型配置创建成功")
        
        # 创建默认平台配置
        print("🌐 创建默认平台配置...")
        platforms_data = [
            {
                "name": "微信公众号",
                "platform_type": "wechat",
                "description": "微信公众号平台",
                "is_active": True,
            },
            {
                "name": "小红书",
                "platform_type": "xiaohongshu",
                "description": "小红书平台",
                "is_active": True,
            },
            {
                "name": "抖音",
                "platform_type": "douyin",
                "description": "抖音平台",
                "is_active": True,
            },
            {
                "name": "快手",
                "platform_type": "kuaishou",
                "description": "快手平台",
                "is_active": True,
            },
            {
                "name": "今日头条",
                "platform_type": "toutiao",
                "description": "今日头条平台",
                "is_active": True,
            },
            {
                "name": "知乎",
                "platform_type": "zhihu",
                "description": "知乎平台",
                "is_active": True,
            },
        ]
        
        for platform_data in platforms_data:
            existing_platform = db.query(Platform).filter(
                Platform.platform_type == platform_data["platform_type"]
            ).first()
            if not existing_platform:
                platform = Platform(**platform_data)
                db.add(platform)
        
        db.commit()
        print("✅ 平台配置创建成功")
        
        print("\n🎉 数据库初始化完成！")
        print("\n📌 下一步:")
        print("1. 配置 .env 文件中的数据库连接和API密钥")
        print("2. 启动后端服务: cd backend && python -m app.main")
        print("3. 启动前端服务: cd frontend && npm run dev")
        print("4. 访问 http://localhost:5173 开始使用")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
