"""
OpenAI服务实现
"""
from typing import Optional, AsyncGenerator, List, Dict, Any, Callable, Awaitable
import httpx
import json
import asyncio
import logging

from .base import AIServiceBase

logger = logging.getLogger(__name__)

# Tool executor 类型定义
ToolExecutor = Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]


class OpenAIService(AIServiceBase):
    """OpenAI服务"""
    
    def __init__(self, api_key: str, config: Optional[dict] = None):
        super().__init__(api_key, config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1") if config else "https://api.openai.com/v1"
        self.model = config.get("model", "gpt-4") if config else "gpt-4"
        self.image_model = config.get("image_model", "dall-e-3") if config else "dall-e-3"
        self.max_retries = 3
        self.retry_delay = 5  # 重试间隔秒数
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本，支持429限流重试"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # OpenRouter 需要额外的 headers
        if "openrouter" in self.base_url.lower():
            headers["HTTP-Referer"] = "http://localhost:3001"
            headers["X-Title"] = "AI Creator"
        
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens or 2000,
            "temperature": temperature or 0.7,
        }
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=request_data,
                        timeout=120.0,
                    )
                    
                    # 如果是429限流错误，进行重试
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                        logger.warning(f"Rate limited (429), attempt {attempt + 1}/{self.max_retries}, waiting {retry_after}s...")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            response.raise_for_status()
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # 处理返回内容
                    content = data["choices"][0]["message"].get("content")
                    if content is None:
                        # 某些模型可能在reasoning字段返回内容
                        reasoning = data["choices"][0]["message"].get("reasoning")
                        if reasoning:
                            content = reasoning
                        else:
                            content = ""
                    
                    return content
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429 and attempt < self.max_retries - 1:
                    logger.warning(f"Rate limited (429), attempt {attempt + 1}/{self.max_retries}, retrying...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
            except Exception as e:
                last_error = e
                logger.error(f"API call failed: {e}")
                raise
        
        # 所有重试都失败
        raise last_error or Exception("所有重试都失败")
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成图片"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": kwargs.get("model", self.image_model),
                    "prompt": prompt,
                    "size": size or "1024x1024",
                    "quality": quality or "standard",
                    "n": 1,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["url"]
    
    async def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def chat_completion(
        self,
        messages: list,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        聊天完成接口（非流式）
        
        Args:
            messages: 消息列表
            stream: 是否流式（此方法不支持，使用 chat_completion_stream）
            temperature: 温度
            max_tokens: 最大 token 数
            tools: OpenAI function calling 工具列表
            tool_choice: 工具选择策略 ("auto", "none", "required", 或具体函数名)
            **kwargs: 其他参数
            
        Returns:
            {
                "content": str | None,  # 文本内容（可能为 None 如果是工具调用）
                "tool_calls": list | None,  # 工具调用列表
                "usage": dict,
                "finish_reason": str  # "stop", "tool_calls", etc.
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # OpenRouter 需要额外的 headers
        if "openrouter" in self.base_url.lower():
            headers["HTTP-Referer"] = "http://localhost:3001"
            headers["X-Title"] = "AI Creator"
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # 添加 tools 支持
        if tools:
            payload["tools"] = tools
            if tool_choice:
                if tool_choice in ("auto", "none", "required"):
                    payload["tool_choice"] = tool_choice
                else:
                    # 指定具体函数
                    payload["tool_choice"] = {
                        "type": "function",
                        "function": {"name": tool_choice}
                    }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            usage = data.get("usage", {})
            message = choice["message"]
            
            return {
                "content": message.get("content"),
                "tool_calls": message.get("tool_calls"),
                "usage": usage,
                "finish_reason": choice.get("finish_reason", "stop")
            }
    
    async def chat_completion_stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成接口 - 真正的流式响应"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
    
    async def chat_with_tool_execution(
        self,
        messages: list,
        tools: List[Dict[str, Any]],
        tool_executor: ToolExecutor,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带工具执行的聊天接口
        
        自动处理工具调用循环：AI 请求工具 -> 执行工具 -> 返回结果 -> AI 继续
        
        Args:
            messages: 消息列表（会被修改，添加工具调用历史）
            tools: OpenAI function calling 工具列表
            tool_executor: 工具执行函数，签名: async (tool_name, arguments) -> result
            temperature: 温度
            max_tokens: 最大 token 数
            max_iterations: 最大工具调用迭代次数（防止无限循环）
            **kwargs: 其他参数
            
        Returns:
            {
                "content": str,  # 最终文本回复
                "tool_results": list,  # 所有工具调用结果
                "iterations": int,  # 迭代次数
                "usage": dict  # 累计 token 使用量
            }
        """
        tool_results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 调用 AI
            result = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                tool_choice="auto",
                **kwargs
            )
            
            # 累计 token 使用
            usage = result.get("usage", {})
            total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
            total_usage["total_tokens"] += usage.get("total_tokens", 0)
            
            # 检查是否需要调用工具
            if result.get("finish_reason") == "tool_calls" or result.get("tool_calls"):
                tool_calls = result["tool_calls"]
                
                # 将 assistant 的工具调用请求添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": result.get("content"),
                    "tool_calls": tool_calls
                })
                
                # 执行每个工具调用
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                    
                    # 执行工具
                    try:
                        tool_result = await tool_executor(tool_name, arguments)
                        tool_results.append({
                            "tool_name": tool_name,
                            "arguments": arguments,
                            "result": tool_result,
                            "success": tool_result.get("success", True)
                        })
                        
                        # 将工具结果添加到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error: {tool_name} - {e}")
                        error_result = {"success": False, "error": str(e)}
                        tool_results.append({
                            "tool_name": tool_name,
                            "arguments": arguments,
                            "result": error_result,
                            "success": False
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(error_result, ensure_ascii=False)
                        })
                
                # 继续循环，让 AI 处理工具结果
                continue
            
            # AI 完成回复（没有工具调用）
            return {
                "content": result.get("content", ""),
                "tool_results": tool_results,
                "iterations": iteration,
                "usage": total_usage
            }
        
        # 达到最大迭代次数
        logger.warning(f"Max tool iterations ({max_iterations}) reached")
        return {
            "content": result.get("content", ""),
            "tool_results": tool_results,
            "iterations": iteration,
            "usage": total_usage,
            "warning": f"达到最大工具调用次数 ({max_iterations})"
        }
