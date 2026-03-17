"""
插件系统 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.plugin import (
    PluginMarket,
    UserPlugin,
    CreationPluginSelection,
    PluginInvocation,
    PluginReview
)
from app.schemas.plugin import (
    # 插件市场
    PluginMarketResponse,
    PluginMarketListItem,
    PluginCategory,
    # 用户插件
    UserPluginInstall,
    UserPluginUpdate,
    UserPluginResponse,
    UserPluginListItem,
    # 插件选择
    PluginSelectionSave,
    PluginSelectionResponse,
    # 插件评价
    PluginReviewCreate,
    PluginReviewUpdate,
    PluginReviewResponse,
    # 创作时使用
    PluginForCreation,
    PluginStats,
)
from app.schemas.common import success_response, error_response
from app.services.plugins.registry import plugin_registry

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 插件市场 API ====================

@router.get("/market", summary="获取插件市场列表")
async def get_plugin_market(
    category: Optional[str] = Query(None, description="分类筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("download_count", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取插件市场列表
    
    - 支持分类筛选、关键词搜索
    - 返回用户是否已安装状态
    """
    # 构建查询
    query = db.query(PluginMarket).filter(
        PluginMarket.is_active == True,
        PluginMarket.is_approved == True
    )
    
    # 分类筛选
    if category:
        query = query.filter(PluginMarket.category == category)
    
    # 搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                PluginMarket.display_name.like(search_pattern),
                PluginMarket.description.like(search_pattern),
                PluginMarket.short_description.like(search_pattern),
            )
        )
    
    # 排序
    sort_column = getattr(PluginMarket, sort_by, PluginMarket.download_count)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # 获取总数
    total = query.count()
    
    # 分页
    plugins = query.offset(skip).limit(limit).all()
    
    # 获取用户已安装的插件
    user_installed = db.query(UserPlugin.plugin_name).filter(
        UserPlugin.user_id == current_user.id
    ).all()
    installed_names = {p.plugin_name for p in user_installed}
    
    # 构建响应
    items = []
    for plugin in plugins:
        item = PluginMarketListItem(
            id=plugin.id,
            name=plugin.name,
            display_name=plugin.display_name,
            short_description=plugin.short_description,
            category=plugin.category,
            icon=plugin.icon,
            tags=plugin.tags or [],
            is_official=plugin.is_official,
            download_count=plugin.download_count,
            rating=float(plugin.rating) if plugin.rating else 0,
            review_count=plugin.review_count,
            is_installed=plugin.name in installed_names
        )
        items.append(item.model_dump())
    
    return success_response({
        "total": total,
        "items": items
    })


@router.get("/market/categories", summary="获取插件分类")
async def get_plugin_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有插件分类及数量"""
    # 分类定义
    category_info = {
        "search": {"name": "搜索工具", "description": "网页搜索、信息检索"},
        "writing": {"name": "写作辅助", "description": "语法检查、文本润色"},
        "media": {"name": "媒体处理", "description": "图片、音视频处理"},
        "utility": {"name": "实用工具", "description": "计算器、格式转换等"},
    }
    
    # 查询各分类数量
    counts = db.query(
        PluginMarket.category,
        func.count(PluginMarket.id).label("count")
    ).filter(
        PluginMarket.is_active == True,
        PluginMarket.is_approved == True
    ).group_by(PluginMarket.category).all()
    
    count_map = {c.category: c.count for c in counts}
    
    # 构建响应
    categories = []
    for key, info in category_info.items():
        categories.append(PluginCategory(
            key=key,
            name=info["name"],
            description=info["description"],
            count=count_map.get(key, 0)
        ).model_dump())
    
    return success_response(categories)


@router.get("/market/{plugin_name}", summary="获取插件详情")
async def get_plugin_detail(
    plugin_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取插件详情"""
    plugin = db.query(PluginMarket).filter(
        PluginMarket.name == plugin_name,
        PluginMarket.is_active == True
    ).first()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    # 检查用户是否已安装
    user_plugin = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == plugin_name
    ).first()
    
    response = PluginMarketResponse(
        id=plugin.id,
        name=plugin.name,
        display_name=plugin.display_name,
        description=plugin.description,
        short_description=plugin.short_description,
        version=plugin.version,
        author=plugin.author,
        author_url=plugin.author_url,
        category=plugin.category,
        icon=plugin.icon,
        icon_url=plugin.icon_url,
        tags=plugin.tags or [],
        screenshot_urls=plugin.screenshot_urls or [],
        is_official=plugin.is_official,
        is_approved=plugin.is_approved,
        is_active=plugin.is_active,
        download_count=plugin.download_count,
        rating=float(plugin.rating) if plugin.rating else 0,
        review_count=plugin.review_count,
        config_schema=plugin.config_schema or {},
        parameters_schema=plugin.parameters_schema or {},
        created_at=plugin.created_at,
        updated_at=plugin.updated_at,
        is_installed=user_plugin is not None,
        user_config=user_plugin.config if user_plugin else None
    )
    
    return success_response(response.model_dump())


