"""
AI服务基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


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
