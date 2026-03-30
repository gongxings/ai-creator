"""
管理员模型调用监控接口
"""
from typing import Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app import models
from app.models.model_usage_log import AIModelUsageLog
from app.utils.deps import get_db, get_admin_user as get_current_admin_user
from app.schemas.common import success_response

router = APIRouter()


@router.get("/logs")
def get_usage_logs(
    page: int = 1,
    page_size: int = 20,
    provider: Optional[str] = None,
    tool: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取模型调用日志（分页）
    
    **权限要求**: 管理员
    """
    query = db.query(AIModelUsageLog)
    
    if provider:
        query = query.filter(AIModelUsageLog.provider == provider)
    if tool:
        query = query.filter(AIModelUsageLog.tool == tool)
    if status:
        query = query.filter(AIModelUsageLog.status == status)
    if user_id:
        query = query.filter(AIModelUsageLog.user_id == user_id)
    
    total = query.count()
    logs = query.order_by(desc(AIModelUsageLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "ai_model_id": log.ai_model_id,
            "creation_id": log.creation_id,
            "provider": log.provider,
            "model_name": log.model_name,
            "tool": log.tool,
            "request_type": log.request_type,
            "input_content": log.input_content,
            "output_content": log.output_content,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": log.total_tokens,
            "status": log.status,
            "error_message": log.error_message,
            "response_time_ms": log.response_time_ms,
            "extra_data": log.extra_data,
            "created_at": str(log.created_at) if log.created_at else None,
        })
    
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        },
        message="success"
    )


@router.get("/logs/{log_id}")
def get_usage_log_detail(
    log_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取单条日志详情
    
    **权限要求**: 管理员
    """
    log = db.query(AIModelUsageLog).filter(AIModelUsageLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return success_response(
        data={
            "id": log.id,
            "user_id": log.user_id,
            "ai_model_id": log.ai_model_id,
            "creation_id": log.creation_id,
            "provider": log.provider,
            "model_name": log.model_name,
            "tool": log.tool,
            "request_type": log.request_type,
            "input_content": log.input_content,
            "output_content": log.output_content,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "total_tokens": log.total_tokens,
            "status": log.status,
            "error_message": log.error_message,
            "response_time_ms": log.response_time_ms,
            "extra_data": log.extra_data,
            "created_at": str(log.created_at) if log.created_at else None,
        },
        message="success"
    )


@router.get("/stats")
def get_usage_stats(
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取模型调用统计概览
    
    **权限要求**: 管理员
    """
    from datetime import timedelta
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    # 总调用次数
    total_calls = db.query(func.count(AIModelUsageLog.id)).scalar() or 0
    
    # 今日调用次数
    today_calls = db.query(func.count(AIModelUsageLog.id)).filter(
        AIModelUsageLog.created_at >= today
    ).scalar() or 0
    
    # 本周调用次数
    week_calls = db.query(func.count(AIModelUsageLog.id)).filter(
        AIModelUsageLog.created_at >= week_ago
    ).scalar() or 0
    
    # 总 token 消耗
    total_tokens = db.query(func.sum(AIModelUsageLog.total_tokens)).filter(
        AIModelUsageLog.total_tokens > 0
    ).scalar() or 0
    
    # 今日 token 消耗
    today_tokens = db.query(func.sum(AIModelUsageLog.total_tokens)).filter(
        AIModelUsageLog.created_at >= today,
        AIModelUsageLog.total_tokens > 0
    ).scalar() or 0
    
    # 失败次数
    failed_calls = db.query(func.count(AIModelUsageLog.id)).filter(
        AIModelUsageLog.status == "failed"
    ).scalar() or 0
    
    # 按厂商统计
    provider_stats = db.query(
        AIModelUsageLog.provider,
        func.count(AIModelUsageLog.id).label("count"),
        func.sum(AIModelUsageLog.total_tokens).label("total_tokens")
    ).group_by(AIModelUsageLog.provider).all()
    
    # 按工具统计
    tool_stats = db.query(
        AIModelUsageLog.tool,
        func.count(AIModelUsageLog.id).label("count"),
        func.sum(AIModelUsageLog.total_tokens).label("total_tokens")
    ).group_by(AIModelUsageLog.tool).all()
    
    return success_response(
        data={
            "overview": {
                "total_calls": total_calls,
                "today_calls": today_calls,
                "week_calls": week_calls,
                "total_tokens": total_tokens,
                "today_tokens": today_tokens,
                "failed_calls": failed_calls,
                "success_rate": round((total_calls - failed_calls) / total_calls * 100, 1) if total_calls > 0 else 0,
            },
            "by_provider": [
                {
                    "provider": p.provider,
                    "count": p.count,
                    "total_tokens": p.total_tokens or 0,
                }
                for p in provider_stats
            ],
            "by_tool": [
                {
                    "tool": t.tool or "unknown",
                    "count": t.count,
                    "total_tokens": t.total_tokens or 0,
                }
                for t in tool_stats
            ],
        },
        message="success"
    )