# ==================== 用户插件 API ====================

@router.post("/install", summary="安装插件")
async def install_plugin(
    request: UserPluginInstall,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """安装插件到用户账户"""
    # 检查插件是否存在
    plugin = db.query(PluginMarket).filter(
        PluginMarket.name == request.plugin_name,
        PluginMarket.is_active == True,
        PluginMarket.is_approved == True
    ).first()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="插件不存在或不可用")
    
    # 检查是否已安装
    existing = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == request.plugin_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="插件已安装")
    
    # 验证配置（如果需要）
    if plugin.config_schema and plugin.config_schema.get("required"):
        required_fields = plugin.config_schema["required"]
        for field in required_fields:
            if field not in request.config or not request.config[field]:
                raise HTTPException(
                    status_code=400,
                    detail=f"缺少必需配置: {field}"
                )
    
    # 创建用户插件记录
    user_plugin = UserPlugin(
        user_id=current_user.id,
        plugin_name=request.plugin_name,
        config=request.config,
        is_enabled=True
    )
    db.add(user_plugin)
    
    # 更新下载次数
    plugin.download_count = plugin.download_count + 1
    
    db.commit()
    db.refresh(user_plugin)
    
    logger.info(f"User {current_user.id} installed plugin: {request.plugin_name}")
    
    return success_response({
        "id": user_plugin.id,
        "plugin_name": user_plugin.plugin_name,
        "installed_at": user_plugin.installed_at.isoformat()
    }, message="插件安装成功")


@router.delete("/uninstall/{plugin_name}", summary="卸载插件")
async def uninstall_plugin(
    plugin_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """卸载用户的插件"""
    user_plugin = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == plugin_name
    ).first()
    
    if not user_plugin:
        raise HTTPException(status_code=404, detail="插件未安装")
    
    db.delete(user_plugin)
    db.commit()
    
    logger.info(f"User {current_user.id} uninstalled plugin: {plugin_name}")
    
    return success_response(None, message="插件卸载成功")


@router.get("/my-plugins", summary="获取我的插件列表")
async def get_my_plugins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户已安装的所有插件"""
    user_plugins = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id
    ).order_by(desc(UserPlugin.installed_at)).all()
    
    items = []
    for up in user_plugins:
        # 获取插件市场信息
        plugin = db.query(PluginMarket).filter(
            PluginMarket.name == up.plugin_name
        ).first()
        
        if plugin:
            item = UserPluginListItem(
                id=up.id,
                plugin_name=up.plugin_name,
                display_name=plugin.display_name,
                category=plugin.category,
                icon=plugin.icon,
                is_enabled=up.is_enabled,
                is_auto_use=up.is_auto_use,
                usage_count=up.usage_count,
                last_used_at=up.last_used_at
            )
            items.append(item.model_dump())
    
    return success_response(items)


@router.get("/my-plugins/{plugin_name}", summary="获取我的插件详情")
async def get_my_plugin_detail(
    plugin_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户已安装插件的详情"""
    user_plugin = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == plugin_name
    ).first()
    
    if not user_plugin:
        raise HTTPException(status_code=404, detail="插件未安装")
    
    plugin = db.query(PluginMarket).filter(
        PluginMarket.name == plugin_name
    ).first()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    response = UserPluginResponse(
        id=user_plugin.id,
        plugin_name=user_plugin.plugin_name,
        is_enabled=user_plugin.is_enabled,
        config=user_plugin.config or {},
        is_auto_use=user_plugin.is_auto_use,
        usage_count=user_plugin.usage_count,
        last_used_at=user_plugin.last_used_at,
        installed_at=user_plugin.installed_at,
        display_name=plugin.display_name,
        description=plugin.description,
        category=plugin.category,
        icon=plugin.icon,
        config_schema=plugin.config_schema or {}
    )
    
    return success_response(response.model_dump())


