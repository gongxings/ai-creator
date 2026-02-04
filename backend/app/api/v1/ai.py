"""
统一AI调用接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import time
from typing import AsyncGenerator

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models import User, OAuthAccount, AIModel, Creation
from app.schemas.api_key import ChatRequest, ChatResponse, AvailableModelsResponse
from app.schemas.common import success_response, error_response
from app.services.model_service import ModelService
from app.services.oauth.litellm_proxy import LiteLLMProxy
from app.services.ai.factory import AIServiceFactory
from app.core.exceptions import BusinessException

router = APIRouter()


@router.get("/models/available")
async def get_available_models(
    scene_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户可用的所有模型（OAuth + API Key）
    
    - **scene_type**: 场景类型（可选：writing/image/video）
    """
    try:
        result = ModelService.get_available_models(db, current_user.id, scene_type)
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型列表失败: {str(e)}"
        )


@router.post("/chat")
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    统一的AI聊天接口（支持OAuth和API Key模型）
    
    - **model_id**: 模型ID（oauth_{account_id}_{model_name} 或 ai_model_{model_id}）
    - **messages**: 消息列表
    - **scene_type**: 场景类型（可选）
    - **stream**: 是否流式响应
    - **temperature**: 温度参数（可选）
    - **max_tokens**: 最大Token数（可选）
    """
    try:
        # 解析model_id
        model_info = ModelService.parse_model_id(request.model_id)
        
        # 根据来源类型调用不同的服务
        if model_info["source_type"] == "oauth":
            # OAuth模型
            result = await _call_oauth_model(
                db, current_user.id, model_info, request
            )
        elif model_info["source_type"] == "api_key":
            # API Key模型
            result = await _call_api_key_model(
                db, current_user.id, model_info, request
            )
        else:
            raise BusinessException("不支持的模型类型")
        
        # 如果是流式响应，返回StreamingResponse
        if request.stream:
            return StreamingResponse(
                _stream_response(result),
                media_type="text/event-stream"
            )
        
        return success_response(data=result)
        
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"调用AI服务失败: {str(e)}"
        )


async def _call_oauth_model(
    db: Session,
    user_id: int,
    model_info: dict,
    request: ChatRequest
) -> ChatResponse:
    """调用OAuth模型"""
    account_id = model_info["account_id"]
    model_name = model_info["model_name"]
    
    # 验证账号
    account = db.query(OAuthAccount).filter(
        OAuthAccount.id == account_id,
        OAuthAccount.user_id == user_id,
        OAuthAccount.is_active == True
    ).first()
    
    if not account:
        raise BusinessException("OAuth账号不存在或已禁用")
    
    if account.is_expired:
        raise BusinessException("OAuth账号已过期")
    
    if account.quota_limit and account.quota_used >= account.quota_limit:
        raise BusinessException("OAuth账号配额已用尽")
    
    # 调用LiteLLM代理
    litellm_proxy = LiteLLMProxy()
    
    # 转换消息格式
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # 调用
    response = await litellm_proxy.chat_completion(
        account_id=account_id,
        model=model_name,
        messages=messages,
        stream=request.stream,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    # 构造响应
    return ChatResponse(
        content=response.get("content", ""),
        model_id=request.model_id,
        model_name=model_name,
        usage=response.get("usage", {}),
        finish_reason=response.get("finish_reason")
    )


async def _call_api_key_model(
    db: Session,
    user_id: int,
    model_info: dict,
    request: ChatRequest
) -> ChatResponse:
    """调用API Key模型"""
    model_id = model_info["model_id"]
    
    # 验证模型
    ai_model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == user_id,
        AIModel.is_active == True
    ).first()
    
    if not ai_model:
        raise BusinessException("AI模型不存在或已禁用")
    
    # 使用AI服务工厂调用
    service = AIServiceFactory.create_service(ai_model.provider, ai_model.to_dict())
    
    # 转换消息格式
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # 调用
    response = await service.chat_completion(
        messages=messages,
        stream=request.stream,
        temperature=request.temperature or 0.7,
        max_tokens=request.max_tokens
    )
    
    # 构造响应
    return ChatResponse(
        content=response.get("content", ""),
        model_id=request.model_id,
        model_name=ai_model.model_name,
        usage=response.get("usage", {}),
        finish_reason=response.get("finish_reason")
    )


async def _stream_response(response: ChatResponse) -> AsyncGenerator[str, None]:
    """流式响应生成器"""
    # 这里简化处理，实际应该从AI服务获取流式数据
    yield f"data: {json.dumps(response.dict())}\n\n"
    yield "data: [DONE]\n\n"
