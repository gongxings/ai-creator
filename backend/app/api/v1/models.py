"""
AI模型管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.ai_model import AIModel
from app.schemas.ai_model import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelTestRequest,
    AIModelTestResponse
)
from app.services.ai.factory import AIServiceFactory

router = APIRouter()


def _model_to_response(model: AIModel, is_admin: bool, current_user_id: int) -> AIModelResponse:
    """将模型转换为响应，自动计算 is_readonly"""
    data = AIModelResponse.model_validate(model)
    data.is_readonly = (model.is_system_builtin and not is_admin) or (
        model.is_system_builtin and model.user_id != current_user_id
    )
    return data


@router.get("", response_model=List[AIModelResponse])
async def get_models(
    capability: Optional[str] = Query(None, description="按能力筛选(text/image/video/audio)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取AI模型列表

    返回用户自己的模型 + 系统内置模型（所有用户可见）
    系统内置模型对普通用户标记为只读
    """
    is_admin = current_user.role == UserRole.ADMIN

    query = db.query(AIModel).filter(
        or_(
            AIModel.user_id == current_user.id,
            AIModel.is_system_builtin == True
        )
    )

    if capability:
        query = query.filter(AIModel.capabilities.contains([capability]))

    models = query.all()
    return [_model_to_response(m, is_admin, current_user.id) for m in models]


@router.get("/{model_id}", response_model=AIModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取AI模型详情"""
    is_admin = current_user.role == UserRole.ADMIN
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        or_(
            AIModel.user_id == current_user.id,
            AIModel.is_system_builtin == True
        )
    ).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    return _model_to_response(model, is_admin, current_user.id)


@router.post("", response_model=AIModelResponse)
async def create_model(
    model_data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    添加AI模型配置

    - 普通用户：is_system_builtin 强制为 False
    - 管理员：可设置 is_system_builtin 为 True（系统内置）
    """
    is_admin = current_user.role == UserRole.ADMIN

    if not is_admin:
        model_data.is_system_builtin = False

    existing = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.name == model_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="模型名称已存在")

    model = AIModel(
        user_id=current_user.id,
        **model_data.model_dump()
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return _model_to_response(model, is_admin, current_user.id)


@router.put("/{model_id}", response_model=AIModelResponse)
async def update_model(
    model_id: int,
    model_data: AIModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新AI模型配置

    - 普通用户：只能编辑自己的模型（is_readonly=True 的不可编辑）
    - 管理员：可编辑所有模型，但只有管理员可将 is_system_builtin 从 False 改为 True
    """
    is_admin = current_user.role == UserRole.ADMIN

    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        or_(
            AIModel.user_id == current_user.id,
            AIModel.is_system_builtin == True
        )
    ).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    if not is_admin and model.is_readonly:
        raise HTTPException(status_code=403, detail="无权限编辑此模型")

    update_data = model_data.model_dump(exclude_unset=True)

    if not is_admin:
        update_data.pop("is_system_builtin", None)

    if model.name and update_data.get("name") and update_data["name"] != model.name:
        existing = db.query(AIModel).filter(
            AIModel.user_id == current_user.id,
            AIModel.name == update_data["name"],
            AIModel.id != model_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="模型名称已存在")

    for field, value in update_data.items():
        setattr(model, field, value)

    db.commit()
    db.refresh(model)

    return _model_to_response(model, is_admin, current_user.id)


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除AI模型配置

    - 普通用户：只能删除自己的模型
    - 管理员：可删除所有模型
    """
    is_admin = current_user.role == UserRole.ADMIN

    if is_admin:
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
    else:
        model = db.query(AIModel).filter(
            AIModel.id == model_id,
            AIModel.user_id == current_user.id
        ).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    db.delete(model)
    db.commit()

    return {"message": "删除成功"}


@router.post("/{model_id}/test", response_model=AIModelTestResponse)
async def test_model(
    model_id: int,
    test_data: AIModelTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试AI模型连接"""
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        or_(
            AIModel.user_id == current_user.id,
            AIModel.is_system_builtin == True
        )
    ).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    try:
        ai_service = AIServiceFactory.create_service(
            provider=model.provider,
            api_key=model.api_key,
            model_name=model.model_name,
            base_url=model.base_url
        )

        response = await ai_service.generate_text(
            prompt=test_data.prompt or "你好，请回复'测试成功'",
            max_tokens=50
        )

        return AIModelTestResponse(
            success=True,
            message="模型连接成功",
            response=response
        )

    except Exception as e:
        return AIModelTestResponse(
            success=False,
            message=f"模型连接失败: {str(e)}",
            response=None
        )


@router.post("/{model_id}/set-default")
async def set_default_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    设置默认模型

    用户只能设置自己模型为默认
    """
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == current_user.id
    ).first()

    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_default == True
    ).update({"is_default": False})

    model.is_default = True

    db.commit()

    return {"message": "已设置为默认模型"}
