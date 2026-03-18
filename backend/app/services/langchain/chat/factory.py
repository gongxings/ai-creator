"""
LangChain Chat Model 工厂
支持 16 个厂商的统一创建接口
"""

import logging
from typing import Optional, Any, Dict, Type
from langchain_core.language_models.chat_models import BaseChatModel

from ..config import get_provider_config, AuthType, PROVIDERS

logger = logging.getLogger(__name__)


class LangChainChatFactory:
    """
    LangChain Chat Model 工厂
    
    支持的厂商：
    - 国外：OpenAI, Anthropic, Google, Stability, Replicate
    - 国内：智谱, 通义, 百度, 火山豆包, 腾讯混元, MiniMax, 讯飞, 月之暗面, DeepSeek, 百川
    """
    
    @classmethod
    def create(
        cls,
        provider: str,
        model_name: str,
        api_key: str,
        api_base: Optional[str] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        创建 Chat Model 实例
        
        Args:
            provider: 厂商标识 (openai, anthropic, zhipu, doubao, etc.)
            model_name: 模型名称 (gpt-4, claude-3, glm-4, etc.)
            api_key: API 密钥
            api_base: 自定义 API 地址 (可选，覆盖默认值)
            **kwargs: 其他参数
                - secret_key: 百度、腾讯的第二密钥
                - group_id: MiniMax 的 Group ID
                - app_id, api_secret: 讯飞的认证参数
                
        Returns:
            BaseChatModel 实例
        """
        config = get_provider_config(provider)
        if not config:
            raise ValueError(f"不支持的厂商: {provider}")
        
        # 确定最终使用的 URL
        base_url = api_base if api_base and config.supports_custom_url else config.base_url
        
        # 根据厂商类型创建
        provider_lower = provider.lower()
        
        # 需要自定义实现的厂商
        if config.langchain_class is None:
            return cls._create_custom_model(provider_lower, model_name, api_key, base_url, **kwargs)
        
        # 使用 LangChain 原生支持的厂商
        return cls._create_langchain_model(
            provider_lower, config.langchain_class, model_name, api_key, base_url, **kwargs
        )
    
    @classmethod
    def _create_langchain_model(
        cls,
        provider: str,
        langchain_class: str,
        model_name: str,
        api_key: str,
        base_url: str,
        **kwargs
    ) -> BaseChatModel:
        """创建 LangChain 原生支持的模型"""
        
        # 动态导入模型类
        model_class = cls._import_class(langchain_class)
        
        # 根据不同厂商构建初始化参数
        init_kwargs = cls._build_init_kwargs(provider, model_name, api_key, base_url, **kwargs)
        
        logger.info(f"Creating LangChain model: {provider}/{model_name}")
        return model_class(**init_kwargs)
    
    @classmethod
    def _build_init_kwargs(
        cls,
        provider: str,
        model_name: str,
        api_key: str,
        base_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """根据不同厂商构建初始化参数"""
        
        if provider == "openai":
            params = {
                "model": model_name,
                "api_key": api_key,
            }
            if base_url and base_url != "https://api.openai.com/v1":
                params["base_url"] = base_url
            # OpenRouter 等兼容服务可能需要额外 headers
            if kwargs.get("headers"):
                params["default_headers"] = kwargs["headers"]
            return params
        
        elif provider == "anthropic":
            params = {
                "model": model_name,
                "api_key": api_key,
            }
            if base_url and base_url != "https://api.anthropic.com/v1":
                params["base_url"] = base_url
            return params
        
        elif provider == "google":
            return {
                "model": model_name,
                "google_api_key": api_key,
            }
        
        elif provider == "zhipu":
            return {
                "model": model_name,
                "api_key": api_key,
            }
        
        elif provider == "qwen":
            return {
                "model": model_name,
                "dashscope_api_key": api_key,
            }
        
        elif provider == "baidu":
            return {
                "model": model_name,
                "qianfan_ak": api_key,
                "qianfan_sk": kwargs.get("secret_key", ""),
            }
        
        elif provider == "hunyuan":
            return {
                "model": model_name,
                "hunyuan_secret_id": api_key,
                "hunyuan_secret_key": kwargs.get("secret_key", ""),
            }
        
        elif provider == "minimax":
            return {
                "model": model_name,
                "minimax_api_key": api_key,
                "minimax_group_id": kwargs.get("group_id", ""),
            }
        
        elif provider == "moonshot":
            return {
                "model": model_name,
                "api_key": api_key,
            }
        
        elif provider == "deepseek":
            # DeepSeek 使用 OpenAI 兼容接口
            return {
                "model": model_name,
                "api_key": api_key,
                "base_url": base_url,
            }
        
        elif provider == "baichuan":
            return {
                "model": model_name,
                "baichuan_api_key": api_key,
            }
        
        elif provider == "replicate":
            return {
                "model": model_name,
                "replicate_api_token": api_key,
            }
        
        else:
            # 默认参数
            return {
                "model": model_name,
                "api_key": api_key,
            }
    
    @classmethod
    def _create_custom_model(
        cls,
        provider: str,
        model_name: str,
        api_key: str,
        base_url: str,
        **kwargs
    ) -> BaseChatModel:
        """创建需要自定义实现的模型"""
        
        if provider == "doubao":
            from .providers.doubao import ChatDoubao
            return ChatDoubao(
                model=model_name,
                api_key=api_key,
                api_base=base_url,
            )
        
        elif provider == "spark":
            from .providers.spark import ChatSpark
            return ChatSpark(
                model=model_name,
                app_id=kwargs.get("app_id", ""),
                api_key=api_key,
                api_secret=kwargs.get("api_secret", ""),
            )
        
        elif provider == "stability":
            # Stability AI 主要用于图片，不支持 chat
            raise ValueError("Stability AI 不支持文本对话，请使用图片生成功能")
        
        else:
            raise ValueError(f"未实现的自定义厂商: {provider}")
    
    @classmethod
    def _import_class(cls, class_path: str) -> Type[BaseChatModel]:
        """动态导入类"""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import {class_path}: {e}")
            raise ImportError(f"无法导入模型类: {class_path}. 请确保已安装相应的 LangChain 包。") from e
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """获取支持的厂商列表"""
        from ..config import get_text_providers
        return get_text_providers()
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """检查厂商是否支持"""
        config = get_provider_config(provider)
        return config is not None
