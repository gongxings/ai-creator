"""
讯飞星火 Chat Model
使用 WebSocket 协议通信
"""

import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime
from time import mktime
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)


class ChatSpark(BaseChatModel):
    """
    讯飞星火 Chat Model
    
    支持的模型:
    - spark-4.0-ultra (v4.0)
    - spark-max (v3.5)  
    - spark-pro (v3.1)
    - spark-lite (v1.1)
    
    使用示例:
        model = ChatSpark(
            model="spark-max",
            app_id="your-app-id",
            api_key="your-api-key",
            api_secret="your-api-secret"
        )
        response = model.invoke("你好")
    """
    
    model: str = "spark-max"
    app_id: str = ""
    api_key: str = ""
    api_secret: str = ""
    temperature: float = 0.5
    max_tokens: int = 4096
    timeout: float = 60.0
    
    # 模型版本映射
    MODEL_VERSIONS = {
        "spark-4.0-ultra": ("v4.0", "generalv3.5"),
        "spark-max": ("v3.5", "generalv3.5"),
        "spark-pro": ("v3.1", "generalv3"),
        "spark-lite": ("v1.1", "general"),
    }
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        return "spark"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "app_id": self.app_id,
            "temperature": self.temperature,
        }
    
    def _get_ws_url(self) -> str:
        """生成 WebSocket 鉴权 URL"""
        version, _ = self.MODEL_VERSIONS.get(self.model, ("v3.5", "generalv3.5"))
        host = "spark-api.xf-yun.com"
        path = f"/{version}/chat"
        
        # 生成 RFC1123 格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        # 构建签名原文
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # HMAC-SHA256 签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode()
        
        # 构建 authorization
        authorization_origin = (
            f'api_key="{self.api_key}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        # 构建 URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": host,
        }
        url = f"wss://{host}{path}?{urlencode(params)}"
        return url
    
    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """将 LangChain 消息转换为 API 格式"""
        converted = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                # 讯飞系统消息放在第一条 user 消息之前
                converted.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                converted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                converted.append({"role": "assistant", "content": msg.content})
            else:
                converted.append({"role": "user", "content": str(msg.content)})
        return converted
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天响应（同步，使用 websockets）"""
        import websockets.sync.client as ws_sync
        
        # 转换消息
        api_messages = self._convert_messages(messages)
        
        # 获取模型域名
        _, domain = self.MODEL_VERSIONS.get(self.model, ("v3.5", "generalv3.5"))
        
        # 构建请求数据
        request_data = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                }
            },
            "payload": {
                "message": {
                    "text": api_messages
                }
            }
        }
        
        # 获取 WebSocket URL
        ws_url = self._get_ws_url()
        
        # 收集响应
        full_content = ""
        usage = {}
        
        try:
            with ws_sync.connect(ws_url) as ws:
                ws.send(json.dumps(request_data))
                
                while True:
                    response = ws.recv()
                    data = json.loads(response)
                    
                    # 检查错误
                    header = data.get("header", {})
                    if header.get("code") != 0:
                        error_msg = header.get("message", "Unknown error")
                        raise ValueError(f"讯飞星火 API 错误: {error_msg}")
                    
                    # 提取内容
                    payload = data.get("payload", {})
                    choices = payload.get("choices", {})
                    text = choices.get("text", [])
                    
                    for item in text:
                        content = item.get("content", "")
                        full_content += content
                    
                    # 检查是否结束
                    status = choices.get("status")
                    if status == 2:  # 结束
                        # 提取使用信息
                        usage_data = payload.get("usage", {}).get("text", {})
                        usage = {
                            "prompt_tokens": usage_data.get("prompt_tokens", 0),
                            "completion_tokens": usage_data.get("completion_tokens", 0),
                            "total_tokens": usage_data.get("total_tokens", 0),
                        }
                        break
                        
        except Exception as e:
            logger.error(f"Spark API error: {e}")
            raise ValueError(f"讯飞星火 API 调用失败: {e}")
        
        # 构建返回结果
        ai_message = AIMessage(content=full_content)
        generation = ChatGeneration(message=ai_message)
        
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
        import websockets
        
        # 转换消息
        api_messages = self._convert_messages(messages)
        
        # 获取模型域名
        _, domain = self.MODEL_VERSIONS.get(self.model, ("v3.5", "generalv3.5"))
        
        # 构建请求数据
        request_data = {
            "header": {
                "app_id": self.app_id,
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                }
            },
            "payload": {
                "message": {
                    "text": api_messages
                }
            }
        }
        
        # 获取 WebSocket URL
        ws_url = self._get_ws_url()
        
        # 收集响应
        full_content = ""
        usage = {}
        
        try:
            async with websockets.connect(ws_url) as ws:
                await ws.send(json.dumps(request_data))
                
                while True:
                    response = await ws.recv()
                    data = json.loads(response)
                    
                    # 检查错误
                    header = data.get("header", {})
                    if header.get("code") != 0:
                        error_msg = header.get("message", "Unknown error")
                        raise ValueError(f"讯飞星火 API 错误: {error_msg}")
                    
                    # 提取内容
                    payload = data.get("payload", {})
                    choices = payload.get("choices", {})
                    text = choices.get("text", [])
                    
                    for item in text:
                        content = item.get("content", "")
                        full_content += content
                    
                    # 检查是否结束
                    status = choices.get("status")
                    if status == 2:  # 结束
                        # 提取使用信息
                        usage_data = payload.get("usage", {}).get("text", {})
                        usage = {
                            "prompt_tokens": usage_data.get("prompt_tokens", 0),
                            "completion_tokens": usage_data.get("completion_tokens", 0),
                            "total_tokens": usage_data.get("total_tokens", 0),
                        }
                        break
                        
        except Exception as e:
            logger.error(f"Spark API error: {e}")
            raise ValueError(f"讯飞星火 API 调用失败: {e}")
        
        # 构建返回结果
        ai_message = AIMessage(content=full_content)
        generation = ChatGeneration(message=ai_message)
        
        return ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": usage,
                "model_name": self.model,
            }
        )
    
    def bind_tools(self, tools: List[Any], **kwargs) -> "ChatSpark":
        """绑定工具（讯飞支持有限的 function calling）"""
        logger.warning("ChatSpark.bind_tools not fully implemented yet")
        return self
