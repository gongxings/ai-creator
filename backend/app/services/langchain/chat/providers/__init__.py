"""
自定义 Chat Model Providers
这些厂商 LangChain 没有原生支持，需要自定义实现
"""

from .doubao import ChatDoubao
from .spark import ChatSpark

__all__ = ["ChatDoubao", "ChatSpark"]
