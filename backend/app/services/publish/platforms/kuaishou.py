"""
快手平台发布器
"""
from typing import Dict, Any, Optional
import httpx
from .base import BasePlatform


class KuaishouPlatform(BasePlatform):
    """快手平台发布器"""
    
    def __init__(self, access_token: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(access_token, config)
        self.base_url = "https://open.kuaishou.com/openapi"
    
    async def publish_text(self, content: str, **kwargs) -> Dict[str, Any]:
        """发布文字内容（快手不支持纯文字）"""
        raise NotImplementedError("快手不支持纯文字发布，请使用视频发布")
    
    async def publish_image(self, content: str, images: list, **kwargs) -> Dict[str, Any]:
        """发布图文内容（快手主要是视频平台）"""
        raise NotImplementedError("快手主要支持视频内容，请使用视频发布")
    
    async def publish_video(
        self,
        title: str,
        video_url: str,
        cover_url: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布视频内容
        
        Args:
            title: 视频标题
            video_url: 视频URL
            cover_url: 封面图URL
            description: 视频描述
            tags: 标签列表
            **kwargs: 其他参数
            
        Returns:
            发布结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 准备发布数据
            data = {
                "title": title,
                "video_url": video_url,
                "caption": description or title,
            }
            
            if cover_url:
                data["cover_url"] = cover_url
            
            if tags:
                data["tags"] = tags[:10]  # 快手最多10个标签
            
            # 其他可选参数
            if kwargs.get("location"):
                data["location"] = kwargs["location"]
            
            if kwargs.get("privacy_level"):
                data["privacy_level"] = kwargs["privacy_level"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/video/create",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("result") == 1:
                    return {
                        "success": True,
                        "platform_id": result.get("photo_id"),
                        "url": f"https://www.kuaishou.com/short-video/{result.get('photo_id')}",
                        "message": "发布成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("error_msg", "发布失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"快手发布失败: {str(e)}"
            }
    
    async def delete_content(self, content_id: str) -> Dict[str, Any]:
        """
        删除内容
        
        Args:
            content_id: 内容ID（photo_id）
            
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
                    f"{self.base_url}/video/delete",
                    headers=headers,
                    json={"photo_id": content_id},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("result") == 1:
                    return {
                        "success": True,
                        "message": "删除成功"
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("error_msg", "删除失败")
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
            content_id: 内容ID（photo_id）
            
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
                    f"{self.base_url}/video/info",
                    headers=headers,
                    params={"photo_id": content_id},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("result") == 1:
                    video_info = result.get("photo_info", {})
                    return {
                        "success": True,
                        "status": video_info.get("status"),
                        "views": video_info.get("view_count", 0),
                        "likes": video_info.get("like_count", 0),
                        "comments": video_info.get("comment_count", 0),
                        "shares": video_info.get("share_count", 0)
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("error_msg", "获取状态失败")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"获取状态失败: {str(e)}"
            }
