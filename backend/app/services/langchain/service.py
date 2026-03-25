"""
LangChain 统一服务入口

提供统一的 AI 调用接口，支持：
- 文本生成（16个厂商）
- 带工具调用的对话
- 流式响应
- 与现有系统的兼容

这是新 LangChain 架构的核心服务层。
"""

import logging
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.tools import BaseTool

from .chat.factory import LangChainChatFactory
from .tools import ToolExecutor, create_tool_from_plugin

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str                              # 文本内容
    role: str = "assistant"                   # 角色
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # 工具调用
    finish_reason: str = "stop"               # 结束原因
    model: str = ""                           # 使用的模型
    usage: Dict[str, int] = field(default_factory=dict)  # token 使用量
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（兼容 OpenAI 格式）"""
        return {
            "choices": [{
                "message": {
                    "role": self.role,
                    "content": self.content,
                    "tool_calls": self.tool_calls if self.tool_calls else None
                },
                "finish_reason": self.finish_reason
            }],
            "model": self.model,
            "usage": self.usage
        }


class LangChainService:
    """
    LangChain 统一服务
    
    统一管理 16 个厂商的 AI 调用，支持文本生成和工具调用。
    
    Example:
        >>> service = LangChainService(
        ...     provider="openai",
        ...     model="gpt-4",
        ...     api_key="sk-xxx"
        ... )
        >>> 
        >>> # 简单对话
        >>> response = await service.chat("你好")
        >>> print(response.content)
        >>> 
        >>> # 带工具的对话
        >>> response = await service.chat_with_tools(
        ...     "2+2等于多少？",
        ...     tools=[calculator_tool]
        ... )
    """
    
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        初始化服务
        
        Args:
            provider: 厂商标识 (openai, anthropic, zhipu, etc.)
            model: 模型名称
            api_key: API 密钥
            api_base: 自定义 API 地址
            **kwargs: 其他厂商特定参数
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.extra_kwargs = kwargs
        
        # 创建 LangChain Chat Model
        self._chat_model = LangChainChatFactory.create(
            provider=provider,
            model_name=model,
            api_key=api_key,
            api_base=api_base,
            **kwargs
        )
        
        # 工具执行器
        self._tool_executor = ToolExecutor()
    
    @property
    def chat_model(self) -> BaseChatModel:
        """获取底层的 LangChain Chat Model"""
        return self._chat_model
    
    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: List[Dict[str, str]] = None,
        **kwargs
    ) -> ChatResponse:
        """
        简单对话（不带工具）
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 历史消息 [{"role": "user/assistant", "content": "..."}]
            **kwargs: 额外参数（temperature, max_tokens 等）
            
        Returns:
            ChatResponse 对象
        """
        messages = self._build_messages(message, system_prompt, history)
        
        try:
            response = await self._chat_model.ainvoke(messages, **kwargs)
            
            return ChatResponse(
                content=response.content if isinstance(response.content, str) else "",
                model=self.model,
                finish_reason="stop"
            )
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            raise
    
    async def chat_with_tools(
        self,
        message: str,
        tools: List[BaseTool],
        system_prompt: Optional[str] = None,
        history: List[Dict[str, str]] = None,
        max_iterations: int = 10,
        auto_execute_tools: bool = True,
        **kwargs
    ) -> ChatResponse:
        """
        带工具调用的对话
        
        实现 ReAct 风格的工具调用循环：
        1. LLM 生成响应（可能包含工具调用）
        2. 如果有工具调用，执行工具
        3. 将工具结果反馈给 LLM
        4. 重复直到 LLM 不再调用工具
        
        Args:
            message: 用户消息
            tools: 可用工具列表
            system_prompt: 系统提示词
            history: 历史消息
            max_iterations: 最大迭代次数（防止无限循环）
            auto_execute_tools: 是否自动执行工具（False 则只返回工具调用请求）
            **kwargs: 额外参数
            
        Returns:
            ChatResponse 对象（最终响应）
        """
        # 注册工具
        self._tool_executor.register_tools(tools)
        
        # 将 tools 绑定到 model
        model_with_tools = self._chat_model.bind_tools(tools)
        
        # 构建消息
        messages = self._build_messages(message, system_prompt, history)
        
        # 工具调用循环
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            logger.debug(f"Tool call iteration {iteration}")
            
            # 调用 LLM
            response: AIMessage = await model_with_tools.ainvoke(messages, **kwargs)
            
            # 检查是否有工具调用
            if not response.tool_calls:
                # 没有工具调用，返回最终响应
                return ChatResponse(
                    content=response.content if isinstance(response.content, str) else "",
                    model=self.model,
                    finish_reason="stop"
                )
            
            # 如果不自动执行，返回工具调用请求
            if not auto_execute_tools:
                return ChatResponse(
                    content=response.content if isinstance(response.content, str) else "",
                    tool_calls=response.tool_calls,
                    model=self.model,
                    finish_reason="tool_calls"
                )
            
            # 将 AI 响应添加到消息历史
            messages.append(response)
            
            # 执行工具调用
            tool_messages = await self._tool_executor.process_ai_message(response)
            
            # 将工具结果添加到消息历史
            messages.extend(tool_messages)
            
            logger.debug(f"Executed {len(tool_messages)} tool calls")
        
        # 达到最大迭代次数
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return ChatResponse(
            content="抱歉，处理过程中遇到了问题（工具调用次数过多）",
            model=self.model,
            finish_reason="max_iterations"
        )
    
    async def chat_stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: List[Dict[str, str]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式对话
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 历史消息
            **kwargs: 额外参数
            
        Yields:
            文本片段
        """
        messages = self._build_messages(message, system_prompt, history)
        
        try:
            async for chunk in self._chat_model.astream(messages, **kwargs):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            raise
    
    async def chat_with_tools_stream(
        self,
        message: str,
        tools: List[BaseTool],
        system_prompt: Optional[str] = None,
        history: List[Dict[str, str]] = None,
        max_iterations: int = 10,
        on_tool_start: Optional[Callable[[str, Dict], None]] = None,
        on_tool_end: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        带工具调用的流式对话
        
        在流式输出的同时支持工具调用。
        
        Args:
            message: 用户消息
            tools: 可用工具列表
            system_prompt: 系统提示词
            history: 历史消息
            max_iterations: 最大迭代次数
            on_tool_start: 工具开始执行回调
            on_tool_end: 工具执行完成回调
            **kwargs: 额外参数
            
        Yields:
            文本片段
        """
        self._tool_executor.register_tools(tools)
        model_with_tools = self._chat_model.bind_tools(tools)
        messages = self._build_messages(message, system_prompt, history)
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # 收集完整响应（需要完整的 tool_calls 信息）
            full_response = None
            content_parts = []
            
            async for chunk in model_with_tools.astream(messages, **kwargs):
                if chunk.content:
                    content_parts.append(chunk.content)
                    yield chunk.content
                full_response = chunk
            
            # 检查是否有工具调用
            if not full_response or not full_response.tool_calls:
                return
            
            # 将 AI 响应添加到消息历史
            ai_message = AIMessage(
                content="".join(content_parts),
                tool_calls=full_response.tool_calls
            )
            messages.append(ai_message)
            
            # 执行工具调用
            for tc in full_response.tool_calls:
                tool_name = tc.get("name", "")
                tool_args = tc.get("args", {})
                
                if on_tool_start:
                    on_tool_start(tool_name, tool_args)
                
                # 执行
                tool = self._tool_executor.get_tool(tool_name)
                if tool:
                    result = await tool.ainvoke(tool_args)
                    
                    if on_tool_end:
                        on_tool_end(tool_name, str(result))
                    
                    # 添加工具结果
                    messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tc.get("id", ""),
                        name=tool_name
                    ))
        
        logger.warning(f"Max iterations ({max_iterations}) reached in stream")
    
    def _build_messages(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: List[Dict[str, str]] = None
    ) -> List[BaseMessage]:
        """
        构建 LangChain 消息列表
        
        Args:
            message: 当前用户消息
            system_prompt: 系统提示词
            history: 历史消息
            
        Returns:
            BaseMessage 列表
        """
        messages: List[BaseMessage] = []
        
        # 系统提示
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        # 历史消息
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
        
        # 当前消息
        messages.append(HumanMessage(content=message))
        
        return messages


# ============================================================================
# 便捷函数
# ============================================================================

async def quick_chat(
    provider: str,
    model: str,
    api_key: str,
    message: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    快速对话（一次性调用）
    
    适合简单的单轮对话场景。
    
    Args:
        provider: 厂商标识
        model: 模型名称
        api_key: API 密钥
        message: 用户消息
        system_prompt: 系统提示词
        **kwargs: 额外参数
        
    Returns:
        AI 响应文本
        
    Example:
        >>> result = await quick_chat(
        ...     "openai", "gpt-4", "sk-xxx",
        ...     "你好",
        ...     system_prompt="你是一个友好的助手"
        ... )
    """
    service = LangChainService(provider, model, api_key, **kwargs)
    response = await service.chat(message, system_prompt=system_prompt)
    return response.content


async def quick_chat_with_plugins(
    provider: str,
    model: str,
    api_key: str,
    message: str,
    plugins: List["PluginInterface"],
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    快速对话（带插件）
    
    自动将插件转换为 LangChain Tools。
    
    Args:
        provider: 厂商标识
        model: 模型名称
        api_key: API 密钥
        message: 用户消息
        plugins: 插件实例列表
        system_prompt: 系统提示词
        **kwargs: 额外参数
        
    Returns:
        AI 响应文本
    """
    # 将插件转换为 Tools
    tools = [create_tool_from_plugin(p) for p in plugins]
    
    service = LangChainService(provider, model, api_key, **kwargs)
    response = await service.chat_with_tools(
        message,
        tools=tools,
        system_prompt=system_prompt
    )
    return response.content


def get_supported_providers() -> List[str]:
    """获取支持文本生成的厂商列表"""
    return LangChainChatFactory.get_supported_providers()


def is_provider_supported(provider: str) -> bool:
    """检查厂商是否支持"""
    return LangChainChatFactory.is_provider_supported(provider)