@router.put("/my-plugins/{plugin_name}", summary="更新插件配置")
async def update_my_plugin(
    plugin_name: str,
    request: UserPluginUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户的插件配置"""
    user_plugin = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == plugin_name
    ).first()
    
    if not user_plugin:
        raise HTTPException(status_code=404, detail="插件未安装")
    
    if request.config is not None:
        user_plugin.config = request.config
    if request.is_enabled is not None:
        user_plugin.is_enabled = request.is_enabled
    if request.is_auto_use is not None:
        user_plugin.is_auto_use = request.is_auto_use
    
    db.commit()
    
    return success_response(None, message="插件配置已更新")


# ==================== 插件选择 API ====================

@router.post("/selection", summary="保存插件选择")
async def save_plugin_selection(
    request: PluginSelectionSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    保存用户对某个写作类型的插件选择
    
    下次创作同类型内容时会自动加载
    """
    # 验证选择的插件是否都已安装
    user_plugins = db.query(UserPlugin.plugin_name).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.is_enabled == True
    ).all()
    installed_names = {p.plugin_name for p in user_plugins}
    
    invalid_plugins = set(request.selected_plugins) - installed_names
    if invalid_plugins:
        raise HTTPException(
            status_code=400,
            detail=f"以下插件未安装或未启用: {', '.join(invalid_plugins)}"
        )
    
    # 查找或创建选择记录
    selection = db.query(CreationPluginSelection).filter(
        CreationPluginSelection.user_id == current_user.id,
        CreationPluginSelection.tool_type == request.tool_type
    ).first()
    
    if selection:
        selection.selected_plugins = request.selected_plugins
    else:
        selection = CreationPluginSelection(
            user_id=current_user.id,
            tool_type=request.tool_type,
            selected_plugins=request.selected_plugins
        )
        db.add(selection)
    
    db.commit()
    
    return success_response(None, message="插件选择已保存")


@router.get("/selection/{tool_type}", summary="获取插件选择")
async def get_plugin_selection(
    tool_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户对某个写作类型的插件选择"""
    selection = db.query(CreationPluginSelection).filter(
        CreationPluginSelection.user_id == current_user.id,
        CreationPluginSelection.tool_type == tool_type
    ).first()
    
    if selection:
        return success_response(PluginSelectionResponse(
            tool_type=selection.tool_type,
            selected_plugins=selection.selected_plugins or [],
            updated_at=selection.updated_at
        ).model_dump())
    else:
        # 返回空选择
        return success_response({
            "tool_type": tool_type,
            "selected_plugins": [],
            "updated_at": None
        })


@router.get("/for-creation/{tool_type}", summary="获取创作可用插件")
async def get_plugins_for_creation(
    tool_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户创作时可用的插件列表
    
    返回用户已安装且启用的插件，以及上次对此类型的选择
    """
    # 获取用户已安装的插件
    user_plugins = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.is_enabled == True
    ).all()
    
    # 获取上次选择
    selection = db.query(CreationPluginSelection).filter(
        CreationPluginSelection.user_id == current_user.id,
        CreationPluginSelection.tool_type == tool_type
    ).first()
    
    selected_names = set(selection.selected_plugins) if selection else set()
    
    # 构建响应
    plugins = []
    for up in user_plugins:
        plugin = db.query(PluginMarket).filter(
            PluginMarket.name == up.plugin_name
        ).first()
        
        if plugin:
            plugins.append(PluginForCreation(
                name=plugin.name,
                display_name=plugin.display_name,
                description=plugin.short_description or plugin.description or "",
                icon=plugin.icon,
                is_enabled=up.is_enabled,
                is_selected=plugin.name in selected_names or up.is_auto_use
            ).model_dump())
    
    return success_response({
        "plugins": plugins,
        "has_previous_selection": selection is not None
    })


