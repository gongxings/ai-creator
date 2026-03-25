"""
Brave Search 插件 - 使用 Brave Search API
"""
from typing import Dict, Any, List
import httpx
import logging

from app.services.plugins.plugin_interface import PluginInterface
from app.services.plugins.registry import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class BraveSearchPlugin(PluginInterface):
    """
    Brave Search 搜索插件
    
    使用 Brave Search API 搜索互联网，获取最新资讯、数据、事实等信息。
    适合用于写作前的资料收集、事实核查、热点追踪等场景。
    免费额度：每月 2000 次请求。
    """
    
    name = "brave_search"
    display_name = "Brave 搜索"
    description = "使用 Brave 搜索引擎搜索互联网，获取最新资讯、数据、事实等信息。适合写作时需要查找最新资料、验证事实、了解热点话题等场景。免费额度每月2000次。"
    version = "1.0.0"
    author = "AI Creator Team"
    category = "search"
    tags = ["联网", "搜索", "信息获取", "资料收集", "Brave"]
    icon = "🦁"
    
    config_schema = {
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "title": "Brave API Key",
                "description": "Brave Search API Key（从 https://brave.com/search/api/ 申请）"
            }
        },
        "required": ["api_key"]
    }
    
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询关键词，可以是问题、短语或关键词组合"
            },
            "max_results": {
                "type": "integer",
                "description": "返回的最大结果数量（1-10）",
                "default": 5,
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["query"]
    }
    
    # Brave Search API 端点
    BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: str = None, **kwargs):
        """
       初始化搜索插件
        
        Args:
            api_key: Brave Search API Key
        """
        super().__init__(**kwargs)
        self.api_key = api_key
    
    async def execute(
        self, 
        query: str, 
        max_results: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数（1-10）
            
        Returns:
            搜索结果字典
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "未配置 Brave API Key，请在插件设置中填写"
            }
        
        try:
            headers = {
                "X-Subscription-Token": self.api_key,
                "Accept": "application/json"
            }
            
            params = {
                "q": query,
                "count": min(max(max_results, 1), 10),
                "text_format": "html"
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.BRAVE_SEARCH_URL,
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 401:
                    return {
                        "success": False,
                        "error": "API Key 无效或已过期"
                    }
                
                if response.status_code == 429:
                    return {
                        "success": False,
                        "error": "搜索请求超出限额，请稍后再试或升级套餐"
                    }
                
                if response.status_code == 403:
                    return {
                        "success": False,
                        "error": "API Key 没有访问权限，请检查是否已激活"
                    }
                
                response.raise_for_status()
                data = response.json()
                
                # 解析搜索结果
                results = []
                web_results = data.get("web", {}).get("results", [])
                
                for item in web_results[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "age": item.get("age", "")
                    })
                
                logger.info(f"Brave Search '{query}' returned {len(results)} results")
                
                return {
                    "success": True,
                    "data": {
                        "query": query,
                        "results": results,
                        "result_count": len(results)
                    }
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "搜索请求超时，请稍后重试"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Brave Search API error: {e}")
            return {
                "success": False,
                "error": f"搜索服务错误: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Brave Search plugin error: {e}")
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}"
            }
