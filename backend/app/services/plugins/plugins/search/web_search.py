"""
网页搜索插件 - 使用 Bing Search API
"""
from typing import Dict, Any, List
import httpx
import logging

from app.services.plugins.plugin_interface import PluginInterface
from app.services.plugins.registry import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class WebSearchPlugin(PluginInterface):
    """
    网页搜索插件
    
    使用 Bing Search API 搜索互联网，获取最新资讯、数据、事实等信息。
    适合用于写作前的资料收集、事实核查、热点追踪等场景。
    """
    
    name = "web_search"
    display_name = "网页搜索"
    description = "使用 Bing 搜索引擎搜索互联网，获取最新资讯、数据、事实等信息。适合写作时需要查找最新资料、验证事实、了解热点话题等场景。"
    version = "1.0.0"
    author = "AI Creator Team"
    category = "search"
    tags = ["联网", "搜索", "信息获取", "资料收集"]
    icon = "🔍"
    
    config_schema = {
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "title": "Bing API Key",
                "description": "Azure Cognitive Services 的 Bing Search API Key（从 Azure 门户获取）"
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
    
    # Bing Search API 端点
    BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
    
    def __init__(self, api_key: str = None, **kwargs):
        """
        初始化搜索插件
        
        Args:
            api_key: Bing Search API Key
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
                "error": "未配置 Bing API Key，请在插件设置中填写"
            }
        
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key
            }
            
            params = {
                "q": query,
                "count": min(max(max_results, 1), 10),
                "responseFilter": "Webpages",
                "textFormat": "HTML",
                "mkt": "zh-CN"  # 中文市场
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.BING_SEARCH_URL,
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
                        "error": "搜索请求过于频繁，请稍后再试"
                    }
                
                response.raise_for_status()
                data = response.json()
                
                # 解析搜索结果
                results = []
                web_pages = data.get("webPages", {})
                
                for item in web_pages.get("value", [])[:max_results]:
                    results.append({
                        "title": item.get("name", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "date_published": item.get("datePublished", "")
                    })
                
                total_matches = web_pages.get("totalEstimatedMatches", 0)
                
                logger.info(f"Search '{query}' returned {len(results)} results")
                
                return {
                    "success": True,
                    "data": {
                        "query": query,
                        "total_estimated_matches": total_matches,
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
            logger.error(f"Bing Search API error: {e}")
            return {
                "success": False,
                "error": f"搜索服务错误: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Search plugin error: {e}")
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}"
            }
