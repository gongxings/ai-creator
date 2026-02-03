"""
LiteLLM代理服务
用于代理AI模型调用
"""
import asyncio
from typing import Dict, Any, Optional, AsyncIterator
from sqlalchemy.orm import Session
from loguru import logger
import litellm
from litellm import completion, acompletion

from app.services.oauth.oauth_service import oauth_service
from app.services.oauth.adapters import get_adapter
from app.models.platform_config import PlatformConfig


class LiteLLMProxy:
    """LiteLLM代理服务"""
    
    def __init__(self):
        """初始化代理服务"""
        # 配置LiteLLM
        litellm.drop_params = True  # 自动删除不支持的参数
        litellm.set_verbose = False  # 关闭详细日志
    
    async def chat_completion(
        self,
        db: Session,
        account_id: int,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行聊天完成
        
        Args:
            db: 数据库会话
            account_id: OAuth账号ID
            messages: 消息列表
            model: 模型名称（可选）
            stream: 是否流式输出
            **kwargs: 其他参数
            
        Returns:
            完成结果
        """
        try:
            # 获取账号凭证
            credentials = oauth_service.get_account_credentials(db, account_id)
            
            # 获取账号信息
            account = oauth_service.get_account(db, account_id)
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # 获取平台配置
            platform_config = db.query(PlatformConfig).filter(
                PlatformConfig.platform_id == account.platform
            ).first()
            
            if not platform_config:
                raise ValueError(f"Platform {account.platform} not found")
            
            # 获取适配器
            adapter = get_adapter(account.platform, {
                "oauth_config": platform_config.oauth_config,
                "litellm_config": platform_config.litellm_config,
                "quota_config": platform_config.quota_config,
            })
            
            if not adapter:
                raise ValueError(f"Adapter for platform {account.platform} not found")
            
            # 构建LiteLLM配置
            litellm_config = adapter.build_litellm_config(credentials)
            
            # 确定使用的模型
            if not model:
                model = litellm_config.get("model")
            
            # 构建请求参数
            request_params = {
                "model": model,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            # 添加额外的headers
            if "extra_headers" in litellm_config:
                request_params["extra_headers"] = litellm_config["extra_headers"]
            
            # 添加api_base
            if "api_base" in litellm_config:
                request_params["api_base"] = litellm_config["api_base"]
            
            # 添加custom_llm_provider
            if "custom_llm_provider" in litellm_config:
                request_params["custom_llm_provider"] = litellm_config["custom_llm_provider"]
            
            logger.info(f"Calling LiteLLM with model {model} for account {account_id}")
            
            # 调用LiteLLM
            if stream:
                return await self._stream_completion(
                    db, account_id, request_params
                )
            else:
                return await self._normal_completion(
                    db, account_id, request_params
                )
                
        except Exception as e:
            logger.error(f"LiteLLM proxy error: {e}")
            
            # 记录错误日志
            oauth_service.log_usage(
                db=db,
                account_id=account_id,
                model=model or "unknown",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                request_data={"messages": messages, **kwargs},
                error_message=str(e),
            )
            
            raise
    
    async def _normal_completion(
        self,
        db: Session,
        account_id: int,
        request_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行普通完成（非流式）
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            request_params: 请求参数
            
        Returns:
            完成结果
        """
        try:
            # 调用LiteLLM
            response = await acompletion(**request_params)
            
            # 提取使用量信息
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # 记录使用日志
            oauth_service.log_usage(
                db=db,
                account_id=account_id,
                model=request_params.get("model", "unknown"),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                request_data=request_params,
                response_data=response,
            )
            
            logger.info(f"Completion successful, tokens: {total_tokens}")
            
            return response
            
        except Exception as e:
            logger.error(f"Completion failed: {e}")
            raise
    
    async def _stream_completion(
        self,
        db: Session,
        account_id: int,
        request_params: Dict[str, Any],
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        执行流式完成
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            request_params: 请求参数
            
        Yields:
            流式响应块
        """
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        
        try:
            # 调用LiteLLM流式API
            response = await acompletion(**request_params)
            
            async for chunk in response:
                # 累计tokens
                if hasattr(chunk, "usage") and chunk.usage:
                    prompt_tokens = chunk.usage.get("prompt_tokens", 0)
                    completion_tokens = chunk.usage.get("completion_tokens", 0)
                    total_tokens = chunk.usage.get("total_tokens", 0)
                
                yield chunk
            
            # 记录使用日志
            oauth_service.log_usage(
                db=db,
                account_id=account_id,
                model=request_params.get("model", "unknown"),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                request_data=request_params,
            )
            
            logger.info(f"Stream completion successful, tokens: {total_tokens}")
            
        except Exception as e:
            logger.error(f"Stream completion failed: {e}")
            
            # 记录错误日志
            oauth_service.log_usage(
                db=db,
                account_id=account_id,
                model=request_params.get("model", "unknown"),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                request_data=request_params,
                error_message=str(e),
            )
            
            raise
    
    def get_available_models(
        self,
        db: Session,
        account_id: int,
    ) -> list:
        """
        获取账号可用的模型列表
        
        Args:
            db: 数据库会话
            account_id: 账号ID
            
        Returns:
            模型列表
        """
        try:
            # 获取账号信息
            account = oauth_service.get_account(db, account_id)
            if not account:
                return []
            
            # 获取平台配置
            platform_config = db.query(PlatformConfig).filter(
                PlatformConfig.platform_id == account.platform
            ).first()
            
            if not platform_config:
                return []
            
            # 获取适配器
            adapter = get_adapter(account.platform, {
                "oauth_config": platform_config.oauth_config,
                "litellm_config": platform_config.litellm_config,
                "quota_config": platform_config.quota_config,
            })
            
            if not adapter:
                return []
            
            # 获取凭证
            credentials = oauth_service.get_account_credentials(db, account_id)
            
            # 构建LiteLLM配置
            litellm_config = adapter.build_litellm_config(credentials)
            
            # 返回可用模型列表
            return litellm_config.get("available_models", [])
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []


# 全局LiteLLM代理实例
litellm_proxy = LiteLLMProxy()
