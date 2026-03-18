"""
兼容性适配器

提供与现有 AIServiceFactory 和 AIServiceBase 的兼容层，
使得现有代码无需修改即可使用新的 LangChain 实现。

策略：
1. LangChainAIService 实现 AIServiceBase 接口
2. LangChainAIServiceFactory 提供与 AIServiceFactory 相同的 API
3. 现有代码可以逐步迁移，无需一次性全部改动
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from .service import LangChainService, ChatResponse
from .chat.factory import LangChainChatFactory
from .tools import PluginToolAdapter, create_tool_from_plugin, ToolExecutor
from .config import get_provider_config

logger = logging.getLogger(__name__)


class LangChainAIService:
    """
    LangChain 实现的 AI 服务
    
    实现与 AIServiceBase 相同的接口，但底层使用 LangChain。
    这样现有使用 AIServiceBase 的代码可以无缝切换到 LangChain。
    
    Example:
        >>> # 原有用法（保持不变）
        >>> service = LangChainAIService("sk-xxx", "gpt-4")
        >>> result = await service.generate_text("你好")
        >>> 
        >>> # 新增能力（工具调用）
        >>> result = await service.chat_with_tools(messages, tools=plugins)
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4",
        base_url: Optional[str] = None,
        provider: str = "openai",
        **kwargs
    ):
        """
        初始化服务
        
        Args:
            api_key: API 密钥
            model_name: 模型名称
            base_url: 自定义 API 地址
            provider: 厂商标识
            **kwargs: 其他参数（如 secret_key, app_id 等）
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.provider = provider
        self.config = kwargs
        
        # 创建 LangChain 服务
        self._service = LangChainService(
            provider=provider,
            model=model_name,
            api_key=api_key,
            api_base=base_url,
            **kwargs
        )
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        生成文本（兼容 AIServiceBase 接口）
        
        Args:
            prompt: 提示词
            max_tokens: 最大 token 数
            temperature: 温度参数
            
        Returns:
            生成的文本
        """
        invoke_kwargs = {}
        if max_tokens:
            invoke_kwargs["max_tokens"] = max_tokens
        if temperature is not None:
            invoke_kwargs["temperature"] = temperature
        invoke_kwargs.update(kwargs)
        
        response = await self._service.chat(prompt, **invoke_kwargs)
        return response.content
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成图片（待阶段2实现）
        
        Args:
            prompt: 提示词
            size: 图片尺寸
            quality: 图片质量
            
        Returns:
            图片 URL
        """
        # TODO: 阶段2实现图片生成
        raise NotImplementedError("图片生成功能将在阶段2实现")
    
    async def check_health(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            是否健康
        """
        try:
            response = await self._service.chat("Hi", max_tokens=5)
            return bool(response.content)
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天完成接口（兼容 AIServiceBase 接口）
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            stream: 是否流式（此方法忽略，使用 chat_completion_stream）
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            {"content": "...", "usage": {...}, "finish_reason": "stop"}
        """
        # 提取消息
        if not messages:
            return {"content": "", "usage": {}, "finish_reason": "stop"}
        
        # 分离系统消息和历史
        system_prompt = None
        history = []
        current_message = ""
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system" and i == 0:
                system_prompt = content
            elif i == len(messages) - 1 and role == "user":
                current_message = content
            else:
                history.append(msg)
        
        # 如果最后一条不是 user，把它作为当前消息
        if not current_message and messages:
            current_message = messages[-1].get("content", "")
            if len(history) > 0:
                history = history[:-1]
        
        invoke_kwargs = {"temperature": temperature}
        if max_tokens:
            invoke_kwargs["max_tokens"] = max_tokens
        invoke_kwargs.update(kwargs)
        
        response = await self._service.chat(
            current_message,
            system_prompt=system_prompt,
            history=history if history else None,
            **invoke_kwargs
        )
        
        return {
            "content": response.content,
            "usage": response.usage,
            "finish_reason": response.finish_reason
        }
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成接口
        
        Yields:
            文本片段
        """
        # 分离消息（与 chat_completion 相同逻辑）
        system_prompt = None
        history = []
        current_message = ""
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system" and i == 0:
                system_prompt = content
            elif i == len(messages) - 1 and role == "user":
                current_message = content
            else:
                history.append(msg)
        
        if not current_message and messages:
            current_message = messages[-1].get("content", "")
            if len(history) > 0:
                history = history[:-1]
        
        invoke_kwargs = {"temperature": temperature}
        if max_tokens:
            invoke_kwargs["max_tokens"] = max_tokens
        invoke_kwargs.update(kwargs)
        
        async for chunk in self._service.chat_stream(
            current_message,
            system_prompt=system_prompt,
            history=history if history else None,
            **invoke_kwargs
        ):
            yield chunk
    
    # ========== 新增：工具调用支持 ==========
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List["PluginInterface"],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带工具调用的聊天
        
        这是新增的方法，支持 Plugins 系统。
        
        Args:
            messages: 消息列表
            tools: 插件列表（PluginInterface 实例）
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            {"content": "...", "tool_calls": [...], "usage": {...}}
        """
        # 将插件转换为 LangChain Tools
        langchain_tools = [create_tool_from_plugin(t) for t in tools]
        
        # 分离消息
        system_prompt = None
        history = []
        current_message = ""
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system" and i == 0:
                system_prompt = content
            elif i == len(messages) - 1 and role == "user":
                current_message = content
            else:
                history.append(msg)
        
        if not current_message and messages:
            current_message = messages[-1].get("content", "")
            if len(history) > 0:
                history = history[:-1]
        
        invoke_kwargs = {"temperature": temperature}
        if max_tokens:
            invoke_kwargs["max_tokens"] = max_tokens
        invoke_kwargs.update(kwargs)
        
        response = await self._service.chat_with_tools(
            current_message,
            tools=langchain_tools,
            system_prompt=system_prompt,
            history=history if history else None,
            **invoke_kwargs
        )
        
        return {
            "content": response.content,
            "tool_calls": response.tool_calls,
            "usage": response.usage,
            "finish_reason": response.finish_reason
        }


class LangChainAIServiceFactory:
    """
    LangChain AI 服务工厂
    
    提供与 AIServiceFactory 相同的 API，但创建 LangChainAIService。
    
    使用方式（与原 AIServiceFactory 完全相同）：
        >>> service = LangChainAIServiceFactory.create_service(
        ...     provider="openai",
        ...     api_key="sk-xxx",
        ...     model_name="gpt-4"
        ... )
        >>> result = await service.generate_text("你好")
    """
    
    @classmethod
    def create_service(
        cls,
        provider: str,
        api_key: str,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> LangChainAIService:
        """
        创建 AI 服务实例
        
        Args:
            provider: 服务提供商
            api_key: API 密钥
            model_name: 模型名称
            base_url: API 基础 URL
            **kwargs: 其他参数
            
        Returns:
            LangChainAIService 实例
        """
        # 检查是否支持该厂商
        config = get_provider_config(provider)
        if not config:
            raise ValueError(f"不支持的AI服务提供商: {provider}")
        
        # 获取默认模型名
        if not model_name:
            from .config import get_default_model
            model_name = get_default_model(provider, "text") or ""
        
        return LangChainAIService(
            api_key=api_key,
            model_name=model_name,
            base_url=base_url,
            provider=provider,
            **kwargs
        )
    
    @classmethod
    def create_from_model(
        cls,
        db: Session,
        model_id: int
    ) -> LangChainAIService:
        """
        从数据库模型创建 AI 服务实例
        
        Args:
            db: 数据库会话
            model_id: 模型 ID
            
        Returns:
            LangChainAIService 实例
        """
        from app.models.ai_model import AIModel
        from app.services.oauth.encryption import encryption_service
        
        model = db.query(AIModel).filter(
            AIModel.id == model_id,
            AIModel.is_active == True
        ).first()
        
        if not model:
            raise ValueError("AI模型不存在或未启用")
        
        # 解密 API 密钥
        api_key = encryption_service.decrypt(model.api_key)
        
        # 准备额外参数
        kwargs = {}
        if model.config:
            kwargs.update(model.config)
        
        return cls.create_service(
            provider=model.provider,
            api_key=api_key,
            model_name=model.model_name,
            base_url=model.base_url,
            **kwargs
        )
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的厂商列表"""
        return LangChainChatFactory.get_supported_providers()
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """检查是否支持该厂商"""
        return LangChainChatFactory.is_provider_supported(provider)


# ============================================================================
# 辅助函数：用于逐步迁移
# ============================================================================

def get_ai_service_factory(use_langchain: bool = True):
    """
    获取 AI 服务工厂
    
    通过开关控制使用哪个实现，便于灰度迁移。
    
    Args:
        use_langchain: 是否使用 LangChain 实现
        
    Returns:
        AIServiceFactory 或 LangChainAIServiceFactory
    """
    if use_langchain:
        return LangChainAIServiceFactory
    else:
        from app.services.ai.factory import AIServiceFactory
        return AIServiceFactory
