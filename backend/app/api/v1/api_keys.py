"""
API Key管理接口
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models import User
from app.schemas.api_key import (
    APIKeyCreate, APIKeyResponse, APIKeyCreateResponse,
    APIKeyUpdate, APIKeyStatsResponse
)
from app.schemas.common import success_response, error_response
from app.services.api_key_service import APIKeyService

router = APIRouter()


@router.post("")
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的API Key
    
    - **key_name**: Key名称
    - **expires_days**: 过期天数（可选，1-365天）
    - **rate_limit**: 速率限制（次/分钟，默认60）
    - **allowed_models**: 允许使用的模型列表（可选，为空表示全部）
    """
    try:
        result = APIKeyService.create_api_key(db, current_user.id, key_data)
        return success_response(data=result, message="API Key创建成功，请妥善保管，仅此一次显示")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建API Key失败: {str(e)}"
        )


@router.get("")
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有API Key列表
    """
    try:
        keys = APIKeyService.get_user_api_keys(db, current_user.id)
        return success_response(data=keys)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API Key列表失败: {str(e)}"
        )


@router.get("/{key_id}")
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定API Key的详情
    """
    try:
        db_key = APIKeyService.get_api_key_by_id(db, key_id, current_user.id)
        if not db_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API Key不存在"
            )
        
        key_display = f"sk-****...****{db_key.id:04d}"
        
        return success_response(data={
            "id": db_key.id,
            "key_name": db_key.key_name,
            "key_display": key_display,
            "is_active": db_key.is_active,
            "rate_limit": db_key.rate_limit,
            "allowed_models": db_key.allowed_models,
            "total_requests": db_key.total_requests,
            "total_tokens": db_key.total_tokens,
            "last_used_at": db_key.last_used_at,
            "expires_at": db_key.expires_at,
            "created_at": db_key.created_at
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API Key失败: {str(e)}"
        )


@router.put("/{key_id}")
async def update_api_key(
    key_id: int,
    update_data: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新API Key
    
    - **key_name**: Key名称（可选）
    - **is_active**: 是否激活（可选）
    - **rate_limit**: 速率限制（可选）
    - **allowed_models**: 允许使用的模型列表（可选）
    """
    try:
        result = APIKeyService.update_api_key(db, key_id, current_user.id, update_data)
        return success_response(data=result, message="API Key更新成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新API Key失败: {str(e)}"
        )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除API Key
    """
    try:
        result = APIKeyService.delete_api_key(db, key_id, current_user.id)
        return success_response(data=result, message="API Key删除成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除API Key失败: {str(e)}"
        )


@router.get("/{key_id}/stats")
async def get_api_key_stats(
    key_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取API Key使用统计
    
    - **limit**: 最近日志数量（默认10条）
    """
    try:
        stats = APIKeyService.get_api_key_stats(db, key_id, current_user.id, limit)
        return success_response(data=stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
