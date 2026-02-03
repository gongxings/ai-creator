"""
OAuth平台适配器
"""
from .base import BasePlatformAdapter
from .qwen import QwenAdapter
from .openai import OpenAIAdapter
from .baidu import BaiduAdapter
from .zhipu import ZhipuAdapter
from .spark import SparkAdapter
from .claude import ClaudeAdapter
from .gemini import GeminiAdapter
from .doubao import DoubaoAdapter

__all__ = [
    'BasePlatformAdapter',
    'QwenAdapter',
    'OpenAIAdapter',
    'BaiduAdapter',
    'ZhipuAdapter',
    'SparkAdapter',
    'ClaudeAdapter',
    'GeminiAdapter',
    'DoubaoAdapter',
]
