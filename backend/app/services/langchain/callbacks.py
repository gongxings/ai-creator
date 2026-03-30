"""
LangChain 回调处理器 - 模型调用监控

自动捕获 LLM 调用事件，记录到数据库。
支持 chat 类型调用的 token 统计和输入输出监控。
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)


class UsageCallbackHandler(BaseCallbackHandler):
    """
    模型调用监控回调处理器
    
    在 LangChain 调用的开始和结束时自动触发，
    记录完整的输入输出、token 消耗和响应时间。
    """
    
    def __init__(
        self,
        user_id: int,
        ai_model_id: int,
        provider: str,
        model_name: str,
        tool: str,
        request_type: str = "chat",
        creation_id: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.user_id = user_id
        self.ai_model_id = ai_model_id
        self.provider = provider
        self.model_name = model_name
        self.tool = tool
        self.request_type = request_type
        self.creation_id = creation_id
        self.extra_data = extra_data or {}
        
        # 运行时状态
        self._start_time: Optional[float] = None
        self._input_messages: Optional[str] = None
        self._response_content: Optional[str] = None
        self._usage_metadata: Dict[str, int] = {}
        self._status: str = "success"
        self._error_message: Optional[str] = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM 调用开始"""
        self._start_time = time.time()
        
        # 提取输入内容
        messages = kwargs.get("invocation_params", {}).get("messages", [])
        if messages:
            self._input_messages = str(messages)
        elif prompts:
            self._input_messages = "\n".join(prompts)
        else:
            self._input_messages = str(kwargs.get("input", ""))
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """LLM 调用结束"""
        if self._start_time is None:
            return
        
        response_time_ms = int((time.time() - self._start_time) * 1000)
        
        # 提取输出内容
        if response.generations:
            gen = response.generations[0]
            if gen:
                self._response_content = gen[0].text
        
        # 提取 token 使用量
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            if usage:
                self._prompt_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
                self._completion_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
                self._total_tokens = usage.get("total_tokens", self._prompt_tokens + self._completion_tokens)
                self._usage_metadata = {
                    "prompt_tokens": self._prompt_tokens,
                    "completion_tokens": self._completion_tokens,
                    "total_tokens": self._total_tokens,
                }
        
        # 提取 usage_metadata（部分厂商支持）
        if response.generations and response.generations[0]:
            gen = response.generations[0][0]
            if hasattr(gen, "generation_info") and gen.generation_info:
                usage_meta = gen.generation_info.get("usage_metadata", {})
                if usage_meta and not self._usage_metadata:
                    self._prompt_tokens = usage_meta.get("input_tokens", 0)
                    self._completion_tokens = usage_meta.get("output_tokens", 0)
                    self._total_tokens = usage_meta.get("total_tokens", 0)
                    self._usage_metadata = {
                        "prompt_tokens": self._prompt_tokens,
                        "completion_tokens": self._completion_tokens,
                        "total_tokens": self._total_tokens,
                    }
        
        # 写入数据库
        self._save_to_db(response_time_ms)
    
    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """LLM 调用错误"""
        self._status = "failed"
        self._error_message = str(error)[:2000]
        
        response_time_ms = 0
        if self._start_time:
            response_time_ms = int((time.time() - self._start_time) * 1000)
        
        self._save_to_db(response_time_ms)
    
    def _save_to_db(self, response_time_ms: int) -> None:
        """保存日志到数据库"""
        try:
            from app.core.database import SessionLocal
            from app.models.model_usage_log import AIModelUsageLog
            
            db = SessionLocal()
            try:
                log = AIModelUsageLog(
                    user_id=self.user_id,
                    ai_model_id=self.ai_model_id,
                    creation_id=self.creation_id,
                    provider=self.provider,
                    model_name=self.model_name,
                    tool=self.tool,
                    request_type=self.request_type,
                    input_content=self._input_messages,
                    output_content=self._response_content,
                    prompt_tokens=getattr(self, "_prompt_tokens", 0) or 0,
                    completion_tokens=getattr(self, "_completion_tokens", 0) or 0,
                    total_tokens=getattr(self, "_total_tokens", 0) or 0,
                    status=self._status,
                    error_message=self._error_message,
                    response_time_ms=response_time_ms,
                    extra_data=self.extra_data if self.extra_data else None,
                )
                db.add(log)
                db.commit()
                logger.debug(
                    f"Usage log saved: provider={self.provider}, model={self.model_name}, "
                    f"tokens={getattr(self, '_total_tokens', 0)}, tool={self.tool}, status={self._status}"
                )
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to save usage log: {e}", exc_info=True)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to create db session for usage log: {e}", exc_info=True)
