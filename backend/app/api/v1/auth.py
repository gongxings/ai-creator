"""
认证相关API路由
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserRegister,
    UserLogin,
    UserResponse,
    PasswordChange,
)
from app.schemas.common import success_response

router = APIRouter()


@router.post("/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> Any:
    """
    用户注册
    """
    # 检查用户名是否已存在
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 检查邮箱是否已存在
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        nickname=user_in.nickname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    """
    用户登录
    """
    # 查找用户
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    # 生成访问令牌和刷新令牌
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return success_response(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse.model_validate(user).model_dump()
    })


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> Any:
    """
    刷新访问令牌
    """
    from jose import JWTError, jwt
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )
    
    # 验证用户是否存在且活跃
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )
    
    # 生成新的访问令牌和刷新令牌
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return success_response(data={
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前用户信息
    """
    return success_response(data=UserResponse.model_validate(current_user).model_dump())


@router.put("/me")
def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    更新当前用户信息
    """
    if "nickname" in user_update:
        current_user.nickname = user_update["nickname"]
    
    if "avatar" in user_update:
        current_user.avatar = user_update["avatar"]
    
    if "phone" in user_update:
        current_user.phone = user_update["phone"]
    
    db.commit()
    db.refresh(current_user)
    
    return success_response(data=UserResponse.model_validate(current_user).model_dump())


@router.post("/change-password")
def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    修改密码
    """
    if not verify_password(password_change.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误",
        )
    
    current_user.password_hash = get_password_hash(password_change.new_password)
    db.commit()
    
    return success_response(message="密码修改成功")
