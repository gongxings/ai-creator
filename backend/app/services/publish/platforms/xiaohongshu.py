"""
小红书平台发布服务
"""
from typing import Dict, Any, Optional
import httpx
from .base import BasePlatform


class XiaohongshuPlatform(BasePlatform):
    """小红书平台发布实现"""
    
    platform_name = "xiaohongshu"
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        验证小红书账号凭证
        
        Args:
            credentials: 包含access_token等凭证信息
            
        Returns:
            bool: 凭证是否有效
        """
        try:
            access_token = credentials.get("access_token")
            if not access_token:
                return False
            
            # 调用小红书API验证token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.xiaohongshu.com/v1/user/info",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"验证小红书凭证失败: {str(e)}")
            return False
    
    async def publish_content(
        self,
        content: str,
        title: str,
        credentials: Dict[str, Any],
        images: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布内容到小红书
        
        Args:
            content: 笔记内容
            title: 笔记标题
            credentials: 账号凭证
            images: 图片列表
            **kwargs: 其他参数（tags, location等）
            
        Returns:
            Dict: 包含note_id和note_url的字典
        """
        try:
            access_token = credentials.get("access_token")
            
            # 准备发布数据
            publish_data = {
                "title": title,
                "content": content,
                "type": "normal",  # normal或video
            }
            
            # 添加标签
            if "tags" in kwargs:
                publish_data["tags"] = kwargs["tags"]
            
            # 添加位置
            if "location" in kwargs:
                publish_data["location"] = kwargs["location"]
            
            # 上传图片
            if images:
                image_ids = []
                for image_url in images[:9]:  # 小红书最多9张图
                    image_id = await self._upload_image(image_url, access_token)
                    if image_id:
                        image_ids.append(image_id)
                publish_data["image_ids"] = image_ids
            
            # 发布笔记
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.xiaohongshu.com/v1/note/publish",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=publish_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    note_id = result.get("note_id")
                    return {
                        "note_id": note_id,
                        "note_url": f"https://www.xiaohongshu.com/explore/{note_id}"
                    }
                else:
                    raise Exception(f"发布失败: {response.text}")
                    
        except Exception as e:
            self.logger.error(f"发布到小红书失败: {str(e)}")
            raise
    
    async def _upload_image(self, image_url: str, access_token: str) -> Optional[str]:
        """
        上传图片到小红书
        
        Args:
            image_url: 图片URL
            access_token: 访问令牌
            
        Returns:
            str: 图片ID
        """
        try:
            async with httpx.AsyncClient() as client:
                # 下载图片
                image_response = await client.get(image_url, timeout=30.0)
                image_data = image_response.content
                
                # 上传到小红书
                files = {"file": ("image.jpg", image_data, "image/jpeg")}
                response = await client.post(
                    "https://api.xiaohongshu.com/v1/media/upload",
                    headers={"Authorization": f"Bearer {access_token}"},
                    files=files,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("image_id")
                    
        except Exception as e:
            self.logger.error(f"上传图片失败: {str(e)}")
            return None
    
    async def get_publish_status(
        self,
        publish_id: str,
        credentials: Dict[str, Any]
    ) -> str:
        """
        获取发布状态
        
        Args:
            publish_id: 笔记ID
            credentials: 账号凭证
            
        Returns:
            str: 状态（published, reviewing, failed）
        """
        try:
            access_token = credentials.get("access_token")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.xiaohongshu.com/v1/note/{publish_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    # 映射小红书状态到统一状态
                    status_map = {
                        "published": "published",
                        "reviewing": "reviewing",
                        "rejected": "failed",
                        "deleted": "failed"
                    }
                    return status_map.get(status, "unknown")
                    
        except Exception as e:
            self.logger.error(f"获取发布状态失败: {str(e)}")
            return "unknown"
