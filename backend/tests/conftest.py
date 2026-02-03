"""
Pytest配置文件
"""
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.platform_config import PlatformConfig
from app.models.oauth_account import OAuthAccount


# 测试数据库URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # 删除测试数据库文件
    if os.path.exists("./test.db"):
        os.remove("./test.db")


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
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
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
    encrypted_cookies = encrypt_data(cookies, settings.ENCRYPTION_KEY)
    
    account = OAuthAccount(
        user_id=test_user.id,
        platform_id=test_platform.platform_id,
        account_name="测试账号",
        encrypted_cookies=encrypted_cookies,
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
