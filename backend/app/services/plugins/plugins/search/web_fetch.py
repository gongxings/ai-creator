"""
网页抓取插件 - 获取指定 URL 的网页内容
"""
from typing import Dict, Any
import httpx
import re
import logging

from app.services.plugins.plugin_interface import PluginInterface
from app.services.plugins.registry import register_plugin

logger = logging.getLogger(__name__)


@register_plugin
class WebFetchPlugin(PluginInterface):
    """
    网页抓取插件
    
    获取指定 URL 的网页内容，提取正文并返回。
    适合用于深入阅读搜索结果、获取特定页面的详细内容。
    """
    
    name = "web_fetch"
    display_name = "网页抓取"
    description = "获取指定 URL 的网页内容，提取正文文本。适合深入阅读搜索结果中的某个页面、获取特定网站的详细内容。"
    version = "1.0.0"
    author = "AI Creator Team"
    category = "search"
    tags = ["抓取", "网页", "内容提取", "阅读"]
    icon = "📄"
    
    config_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "要抓取的网页 URL"
            },
            "max_length": {
                "type": "integer",
                "description": "返回内容的最大字符数",
                "default": 5000,
                "minimum": 500,
                "maximum": 20000
            }
        },
        "required": ["url"]
    }
    
    # 常见的 User-Agent
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def execute(
        self, 
        url: str, 
        max_length: int = 5000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        抓取网页内容
        
        Args:
            url: 网页 URL
            max_length: 最大内容长度
            
        Returns:
            网页内容字典
        """
        # 验证 URL
        if not url or not url.startswith(('http://', 'https://')):
            return {
                "success": False,
                "error": "无效的 URL，必须以 http:// 或 https:// 开头"
            }
        
        try:
            headers = {
                "User-Agent": self.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            
            async with httpx.AsyncClient(
                timeout=20.0, 
                follow_redirects=True,
                max_redirects=5
            ) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # 获取内容类型
                content_type = response.headers.get("content-type", "")
                
                if "text/html" not in content_type.lower():
                    return {
                        "success": False,
                        "error": f"不支持的内容类型: {content_type}"
                    }
                
                html = response.text
                
                # 提取标题
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else ""
                
                # 提取正文（简单版本，移除标签）
                # 移除 script, style, nav, header, footer 等标签
                html = re.sub(r'<(script|style|nav|header|footer|aside|noscript)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                
                # 移除所有 HTML 标签
                text = re.sub(r'<[^>]+>', ' ', html)
                
                # 清理空白字符
                text = re.sub(r'\s+', ' ', text).strip()
                
                # 解码 HTML 实体
                import html as html_module
                text = html_module.unescape(text)
                
                # 截断内容
                if len(text) > max_length:
                    text = text[:max_length] + "..."
                
                logger.info(f"Fetched {url}, title: {title}, length: {len(text)}")
                
                return {
                    "success": True,
                    "data": {
                        "url": str(response.url),  # 可能经过重定向
                        "title": title,
                        "content": text,
                        "content_length": len(text),
                        "status_code": response.status_code
                    }
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "请求超时，网页加载时间过长"
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP 错误: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Web fetch error for {url}: {e}")
            return {
                "success": False,
                "error": f"抓取失败: {str(e)}"
            }
