"""
图库搜索 API
提供图库搜索、关键词建议等功能
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ai_model import AIModel
from app.models.user import User
from app.schemas.image_stock import (
    ImageSource,
    ImageOrientation,
    ImageSearchRequest,
    ImageSearchResponse,
    KeywordSuggestRequest,
    KeywordSuggestResponse,
)
from app.services.image_stock_service import ImageStockService
from app.utils.deps import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sources")
async def get_sources_status():
    """
    获取图库源配置状态
    
    无需登录即可访问
    """
    return ImageStockService.get_sources_status()


@router.get("/search", response_model=ImageSearchResponse)
async def search_images(
    query: str = Query(..., description="搜索关键词", min_length=1, max_length=100),
    source: Optional[ImageSource] = Query(None, description="图库来源（不指定则搜索全部）"),
    orientation: Optional[ImageOrientation] = Query(None, description="图片方向"),
    page: int = Query(1, description="页码", ge=1),
    per_page: int = Query(20, description="每页数量", ge=1, le=30),
    color: Optional[str] = Query(None, description="主色调（仅 Unsplash 支持）"),
):
    """
    搜索图库
    
    无需登录即可使用基础搜索功能
    
    支持的图库：
    - unsplash: Unsplash 高质量图库
    - pexels: Pexels 免费图库
    
    图片方向：
    - landscape: 横向
    - portrait: 纵向
    - square: 正方形
    """
    request = ImageSearchRequest(
        query=query,
        source=source,
        orientation=orientation,
        page=page,
        per_page=per_page,
        color=color,
    )
    
    try:
        result = await ImageStockService.search(request)
        return result
    except Exception as e:
        logger.error(f"图库搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=ImageSearchResponse)
async def search_images_post(request: ImageSearchRequest):
    """
    搜索图库（POST 方式）
    
    适合复杂搜索条件
    """
    try:
        result = await ImageStockService.search(request)
        return result
    except Exception as e:
        logger.error(f"图库搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-keywords", response_model=KeywordSuggestResponse)
async def suggest_keywords(
    request: KeywordSuggestRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    根据文章内容建议搜索关键词
    
    AI 分析文章内容，生成适合图库搜索的关键词
    
    - 需要登录使用 AI 分析（消耗 AI 调用额度）
    - 未登录用户返回基础关键词提取结果
    """
    ai_model = None
    
    if current_user:
        ai_model = db.query(AIModel).filter(
            AIModel.user_id == current_user.id,
            AIModel.is_active == True,
            
        ).first()
    
    try:
        result = await ImageStockService.suggest_keywords(
            request=request,
            ai_model=ai_model,
        )
        return result
    except Exception as e:
        logger.error(f"关键词建议失败: {e}")
        # 返回默认关键词
        return ImageStockService._get_default_keywords(request.content)
