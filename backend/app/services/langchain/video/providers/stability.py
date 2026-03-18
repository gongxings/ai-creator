"""
Stability AI 视频生成

支持 Stable Video Diffusion (SVD) 模型
- 仅支持图生视频 (image-to-video)
"""

import asyncio
import base64
import logging
from typing import List, Optional, Tuple, Any

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class StabilityVideoGenerator(VideoGeneratorBase):
    """
    Stability AI 视频生成器
    
    支持模型：
    - stable-video-diffusion: SVD 1.1，从图片生成短视频
    
    特点：
    - 仅支持图生视频 (image-to-video)
    - 需要提供起始帧图片
    - 生成的视频长度约 2-4 秒
    """
    
    provider_name = "stability"
    
    # SVD 仅支持图生视频
    supported_modes = [VideoGenerationMode.IMAGE_TO_VIDEO]
    
    # SVD 对输入图片尺寸有要求
    SUPPORTED_SIZES = ["1024x576", "576x1024", "768x768"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "stable-video-diffusion",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.stability.ai/v2beta"
    
    async def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        size: str = "1024x576",
        duration: float = 4.0,
        fps: int = 24,
        style: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """生成视频（需要提供图片）"""
        
        # SVD 需要图片
        if not image_url:
            return VideoGenerationResult.fail(
                "Stability SVD 需要提供图片 (image_url)，仅支持图生视频",
                self.provider_name
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            # 下载图片并转换为 base64
            async with httpx.AsyncClient(timeout=30.0) as client:
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    return VideoGenerationResult.fail("无法下载参考图片", self.provider_name)
                
                image_data = img_response.content
            
            # 构建 multipart 请求
            files = {
                "image": ("image.png", image_data, "image/png"),
            }
            
            data = {
                "seed": kwargs.get("seed", 0),
                "cfg_scale": kwargs.get("cfg_scale", 2.5),
                "motion_bucket_id": kwargs.get("motion_bucket_id", 40),
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 提交任务
                response = await client.post(
                    f"{self.base_url}/image-to-video",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    # 同步返回
                    result_data = response.json()
                    video_data = result_data.get("video")
                    
                    if video_data:
                        return VideoGenerationResult.ok(
                            videos=[video_data],  # base64 编码的视频
                            model=model or self.default_model,
                            provider=self.provider_name,
                            is_base64=True
                        )
                
                elif response.status_code == 202:
                    # 异步任务
                    result_data = response.json()
                    generation_id = result_data.get("id")
                    
                    if generation_id:
                        # 轮询获取结果
                        return await self._poll_task_result(
                            generation_id,
                            self._check_task_status,
                            max_attempts=60,
                            interval=10.0
                        )
                
                # 错误处理
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", str(response.status_code))
                except:
                    error_msg = response.text or str(response.status_code)
                
                return VideoGenerationResult.fail(f"Stability API 错误: {error_msg}", self.provider_name)
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Stability video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def _check_task_status(self, generation_id: str) -> Tuple[bool, Optional[VideoGenerationResult], Optional[str]]:
        """检查任务状态"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/image-to-video/result/{generation_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                video_data = data.get("video")
                
                if video_data:
                    result = VideoGenerationResult.ok(
                        videos=[video_data],
                        model=self.default_model,
                        provider=self.provider_name,
                        is_base64=True,
                        task_id=generation_id
                    )
                    return True, result, None
                else:
                    return True, None, "未获取到视频结果"
            
            elif response.status_code == 202:
                # 仍在处理中
                return False, None, None
            
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "未知错误")
                except:
                    error_msg = f"HTTP {response.status_code}"
                return True, None, error_msg
    
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """检查任务状态（公开方法）"""
        try:
            is_done, result, error = await self._check_task_status(task_id)
            
            if error:
                return VideoGenerationResult.fail(error, self.provider_name)
            
            if is_done and result:
                return result
            
            return VideoGenerationResult.pending(task_id, self.provider_name)
            
        except Exception as e:
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["stable-video-diffusion"]
