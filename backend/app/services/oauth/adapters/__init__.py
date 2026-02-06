"""
OAuth平台适配器
"""
from typing import Dict, Any, Optional
from .base import PlatformAdapter
from .qwen import QwenAdapter
from .chatqwen import ChatQwenAdapter
from .qianwen import QianwenAdapter
from .openai import OpenAIAdapter
from .baidu import BaiduAdapter
from .zhipu import ZhipuAdapter
from .spark import SparkAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .doubao import DoubaoAdapter

# 为了向后兼容，保留旧名称
BasePlatformAdapter = PlatformAdapter

# 平台适配器映射
ADAPTER_MAP = {
    'qwen': QwenAdapter,
    'chatqwen': ChatQwenAdapter,  # 新版通义千问 (chat.qwen.ai)
    'qianwen': QianwenAdapter,  # 通义千问 (www.qianwen.com)
    'openai': OpenAIAdapter,
    'baidu': BaiduAdapter,
    'zhipu': ZhipuAdapter,
    'spark': SparkAdapter,
    'claude': ClaudeAdapter,
    'gemini': GeminiAdapter,
    'doubao': DoubaoAdapter,
}

# 兼容旧名称
PLATFORM_ADAPTERS = ADAPTER_MAP


def get_adapter(platform_id: str, config: Dict[str, Any]) -> Optional[PlatformAdapter]:
    """
    获取平台适配器实例
    
    Args:
        platform_id: 平台ID
        config: 平台配置
        
    Returns:
        适配器实例，如果平台不支持则返回None
    """
    adapter_class = ADAPTER_MAP.get(platform_id)
    if adapter_class:
        return adapter_class(platform_id, config)
    return None


def get_supported_platforms():
    """
    获取支持的平台列表
    
    Returns:
        支持的平台ID列表
    """
    return list(ADAPTER_MAP.keys())


__all__ = [
    'PlatformAdapter',
    'BasePlatformAdapter',
    'QwenAdapter',
    'ChatQwenAdapter',
    'QianwenAdapter',
    'OpenAIAdapter',
    'BaiduAdapter',
    'ZhipuAdapter',
    'SparkAdapter',
    'ClaudeAdapter',
    'GeminiAdapter',
    'DoubaoAdapter',
    'ADAPTER_MAP',
    'PLATFORM_ADAPTERS',
    'get_adapter',
    'get_supported_platforms',
]
