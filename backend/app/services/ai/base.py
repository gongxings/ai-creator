"""
AI服务基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator


class AIServiceBase(ABC):
    """AI服务基类"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化AI服务
        
        Args:
            api_key: API密钥
            config: 额外配置
        """
        self.api_key = api_key
        self.config = config or {}
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大令牌数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成图片
        
        Args:
            prompt: 提示词
            size: 图片尺寸
            quality: 图片质量
            **kwargs: 其他参数
            
        Returns:
            图片URL
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            是否健康
        """
        pass
    
    async def chat_completion(
        self,
        messages: list,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            stream: 是否流式响应
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            {"content": "...", "usage": {...}, "finish_reason": "stop"}
        """
        # 默认实现：将最后一条消息作为prompt调用generate_text
        last_message = messages[-1]["content"] if messages else ""
        content = await self.generate_text(
            prompt=last_message,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return {
            "content": content,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "finish_reason": "stop"
        }
    
    async def chat_completion_stream(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成接口
        
        Yields:
            文本片段
        """
        # 默认实现：获取完整响应然后分块返回
        result = await self.chat_completion(
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        content = result.get("content", "")
        # 按句子/段落分块
        chunk_size = 20
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]
