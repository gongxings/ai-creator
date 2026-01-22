"""
抖音平台发布服务
"""
from typing import Dict, Any, Optional
import httpx
from .base import BasePlatform


class DouyinPlatform(BasePlatform):
    """抖音平台发布实现"""
    
    platform_name = "douyin"
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        验证抖音账号凭证
        
        Args:
            credentials: 包含access_token等凭证信息
            
        Returns:
            bool: 凭证是否有效
        """
        try:
            access_token = credentials.get("access_token")
            open_id = credentials.get("open_id")
            
            if not access_token or not open_id:
                return False
            
            # 调用抖音API验证token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://open.douyin.com/oauth/userinfo/",
                    params={
                        "access_token": access_token,
                        "open_id": open_id
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("data", {}).get("error_code") == 0
                return False
                
        except Exception as e:
            self.logger.error(f"验证抖音凭证失败: {str(e)}")
            return False
    
    async def publish_content(
        self,
        content: str,
        title: str,
        credentials: Dict[str, Any],
        video_url: Optional[str] = None,
        cover_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发布内容到抖音
        
        Args:
            content: 视频描述
            title: 视频标题
            credentials: 账号凭证
            video_url: 视频URL
            cover_url: 封面URL
            **kwargs: 其他参数（poi_id, micro_app_id等）
            
        Returns:
            Dict: 包含item_id的字典
        """
        try:
            access_token = credentials.get("access_token")
            open_id = credentials.get("open_id")
            
            if not video_url:
                raise ValueError("抖音发布需要提供视频URL")
            
            # 上传视频
            video_id = await self._upload_video(video_url, access_token, open_id)
            if not video_id:
                raise Exception("视频上传失败")
            
            # 准备发布数据
            publish_data = {
                "open_id": open_id,
                "access_token": access_token,
                "video_id": video_id,
                "text": f"{title}\n\n{content}",
            }
            
            # 添加封面
            if cover_url:
                cover_id = await self._upload_image(cover_url, access_token, open_id)
                if cover_id:
                    publish_data["cover_tsp"] = cover_id
            
            # 添加POI（地理位置）
            if "poi_id" in kwargs:
                publish_data["poi_id"] = kwargs["poi_id"]
            
            # 添加小程序
            if "micro_app_id" in kwargs:
                publish_data["micro_app_id"] = kwargs["micro_app_id"]
                publish_data["micro_app_title"] = kwargs.get("micro_app_title", "")
                publish_data["micro_app_url"] = kwargs.get("micro_app_url", "")
            
            # 发布视频
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.douyin.com/video/create/",
                    json=publish_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get("data", {})
                    
                    if data.get("error_code") == 0:
                        item_id = data.get("item_id")
                        return {
                            "item_id": item_id,
                            "share_url": f"https://www.douyin.com/video/{item_id}"
                        }
                    else:
                        raise Exception(f"发布失败: {data.get('description')}")
                else:
                    raise Exception(f"发布失败: {response.text}")
                    
        except Exception as e:
            self.logger.error(f"发布到抖音失败: {str(e)}")
            raise
    
    async def _upload_video(
        self,
        video_url: str,
        access_token: str,
        open_id: str
    ) -> Optional[str]:
        """
        上传视频到抖音
        
        Args:
            video_url: 视频URL
            access_token: 访问令牌
            open_id: 用户open_id
            
        Returns:
            str: 视频ID
        """
        try:
            async with httpx.AsyncClient() as client:
                # 下载视频
                video_response = await client.get(video_url, timeout=60.0)
                video_data = video_response.content
                
                # 初始化上传
                init_response = await client.post(
                    "https://open.douyin.com/video/upload/",
                    params={
                        "open_id": open_id,
                        "access_token": access_token
                    },
                    timeout=10.0
                )
                
                if init_response.status_code != 200:
                    return None
                
                init_result = init_response.json()
                upload_url = init_result.get("data", {}).get("upload_url")
                
                if not upload_url:
                    return None
                
                # 上传视频文件
                files = {"video": ("video.mp4", video_data, "video/mp4")}
                upload_response = await client.post(
                    upload_url,
                    files=files,
                    timeout=120.0
                )
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.json()
                    return upload_result.get("data", {}).get("video_id")
                    
        except Exception as e:
            self.logger.error(f"上传视频失败: {str(e)}")
            return None
    
    async def _upload_image(
        self,
        image_url: str,
        access_token: str,
        open_id: str
    ) -> Optional[str]:
        """
        上传图片到抖音
        
        Args:
            image_url: 图片URL
            access_token: 访问令牌
            open_id: 用户open_id
            
        Returns:
            str: 图片ID
        """
        try:
            async with httpx.AsyncClient() as client:
                # 下载图片
                image_response = await client.get(image_url, timeout=30.0)
                image_data = image_response.content
                
                # 上传到抖音
                files = {"image": ("cover.jpg", image_data, "image/jpeg")}
                response = await client.post(
                    "https://open.douyin.com/image/upload/",
                    params={
                        "open_id": open_id,
                        "access_token": access_token
                    },
                    files=files,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("data", {}).get("image_id")
                    
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
            publish_id: 视频ID
            credentials: 账号凭证
            
        Returns:
            str: 状态（published, reviewing, failed）
        """
        try:
            access_token = credentials.get("access_token")
            open_id = credentials.get("open_id")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://open.douyin.com/video/data/",
                    params={
                        "open_id": open_id,
                        "access_token": access_token,
                        "item_ids": publish_id
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get("data", {})
                    
                    if data.get("error_code") == 0:
                        items = data.get("list", [])
                        if items:
                            status = items[0].get("status")
                            # 映射抖音状态到统一状态
                            status_map = {
                                1: "published",  # 已发布
                                2: "reviewing",  # 审核中
                                3: "failed",     # 审核失败
                                4: "failed"      # 已删除
                            }
                            return status_map.get(status, "unknown")
                    
        except Exception as e:
            self.logger.error(f"获取发布状态失败: {str(e)}")
            return "unknown"
