"""
测试数据库模型
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.ai_model import AIModel
from app.models.creation import Creation
from app.models.publish import PublishRecord
from app.models.credit import CreditTransaction, MembershipOrder
from app.models.operation import Activity, ActivityParticipation, Coupon, UserCoupon, ReferralRecord, OperationStatistics
from app.models.oauth_account import OAuthAccount
from app.models.platform_config import PlatformConfig
from app.core.security import get_password_hash, verify_password


class TestUserModel:
    """测试用户模型"""
    
    def test_create_user(self, db_session):
        """测试创建用户"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.created_at is not None
        assert verify_password("password123", user.hashed_password)
    
    def test_user_unique_username(self, db_session):
        """测试用户名唯一性"""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="testuser",
            email="test2@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_unique_email(self, db_session):
        """测试邮箱唯一性"""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="testuser2",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_default_values(self, db_session):
        """测试用户默认值"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.credits == 0
        assert user.membership_level == "free"
        assert user.membership_expires_at is None


class TestAIModelModel:
    """测试AI模型配置模型"""
    
    def test_create_ai_model(self, db_session, test_user):
        """测试创建AI模型配置"""
        model = AIModel(
            user_id=test_user.id,
            name="GPT-4",
            provider="openai",
            model_name="gpt-4",
            api_key="sk-test123",
            is_active=True,
            is_default=True
        )
        db_session.add(model)
        db_session.commit()
        db_session.refresh(model)
        
        assert model.id is not None
        assert model.user_id == test_user.id
        assert model.name == "GPT-4"
        assert model.provider == "openai"
        assert model.is_active is True
        assert model.is_default is True
    
    def test_ai_model_with_base_url(self, db_session, test_user):
        """测试带自定义URL的AI模型"""
        model = AIModel(
            user_id=test_user.id,
            name="Custom Model",
            provider="custom",
            model_name="custom-model",
            api_key="test-key",
            base_url="https://api.custom.com/v1"
        )
        db_session.add(model)
        db_session.commit()
        db_session.refresh(model)
        
        assert model.base_url == "https://api.custom.com/v1"


class TestCreationModel:
    """测试创作记录模型"""
    
    def test_create_creation(self, db_session, test_user):
        """测试创建创作记录"""
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="测试文章",
            content="这是测试内容",
            prompt="写一篇关于AI的文章",
            status="completed"
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        assert creation.id is not None
        assert creation.user_id == test_user.id
        assert creation.tool_type == "wechat_article"
        assert creation.title == "测试文章"
        assert creation.status == "completed"
    
    def test_creation_with_metadata(self, db_session, test_user):
        """测试带元数据的创作记录"""
        metadata = {
            "word_count": 1000,
            "keywords": ["AI", "技术"],
            "seo_score": 85
        }
        creation = Creation(
            user_id=test_user.id,
            tool_type="wechat_article",
            title="测试文章",
            content="内容",
            prompt="提示词",
            metadata=metadata
        )
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        
        assert creation.metadata == metadata
        assert creation.metadata["word_count"] == 1000


class TestPublishModel:
    """测试发布记录模型"""
    
    def test_create_publish_record(self, db_session, test_user):
        """测试创建发布记录"""
        record = PublishRecord(
            user_id=test_user.id,
            creation_id=1,
            platform="wechat",
            title="测试文章",
            content="内容",
            status="pending"
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.id is not None
        assert record.platform == "wechat"
        assert record.status == "pending"
    
    def test_publish_record_with_result(self, db_session, test_user):
        """测试带发布结果的记录"""
        result = {
            "url": "https://mp.weixin.qq.com/s/xxx",
            "article_id": "12345"
        }
        record = PublishRecord(
            user_id=test_user.id,
            creation_id=1,
            platform="wechat",
            title="测试",
            content="内容",
            status="success",
            publish_result=result
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.publish_result == result
        assert record.status == "success"


class TestCreditModel:
    """测试积分模型"""
    
    def test_create_credit_transaction(self, db_session, test_user):
        """测试创建积分交易"""
        transaction = CreditTransaction(
            user_id=test_user.id,
            amount=100,
            transaction_type="recharge",
            description="充值积分"
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        
        assert transaction.id is not None
        assert transaction.amount == 100
        assert transaction.transaction_type == "recharge"
    
    def test_create_membership_order(self, db_session, test_user):
        """测试创建会员订单"""
        order = MembershipOrder(
            user_id=test_user.id,
            membership_level="premium",
            duration_days=30,
            amount=99.00,
            status="pending"
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        assert order.id is not None
        assert order.membership_level == "premium"
        assert order.duration_days == 30
        assert order.amount == 99.00


class TestOperationModel:
    """测试运营功能模型"""
    
    def test_create_activity(self, db_session):
        """测试创建活动"""
        from datetime import datetime, timedelta
        activity = Activity(
            title="测试活动",
            activity_type="credit_gift",
            status="active",
            description="测试活动描述",
            rules={"gift_amount": 100},
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=7)
        )
        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)
        
        assert activity.id is not None
        assert activity.title == "测试活动"
        assert activity.activity_type == "credit_gift"
    
    def test_create_coupon(self, db_session):
        """测试创建优惠券"""
        from datetime import datetime, timedelta
        coupon = Coupon(
            code="TEST2024",
            name="测试优惠券",
            coupon_type="recharge_discount",
            discount_type="percent",
            discount_value=10.0,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=30)
        )
        db_session.add(coupon)
        db_session.commit()
        db_session.refresh(coupon)
        
        assert coupon.id is not None
        assert coupon.code == "TEST2024"
        assert coupon.coupon_type == "recharge_discount"


class TestOAuthModels:
    """测试OAuth相关模型"""
    
    def test_create_platform_config(self, db_session):
        """测试创建平台配置"""
        config = PlatformConfig(
            platform_id="test_platform",
            platform_name="测试平台",
            description="测试用",
            oauth_config={"auth_url": "https://test.com"},
            litellm_config={"provider": "test"},
            quota_config={"daily_limit": 1000},
            is_enabled=True
        )
        db_session.add(config)
        db_session.commit()
        db_session.refresh(config)
        
        assert config.platform_id == "test_platform"
        assert config.is_enabled is True
    
    def test_create_oauth_account(self, db_session, test_user, test_platform):
        """测试创建OAuth账号"""
        account = OAuthAccount(
            user_id=test_user.id,
            platform_id=test_platform.platform_id,
            account_name="测试账号",
            encrypted_cookies="encrypted_data",
            is_active=True
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.platform_id == test_platform.platform_id
        assert account.is_active is True
