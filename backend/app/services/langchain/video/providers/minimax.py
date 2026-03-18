"""
MiniMax 视频生成

支持 MiniMax video-01 模型进行视频生成
"""

import asyncio
import logging
from typing import List, Optional, Tuple, Any

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class MiniMaxVideoGenerator(VideoGeneratorBase):
    """
    MiniMax 视频生成器
    
    支持模型：
    - video-01: MiniMax 视频生成模型
    - video-01-hd: MiniMax 高清视频生成模型
    
    特点：
    - 需要 group_id 参数
    - 支持文生视频和图生视频
    """
    
    provider_name = "minimax"
    
    supported_modes = [VideoGenerationMode.TEXT_TO_VIDEO, VideoGenerationMode.IMAGE_TO_VIDEO]
    
    SUPPORTED_SIZES = ["1280x720", "720x1280", "1024x1024"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "video-01",
        group_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.minimax.chat/v1"
        self.group_id = group_id or kwargs.get("group_id", "")
    
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
        
        if not self.group_id:
            return VideoGenerationResult.fail("MiniMax 需要 group_id 参数", self.provider_name)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            payload = {
                "model": model,
                "prompt": prompt,
            }
            
            if image_url:
                payload["first_frame_image"] = image_url
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 提交任务
                response = await client.post(
                    f"{self.base_url}/video_generation?GroupId={self.group_id}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("base_resp", {}).get("status_msg", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return VideoGenerationResult.fail(f"MiniMax API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                
                # 检查错误
                base_resp = data.get("base_resp", {})
                if base_resp.get("status_code") != 0:
                    return VideoGenerationResult.fail(base_resp.get("status_msg", "未知错误"), self.provider_name)
                
                task_id = data.get("task_id")
                
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
            logger.error(f"MiniMax video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def _check_task_status(self, task_id: str) -> Tuple[bool, Optional[VideoGenerationResult], Optional[str]]:
        """检查任务状态"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/query/video_generation?GroupId={self.group_id}&task_id={task_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                return False, None, None
            
            data = response.json()
            
            # 检查错误
            base_resp = data.get("base_resp", {})
            if base_resp.get("status_code") != 0:
                return True, None, base_resp.get("status_msg", "未知错误")
            
            status = data.get("status")
            
            if status == "Success":
                file_id = data.get("file_id")
                
                if file_id:
                    # 构建视频 URL
                    video_url = f"https://api.minimax.chat/v1/files/retrieve?GroupId={self.group_id}&file_id={file_id}"
                    
                    result = VideoGenerationResult.ok(
                        videos=[video_url],
                        model=self.default_model,
                        provider=self.provider_name,
                        task_id=task_id,
                        file_id=file_id
                    )
                    return True, result, None
                else:
                    return True, None, "未获取到视频结果"
            
            elif status == "Failed":
                return True, None, "视频生成失败"
            
            # 仍在处理中 (Processing, Queueing)
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
        return ["video-01", "video-01-hd"]
