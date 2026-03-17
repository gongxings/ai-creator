"""
搜索类插件
"""
from app.services.plugins.plugins.search.web_search import WebSearchPlugin
from app.services.plugins.plugins.search.web_fetch import WebFetchPlugin

__all__ = ["WebSearchPlugin", "WebFetchPlugin"]
