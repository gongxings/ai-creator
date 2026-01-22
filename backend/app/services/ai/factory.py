"""
AI服务工厂
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.ai_model import AIModel
from app.core.security import decrypt_api_key
from .base import AIServiceBase
from .openai_service import OpenAIService
from .anthropic_service import AnthropicService
from .zhipu_service import ZhipuService
from .baidu_service import BaiduService
from .qwen_service import QwenService


class AIServiceFactory:
    """AI服务工厂"""
    
    # 服务提供商映射
    SERVICE_MAP = {
        "openai": OpenAIService,
        "anthropic": AnthropicService,
        "zhipu": ZhipuService,
        "baidu": BaiduService,
        "qwen": QwenService,
    }
    
    @classmethod
    def create_service(
        cls,
        provider: str,
        api_key: str,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> AIServiceBase:
        """
        创建AI服务实例
        
        Args:
            provider: 服务提供商
            api_key: API密钥
            model_name: 模型名称
            base_url: API基础URL
            **kwargs: 其他参数（如百度的secret_key）
            
        Returns:
            AI服务实例
            
        Raises:
            ValueError: 不支持的服务提供商
        """
        service_class = cls.SERVICE_MAP.get(provider.lower())
        if not service_class:
            raise ValueError(f"不支持的AI服务提供商: {provider}")
        
        # 根据不同服务构造参数
        if provider.lower() == "baidu":
            # 百度需要secret_key
            secret_key = kwargs.get("secret_key", "")
            return service_class(api_key, secret_key, model_name or "ernie-bot-4")
        elif provider.lower() == "zhipu":
            # 智谱AI
            return service_class(api_key, model_name or "glm-4", base_url or "https://open.bigmodel.cn/api/paas/v4")
        elif provider.lower() == "anthropic":
            # Anthropic
            return service_class(api_key, model_name or "claude-3-sonnet-20240229")
        elif provider.lower() == "qwen":
            # 阿里通义千问
            return service_class(api_key, model_name or "qwen-turbo", base_url or "https://dashscope.aliyuncs.com/api/v1")
        else:
            # OpenAI及兼容接口
            return service_class(api_key, model_name or "gpt-4", base_url)
    
    @classmethod
    def create_from_model(
        cls,
        db: Session,
        model_id: int
    ) -> AIServiceBase:
        """
        从数据库模型创建AI服务实例
        
        Args:
            db: 数据库会话
            model_id: 模型ID
            
        Returns:
            AI服务实例
            
        Raises:
            ValueError: 模型不存在或未启用
        """
        model = db.query(AIModel).filter(
            AIModel.id == model_id,
            AIModel.is_active == True
        ).first()
        
        if not model:
            raise ValueError("AI模型不存在或未启用")
        
        # 解密API密钥
        api_key = decrypt_api_key(model.api_key)
        
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
