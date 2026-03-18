"""
智谱 AI 视频生成

支持 CogVideoX 系列模型进行视频生成
- 文生视频 (text-to-video)
- 图生视频 (image-to-video)
"""

import asyncio
import logging
from typing import List, Optional, Tuple, Any

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class ZhipuVideoGenerator(VideoGeneratorBase):
    """
    智谱 AI CogVideoX 视频生成器
    
    支持模型：
    - cogvideox: CogVideoX 标准版，支持文生视频和图生视频
    - cogvideox-flash: CogVideoX 快速版
    
    API 文档: https://open.bigmodel.cn/dev/api/video-generation
    """
    
    provider_name = "zhipu"
    
    supported_modes = [VideoGenerationMode.TEXT_TO_VIDEO, VideoGenerationMode.IMAGE_TO_VIDEO]
    
    SUPPORTED_SIZES = ["1920x1080", "1080x1920", "1280x720", "720x1280"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "cogvideox",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://open.bigmodel.cn/api/paas/v4"
    
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
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            if image_url:
                # 图生视频
                payload = {
                    "model": model,
                    "image_url": image_url,
                    "prompt": prompt,
                }
            else:
                # 文生视频
                payload = {
                    "model": model,
                    "prompt": prompt,
                }
            
            # 可选参数
            if kwargs.get("quality"):
                payload["quality"] = kwargs["quality"]
            
            if kwargs.get("with_audio"):
                payload["with_audio"] = kwargs["with_audio"]
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 提交任务
                response = await client.post(
                    f"{self.base_url}/videos/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return VideoGenerationResult.fail(f"智谱 API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                task_id = data.get("id")
                
                if not task_id:
                    return VideoGenerationResult.fail("未获取到任务ID", self.provider_name)
                
                # 轮询获取结果
                return await self._poll_task_result(
                    task_id,
                    self._check_task_status,
                    max_attempts=120,  # 视频生成需要较长时间
                    interval=5.0
                )
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Zhipu video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def _check_task_status(self, task_id: str) -> Tuple[bool, Optional[VideoGenerationResult], Optional[str]]:
        """检查任务状态"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/async-result/{task_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                return False, None, None
            
            data = response.json()
            task_status = data.get("task_status")
            
            if task_status == "SUCCESS":
                video_result = data.get("video_result", [])
                videos = []
                
                for item in video_result:
                    url = item.get("url")
                    if url:
                        videos.append(url)
                
                if videos:
                    result = VideoGenerationResult.ok(
                        videos=videos,
                        model=self.default_model,
                        provider=self.provider_name,
                        task_id=task_id
                    )
                    return True, result, None
                else:
                    return True, None, "未获取到视频结果"
            
            elif task_status == "FAIL":
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
        return ["cogvideox", "cogvideox-flash"]
