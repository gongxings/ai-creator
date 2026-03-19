"""
图库搜索服务
支持 Unsplash 和 Pexels 图库搜索
"""
import httpx
import logging
import os
from typing import List, Optional, Tuple

from app.schemas.image_stock import (
    ImageSource,
    ImageOrientation,
    ImageItem,
    ImageSearchRequest,
    ImageSearchResponse,
    KeywordSuggestRequest,
    KeywordSuggestResponse,
)

logger = logging.getLogger(__name__)


class ImageStockService:
    """图库搜索服务"""
    
    # Unsplash API 配置
    UNSPLASH_BASE_URL = "https://api.unsplash.com"
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
    
    # Pexels API 配置
    PEXELS_BASE_URL = "https://api.pexels.com/v1"
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    
    @classmethod
    async def search(
        cls,
        request: ImageSearchRequest
    ) -> ImageSearchResponse:
        """
        搜索图库
        
        Args:
            request: 搜索请求
            
        Returns:
            ImageSearchResponse
        """
        images: List[ImageItem] = []
        total = 0
        
        # 根据来源搜索
        if request.source == ImageSource.UNSPLASH:
            images, total = await cls._search_unsplash(request)
        elif request.source == ImageSource.PEXELS:
            images, total = await cls._search_pexels(request)
        else:
            # 搜索全部图库，合并结果
            unsplash_images, unsplash_total = await cls._search_unsplash(request)
            pexels_images, pexels_total = await cls._search_pexels(request)
            
            # 交替合并结果以获得更好的混合效果
            images = cls._interleave_results(unsplash_images, pexels_images)
            total = unsplash_total + pexels_total
        
        return ImageSearchResponse(
            query=request.query,
            total=total,
            page=request.page,
            per_page=request.per_page,
            images=images[:request.per_page],
        )
    
    @classmethod
    async def _search_unsplash(
        cls,
        request: ImageSearchRequest
    ) -> Tuple[List[ImageItem], int]:
        """搜索 Unsplash 图库"""
        if not cls.UNSPLASH_ACCESS_KEY:
            logger.warning("Unsplash API key not configured")
            return [], 0
        
        url = f"{cls.UNSPLASH_BASE_URL}/search/photos"
        params = {
            "query": request.query,
            "page": request.page,
            "per_page": request.per_page,
        }
        
        # 添加可选参数
        if request.orientation:
            params["orientation"] = request.orientation.value
        if request.color:
            params["color"] = request.color
        
        headers = {
            "Authorization": f"Client-ID {cls.UNSPLASH_ACCESS_KEY}",
            "Accept-Version": "v1",
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                images = []
                for item in data.get("results", []):
                    images.append(ImageItem(
                        id=item.get("id", ""),
                        source=ImageSource.UNSPLASH,
                        url=item.get("urls", {}).get("regular", ""),
                        thumb_url=item.get("urls", {}).get("thumb", ""),
                        width=item.get("width", 0),
                        height=item.get("height", 0),
                        alt=item.get("alt_description"),
                        photographer=item.get("user", {}).get("name"),
                        photographer_url=item.get("user", {}).get("links", {}).get("html"),
                        download_url=item.get("links", {}).get("download"),
                        color=item.get("color"),
                    ))
                
                return images, data.get("total", 0)
                
        except httpx.TimeoutException:
            logger.error("Unsplash API timeout")
            return [], 0
        except httpx.HTTPStatusError as e:
            logger.error(f"Unsplash API error: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"Unsplash search error: {e}")
            return [], 0
    
    @classmethod
    async def _search_pexels(
        cls,
        request: ImageSearchRequest
    ) -> Tuple[List[ImageItem], int]:
        """搜索 Pexels 图库"""
        if not cls.PEXELS_API_KEY:
            logger.warning("Pexels API key not configured")
            return [], 0
        
        url = f"{cls.PEXELS_BASE_URL}/search"
        params = {
            "query": request.query,
            "page": request.page,
            "per_page": request.per_page,
        }
        
        # 添加可选参数
        if request.orientation:
            params["orientation"] = request.orientation.value
        
        headers = {
            "Authorization": cls.PEXELS_API_KEY,
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                images = []
                for item in data.get("photos", []):
                    images.append(ImageItem(
                        id=str(item.get("id", "")),
                        source=ImageSource.PEXELS,
                        url=item.get("src", {}).get("large", ""),
                        thumb_url=item.get("src", {}).get("medium", ""),
                        width=item.get("width", 0),
                        height=item.get("height", 0),
                        alt=item.get("alt"),
                        photographer=item.get("photographer"),
                        photographer_url=item.get("photographer_url"),
                        download_url=item.get("src", {}).get("original"),
                        color=item.get("avg_color"),
                    ))
                
                return images, data.get("total_results", 0)
                
        except httpx.TimeoutException:
            logger.error("Pexels API timeout")
            return [], 0
        except httpx.HTTPStatusError as e:
            logger.error(f"Pexels API error: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"Pexels search error: {e}")
            return [], 0
    
    @classmethod
    def _interleave_results(
        cls,
        list1: List[ImageItem],
        list2: List[ImageItem]
    ) -> List[ImageItem]:
        """交替合并两个列表"""
        result = []
        i, j = 0, 0
        while i < len(list1) or j < len(list2):
            if i < len(list1):
                result.append(list1[i])
                i += 1
            if j < len(list2):
                result.append(list2[j])
                j += 1
        return result
    
    @classmethod
    async def suggest_keywords(
        cls,
        request: KeywordSuggestRequest,
        ai_model=None,
    ) -> KeywordSuggestResponse:
        """
        根据文章内容建议搜索关键词
        
        Args:
            request: 关键词建议请求
            ai_model: AI 模型配置
            
        Returns:
            KeywordSuggestResponse
        """
        from app.services.langchain import LangChainService
        import json
        
        prompt = f"""你是一位专业的配图助手，请根据以下文章内容，生成适合在图库（如 Unsplash、Pexels）中搜索的关键词。

## 文章内容
{request.content}

## 要求
1. 生成 {request.count} 个中文关键词
2. 生成对应的 {request.count} 个英文关键词（图库搜索更准确）
3. 关键词应该能搜索到与文章主题相关的高质量图片
4. 关键词要具体、有画面感，避免过于抽象

## 输出格式
严格按照 JSON 格式输出：
```json
{{
  "keywords": ["中文关键词1", "中文关键词2"],
  "keywords_en": ["english keyword 1", "english keyword 2"]
}}
```"""
        
        try:
            if ai_model:
                service = LangChainService(
                    provider=ai_model.provider,
                    model=ai_model.model_name or "gpt-4",
                    api_key=ai_model.api_key,
                    api_base=ai_model.base_url,
                )
            else:
                service = LangChainService(
                    provider="openai",
                    model="gpt-3.5-turbo",
                )
            
            response = await service.chat(prompt)
            
            # 解析响应
            json_str = response.content
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            data = json.loads(json_str.strip())
            
            return KeywordSuggestResponse(
                keywords=data.get("keywords", []),
                keywords_en=data.get("keywords_en", []),
            )
            
        except Exception as e:
            logger.error(f"关键词建议生成失败: {e}")
            # 返回默认关键词
            return cls._get_default_keywords(request.content)
    
    @classmethod
    def _get_default_keywords(cls, content: str) -> KeywordSuggestResponse:
        """获取默认关键词（AI 失败时的兜底）"""
        # 简单提取内容中可能的关键词
        import re
        # 移除标点和空格，获取可能的名词
        words = re.findall(r'[\u4e00-\u9fff]+', content)
        keywords = list(set(words))[:5] if words else ["背景", "图片"]
        
        return KeywordSuggestResponse(
            keywords=keywords,
            keywords_en=["background", "abstract", "business", "technology", "nature"][:len(keywords)],
        )
    
    @classmethod
    def get_sources_status(cls) -> dict:
        """获取图库源配置状态"""
        return {
            "unsplash": {
                "configured": bool(cls.UNSPLASH_ACCESS_KEY),
                "name": "Unsplash",
                "rate_limit": "50次/小时（免费）",
            },
            "pexels": {
                "configured": bool(cls.PEXELS_API_KEY),
                "name": "Pexels",
                "rate_limit": "200次/小时（免费）",
            },
        }
