"""
AI模型管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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


@router.get("", response_model=List[AIModelResponse])
async def get_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取AI模型列表
    
    返回用户配置的所有AI模型
    """
    models = db.query(AIModel).filter(AIModel.user_id == current_user.id).all()
    return models


@router.get("/{model_id}", response_model=AIModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取AI模型详情
    """
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    return model


@router.post("", response_model=AIModelResponse)
async def create_model(
    model_data: AIModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    添加AI模型配置
    
    支持的提供商：openai, anthropic, zhipu, baidu, ali, tencent
    """
    # 检查是否已存在相同名称的模型
    existing = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.name == model_data.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="模型名称已存在")
    
    # 创建模型
    model = AIModel(
        user_id=current_user.id,
        **model_data.model_dump()
    )
    
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return model


@router.put("/{model_id}", response_model=AIModelResponse)
async def update_model(
    model_id: int,
    model_data: AIModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新AI模型配置
    """
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 检查名称是否与其他模型冲突
    if model_data.name and model_data.name != model.name:
        existing = db.query(AIModel).filter(
            AIModel.user_id == current_user.id,
            AIModel.name == model_data.name,
            AIModel.id != model_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="模型名称已存在")
    
    # 更新字段
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    
    return model


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除AI模型配置
    """
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
    """
    测试AI模型连接
    
    发送测试请求验证模型配置是否正确
    """
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    try:
        # 创建AI服务实例
        ai_service = AIServiceFactory.create_service(
            provider=model.provider,
            api_key=model.api_key,
            model_name=model.model_name,
            base_url=model.base_url
        )
        
        # 发送测试请求
        response = await ai_service.generate_text(
            prompt=test_data.prompt or "你好，请回复'测试成功'",
            max_tokens=50
        )
        
        return {
            "success": True,
            "message": "模型连接成功",
            "response": response
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"模型连接失败: {str(e)}",
            "response": None
        }


@router.post("/{model_id}/set-default")
async def set_default_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    设置默认模型
    
    将指定模型设置为默认使用的模型
    """
    model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 取消其他模型的默认状态
    db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_default == True
    ).update({"is_default": False})
    
    # 设置当前模型为默认
    model.is_default = True
    
    db.commit()
    
    return {"message": "已设置为默认模型"}
