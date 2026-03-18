"""
工具执行器

提供工具调用的统一执行层，支持：
- 并行执行多个工具
- 错误处理和重试
- 执行结果格式化
- 工具调用追踪和日志
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain_core.tools import BaseTool
from langchain_core.messages import ToolMessage, AIMessage

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """工具调用请求"""
    id: str                           # 调用 ID（来自 LLM）
    name: str                         # 工具名称
    arguments: Dict[str, Any]         # 调用参数
    
    @classmethod
    def from_openai_format(cls, tool_call: dict) -> "ToolCall":
        """从 OpenAI 格式解析"""
        return cls(
            id=tool_call.get("id", ""),
            name=tool_call.get("function", {}).get("name", ""),
            arguments=json.loads(tool_call.get("function", {}).get("arguments", "{}"))
        )
    
    @classmethod
    def from_langchain_format(cls, tool_call: dict) -> "ToolCall":
        """从 LangChain AIMessage.tool_calls 格式解析"""
        return cls(
            id=tool_call.get("id", ""),
            name=tool_call.get("name", ""),
            arguments=tool_call.get("args", {})
        )


@dataclass
class ToolResult:
    """工具执行结果"""
    call_id: str                      # 对应的调用 ID
    name: str                         # 工具名称
    success: bool                     # 是否成功
    output: str                       # 输出内容（字符串）
    error: Optional[str] = None       # 错误信息
    execution_time_ms: float = 0      # 执行时间（毫秒）
    
    def to_tool_message(self) -> ToolMessage:
        """转换为 LangChain ToolMessage"""
        return ToolMessage(
            content=self.output if self.success else f"Error: {self.error}",
            tool_call_id=self.call_id,
            name=self.name
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "call_id": self.call_id,
            "name": self.name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms
        }


class ToolExecutor:
    """
    工具执行器
    
    管理工具的注册、查找和执行。
    
    Example:
        >>> executor = ToolExecutor()
        >>> executor.register_tool(calculator_tool)
        >>> executor.register_tool(web_search_tool)
        >>> 
        >>> # 执行单个工具调用
        >>> result = await executor.execute(
        ...     ToolCall(id="1", name="calculator", arguments={"expression": "2+2"})
        ... )
        >>> 
        >>> # 批量执行
        >>> results = await executor.execute_batch([call1, call2, call3])
    """
    
    def __init__(self, tools: List[BaseTool] = None):
        """
        初始化执行器
        
        Args:
            tools: 初始工具列表
        """
        self._tools: Dict[str, BaseTool] = {}
        
        if tools:
            for tool in tools:
                self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        注册工具
        
        Args:
            tool: LangChain BaseTool 实例
        """
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def register_tools(self, tools: List[BaseTool]) -> None:
        """批量注册工具"""
        for tool in tools:
            self.register_tool(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有已注册的工具"""
        return list(self._tools.values())
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        获取 OpenAI 格式的工具定义（用于 LLM 调用）
        
        Returns:
            OpenAI tools 格式的列表
        """
        tools_def = []
        for tool in self._tools.values():
            # 获取工具的 schema
            schema = tool.args_schema.model_json_schema() if tool.args_schema else {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            tools_def.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": schema
                }
            })
        
        return tools_def
    
    async def execute(
        self,
        call: ToolCall,
        timeout: float = 30.0
    ) -> ToolResult:
        """
        执行单个工具调用
        
        Args:
            call: 工具调用请求
            timeout: 超时时间（秒）
            
        Returns:
            ToolResult 执行结果
        """
        start_time = datetime.now()
        
        tool = self.get_tool(call.name)
        if not tool:
            return ToolResult(
                call_id=call.id,
                name=call.name,
                success=False,
                output="",
                error=f"未找到工具: {call.name}"
            )
        
        try:
            logger.info(f"Executing tool: {call.name} with args: {call.arguments}")
            
            # 异步执行工具
            result = await asyncio.wait_for(
                tool.ainvoke(call.arguments),
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"Tool {call.name} completed in {execution_time:.2f}ms")
            
            return ToolResult(
                call_id=call.id,
                name=call.name,
                success=True,
                output=str(result),
                execution_time_ms=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.warning(f"Tool {call.name} timed out after {timeout}s")
            
            return ToolResult(
                call_id=call.id,
                name=call.name,
                success=False,
                output="",
                error=f"工具执行超时（{timeout}秒）",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Tool {call.name} error: {e}", exc_info=True)
            
            return ToolResult(
                call_id=call.id,
                name=call.name,
                success=False,
                output="",
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def execute_batch(
        self,
        calls: List[ToolCall],
        parallel: bool = True,
        timeout: float = 30.0
    ) -> List[ToolResult]:
        """
        批量执行工具调用
        
        Args:
            calls: 工具调用列表
            parallel: 是否并行执行
            timeout: 单个工具的超时时间
            
        Returns:
            ToolResult 列表（顺序与输入一致）
        """
        if not calls:
            return []
        
        if parallel:
            # 并行执行
            tasks = [self.execute(call, timeout) for call in calls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理可能的异常
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(ToolResult(
                        call_id=calls[i].id,
                        name=calls[i].name,
                        success=False,
                        output="",
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            # 串行执行
            return [await self.execute(call, timeout) for call in calls]
    
    def execute_from_ai_message(
        self,
        message: AIMessage
    ) -> List[ToolCall]:
        """
        从 LangChain AIMessage 中提取工具调用
        
        Args:
            message: 包含 tool_calls 的 AIMessage
            
        Returns:
            ToolCall 列表
        """
        if not message.tool_calls:
            return []
        
        return [
            ToolCall.from_langchain_format(tc)
            for tc in message.tool_calls
        ]
    
    async def process_ai_message(
        self,
        message: AIMessage,
        parallel: bool = True,
        timeout: float = 30.0
    ) -> List[ToolMessage]:
        """
        处理 AI 消息中的工具调用，返回 ToolMessage 列表
        
        这是一个便捷方法，用于 Agent 循环中处理工具调用。
        
        Args:
            message: AIMessage（可能包含 tool_calls）
            parallel: 是否并行执行
            timeout: 超时时间
            
        Returns:
            ToolMessage 列表，可直接添加到消息历史
        """
        calls = self.execute_from_ai_message(message)
        if not calls:
            return []
        
        results = await self.execute_batch(calls, parallel, timeout)
        return [r.to_tool_message() for r in results]


def parse_tool_calls_from_response(response: dict) -> List[ToolCall]:
    """
    从 OpenAI 格式的响应中解析工具调用
    
    Args:
        response: OpenAI API 响应格式
        
    Returns:
        ToolCall 列表
    """
    tool_calls = []
    
    # 从 choices[0].message.tool_calls 获取
    message = response.get("choices", [{}])[0].get("message", {})
    raw_calls = message.get("tool_calls", [])
    
    for tc in raw_calls:
        try:
            tool_calls.append(ToolCall.from_openai_format(tc))
        except Exception as e:
            logger.warning(f"Failed to parse tool call: {e}")
    
    return tool_calls
