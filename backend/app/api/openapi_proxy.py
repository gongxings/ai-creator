"""
OpenAPI代理接口（兼容OpenAI API格式）
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator
import json
import time

from app.core.database import get_db
from app.models import APIKey, OAuthAccount, AIModel
from app.services.api_key_service import APIKeyService
from app.services.model_service import ModelService
from app.services.oauth.litellm_proxy import LiteLLMProxy
from app.services.ai.factory import AIServiceFactory
from app.core.exceptions import BusinessException

router = APIRouter()


async def verify_api_key_auth(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    验证API Key认证
    
    从Authorization头提取Bearer Token并验证
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "").strip()
    
    # 验证API Key
    db_key = APIKeyService.verify_api_key(db, api_key)
    if not db_key:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")
    
    # 实现速率限制检查（使用Redis）
    if db_key.rate_limit and db_key.rate_limit > 0:
        from app.utils.cache import redis_client
        import time
        
        # 使用滑动窗口算法实现速率限制
        rate_limit_key = f"api_key_rate_limit:{db_key.id}"
        current_time = int(time.time())
        window_start = current_time - 60  # 1分钟窗口
        
        try:
            # 移除过期的请求记录
            redis_client.zremrangebyscore(rate_limit_key, 0, window_start)
            
            # 获取当前窗口内的请求数
            request_count = redis_client.zcard(rate_limit_key)
            
            # 检查是否超过限制
            if request_count >= db_key.rate_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Limit: {db_key.rate_limit} requests per minute"
                )
            
            # 记录当前请求
            redis_client.zadd(rate_limit_key, {str(current_time): current_time})
            
            # 设置过期时间（2分钟）
            redis_client.expire(rate_limit_key, 120)
            
        except Exception as e:
            # Redis连接失败时，记录日志但不阻止请求
            import logging
            logging.warning(f"Rate limit check failed: {str(e)}")
    
    return db_key


@router.get("/v1/models")
async def list_models(
    db_key: APIKey = Depends(verify_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    获取可用模型列表（兼容OpenAI格式）
    
    返回该API Key可访问的所有模型
    """
    try:
        # 获取用户的所有可用模型
        models_response = ModelService.get_available_models(
            db, db_key.user_id, None
        )
        
        # 过滤allowed_models
        models = models_response.models
        if db_key.allowed_models:
            models = [m for m in models if m.model_id in db_key.allowed_models]
        
        # 转换为OpenAI格式
        openai_models = []
        for model in models:
            openai_models.append({
                "id": model.model_id,
                "object": "model",
                "created": int(time.time()),
                "owned_by": model.provider,
                "permission": [],
                "root": model.model_id,
                "parent": None
            })
        
        return {
            "object": "list",
            "data": openai_models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    db_key: APIKey = Depends(verify_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    聊天完成接口（兼容OpenAI格式）
    
    支持流式和非流式响应
    """
    start_time = time.time()
    
    try:
        # 解析请求体
        body = await request.json()
        
        model_id = body.get("model")
        messages = body.get("messages", [])
        stream = body.get("stream", False)
        temperature = body.get("temperature", 0.7)
        max_tokens = body.get("max_tokens")
        
        if not model_id or not messages:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # 检查模型权限
        if db_key.allowed_models and model_id not in db_key.allowed_models:
            raise HTTPException(status_code=403, detail="Model not allowed for this API key")
        
        # 解析model_id
        model_info = ModelService.parse_model_id(model_id)
        
        # 调用对应的服务
        if model_info["source_type"] == "oauth":
            response = await _call_oauth_model_openapi(
                db, db_key.user_id, model_info, messages, stream, temperature, max_tokens
            )
        elif model_info["source_type"] == "api_key":
            response = await _call_api_key_model_openapi(
                db, db_key.user_id, model_info, messages, stream, temperature, max_tokens
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid model ID")
        
        # 记录使用日志
        response_time = int((time.time() - start_time) * 1000)
        
        # 如果是流式响应
        if stream:
            return StreamingResponse(
                _stream_openai_response(
                    response, model_id, db, db_key.id, body, response_time, request
                ),
                media_type="text/event-stream"
            )
        
        # 非流式响应
        usage = response.get("usage", {})
        APIKeyService.log_api_key_usage(
            db=db,
            api_key_id=db_key.id,
            model_id=model_id,
            model_name=model_info.get("model_name"),
            endpoint="/v1/chat/completions",
            method="POST",
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            request_data=body,
            response_data=response,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            response_time=response_time,
            status_code=200
        )
        
        # 返回OpenAI格式响应
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.get("content", "")
                    },
                    "finish_reason": response.get("finish_reason", "stop")
                }
            ],
            "usage": usage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # 记录错误日志
        response_time = int((time.time() - start_time) * 1000)
        try:
            APIKeyService.log_api_key_usage(
                db=db,
                api_key_id=db_key.id,
                model_id=body.get("model") if 'body' in locals() else None,
                model_name=None,
                endpoint="/v1/chat/completions",
                method="POST",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                request_data=body if 'body' in locals() else None,
                error_message=str(e),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                response_time=response_time,
                status_code=500
            )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))


async def _call_oauth_model_openapi(
    db: Session,
    user_id: int,
    model_info: dict,
    messages: list,
    stream: bool,
    temperature: float,
    max_tokens: Optional[int]
) -> dict:
    """调用OAuth模型（OpenAPI格式）"""
    account_id = model_info["account_id"]
    model_name = model_info["model_name"]
    
    # 验证账号
    account = db.query(OAuthAccount).filter(
        OAuthAccount.id == account_id,
        OAuthAccount.user_id == user_id,
        OAuthAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="OAuth account not found")
    
    if account.is_expired:
        raise HTTPException(status_code=403, detail="OAuth account expired")
    
    if account.quota_limit and account.quota_used >= account.quota_limit:
        raise HTTPException(status_code=429, detail="Quota exceeded")
    
    # 调用LiteLLM代理
    litellm_proxy = LiteLLMProxy()
    
    response = await litellm_proxy.chat_completion(
        account_id=account_id,
        model=model_name,
        messages=messages,
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response


async def _call_api_key_model_openapi(
    db: Session,
    user_id: int,
    model_info: dict,
    messages: list,
    stream: bool,
    temperature: float,
    max_tokens: Optional[int]
) -> dict:
    """调用API Key模型（OpenAPI格式）"""
    model_id = model_info["model_id"]
    
    # 验证模型
    ai_model = db.query(AIModel).filter(
        AIModel.id == model_id,
        AIModel.user_id == user_id,
        AIModel.is_active == True
    ).first()
    
    if not ai_model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # 使用AI服务工厂调用
    service = AIServiceFactory.create_service(ai_model.provider, ai_model.to_dict())
    
    response = await service.chat_completion(
        messages=messages,
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response


async def _stream_openai_response(
    response: dict,
    model_id: str,
    db: Session,
    api_key_id: int,
    request_body: dict,
    response_time: int,
    request: Request
) -> AsyncGenerator[str, None]:
    """流式响应生成器（OpenAI格式）"""
    try:
        content = response.get("content", "")
        
        # 发送流式数据
        chunk_id = f"chatcmpl-{int(time.time())}"
        
        # 分块发送内容
        for i, char in enumerate(content):
            chunk = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_id,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": char} if i == 0 else {"content": char},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # 发送结束标记
        final_chunk = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
        # 记录使用日志
        usage = response.get("usage", {})
        APIKeyService.log_api_key_usage(
            db=db,
            api_key_id=api_key_id,
            model_id=model_id,
            model_name=response.get("model_name"),
            endpoint="/v1/chat/completions",
            method="POST",
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            request_data=request_body,
            response_data={"content": content, "usage": usage},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            response_time=response_time,
            status_code=200
        )
    except Exception as e:
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error",
                "code": "internal_error"
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
