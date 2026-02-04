"""
安全认证模块
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(subject: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 用户ID
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: int) -> str:
    """
    创建刷新令牌
    
    Args:
        subject: 用户ID
        
    Returns:
        str: JWT令牌
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    解码令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 解码后的数据
        
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        print(f"Token decoded successfully: {payload}")
        return payload
    except JWTError as e:
        print(f"Token decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    
    Args:
        credentials: HTTP认证凭证
        db: 数据库会话
        
    Returns:
        User: 当前用户
        
    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户
        
    Raises:
        HTTPException: 用户未激活
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户未激活"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前管理员用户
        
    Raises:
        HTTPException: 权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user
