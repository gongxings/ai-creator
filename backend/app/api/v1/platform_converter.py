"""
多平台内容转换 API
提供内容转换、批量转换等功能
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.ai_model import AIModel
from app.utils.deps import get_current_user
from app.schemas.platform_converter import (
    TargetPlatform,
    PlatformInfo,
    ConvertRequest,
    ConvertResult,
    BatchConvertRequest,
    BatchConvertResult,
)
from app.services.platform_converter_service import PlatformConverterService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/platforms", response_model=List[PlatformInfo])
async def get_platforms():
    """
    获取支持的目标平台列表
    
    无需登录即可访问
    """
    return PlatformConverterService.get_platforms()


@router.get("/platforms/{platform}", response_model=PlatformInfo)
async def get_platform_info(platform: TargetPlatform):
    """
    获取指定平台的详细信息
    
    无需登录即可访问
    """
    info = PlatformConverterService.get_platform_info(platform)
    if not info:
        raise HTTPException(status_code=404, detail="平台不存在")
    return info


@router.post("/convert", response_model=ConvertResult)
async def convert_content(
    request: ConvertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    转换内容到目标平台
    
    将已有的创作内容转换为指定平台的格式。
    转换后会生成新的创作记录，并关联到原创作。
    
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
            detail="请先配置 AI 模型才能使用内容转换功能"
        )
    
    try:
        result = await PlatformConverterService.convert(
            request=request,
            db=db,
            user_id=current_user.id,
            ai_model=ai_model,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"内容转换失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-convert", response_model=BatchConvertResult)
async def batch_convert_content(
    request: BatchConvertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量转换内容到多个平台
    
    一次性将内容转换到多个目标平台。
    
    - 需要登录
    - 消耗 AI 调用额度（按平台数量计算）
    """
    if len(request.target_platforms) > 5:
        raise HTTPException(
            status_code=400,
            detail="单次最多转换到5个平台"
        )
    
    # 获取用户的默认 AI 模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True,
        AIModel.model_type == "text",
    ).first()
    
    if not ai_model:
        raise HTTPException(
            status_code=400,
            detail="请先配置 AI 模型才能使用内容转换功能"
        )
    
    try:
        result = await PlatformConverterService.batch_convert(
            request=request,
            db=db,
            user_id=current_user.id,
            ai_model=ai_model,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量转换失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
