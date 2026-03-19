"""
管理员用户管理接口
提供用户列表、详情、模型管理等功能
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.core.deps import get_db, get_current_admin_user
from app.services.api_key_service import APIKeyService
from app.schemas.common import success_response

router = APIRouter()


@router.get("/list")
def get_user_list(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取用户列表（分页）
    
    **权限要求**: 管理员
    
    **参数**:
    - page: 页码（默认 1）
    - page_size: 每页数量（默认 20）
    - keyword: 搜索关键词（用户名/邮箱）
    
    **返回**:
    - 用户列表及分页信息
    """
    query = db.query(models.User)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (models.User.username.like(f"%{keyword}%")) |
            (models.User.email.like(f"%{keyword}%"))
        )
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    users = query.order_by(models.User.created_at.desc()).offset(offset).limit(page_size).all()
    
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "status": user.status,
            "credits": user.credits,
            "is_member": user.is_member,
            "total_creations": user.total_creations,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at
        })
    
    return success_response(
        data={
            "users": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取用户详情（包含 AIModel 和使用统计）
    
    **权限要求**: 管理员
    
    **参数**:
    - user_id: 用户 ID
    
    **返回**:
    - 用户详细信息、模型列表、使用统计
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取用户的 AIModel 列表
    ai_models = db.query(models.AIModel).filter(
        models.AIModel.user_id == user_id
    ).all()
    
    models_data = []
    for model in ai_models:
        models_data.append({
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
            "model_name": model.model_name,
            "is_default": model.is_default,
            "is_active": model.is_active,
            "system_default_source": model.system_default_source,
            "source_api_key_id": model.source_api_key_id,
            "created_at": model.created_at
        })
    
    # 统计用户的 API 使用情况
    usage_stats = db.query(
        func.count(models.APIKeyUsageLog.id).label('total_requests'),
        func.sum(models.APIKeyUsageLog.total_tokens).label('total_tokens')
    ).filter(
        models.APIKeyUsageLog.used_by_user_id == user_id
    ).first()
    
    return success_response(
        data={
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "phone": user.phone,
                "role": user.role,
                "status": user.status,
                "credits": user.credits,
                "daily_quota": user.daily_quota,
                "used_quota": user.used_quota,
                "total_creations": user.total_creations,
                "is_member": user.is_member,
                "member_expired_at": user.member_expired_at,
                "last_login_at": user.last_login_at,
                "last_login_ip": user.last_login_ip,
                "created_at": user.created_at,
                "referral_code": user.referral_code
            },
            "ai_models": models_data,
            "usage_stats": {
                "total_requests": usage_stats.total_requests or 0,
                "total_tokens": usage_stats.total_tokens or 0
            }
        }
    )


@router.post("/{user_id}/reset-models")
def reset_user_models(
    user_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    重置用户模型为当前系统默认
    
    **权限要求**: 管理员
    
    **说明**:
    - 删除用户所有来源于系统默认的模型
    - 重新分配当前的系统默认模型
    - 保留用户自定义的模型
    
    **参数**:
    - user_id: 用户 ID
    
    **返回**:
    - 新分配的模型列表
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户所有系统默认来源的模型
    db.query(models.AIModel).filter(
        models.AIModel.user_id == user_id,
        models.AIModel.system_default_source == True
    ).delete()
    
    db.commit()
    
    # 重新分配系统默认模型
    new_models = APIKeyService.assign_system_default_models_to_user(
        db=db,
        user_id=user_id
    )
    
    models_data = []
    for model in new_models:
        models_data.append({
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
            "model_name": model.model_name,
            "system_default_source": model.system_default_source
        })
    
    return success_response(
        data={"models": models_data},
        message=f"已为用户重置模型，共分配 {len(new_models)} 个系统默认模型"
    )


@router.post("/{user_id}/toggle-model-status")
def toggle_model_status(
    user_id: int,
    model_id: int,
    is_active: bool,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    切换用户模型的启用/禁用状态
    
    **权限要求**: 管理员
    
    **参数**:
    - user_id: 用户 ID
    - model_id: 模型 ID
    - is_active: 是否启用
    
    **返回**:
    - 更新后的模型信息
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    model = db.query(models.AIModel).filter(
        models.AIModel.id == model_id,
        models.AIModel.user_id == user_id
    ).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    # 检查是否是系统默认模型
    if model.system_default_source and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用系统默认模型"
        )
    
    model.is_active = is_active
    db.commit()
    db.refresh(model)
    
    return success_response(
        data={
            "id": model.id,
            "name": model.name,
            "is_active": model.is_active
        },
        message=f"模型已{'启用' if is_active else '禁用'}"
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除用户（软删除）
    
    **权限要求**: 管理员
    
    **警告**: 此操作会删除用户及其所有相关数据
    
    **参数**:
    - user_id: 用户 ID
    
    **返回**:
    - 删除结果
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    # 软删除
    from datetime import datetime
    user.deleted_at = datetime.now()
    user.status = "inactive"
    db.commit()
    
    return success_response(message="用户已成功删除")
