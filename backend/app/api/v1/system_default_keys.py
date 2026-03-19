"""
系统默认APIKey管理接口
提供系统默认APIKey 的设置、取消、监控等功能
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.schemas.api_key import APIKeyResponse
from app.core.deps import get_db, get_current_admin_user
from app.services.api_key_service import APIKeyService
from app.schemas.common import success_response

router = APIRouter()


@router.post("/{key_id}/set-system-default")
def set_system_default(
    key_id: int,
    order: int = 99,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    将 API Key 设为系统默认
    
    **权限要求**: 管理员
    
    **参数**:
    - key_id: API Key ID
    - order: 排序值（数字越小越优先）
    
    **返回**:
    - 更新后的 API Key 信息
    """
    try:
        api_key = APIKeyService.set_system_default_api_key(
            db=db,
            key_id=key_id,
            user_id=current_user.id,
            order=order
        )
        
        return success_response(
            data={
                "id": api_key.id,
                "key_name": api_key.key_name,
                "is_system_default": api_key.is_system_default,
                "system_default_order": api_key.system_default_order,
                "provider": api_key.provider,
                "model_name": api_key.model_name
            },
            message="已成功设为系统默认API Key"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{key_id}/unset-system-default")
def unset_system_default(
    key_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    取消 API Key 的系统默认标记
    
    **权限要求**: 管理员
    
    **参数**:
    - key_id: API Key ID
    
    **返回**:
    - 更新后的 API Key 信息
    """
    try:
        api_key = APIKeyService.unset_system_default_api_key(
            db=db,
            key_id=key_id,
            user_id=current_user.id
        )
        
        return success_response(
            data={
                "id": api_key.id,
                "key_name": api_key.key_name,
                "is_system_default": api_key.is_system_default,
                "system_default_order": api_key.system_default_order
            },
            message="已取消系统默认标记"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/list")
def list_system_default_keys(
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有系统默认API Key 列表
    
    **权限要求**: 管理员
    
    **返回**:
    - 系统默认API Key 列表（按排序升序）
    """
    keys = APIKeyService.get_system_default_api_keys(db=db)
    
    data = []
    for key in keys:
        data.append({
            "id": key.id,
            "key_name": key.key_name,
            "key_display": f"{key.key_prefix}...{key.key_suffix}",
            "provider": key.provider,
            "model_name": key.model_name,
            "base_url": key.base_url,
            "system_default_order": key.system_default_order,
            "total_assigned_users": key.total_assigned_users,
            "is_active": key.is_active,
            "created_at": key.created_at
        })
    
    return success_response(
        data=data,
        total=len(data)
    )


@router.get("/{key_id}/usage-stats")
def get_key_usage_stats(
    key_id: int,
    days: int = 30,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取系统默认API Key 的使用统计
    
    **权限要求**: 管理员
    
    **参数**:
    - key_id: API Key ID
    - days: 统计天数（默认 30 天）
    
    **返回**:
    - 使用统计信息（总请求数、Token 数、用户分布等）
    """
    # 验证 API Key 存在且属于当前用户
    api_key = APIKeyService.get_api_key_by_id(db, key_id, current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key 不存在或无权访问"
        )
    
    stats = APIKeyService.get_user_usage_for_api_key(
        db=db,
        api_key_id=key_id,
        days=days
    )
    
    return success_response(data=stats)


@router.get("/{key_id}/decrypt")
def decrypt_api_key_endpoint(
    key_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    解密获取 API Key 明文（仅管理员可操作）
    
    **警告**: 此接口会返回完整的 API Key 明文，请谨慎使用
    
    **权限要求**: 管理员
    
    **返回**:
    - API Key 明文
    """
    try:
        # 验证 API Key 存在且属于当前用户
        api_key = APIKeyService.get_api_key_by_id(db, key_id, current_user.id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API Key 不存在或无权访问"
            )
        
        # 解密 API Key
        decrypted_key = APIKeyService.get_api_key_for_use(db, key_id)
        
        return success_response(
            data={"api_key": decrypted_key},
            message="解密成功，请妥善保管"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
