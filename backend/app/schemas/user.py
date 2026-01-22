"""
用户Schema模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole, UserStatus


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "nickname": "测试用户"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123"
            }
        }


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 7200
            }
        }


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    daily_quota: int
    used_quota: int
    total_creations: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "nickname": "测试用户",
                "avatar": "https://example.com/avatar.jpg",
                "phone": "13800138000",
                "role": "user",
                "status": "active",
                "daily_quota": 100,
                "used_quota": 10,
                "total_creations": 50,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class UserUpdate(BaseModel):
    """用户更新请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "新昵称",
                "avatar": "https://example.com/new-avatar.jpg",
                "phone": "13800138000"
            }
        }


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }
