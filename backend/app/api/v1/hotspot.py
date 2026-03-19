"""
热点追踪 API
提供热点列表获取、AI 选题建议等功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.ai_model import AIModel
from app.utils.deps import get_current_user, get_current_user_optional
from app.schemas.hotspot import (
    HotspotListResponse,
    PlatformInfo,
    PlatformListResponse,
    CategoryInfo,
    CategoryListResponse,
    TopicSuggestRequest,
    TopicSuggestResponse,
)
from app.services.hotspot_service import HotspotService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories():
    """
    获取热点分类列表
    
    无需登录即可访问
    """
    categories = HotspotService.get_categories()
    return CategoryListResponse(categories=categories)


@router.get("/platforms", response_model=PlatformListResponse)
async def get_platforms():
    """
    获取支持的热点平台列表
    
    无需登录即可访问
    """
    platforms = HotspotService.get_platforms()
    return PlatformListResponse(platforms=platforms)


@router.get("/list", response_model=HotspotListResponse)
async def get_hot_list(
    platform: str = Query(..., description="平台代码，如 weibo, baidu, zhihu 等"),
    limit: int = Query(20, ge=1, le=50, description="返回数量，默认20，最大50"),
    type: Optional[str] = Query(None, description="子类型，如百度的 realtime/car/game/movie/novel/teleplay"),
):
    """
    获取指定平台的热点列表
    
    无需登录即可访问
    
    支持的平台分类：
    - social: 社交媒体（微博、抖音、快手、B站、A站）
    - news: 新闻资讯（百度、头条、澎湃、新浪、网易、腾讯）
    - tech: 科技数码（36氪、IT之家、少数派、酷安等）
    - dev: 开发者（GitHub、掘金、CSDN、V2EX等）
    - knowledge: 知识社区（知乎、贴吧、豆瓣、简书等）
    - game: 游戏动漫（米游社、原神、NGA等）
    - entertainment: 影音娱乐（豆瓣电影、微信读书、虎扑等）
    - international: 国际媒体（TheVerge、TechCrunch、纽约时报等）
    - other: 其他（吾爱破解、虎嗅、气象预警等）
    
    百度支持子类型（type参数）：
    - realtime: 热搜（默认）
    - car: 汽车
    - game: 游戏
    - movie: 电影
    - novel: 小说
    - teleplay: 电视剧
    """
    try:
        result = await HotspotService.get_hot_list(platform=platform, limit=limit, subtype=type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取热点列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi", response_model=List[HotspotListResponse])
async def get_multi_platform_hot_list(
    platforms: str = Query(
        "weibo,baidu,zhihu",
        description="平台代码，多个用逗号分隔"
    ),
    limit: int = Query(10, ge=1, le=20, description="每个平台返回数量"),
):
    """
    获取多个平台的热点列表
    
    无需登录即可访问
    """
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
    
    if not platform_list:
        raise HTTPException(status_code=400, detail="请指定至少一个平台")
    
    if len(platform_list) > 10:
        raise HTTPException(status_code=400, detail="最多同时查询10个平台")
    
    results = []
    for platform in platform_list:
        try:
            result = await HotspotService.get_hot_list(platform=platform, limit=limit)
            results.append(result)
        except ValueError:
            # 跳过不支持的平台
            logger.warning(f"跳过不支持的平台: {platform}")
            continue
        except Exception as e:
            logger.error(f"获取 {platform} 热点失败: {e}")
            continue
    
    return results


@router.post("/suggest", response_model=TopicSuggestResponse)
async def get_topic_suggestions(
    request: TopicSuggestRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    根据热点生成 AI 选题建议
    
    需要登录才能使用 AI 分析功能（会消耗 AI 调用额度）
    未登录用户返回默认建议
    """
    ai_model = None
    
    if current_user:
        # 获取用户的默认 AI 模型
        ai_model = db.query(AIModel).filter(
            AIModel.user_id == current_user.id,
            AIModel.is_active == True,
            
        ).first()
    
    try:
        result = await HotspotService.get_topic_suggestions(
            hot_title=request.hot_title,
            user_domain=request.user_domain,
            target_platforms=request.target_platforms,
            ai_model=ai_model,
            db=db,
        )
        return result
    except Exception as e:
        logger.error(f"获取选题建议失败: {e}")
        # 返回默认建议而不是抛出异常
        return HotspotService._get_default_suggestions(
            hot_title=request.hot_title,
            target_platforms=request.target_platforms,
        )
