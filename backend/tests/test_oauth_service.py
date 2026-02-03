"""
OAuth服务测试
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.oauth.oauth_service import OAuthService
from app.services.oauth.encryption import encrypt_credentials, decrypt_credentials
from app.core.config import settings


class TestOAuthService:
    """OAuth服务测试类"""
    
    @pytest.mark.asyncio
    async def test_get_platforms(self, db_session, test_platform):
        """测试获取平台列表"""
        service = OAuthService(db_session)
        platforms = await service.get_platforms()
        
        assert len(platforms) > 0
        assert any(p.platform_id == test_platform.platform_id for p in platforms)
    
    @pytest.mark.asyncio
    async def test_get_platform_by_id(self, db_session, test_platform):
        """测试根据ID获取平台"""
        service = OAuthService(db_session)
        platform = await service.get_platform_by_id(test_platform.platform_id)
        
        assert platform is not None
        assert platform.platform_id == test_platform.platform_id
        assert platform.platform_name == test_platform.platform_name
    
    @pytest.mark.asyncio
    async def test_get_platform_by_id_not_found(self, db_session):
        """测试获取不存在的平台"""
        service = OAuthService(db_session)
        platform = await service.get_platform_by_id("nonexistent")
        
        assert platform is None
    
    @pytest.mark.asyncio
    async def test_get_user_accounts(self, db_session, test_user, test_oauth_account):
        """测试获取用户OAuth账号列表"""
        service = OAuthService(db_session)
        accounts = await service.get_user_accounts(test_user.id)
        
        assert len(accounts) > 0
        assert any(a.id == test_oauth_account.id for a in accounts)
    
    @pytest.mark.asyncio
    async def test_get_account_by_id(self, db_session, test_user, test_oauth_account):
        """测试根据ID获取OAuth账号"""
        service = OAuthService(db_session)
        account = await service.get_account_by_id(test_oauth_account.id, test_user.id)
        
        assert account is not None
        assert account.id == test_oauth_account.id
        assert account.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_account_by_id_wrong_user(self, db_session, test_oauth_account):
        """测试获取其他用户的OAuth账号"""
        service = OAuthService(db_session)
        account = await service.get_account_by_id(test_oauth_account.id, 99999)
        
        assert account is None
    
    @pytest.mark.asyncio
    async def test_create_account(self, db_session, test_user, test_platform):
        """测试创建OAuth账号"""
        service = OAuthService(db_session)
        cookies = {"session_id": "new_session_123"}
        
        account = await service.create_account(
            user_id=test_user.id,
            platform_id=test_platform.platform_id,
            account_name="新账号",
            cookies=cookies,
        )
        
        assert account is not None
        assert account.user_id == test_user.id
        assert account.platform_id == test_platform.platform_id
        assert account.account_name == "新账号"
        assert account.is_active is True
        
        # 验证Cookie加密
        decrypted = decrypt_credentials(account.encrypted_cookies)
        assert decrypted == cookies
    
    @pytest.mark.asyncio
    async def test_update_account_cookies(self, db_session, test_user, test_oauth_account):
        """测试更新OAuth账号Cookie"""
        service = OAuthService(db_session)
        new_cookies = {"session_id": "updated_session_456"}
        
        updated = await service.update_account_cookies(
            account_id=test_oauth_account.id,
            user_id=test_user.id,
            cookies=new_cookies,
        )
        
        assert updated is not None
        decrypted = decrypt_credentials(updated.encrypted_cookies)
        assert decrypted == new_cookies
    
    @pytest.mark.asyncio
    async def test_delete_account(self, db_session, test_user, test_oauth_account):
        """测试删除OAuth账号"""
        service = OAuthService(db_session)
        
        result = await service.delete_account(test_oauth_account.id, test_user.id)
        assert result is True
        
        # 验证账号已删除
        account = await service.get_account_by_id(test_oauth_account.id, test_user.id)
        assert account is None
    
    @pytest.mark.asyncio
    async def test_check_account_validity(self, db_session, test_user, test_oauth_account):
        """测试检查账号有效性"""
        service = OAuthService(db_session)
        
        with patch('app.services.oauth.oauth_service.OAuthService._test_cookies') as mock_test:
            mock_test.return_value = True
            
            result = await service.check_account_validity(
                test_oauth_account.id,
                test_user.id
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_account_cookies(self, db_session, test_user, test_oauth_account):
        """测试获取账号Cookie"""
        service = OAuthService(db_session)
        
        cookies = await service.get_account_cookies(
            test_oauth_account.id,
            test_user.id
        )
        
        assert cookies is not None
        assert "session_id" in cookies
        assert cookies["session_id"] == "test_session_123"


class TestEncryption:
    """加密解密测试类"""
    
    def test_encrypt_decrypt(self):
        """测试加密解密"""
        data = {"key": "value", "number": 123}
        
        encrypted = encrypt_credentials(data)
        assert encrypted != str(data)
        assert isinstance(encrypted, str)
        
        decrypted = decrypt_credentials(encrypted)
        assert decrypted == data
    
    def test_encrypt_decrypt_complex_data(self):
        """测试复杂数据加密解密"""
        data = {
            "cookies": [
                {"name": "session", "value": "abc123"},
                {"name": "token", "value": "xyz789"},
            ],
            "metadata": {
                "created_at": "2024-01-01",
                "expires_at": "2024-12-31",
            }
        }
        
        encrypted = encrypt_credentials(data)
        decrypted = decrypt_credentials(encrypted)
        
        assert decrypted == data
    
    def test_decrypt_invalid_data(self):
        """测试解密无效数据"""
        with pytest.raises(Exception):
            decrypt_credentials("invalid_encrypted_data")


@pytest.mark.asyncio
class TestPlaywrightService:
    """Playwright服务测试类"""
    
    async def test_launch_browser(self, mock_playwright):
        """测试启动浏览器"""
        from app.services.oauth.playwright_service import PlaywrightService
        
        with patch('app.services.oauth.playwright_service.async_playwright', return_value=mock_playwright):
            service = PlaywrightService()
            result = await service.launch_browser("https://test.example.com")
            
            assert result is not None
            assert "screenshot" in result
            assert "cookies" in result
    
    async def test_get_cookies(self, mock_playwright):
        """测试获取Cookie"""
        from app.services.oauth.playwright_service import PlaywrightService
        
        with patch('app.services.oauth.playwright_service.async_playwright', return_value=mock_playwright):
            service = PlaywrightService()
            await service.launch_browser("https://test.example.com")
            
            cookies = await service.get_cookies()
            
            assert cookies is not None
            assert len(cookies) > 0
            assert cookies[0]["name"] == "session_id"
