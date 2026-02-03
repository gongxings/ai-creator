"""
测试Pydantic模型
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user import (
    UserRegister, UserLogin, UserResponse, UserUpdate, PasswordChange
)
from app.schemas.ai_model import (
    AIModelCreate, AIModelUpdate, AIModelResponse, AIModelListResponse
)
from app.schemas.creation import (
    CreationGenerate, CreationUpdate, CreationResponse
)
from app.schemas.publish import (
    PublishCreate, PublishRecordResponse
)
from app.schemas.credit import (
    CreditRechargeRequest, MembershipPurchaseRequest
)
from app.schemas.common import Response, PaginationParams, PaginatedResponse


class TestUserSchemas:
    """测试用户相关Schema"""
    
    def test_user_register_valid(self):
        """测试有效的用户注册数据"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        schema = UserRegister(**data)
        assert schema.username == "testuser"
        assert schema.email == "test@example.com"
        assert schema.password == "password123"
    
    def test_user_register_invalid_email(self):
        """测试无效的邮箱格式"""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)
    
    def test_user_login_valid(self):
        """测试有效的登录数据"""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        schema = UserLogin(**data)
        assert schema.username == "testuser"
        assert schema.password == "password123"
    
    def test_user_update_partial(self):
        """测试部分更新用户数据"""
        data = {"email": "newemail@example.com"}
        schema = UserUpdate(**data)
        assert schema.email == "newemail@example.com"
        assert schema.username is None
    
    def test_password_change_valid(self):
        """测试有效的密码修改"""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123"
        }
        schema = PasswordChange(**data)
        assert schema.old_password == "oldpass123"
        assert schema.new_password == "newpass123"


class TestAIModelSchemas:
    """测试AI模型相关Schema"""
    
    def test_ai_model_create_valid(self):
        """测试创建AI模型配置"""
        data = {
            "name": "GPT-4",
            "provider": "openai",
            "model_name": "gpt-4",
            "api_key": "sk-test123"
        }
        schema = AIModelCreate(**data)
        assert schema.name == "GPT-4"
        assert schema.provider == "openai"
        assert schema.is_active is True  # 默认值
    
    def test_ai_model_create_with_base_url(self):
        """测试带自定义URL的模型配置"""
        data = {
            "name": "Custom",
            "provider": "custom",
            "model_name": "custom-model",
            "api_key": "test-key",
            "base_url": "https://api.custom.com"
        }
        schema = AIModelCreate(**data)
        assert schema.base_url == "https://api.custom.com"
    
    def test_ai_model_update_partial(self):
        """测试部分更新模型配置"""
        data = {"is_active": False}
        schema = AIModelUpdate(**data)
        assert schema.is_active is False
        assert schema.name is None
    
    def test_ai_model_list_response(self):
        """测试模型列表响应"""
        model_data = {
            "id": 1,
            "user_id": 1,
            "name": "GPT-4",
            "provider": "openai",
            "model_name": "gpt-4",
            "is_active": True,
            "is_default": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        model = AIModelResponse(**model_data)
        
        list_data = {
            "items": [model],
            "total": 1
        }
        schema = AIModelListResponse(**list_data)
        assert len(schema.items) == 1
        assert schema.total == 1


class TestCreationSchemas:
    """测试创作相关Schema"""
    
    def test_creation_generate_valid(self):
        """测试生成创作请求"""
        data = {
            "tool_type": "wechat_article",
            "prompt": "写一篇关于AI的文章",
            "parameters": {
                "tone": "professional",
                "length": "medium"
            }
        }
        schema = CreationGenerate(**data)
        assert schema.tool_type == "wechat_article"
        assert schema.prompt == "写一篇关于AI的文章"
        assert schema.parameters["tone"] == "professional"
    
    def test_creation_update_valid(self):
        """测试更新创作内容"""
        data = {
            "title": "新标题",
            "content": "新内容"
        }
        schema = CreationUpdate(**data)
        assert schema.title == "新标题"
        assert schema.content == "新内容"


class TestPublishSchemas:
    """测试发布相关Schema"""
    
    def test_publish_create_single_platform(self):
        """测试单平台发布请求"""
        data = {
            "creation_id": 1,
            "platform_account_ids": [1],
            "title": "测试文章",
            "content": "内容"
        }
        schema = PublishCreate(**data)
        assert schema.creation_id == 1
        assert len(schema.platform_account_ids) == 1
        assert 1 in schema.platform_account_ids
    
    def test_publish_create_multiple_platforms(self):
        """测试多平台发布请求"""
        data = {
            "creation_id": 1,
            "platform_account_ids": [1, 2, 3],
            "title": "测试文章",
            "content": "内容"
        }
        schema = PublishCreate(**data)
        assert len(schema.platform_account_ids) == 3
    
    def test_publish_create_with_schedule(self):
        """测试定时发布请求"""
        from datetime import timedelta
        schedule_time = datetime.utcnow() + timedelta(hours=1)
        data = {
            "creation_id": 1,
            "platform_account_ids": [1],
            "title": "测试",
            "content": "内容",
            "scheduled_at": schedule_time
        }
        schema = PublishCreate(**data)
        assert schema.scheduled_at == schedule_time
    
    def test_publish_create_invalid_schedule(self):
        """测试无效的定时发布时间"""
        from datetime import timedelta
        past_time = datetime.utcnow() - timedelta(hours=1)
        data = {
            "creation_id": 1,
            "platform_account_ids": [1],
            "title": "测试",
            "content": "内容",
            "scheduled_at": past_time
        }
        with pytest.raises(ValidationError):
            PublishCreate(**data)


class TestCreditSchemas:
    """测试积分相关Schema"""
    
    def test_credit_recharge_valid(self):
        """测试积分充值请求"""
        data = {
            "amount": 100,
            "payment_method": "alipay"
        }
        schema = CreditRechargeRequest(**data)
        assert schema.amount == 100
        assert schema.payment_method == "alipay"
    
    def test_credit_recharge_invalid_amount(self):
        """测试无效的充值金额"""
        data = {
            "amount": -10,
            "payment_method": "alipay"
        }
        with pytest.raises(ValidationError):
            CreditRechargeRequest(**data)
    
    def test_membership_purchase_valid(self):
        """测试会员购买请求"""
        data = {
            "membership_level": "premium",
            "duration_days": 30,
            "payment_method": "wechat"
        }
        schema = MembershipPurchaseRequest(**data)
        assert schema.membership_level == "premium"
        assert schema.duration_days == 30


class TestCommonSchemas:
    """测试通用Schema"""
    
    def test_response_success(self):
        """测试成功响应"""
        data = {"key": "value"}
        response = Response[dict](code=200, message="success", data=data)
        assert response.code == 200
        assert response.message == "success"
        assert response.data == data
    
    def test_response_error(self):
        """测试错误响应"""
        response = Response[None](code=400, message="Bad Request", data=None)
        assert response.code == 400
        assert response.message == "Bad Request"
        assert response.data is None
    
    def test_pagination_params_default(self):
        """测试分页参数默认值"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20
    
    def test_pagination_params_custom(self):
        """测试自定义分页参数"""
        params = PaginationParams(page=2, page_size=50)
        assert params.page == 2
        assert params.page_size == 50
    
    def test_paginated_response(self):
        """测试分页响应"""
        items = [{"id": 1}, {"id": 2}]
        response = PaginatedResponse[dict](
            items=items,
            total=100,
            page=1,
            page_size=20,
            total_pages=5
        )
        assert len(response.items) == 2
        assert response.total == 100
        assert response.total_pages == 5
