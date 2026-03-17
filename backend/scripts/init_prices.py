"""
初始化积分价格和会员价格配置
运行方式: python -m scripts.init_prices
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.credit import CreditPrice, MembershipPrice, MembershipType


def init_credit_prices(db: Session):
    """初始化积分价格套餐（1元=100积分）"""
    
    # 检查是否已有数据
    existing = db.query(CreditPrice).count()
    if existing > 0:
        print(f"积分价格套餐已存在 {existing} 条记录，跳过初始化")
        return
    
    credit_prices = [
        {
            "name": "10元套餐",
            "amount": 10.00,
            "credits": 1000,
            "bonus_credits": 0,
            "is_active": True,
            "sort_order": 1,
            "description": "1000积分，适合轻度使用"
        },
        {
            "name": "50元套餐",
            "amount": 50.00,
            "credits": 5000,
            "bonus_credits": 200,
            "is_active": True,
            "sort_order": 2,
            "description": "5000积分+赠送200积分"
        },
        {
            "name": "100元套餐",
            "amount": 100.00,
            "credits": 10000,
            "bonus_credits": 500,
            "is_active": True,
            "sort_order": 3,
            "description": "10000积分+赠送500积分，超值推荐"
        },
        {
            "name": "200元套餐",
            "amount": 200.00,
            "credits": 20000,
            "bonus_credits": 1500,
            "is_active": True,
            "sort_order": 4,
            "description": "20000积分+赠送1500积分，性价比最高"
        },
    ]
    
    for price_data in credit_prices:
        price = CreditPrice(**price_data)
        db.add(price)
    
    db.commit()
    print(f"成功初始化 {len(credit_prices)} 个积分价格套餐")


def init_membership_prices(db: Session):
    """初始化会员价格套餐"""
    
    # 检查是否已有数据
    existing = db.query(MembershipPrice).count()
    if existing > 0:
        print(f"会员价格套餐已存在 {existing} 条记录，跳过初始化")
        return
    
    membership_prices = [
        {
            "name": "月度会员",
            "membership_type": MembershipType.MONTHLY,
            "amount": 29.00,
            "original_amount": 39.00,
            "duration_days": 30,
            "is_active": True,
            "sort_order": 1,
            "description": "适合尝试体验",
            "features": '["所有AI创作工具不限次数", "不消耗积分", "基础客服支持"]'
        },
        {
            "name": "季度会员",
            "membership_type": MembershipType.QUARTERLY,
            "amount": 79.00,
            "original_amount": 117.00,
            "duration_days": 90,
            "is_active": True,
            "sort_order": 2,
            "description": "省38元，性价比之选",
            "features": '["所有AI创作工具不限次数", "不消耗积分", "优先客服支持", "新功能优先体验"]'
        },
        {
            "name": "年度会员",
            "membership_type": MembershipType.YEARLY,
            "amount": 299.00,
            "original_amount": 468.00,
            "duration_days": 365,
            "is_active": True,
            "sort_order": 3,
            "description": "省169元，长期用户首选",
            "features": '["所有AI创作工具不限次数", "不消耗积分", "专属客服经理", "新功能优先体验", "定制化服务支持"]'
        },
    ]
    
    for price_data in membership_prices:
        price = MembershipPrice(**price_data)
        db.add(price)
    
    db.commit()
    print(f"成功初始化 {len(membership_prices)} 个会员价格套餐")


def main():
    """主函数"""
    print("开始初始化积分和会员价格配置...")
    
    db = SessionLocal()
    try:
        init_credit_prices(db)
        init_membership_prices(db)
        print("初始化完成！")
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
