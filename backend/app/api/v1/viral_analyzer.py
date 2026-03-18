"""
爆款模仿 API
分析爆款文章风格并生成类似内容
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.ai_model import AIModel
from app.utils.deps import get_current_user
from app.schemas.viral_analyzer import (
    AnalyzeRequest,
    AnalyzeResponse,
    ImitateRequest,
    ImitateResponse,
)
from app.services.viral_analyzer_service import ViralAnalyzerService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/elements")
async def get_viral_elements():
    """
    获取爆款元素列表
    
    无需登录即可访问
    """
    elements = [
        {"key": key, "name": key, "description": desc}
        for key, desc in ViralAnalyzerService.VIRAL_ELEMENTS.items()
    ]
    return {"elements": elements}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分析爆款内容
    
    深度分析爆款文章的成功要素，包括：
    - 爆款元素识别与评分
    - 内容类别判断
    - 结构与风格分析
    - 写作技巧提取
    - 改进建议
    
    - 需要登录
    - 消耗 AI 调用额度
    """
    # 获取用户的默认 AI 模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True,
        AIModel.model_type == "text",
    ).first()
    
    if not ai_model:
        raise HTTPException(
            status_code=400,
            detail="请先配置 AI 模型才能使用爆款分析功能"
        )
    
    try:
        result = await ViralAnalyzerService.analyze(
            request=request,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"爆款分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/imitate", response_model=ImitateResponse)
async def imitate_content(
    request: ImitateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    模仿爆款生成内容
    
    参考爆款文章的风格，围绕新主题创作类似内容。
    
    支持：
    - 调整风格模仿强度
    - 保持或调整文章结构
    - 添加额外创作要求
    
    - 需要登录
    - 消耗 AI 调用额度
    - 生成的内容会保存为新的创作记录
    """
    # 获取用户的默认 AI 模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True,
        AIModel.model_type == "text",
    ).first()
    
    if not ai_model:
        raise HTTPException(
            status_code=400,
            detail="请先配置 AI 模型才能使用爆款模仿功能"
        )
    
    try:
        result = await ViralAnalyzerService.imitate(
            request=request,
            db=db,
            user_id=current_user.id,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"爆款模仿失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