# ==================== 插件评价 API ====================

@router.post("/reviews", summary="提交插件评价")
async def create_plugin_review(
    request: PluginReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交插件评价（需要已安装）"""
    # 检查是否已安装
    user_plugin = db.query(UserPlugin).filter(
        UserPlugin.user_id == current_user.id,
        UserPlugin.plugin_name == request.plugin_name
    ).first()
    
    if not user_plugin:
        raise HTTPException(status_code=400, detail="请先安装插件再评价")
    
    # 检查是否已评价
    existing = db.query(PluginReview).filter(
        PluginReview.user_id == current_user.id,
        PluginReview.plugin_name == request.plugin_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已评价过此插件")
    
    # 创建评价
    review = PluginReview(
        user_id=current_user.id,
        plugin_name=request.plugin_name,
        rating=request.rating,
        comment=request.comment
    )
    db.add(review)
    
    # 更新插件评分
    plugin = db.query(PluginMarket).filter(
        PluginMarket.name == request.plugin_name
    ).first()
    
    if plugin:
        # 计算新评分
        avg_rating = db.query(func.avg(PluginReview.rating)).filter(
            PluginReview.plugin_name == request.plugin_name
        ).scalar()
        
        plugin.rating = avg_rating or request.rating
        plugin.review_count = plugin.review_count + 1
    
    db.commit()
    
    return success_response(None, message="评价提交成功")


@router.get("/reviews/{plugin_name}", summary="获取插件评价列表")
async def get_plugin_reviews(
    plugin_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取插件的评价列表"""
    query = db.query(PluginReview).filter(
        PluginReview.plugin_name == plugin_name
    ).order_by(desc(PluginReview.created_at))
    
    total = query.count()
    reviews = query.offset(skip).limit(limit).all()
    
    items = []
    for review in reviews:
        # 获取用户名
        user = db.query(User).filter(User.id == review.user_id).first()
        items.append(PluginReviewResponse(
            id=review.id,
            user_id=review.user_id,
            plugin_name=review.plugin_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            username=user.username if user else None
        ).model_dump())
    
    return success_response({
        "total": total,
        "items": items
    })


# ==================== 插件统计 API ====================

@router.get("/stats", summary="获取插件使用统计")
async def get_plugin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的插件使用统计"""
    from sqlalchemy import case
    
    # 按插件分组统计
    stats = db.query(
        PluginInvocation.plugin_name,
        func.count(PluginInvocation.id).label("total_calls"),
        func.sum(
            case((PluginInvocation.error.is_(None), 1), else_=0)
        ).label("success_calls"),
        func.avg(PluginInvocation.duration_ms).label("avg_duration_ms"),
        func.max(PluginInvocation.invoked_at).label("last_used_at")
    ).filter(
        PluginInvocation.user_id == current_user.id
    ).group_by(PluginInvocation.plugin_name).all()
    
    items = []
    for stat in stats:
        plugin = db.query(PluginMarket).filter(
            PluginMarket.name == stat.plugin_name
        ).first()
        
        items.append(PluginStats(
            plugin_name=stat.plugin_name,
            display_name=plugin.display_name if plugin else stat.plugin_name,
            total_calls=stat.total_calls,
            success_calls=stat.success_calls or 0,
            failed_calls=(stat.total_calls - (stat.success_calls or 0)),
            avg_duration_ms=float(stat.avg_duration_ms) if stat.avg_duration_ms else None,
            last_used_at=stat.last_used_at
        ).model_dump())
    
    return success_response(items)
