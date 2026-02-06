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
        query = query.filter(Creation.creation_type == content_type)
    
    # 工具类型筛选
    if tool_type:
        query = query.filter(Creation.creation_type == tool_type)
    
    # 搜索功能
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Creation.title.like(search_pattern),
                Creation.output_content.like(search_pattern)
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
        title=creation_data.title,
        creation_type=creation_data.content_type,
        output_content=creation_data.content,
        input_data=creation_data.input_data,
        extra_data=creation_data.extra_data
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
    if creation_data.content and creation_data.content != creation.output_content:
        from app.models.creation import CreationVersion
        new_version = CreationVersion(
            creation_id=creation.id,
            version_number=creation.version_count + 1,
            content=creation.output_content
        )
        db.add(new_version)
        creation.version_count = creation.version_count + 1
    
    # 更新字段
    if creation_data.title is not None:
        creation.title = creation_data.title
    if creation_data.content is not None:
        creation.output_content = creation_data.content
    if creation_data.extra_data is not None:
        creation.extra_data = creation_data.extra_data
    
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
    from app.models.creation import CreationVersion
    
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    versions = db.query(CreationVersion).filter(
        CreationVersion.creation_id == creation_id
    ).order_by(CreationVersion.version_number).all()
    
    return versions


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
    from app.models.creation import CreationVersion
    
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="创作记录不存在")
    
    target_version = db.query(CreationVersion).filter(
        CreationVersion.creation_id == creation_id,
        CreationVersion.version_number == version
    ).first()
    
    if not target_version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 保存当前版本到历史
    current_version = CreationVersion(
        creation_id=creation.id,
        version_number=creation.version_count + 1,
        content=creation.output_content
    )
    db.add(current_version)
    
    # 恢复到指定版本
    creation.output_content = target_version.content
    creation.version_count = creation.version_count + 1
    
    db.commit()
    db.refresh(creation)
    
    return {"message": f"已恢复到版本 {version}"}
