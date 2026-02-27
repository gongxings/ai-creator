# -*- coding: utf-8 -*-
"""
Pytest配置文件
"""
import os
import sys
from pathlib import Path

# 在导入任何 app 模块之前设置测试配置
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["LOG_LEVEL"] = "ERROR"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入 app.core.config 并修改 DATABASE_URL
from app.core import config
original_db_url = config.settings.DATABASE_URL
config.settings.DATABASE_URL = "sqlite:///./test.db"

from app.core.database import Base, get_db
from app.models.user import User
from app.models.platform_config import PlatformConfig
from app.models.oauth_account import OAuthAccount

# 延迟导入 app
from app.main import app


# 测试数据库URL - 使用内存数据库避免文件锁问题
import uuid


def get_test_db_url():
    """生成唯一的测试数据库URL"""
    return f"sqlite:///./test_{uuid.uuid4().hex[:8]}.db"


@pytest.fixture(scope="function")
def engine():
    """创建测试数据库引擎"""
    test_db_url = get_test_db_url()
    test_engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False}
    )
    
    # 修复 SQLite BigInteger 自增问题 - 预先修改 Base 元数据中的列类型
    from sqlalchemy import BigInteger, Integer
    
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, BigInteger) and column.primary_key:
                column.type = Integer()
                column.autoincrement = True
    
    # 清除所有已存在的表（防止之前的索引残留）
    Base.metadata.drop_all(bind=test_engine)
    # 重新创建所有表
    Base.metadata.create_all(bind=test_engine)
    
    # 替换 app 的数据库引擎
    import app.core.database as db_module
    original_engine = db_module.engine
    original_session = db_module.SessionLocal
    db_module.engine = test_engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    yield test_engine
    
    # 恢复原始引擎
    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    
    # 清理
    test_engine.dispose()
    # 删除测试数据库文件
    db_path = test_db_url.replace("sqlite:///", "")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass  # 忽略文件删除错误


@pytest.fixture(scope="function")
def db_session(engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    from app.core.security import get_password_hash
    from app.models.user import UserStatus
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_platform(db_session):
    """创建测试平台配置"""
    platform = PlatformConfig(
        platform_id="test_platform",
        platform_name="测试平台",
        description="用于测试的平台",
        oauth_config={
            "auth_url": "https://test.example.com",
            "login_selectors": {
                "username_input": "input[name='username']",
                "password_input": "input[name='password']",
                "submit_button": "button[type='submit']",
            },
            "cookie_names": ["session_id"],
        },
        litellm_config={
            "provider": "test",
            "api_base": "https://api.test.example.com",
            "default_model": "test-model",
            "available_models": ["test-model"],
        },
        quota_config={
            "daily_limit": 1000,
            "rate_limit": 10,
        },
        is_enabled=True,
    )
    db_session.add(platform)
    db_session.commit()
    db_session.refresh(platform)
    return platform


@pytest.fixture
def test_oauth_account(db_session, test_user, test_platform):
    """创建测试OAuth账号"""
    from app.services.oauth.encryption import encrypt_data
    
    cookies = {"session_id": "test_session_123"}
    encrypted_credentials = encrypt_data(cookies, settings.ENCRYPTION_KEY)
    
    account = OAuthAccount(
        user_id=test_user.id,
        platform=test_platform.platform_id,
        account_name="测试账号",
        credentials=encrypted_credentials,
        is_active=True,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        }
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_playwright():
    """Mock Playwright"""
    from unittest.mock import AsyncMock, MagicMock
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_url = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot")
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.cookies = AsyncMock(return_value=[
        {"name": "session_id", "value": "test_session_123", "domain": ".example.com"}
    ])
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    
    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    return mock_playwright
