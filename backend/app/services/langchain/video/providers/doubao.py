"""
火山豆包视频生成

支持 Seedance 系列模型进行视频生成
- 文生视频 (text-to-video)
- 图生视频 (image-to-video)
"""

import asyncio
import logging
from typing import List, Optional, Tuple, Any

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class DoubaoVideoGenerator(VideoGeneratorBase):
    """
    火山豆包 Seedance 视频生成器
    
    支持模型：
    - seedance-1.0-lite: Seedance 轻量版
    - seedance-1.0-pro: Seedance 专业版
    
    API 采用异步任务模式
    """
    
    provider_name = "doubao"
    
    supported_modes = [VideoGenerationMode.TEXT_TO_VIDEO, VideoGenerationMode.IMAGE_TO_VIDEO]
    
    SUPPORTED_SIZES = ["1280x720", "720x1280", "1024x1024"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "seedance-1.0-lite",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://ark.cn-beijing.volces.com/api/v3"
    
    async def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        size: str = "1280x720",
        duration: float = 4.0,
        fps: int = 24,
        style: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """生成视频（异步任务模式）"""
        model = model or self.default_model
        width, height = self.parse_size(size)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            payload = {
                "model": model,
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
                "video_parameters": {
                    "width": width,
                    "height": height,
                    "duration": min(int(duration), 10),
                    "fps": fps
                }
            }
            
            if image_url:
                payload["content"].insert(0, {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            
            if kwargs.get("seed"):
                payload["video_parameters"]["seed"] = kwargs["seed"]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 提交任务
                response = await client.post(
                    f"{self.base_url}/contents/generations/tasks",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return VideoGenerationResult.fail(f"豆包 API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                task_id = data.get("id")
                
                if not task_id:
                    return VideoGenerationResult.fail("未获取到任务ID", self.provider_name)
                
                # 轮询获取结果
                return await self._poll_task_result(
                    task_id,
                    self._check_task_status,
                    max_attempts=120,
                    interval=5.0
                )
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Doubao video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def _check_task_status(self, task_id: str) -> Tuple[bool, Optional[VideoGenerationResult], Optional[str]]:
        """检查任务状态"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/contents/generations/tasks/{task_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                return False, None, None
            
            data = response.json()
            status = data.get("status")
            
            if status == "succeeded":
                content = data.get("content", {})
                video_url = content.get("video_url")
                
                if video_url:
                    result = VideoGenerationResult.ok(
                        videos=[video_url],
                        model=self.default_model,
                        provider=self.provider_name,
                        task_id=task_id,
                        duration=content.get("duration")
                    )
                    return True, result, None
                else:
                    return True, None, "未获取到视频结果"
            
            elif status == "failed":
                error_msg = data.get("error", {}).get("message", "任务失败")
                return True, None, error_msg
            
            # 仍在处理中
            return False, None, None
    
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
        return ["seedance-1.0-lite", "seedance-1.0-pro"]
