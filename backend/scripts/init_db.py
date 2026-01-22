"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base
from app.models.user import User
from app.models.ai_model import AIModel
from app.models.creation import Creation
from app.models.publish import PlatformAccount, PublishRecord
from app.models.credit import (
    CreditTransaction,
    MembershipOrder,
    RechargeOrder,
    CreditPrice,
    MembershipPrice
)
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
from datetime import datetime


def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")
    
    # 创建数据库会话
    db = Session(bind=engine)
    
    try:
        # 检查是否已有数据
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠ 数据库已有数据，跳过初始化")
            return
        
        # 创建测试用户
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password=get_password_hash("test123456"),
            credits=100,  # 初始积分
            is_member=False
        )
        db.add(test_user)
        db.flush()
        print("✓ 测试用户创建完成")
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123456"),
            is_admin=True,
            credits=1000,
            is_member=True,
            member_expired_at=datetime(2026, 12, 31)
        )
        db.add(admin_user)
        db.flush()
        print("✓ 管理员用户创建完成")
        
        # 创建AI模型配置
        models = [
            AIModel(
                name="GPT-4",
                provider="openai",
                model_id="gpt-4",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
            AIModel(
                name="GPT-3.5 Turbo",
                provider="openai",
                model_id="gpt-3.5-turbo",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
            AIModel(
                name="Claude 3 Opus",
                provider="anthropic",
                model_id="claude-3-opus-20240229",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
            AIModel(
                name="文心一言",
                provider="baidu",
                model_id="ernie-bot-4",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
            AIModel(
                name="智谱AI",
                provider="zhipu",
                model_id="glm-4",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
            AIModel(
                name="通义千问",
                provider="qwen",
                model_id="qwen-max",
                api_key="",
                is_active=True,
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ),
        ]
        
        for model in models:
            db.add(model)
        db.flush()
        print("✓ AI模型配置创建完成")
        
        # 创建积分价格配置
        credit_prices = [
            CreditPrice(
                amount=10,
                price=1.00,
                bonus=0,
                is_active=True,
                sort_order=1
            ),
            CreditPrice(
                amount=100,
                price=10.00,
                bonus=10,
                is_active=True,
                sort_order=2
            ),
            CreditPrice(
                amount=500,
                price=50.00,
                bonus=100,
                is_active=True,
                sort_order=3
            ),
            CreditPrice(
                amount=1000,
                price=100.00,
                bonus=300,
                is_active=True,
                sort_order=4
            ),
        ]
        
        for price in credit_prices:
            db.add(price)
        db.flush()
        print("✓ 积分价格配置创建完成")
        
        # 创建会员价格配置
        membership_prices = [
            MembershipPrice(
                membership_type="monthly",
                duration_days=30,
                price=9.90,
                original_price=19.90,
                is_active=True,
                sort_order=1
            ),
            MembershipPrice(
                membership_type="quarterly",
                duration_days=90,
                price=25.00,
                original_price=59.70,
                is_active=True,
                sort_order=2
            ),
            MembershipPrice(
                membership_type="yearly",
                duration_days=365,
                price=88.00,
                original_price=238.80,
                is_active=True,
                sort_order=3
            ),
        ]
        
        for price in membership_prices:
            db.add(price)
        db.flush()
        print("✓ 会员价格配置创建完成")
        
        # 提交事务
        db.commit()
        print("\n✓ 数据库初始化完成！")
        print("\n测试账号信息：")
        print("  普通用户 - 用户名: test_user, 密码: test123456, 积分: 100")
        print("  管理员 - 用户名: admin, 密码: admin123456, 积分: 1000, 会员至: 2026-12-31")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 数据库初始化失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
