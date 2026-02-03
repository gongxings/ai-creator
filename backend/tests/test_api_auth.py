"""
测试认证API
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthAPI:
    """测试认证相关API"""
    
    def test_register_success(self, client):
        """测试成功注册"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_register_duplicate_username(self, client, test_user):
        """测试注册重复用户名"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client, test_user):
        """测试注册重复邮箱"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "anotheruser",
                "email": test_user.email,
                "password": "password123"
            }
        )
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_login_success(self, client, test_user):
        """测试成功登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
    
    def test_login_wrong_password(self, client, test_user):
        """测试错误密码"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """测试不存在的用户"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "username" in data["data"]
        assert "email" in data["data"]
    
    def test_get_current_user_unauthorized(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """测试无效token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_refresh_token(self, client, test_user):
        """测试刷新token"""
        # 先登录获取refresh_token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # 使用refresh_token获取新的access_token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
    
    def test_update_profile(self, client, auth_headers):
        """测试更新用户资料"""
        response = client.put(
            "/api/v1/auth/profile",
            headers=auth_headers,
            json={
                "email": "newemail@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "newemail@example.com"
    
    def test_change_password(self, client, auth_headers):
        """测试修改密码"""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "testpass123",
                "new_password": "newpass123"
            }
        )
        assert response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, auth_headers):
        """测试修改密码时旧密码错误"""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "wrongpass",
                "new_password": "newpass123"
            }
        )
        assert response.status_code == 400
