"""
今日头条平台发布器
"""
from typing import Dict, Any, Optional
import httpx
from .base import BasePlatform


class ToutiaoPlatform(BasePlatform):
    """今日头条平台发布器"""
    
    def __init__(self, access_token: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(access_token, config)
        self.base_url = "https://open.toutiao.com/api"
    
    async def publish_text(
        self,
        content: str,
        title: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布文字内容（微头条）
        
        Args:
            content: 文字内容
            title: 标题（可选）
            **kwargs: 其他参数
            
        Returns:
            发布结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "content": content,
                "content_type": "micro"  # 微头条
            }
            
            if title:
                data["title"] = title
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/micro/create",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("err_no") == 0:
                    item_id = result.get("data", {}).get("item_id")
                    return {
                        "success": True,
                        "platform_id": item_id,
                        "url": f"https://www.toutiao.com/item/{item_id}/",
                        "message": "发布成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_tips", "发布失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"今日头条发布失败: {str(e)}"
            }
    
    async def publish_image(
        self,
        content: str,
        images: list,
        title: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布图文内容
        
        Args:
            content: 文字内容
            images: 图片URL列表
            title: 标题
            **kwargs: 其他参数
            
        Returns:
            发布结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "title": title or content[:50],
                "content": content,
                "images": images[:9],  # 最多9张图片
                "content_type": "article"
            }
            
            # 可选参数
            if kwargs.get("category"):
                data["category"] = kwargs["category"]
            
            if kwargs.get("tags"):
                data["tags"] = kwargs["tags"]
            
            if kwargs.get("cover_images"):
                data["cover_images"] = kwargs["cover_images"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/article/create",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("err_no") == 0:
                    article_id = result.get("data", {}).get("article_id")
                    return {
                        "success": True,
                        "platform_id": article_id,
                        "url": f"https://www.toutiao.com/article/{article_id}/",
                        "message": "发布成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_tips", "发布失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"今日头条发布失败: {str(e)}"
            }
    
    async def publish_video(
        self,
        title: str,
        video_url: str,
        cover_url: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布视频内容
        
        Args:
            title: 视频标题
            video_url: 视频URL
            cover_url: 封面图URL
            description: 视频描述
            **kwargs: 其他参数
            
        Returns:
            发布结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "title": title,
                "video_url": video_url,
                "content_type": "video"
            }
            
            if cover_url:
                data["cover_url"] = cover_url
            
            if description:
                data["abstract"] = description
            
            # 可选参数
            if kwargs.get("category"):
                data["category"] = kwargs["category"]
            
            if kwargs.get("tags"):
                data["tags"] = kwargs["tags"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/video/create",
                    headers=headers,
                    json=data,
                    timeout=120.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("err_no") == 0:
                    video_id = result.get("data", {}).get("video_id")
                    return {
                        "success": True,
                        "platform_id": video_id,
                        "url": f"https://www.toutiao.com/video/{video_id}/",
                        "message": "发布成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_tips", "发布失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"今日头条发布失败: {str(e)}"
            }
    
    async def delete_content(self, content_id: str) -> Dict[str, Any]:
        """
        删除内容
        
        Args:
            content_id: 内容ID
            
        Returns:
            删除结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/content/delete",
                    headers=headers,
                    json={"item_id": content_id},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("err_no") == 0:
                    return {
                        "success": True,
                        "message": "删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_tips", "删除失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    async def get_content_status(self, content_id: str) -> Dict[str, Any]:
        """
        获取内容状态
        
        Args:
            content_id: 内容ID
            
        Returns:
            内容状态信息
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/content/detail",
                    headers=headers,
                    params={"item_id": content_id},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("err_no") == 0:
                    data = result.get("data", {})
                    return {
                        "success": True,
                        "status": data.get("status"),
                        "views": data.get("read_count", 0),
                        "likes": data.get("digg_count", 0),
                        "comments": data.get("comment_count", 0),
                        "shares": data.get("share_count", 0)
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("err_tips", "获取状态失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"获取状态失败: {str(e)}"
            }
