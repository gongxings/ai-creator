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
from app.models.credit import TransactionType
from app.schemas.user import (
    TokenResponse,
    UserRegister,
    UserLogin,
    UserResponse,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.common import success_response
from app.services.credit_service import CreditService

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
    
    # 新用户注册赠送1000积分
    try:
        CreditService.add_credits(
            db=db,
            user_id=user.id,
            amount=1000,
            transaction_type=TransactionType.REWARD,
            description="新用户注册奖励"
        )
    except Exception as e:
        # 赠送积分失败不影响注册流程
        import logging
        logging.error(f"新用户注册赠送积分失败: {e}")
    
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


@router.post("/password-reset/request")
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    请求密码重置（发送重置令牌）
    
    由于当前未集成邮件服务，此接口会直接返回重置令牌。
    生产环境应通过邮件发送令牌。
    """
    from jose import jwt
    from datetime import datetime, timedelta
    
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # 为防止邮箱枚举攻击，即使用户不存在也返回成功
        return success_response(message="如果该邮箱已注册，重置链接已发送")
    
    # 生成重置令牌（有效期30分钟）
    reset_token = jwt.encode(
        {
            "sub": str(user.id),
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(minutes=30),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    # TODO: 集成邮件服务后，通过邮件发送重置链接
    # 当前开发阶段直接返回令牌
    return success_response(
        data={"reset_token": reset_token},
        message="密码重置令牌已生成（开发模式下直接返回令牌）"
    )


@router.post("/password-reset/confirm")
def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Any:
    """
    确认密码重置
    """
    from jose import JWTError, jwt
    
    try:
        payload = jwt.decode(
            reset_confirm.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的重置令牌",
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的重置令牌",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌已过期或无效",
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    user.password_hash = get_password_hash(reset_confirm.new_password)
    db.commit()
    
    return success_response(message="密码重置成功，请使用新密码登录")
