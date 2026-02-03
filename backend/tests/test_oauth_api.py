"""
OAuth API测试
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestOAuthAPI:
    """OAuth API测试类"""
    
    def test_get_platforms(self, client, auth_headers, test_platform):
        """测试获取平台列表API"""
        response = client.get(
            "/api/v1/oauth/platforms",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]) > 0
        assert any(p["platform_id"] == test_platform.platform_id for p in data["data"])
    
    def test_get_platform_detail(self, client, auth_headers, test_platform):
        """测试获取平台详情API"""
        response = client.get(
            f"/api/v1/oauth/platforms/{test_platform.platform_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["platform_id"] == test_platform.platform_id
    
    def test_get_user_accounts(self, client, auth_headers, test_oauth_account):
        """测试获取用户账号列表API"""
        response = client.get(
            "/api/v1/oauth/accounts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]) > 0
    
    def test_get_account_detail(self, client, auth_headers, test_oauth_account):
        """测试获取账号详情API"""
        response = client.get(
            f"/api/v1/oauth/accounts/{test_oauth_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == test_oauth_account.id
    
    @patch('app.services.oauth.playwright_service.PlaywrightService.launch_browser')
    def test_start_oauth_flow(self, mock_launch, client, auth_headers, test_platform):
        """测试启动OAuth流程API"""
        mock_launch.return_value = {
            "screenshot": "base64_screenshot_data",
            "cookies": []
        }
        
        response = client.post(
            "/api/v1/oauth/start",
            headers=auth_headers,
            json={
                "platform_id": test_platform.platform_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "session_id" in data["data"]
    
    @patch('app.services.oauth.playwright_service.PlaywrightService.perform_action')
    def test_perform_oauth_action(self, mock_action, client, auth_headers):
        """测试执行OAuth操作API"""
        mock_action.return_value = {
            "screenshot": "base64_screenshot_data",
            "success": True
        }
        
        response = client.post(
            "/api/v1/oauth/action",
            headers=auth_headers,
            json={
                "session_id": "test_session",
                "action": "click",
                "selector": "button[type='submit']"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    @patch('app.services.oauth.playwright_service.PlaywrightService.get_cookies')
    def test_complete_oauth_flow(self, mock_cookies, client, auth_headers, test_platform):
        """测试完成OAuth流程API"""
        mock_cookies.return_value = [
            {"name": "session_id", "value": "test_123", "domain": ".example.com"}
        ]
        
        response = client.post(
            "/api/v1/oauth/complete",
            headers=auth_headers,
            json={
                "session_id": "test_session",
                "platform_id": test_platform.platform_id,
                "account_name": "测试账号"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "account_id" in data["data"]
    
    def test_delete_account(self, client, auth_headers, test_oauth_account):
        """测试删除账号API"""
        response = client.delete(
            f"/api/v1/oauth/accounts/{test_oauth_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_check_account_validity(self, client, auth_headers, test_oauth_account):
        """测试检查账号有效性API"""
        with patch('app.services.oauth.oauth_service.OAuthService.check_account_validity') as mock_check:
            mock_check.return_value = True
            
            response = client.post(
                f"/api/v1/oauth/accounts/{test_oauth_account.id}/check",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            assert data["data"]["is_valid"] is True
    
    def test_unauthorized_access(self, client, test_platform):
        """测试未授权访问"""
        response = client.get("/api/v1/oauth/platforms")
        assert response.status_code == 401
    
    def test_get_nonexistent_platform(self, client, auth_headers):
        """测试获取不存在的平台"""
        response = client.get(
            "/api/v1/oauth/platforms/nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_nonexistent_account(self, client, auth_headers):
        """测试获取不存在的账号"""
        response = client.get(
            "/api/v1/oauth/accounts/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestLiteLLMProxy:
    """LiteLLM代理测试类"""
    
    @patch('litellm.completion')
    def test_chat_completion(self, mock_completion, client, auth_headers, test_oauth_account):
        """测试聊天完成API"""
        mock_completion.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "这是AI的回复"
                    }
                }
            ],
            "usage": {
                "total_tokens": 100
            }
        }
        
        response = client.post(
            "/api/v1/oauth/chat/completions",
            headers=auth_headers,
            json={
                "account_id": test_oauth_account.id,
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "test-model"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "choices" in data["data"]
    
    def test_chat_completion_invalid_account(self, client, auth_headers):
        """测试使用无效账号的聊天完成"""
        response = client.post(
            "/api/v1/oauth/chat/completions",
            headers=auth_headers,
            json={
                "account_id": 99999,
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "model": "test-model"
            }
        )
        
        assert response.status_code == 404
