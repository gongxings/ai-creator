"""
API 监控接口
提供系统默认APIKey 的使用监控、统计分析等功能
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app import models
from app.utils.deps import get_db, get_admin_user as get_current_admin_user
from app.schemas.common import success_response

router = APIRouter()


@router.get("/overview")
def get_monitor_overview(
    days: int = 7,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取 API 监控概览
    
    **权限要求**: 管理员
    
    **参数**:
    - days: 统计天数（默认 7 天）
    
    **返回**:
    - 系统默认APIKey 总体使用情况
    - 请求趋势
    - Token 消耗统计
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 获取所有系统默认API Key
    system_keys = db.query(models.APIKey).filter(
        models.APIKey.is_system_default == True,
        models.APIKey.is_active == True
    ).all()
    
    key_ids = [key.id for key in system_keys]
    
    if not key_ids:
        return success_response(
            data={
                "total_requests": 0,
                "total_tokens": 0,
                "active_users": 0,
                "total_keys": 0,
                "avg_daily_requests": 0,
                "top_models": []
            }
        )
    
    # 总请求数和 Token 数
    stats = db.query(
        func.count(models.APIKeyUsageLog.id).label('total_requests'),
        func.sum(models.APIKeyUsageLog.total_tokens).label('total_tokens')
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date
        )
    ).first()
    
    # 活跃用户数
    active_users = db.query(
        func.count(func.distinct(models.APIKeyUsageLog.used_by_user_id))
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.used_by_user_id.isnot(None),
            models.APIKeyUsageLog.created_at >= start_date
        )
    ).scalar() or 0
    
    # 平均每日请求数
    avg_daily_requests = stats.total_requests / days if days > 0 else 0
    
    # Top 使用的模型
    top_models = db.query(
        models.APIKeyUsageLog.model_name,
        func.count(models.APIKeyUsageLog.id).label('request_count'),
        func.sum(models.APIKeyUsageLog.total_tokens).label('token_count')
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date,
            models.APIKeyUsageLog.model_name.isnot(None)
        )
    ).group_by(
        models.APIKeyUsageLog.model_name
    ).order_by(
        func.count(models.APIKeyUsageLog.id).desc()
    ).limit(10).all()
    
    top_models_data = [
        {
            "model_name": model.model_name,
            "request_count": model.request_count,
            "token_count": model.token_count or 0
        }
        for model in top_models
    ]
    
    return success_response(
        data={
            "total_requests": stats.total_requests or 0,
            "total_tokens": stats.total_tokens or 0,
            "active_users": active_users,
            "total_keys": len(system_keys),
            "avg_daily_requests": round(avg_daily_requests, 2),
            "period_days": days,
            "top_models": top_models_data
        }
    )


@router.get("/user-usage")
def get_user_usage_details(
    user_id: Optional[int] = Query(None, description="用户 ID（可选）"),
    key_id: Optional[int] = Query(None, description="API Key ID（可选）"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取用户使用详情
    
    **权限要求**: 管理员
    
    **参数**:
    - user_id: 按用户筛选（可选）
    - key_id: 按 API Key 筛选（可选）
    - days: 统计天数（默认 30 天）
    - page: 页码
    - page_size: 每页数量
    
    **返回**:
    - 使用记录列表及分页信息
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 基础查询
    query = db.query(
        models.APIKeyUsageLog,
        models.User.username.label('username'),
        models.APIKey.key_name.label('key_name')
    ).join(
        models.User,
        models.APIKeyUsageLog.used_by_user_id == models.User.id,
        isouter=True
    ).join(
        models.APIKey,
        models.APIKeyUsageLog.api_key_id == models.APIKey.id,
        isouter=True
    ).filter(
        models.APIKeyUsageLog.created_at >= start_date
    )
    
    # 按用户筛选
    if user_id:
        query = query.filter(models.APIKeyUsageLog.used_by_user_id == user_id)
    
    # 按 API Key 筛选
    if key_id:
        query = query.filter(models.APIKeyUsageLog.api_key_id == key_id)
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    logs = query.order_by(
        models.APIKeyUsageLog.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    data = []
    for log, username, key_name in logs:
        data.append({
            "id": log.id,
            "username": username or "未知",
            "key_name": key_name or "未知",
            "model_name": log.model_name,
            "endpoint": log.endpoint,
            "method": log.method,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": log.total_tokens,
            "status_code": log.status_code,
            "error_message": log.error_message,
            "response_time": log.response_time,
            "created_at": log.created_at
        })
    
    return success_response(
        data={
            "logs": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/daily-stats")
def get_daily_statistics(
    days: int = Query(30, ge=1, le=90, description="统计天数"),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取每日统计趋势
    
    **权限要求**: 管理员
    
    **参数**:
    - days: 统计天数（默认 30 天）
    
    **返回**:
    - 每日请求数、Token 数、活跃用户数趋势
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 获取所有系统默认API Key
    system_keys = db.query(models.APIKey).filter(
        models.APIKey.is_system_default == True
    ).all()
    
    key_ids = [key.id for key in system_keys]
    
    if not key_ids:
        return success_response(data=[])
    
    # 按日期分组统计
    from sqlalchemy import extract
    
    daily_stats = db.query(
        extract('year', models.APIKeyUsageLog.created_at).label('year'),
        extract('month', models.APIKeyUsageLog.created_at).label('month'),
        extract('day', models.APIKeyUsageLog.created_at).label('day'),
        func.count(models.APIKeyUsageLog.id).label('requests'),
        func.sum(models.APIKeyUsageLog.total_tokens).label('tokens'),
        func.count(func.distinct(models.APIKeyUsageLog.used_by_user_id)).label('active_users')
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date
        )
    ).group_by(
        extract('year', models.APIKeyUsageLog.created_at),
        extract('month', models.APIKeyUsageLog.created_at),
        extract('day', models.APIKeyUsageLog.created_at)
    ).order_by(
        'year', 'month', 'day'
    ).all()
    
    data = []
    for stat in daily_stats:
        date_str = f"{int(stat.year)}-{int(stat.month):02d}-{int(stat.day):02d}"
        data.append({
            "date": date_str,
            "requests": stat.requests,
            "tokens": stat.tokens or 0,
            "active_users": stat.active_users or 0
        })
    
    return success_response(data=data)


@router.get("/error-analysis")
def get_error_analysis(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    错误分析
    
    **权限要求**: 管理员
    
    **参数**:
    - days: 统计天数（默认 7 天）
    
    **返回**:
    - 错误类型分布
    - 高频错误信息
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 获取所有系统默认API Key
    system_keys = db.query(models.APIKey).filter(
        models.APIKey.is_system_default == True
    ).all()
    
    key_ids = [key.id for key in system_keys]
    
    if not key_ids:
        return success_response(
            data={
                "total_errors": 0,
                "error_rate": 0,
                "error_types": [],
                "top_errors": []
            }
        )
    
    # 总请求数
    total_requests = db.query(
        func.count(models.APIKeyUsageLog.id)
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date
        )
    ).scalar() or 0
    
    # 错误请求数
    error_requests = db.query(
        func.count(models.APIKeyUsageLog.id)
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date,
            models.APIKeyUsageLog.error_message.isnot(None)
        )
    ).scalar() or 0
    
    # 错误率
    error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
    
    # 按状态码统计错误类型
    error_types = db.query(
        models.APIKeyUsageLog.status_code,
        func.count(models.APIKeyUsageLog.id).label('count')
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date,
            models.APIKeyUsageLog.error_message.isnot(None),
            models.APIKeyUsageLog.status_code.isnot(None)
        )
    ).group_by(
        models.APIKeyUsageLog.status_code
    ).order_by(
        func.count(models.APIKeyUsageLog.id).desc()
    ).limit(10).all()
    
    error_types_data = [
        {
            "status_code": stat.status_code,
            "count": stat.count,
            "percentage": round(stat.count / error_requests * 100, 2) if error_requests > 0 else 0
        }
        for stat in error_types
    ]
    
    # Top 错误信息
    top_errors = db.query(
        models.APIKeyUsageLog.error_message,
        func.count(models.APIKeyUsageLog.id).label('count')
    ).filter(
        and_(
            models.APIKeyUsageLog.api_key_id.in_(key_ids),
            models.APIKeyUsageLog.created_at >= start_date,
            models.APIKeyUsageLog.error_message.isnot(None)
        )
    ).group_by(
        models.APIKeyUsageLog.error_message
    ).order_by(
        func.count(models.APIKeyUsageLog.id).desc()
    ).limit(10).all()
    
    top_errors_data = [
        {
            "error_message": stat.error_message[:200],  # 截断过长的错误信息
            "count": stat.count,
            "percentage": round(stat.count / error_requests * 100, 2) if error_requests > 0 else 0
        }
        for stat in top_errors
    ]
    
    return success_response(
        data={
            "total_errors": error_requests,
            "error_rate": round(error_rate, 2),
            "period_days": days,
            "error_types": error_types_data,
            "top_errors": top_errors_data
        }
    )
