"""
火山引擎/豆包 Chat Model
支持 Doubao 系列模型
"""

import json
import logging
from typing import Any, Dict, Iterator, List, Optional

import httpx
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

logger = logging.getLogger(__name__)


class ChatDoubao(BaseChatModel):
    """
    火山引擎/豆包 Chat Model
    
    支持的模型:
    - doubao-1.5-pro-256k / doubao-1.5-pro-32k
    - doubao-pro-256k / doubao-pro-32k / doubao-pro-4k
    - doubao-lite-32k / doubao-lite-4k
    
    使用示例:
        model = ChatDoubao(
            model="doubao-pro-32k",
            api_key="your-ark-api-key",
            api_base="https://ark.cn-beijing.volces.com/api/v3"
        )
        response = model.invoke("你好")
    """
    
    model: str = "doubao-pro-32k"
    api_key: str = ""
    api_base: str = "https://ark.cn-beijing.volces.com/api/v3"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: float = 120.0
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        return "doubao"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "api_base": self.api_base,
            "temperature": self.temperature,
        }
    
    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """将 LangChain 消息转换为 API 格式"""
        converted = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                converted.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                converted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                converted.append({"role": "assistant", "content": msg.content})
            else:
                # 默认作为用户消息
                converted.append({"role": "user", "content": str(msg.content)})
        return converted
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天响应"""
        
        # 转换消息
        api_messages = self._convert_messages(messages)
        
        # 构建请求
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": kwargs.get("temperature", self.temperature),
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop
        
        # 发送请求
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Doubao API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Doubao API 调用失败: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Doubao API error: {e}")
            raise ValueError(f"Doubao API 调用失败: {e}")
        
        # 解析响应
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        
        # 构建返回结果
        ai_message = AIMessage(content=content)
        generation = ChatGeneration(message=ai_message)
        
        # 使用信息
        usage = data.get("usage", {})
        
        return ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": usage,
                "model_name": self.model,
            }
        )
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """异步生成聊天响应"""
        
        # 转换消息
        api_messages = self._convert_messages(messages)
        
        # 构建请求
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": kwargs.get("temperature", self.temperature),
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop
        
        # 发送异步请求
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Doubao API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"Doubao API 调用失败: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Doubao API error: {e}")
            raise ValueError(f"Doubao API 调用失败: {e}")
        
        # 解析响应
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        
        # 构建返回结果
        ai_message = AIMessage(content=content)
        generation = ChatGeneration(message=ai_message)
        
        # 使用信息
        usage = data.get("usage", {})
        
        return ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": usage,
                "model_name": self.model,
            }
        )
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """流式生成"""
        
        # 转换消息
        api_messages = self._convert_messages(messages)
        
        # 构建请求
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": True,
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop
        
        # 发送流式请求
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                chunk = ChatGenerationChunk(
                                    message=AIMessage(content=content)
                                )
                                yield chunk
                                
                                if run_manager:
                                    run_manager.on_llm_new_token(content)
                        except json.JSONDecodeError:
                            continue
    
    def bind_tools(self, tools: List[Any], **kwargs) -> "ChatDoubao":
        """绑定工具（豆包支持 function calling）"""
        # TODO: 实现工具绑定
        logger.warning("ChatDoubao.bind_tools not fully implemented yet")
        return self
