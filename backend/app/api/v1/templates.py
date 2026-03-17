"""
文章模板管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.template import ArticleTemplate
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    TemplateCloneRequest
)

router = APIRouter()


@router.get("", response_model=TemplateListResponse)
async def get_templates(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
    is_system: Optional[bool] = Query(None, description="筛选系统模板"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取模板列表
    
    返回系统模板 + 当前用户的自定义模板 + 公开的模板
    """
    # 构建查询条件：系统模板 OR 用户自己的模板 OR 公开模板
    query = db.query(ArticleTemplate).filter(
        or_(
            ArticleTemplate.is_system == True,
            ArticleTemplate.user_id == current_user.id,
            ArticleTemplate.is_public == True
        )
    )
    
    # 筛选系统模板
    if is_system is not None:
        query = query.filter(ArticleTemplate.is_system == is_system)
    
    # 搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                ArticleTemplate.name.like(search_pattern),
                ArticleTemplate.description.like(search_pattern)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 分页和排序（系统模板优先，然后按使用次数排序）
    templates = query.order_by(
        desc(ArticleTemplate.is_system),
        desc(ArticleTemplate.use_count),
        desc(ArticleTemplate.created_at)
    ).offset(skip).limit(limit).all()
    
    return TemplateListResponse(total=total, items=templates)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取模板详情
    """
    template = db.query(ArticleTemplate).filter(
        ArticleTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查访问权限：系统模板、公开模板、或自己的模板
    if not template.is_system and not template.is_public and template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此模板")
    
    return template


@router.post("", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建自定义模板
    """
    # 检查名称是否已存在（同一用户下）
    existing = db.query(ArticleTemplate).filter(
        ArticleTemplate.name == template_data.name,
        ArticleTemplate.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="模板名称已存在")
    
    # 创建模板
    template = ArticleTemplate(
        name=template_data.name,
        description=template_data.description,
        thumbnail=template_data.thumbnail,
        styles=template_data.styles,
        is_public=template_data.is_public,
        is_system=False,  # 用户创建的不是系统模板
        user_id=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新模板（仅限自己的模板）
    """
    template = db.query(ArticleTemplate).filter(
        ArticleTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 系统模板不能修改
    if template.is_system:
        raise HTTPException(status_code=403, detail="系统模板不能修改")
    
    # 只能修改自己的模板
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此模板")
    
    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除模板（仅限自己的模板）
    """
    template = db.query(ArticleTemplate).filter(
        ArticleTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 系统模板不能删除
    if template.is_system:
        raise HTTPException(status_code=403, detail="系统模板不能删除")
    
    # 只能删除自己的模板
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此模板")
    
    db.delete(template)
    db.commit()
    
    return {"message": "模板已删除"}


@router.post("/{template_id}/clone", response_model=TemplateResponse)
async def clone_template(
    template_id: int,
    clone_data: Optional[TemplateCloneRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    克隆模板为自定义模板
    """
    # 查找原模板
    original = db.query(ArticleTemplate).filter(
        ArticleTemplate.id == template_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查访问权限
    if not original.is_system and not original.is_public and original.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权克隆此模板")
    
    # 生成新名称
    new_name = clone_data.name if clone_data and clone_data.name else f"{original.name}-副本"
    
    # 检查名称是否已存在
    existing = db.query(ArticleTemplate).filter(
        ArticleTemplate.name == new_name,
        ArticleTemplate.user_id == current_user.id
    ).first()
    
    if existing:
        # 自动添加数字后缀
        base_name = new_name
        counter = 1
        while existing:
            new_name = f"{base_name}({counter})"
            existing = db.query(ArticleTemplate).filter(
                ArticleTemplate.name == new_name,
                ArticleTemplate.user_id == current_user.id
            ).first()
            counter += 1
    
    # 创建克隆
    cloned = ArticleTemplate(
        name=new_name,
        description=original.description,
        thumbnail=original.thumbnail,
        styles=original.styles,
        is_public=False,  # 克隆的模板默认不公开
        is_system=False,
        user_id=current_user.id
    )
    
    db.add(cloned)
    db.commit()
    db.refresh(cloned)
    
    return cloned


@router.post("/{template_id}/use")
async def use_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    记录模板使用（增加使用次数）
    """
    template = db.query(ArticleTemplate).filter(
        ArticleTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 增加使用次数
    template.use_count = (template.use_count or 0) + 1
    db.commit()
    
    return {"message": "使用次数已更新", "use_count": template.use_count}
