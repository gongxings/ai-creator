"""
创作记录管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.creation import Creation
from app.schemas.creation import (
    CreationCreate,
    CreationUpdate,
    CreationResponse,
    CreationListResponse,
    CreationVersionResponse
)

router = APIRouter()


@router.get("", response_model=CreationListResponse)
async def get_creations(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    content_type: Optional[str] = Query(None, description="内容类型筛选"),
    tool_type: Optional[str] = Query(None, description="工具类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取创作列表
    
    支持分页、筛选和搜索功能
    """
    # 构建查询
    query = db.query(Creation).filter(Creation.user_id == current_user.id)
    
    # 内容类型筛选
    if content_type:
        query = query.filter(Creation.content_type == content_type)
    
    # 工具类型筛选
    if tool_type:
        query = query.filter(Creation.tool_type == tool_type)
    
    # 搜索功能
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Creation.title.like(search_pattern),
                Creation.content.like(search_pattern)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 分页和排序
    creations = query.order_by(desc(Creation.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": creations
    }


@router.get("/{creation_id}", response_model=CreationResponse)
async def get_creation(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取创作详情
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    return creation


@router.post("", response_model=CreationResponse)
async def create_creation(
    creation_data: CreationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建创作记录
    """
    creation = Creation(
        user_id=current_user.id,
        **creation_data.model_dump()
    )
    
    db.add(creation)
    db.commit()
    db.refresh(creation)
    
    return creation


@router.put("/{creation_id}", response_model=CreationResponse)
async def update_creation(
    creation_id: int,
    creation_data: CreationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新创作内容
    
    支持部分更新，只更新提供的字段
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    # 保存版本历史
    if creation_data.content and creation_data.content != creation.content:
        if not creation.version_history:
            creation.version_history = []
        
        creation.version_history.append({
            "version": len(creation.version_history) + 1,
            "content": creation.content,
            "updated_at": creation.updated_at.isoformat()
        })
    
    # 更新字段
    update_data = creation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(creation, field, value)
    
    db.commit()
    db.refresh(creation)
    
    return creation


@router.delete("/{creation_id}")
async def delete_creation(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除创作记录（软删除）
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    # 软删除
    db.delete(creation)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/{creation_id}/versions", response_model=List[CreationVersionResponse])
async def get_creation_versions(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取创作的版本历史
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    if not creation.version_history:
        return []
    
    return creation.version_history


@router.post("/{creation_id}/restore/{version}")
async def restore_creation_version(
    creation_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    恢复到指定版本
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    if not creation.version_history or version > len(creation.version_history):
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 保存当前版本到历史
    creation.version_history.append({
        "version": len(creation.version_history) + 1,
        "content": creation.content,
        "updated_at": creation.updated_at.isoformat()
    })
    
    # 恢复到指定版本
    target_version = creation.version_history[version - 1]
    creation.content = target_version["content"]
    
    db.commit()
    db.refresh(creation)
    
    return {"message": f"已恢复到版本 {version}"}
