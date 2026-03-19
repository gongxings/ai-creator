"""
爆款标题生成 API
提供标题生成、优化、分析功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.ai_model import AIModel
from app.utils.deps import get_current_user, get_current_user_optional
from app.schemas.title import (
    TitleGenerateRequest,
    TitleGenerateResponse,
    TitleOptimizeRequest,
    TitleOptimizeResponse,
    TitleAnalyzeRequest,
    TitleAnalyzeResponse,
    TitleStyle,
    PlatformType,
)
from app.services.title_service import TitleService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/styles")
async def get_title_styles():
    """
    获取支持的标题风格列表
    
    无需登录即可访问
    """
    styles = [
        {
            "value": style.value,
            "label": TitleService.STYLE_DESCRIPTIONS.get(style, style.value),
        }
        for style in TitleStyle
    ]
    return {"styles": styles}


@router.get("/platforms")
async def get_platforms():
    """
    获取支持的目标平台列表
    
    无需登录即可访问
    """
    platforms = [
        {
            "value": pt.value,
            "label": TitleService.PLATFORM_FEATURES.get(pt, {}).get("name", pt.value),
            "max_length": TitleService.PLATFORM_FEATURES.get(pt, {}).get("max_length", 50),
            "tips": TitleService.PLATFORM_FEATURES.get(pt, {}).get("tips", []),
        }
        for pt in PlatformType
    ]
    return {"platforms": platforms}


@router.post("/generate", response_model=TitleGenerateResponse)
async def generate_titles(
    request: TitleGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    生成爆款标题
    
    根据内容主题生成多个风格的爆款标题。
    
    - 需要登录使用 AI 生成（消耗 AI 调用额度）
    - 未登录用户返回基础模板标题
    """
    ai_model = None
    
    if current_user:
        # 获取用户的默认 AI 模型
        ai_model = db.query(AIModel).filter(
            AIModel.user_id == current_user.id,
            AIModel.is_active == True,
            
        ).first()
    
    try:
        result = await TitleService.generate_titles(
            request=request,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"标题生成失败: {e}")
        # 返回兜底标题
        return TitleService._get_fallback_titles(request)


@router.post("/optimize", response_model=TitleOptimizeResponse)
async def optimize_title(
    request: TitleOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    优化现有标题
    
    分析原标题的问题，并生成多个优化版本。
    
    - 需要登录
    - 消耗 AI 调用额度
    """
    # 获取用户的默认 AI 模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True,
        
    ).first()
    
    if not ai_model:
        raise HTTPException(
            status_code=400,
            detail="请先配置 AI 模型才能使用标题优化功能"
        )
    
    try:
        result = await TitleService.optimize_title(
            request=request,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"标题优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=TitleAnalyzeResponse)
async def analyze_title(
    request: TitleAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分析标题质量
    
    深度分析标题的优缺点，识别使用的钩子技巧，给出改进建议。
    
    - 需要登录
    - 消耗 AI 调用额度
    """
    # 获取用户的默认 AI 模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True,
        
    ).first()
    
    if not ai_model:
        raise HTTPException(
            status_code=400,
            detail="请先配置 AI 模型才能使用标题分析功能"
        )
    
    try:
        result = await TitleService.analyze_title(
            request=request,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"标题分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
