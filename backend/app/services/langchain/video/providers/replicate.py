"""
Replicate 视频生成

支持多种开源视频生成模型
- Zeroscope V2
- AnimateDiff
- 等
"""

import asyncio
import logging
from typing import List, Optional, Tuple, Any

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class ReplicateVideoGenerator(VideoGeneratorBase):
    """
    Replicate 视频生成器
    
    支持模型：
    - anotherjesse/zeroscope-v2-xl: Zeroscope V2 XL，文生视频
    - lucataco/animate-diff: AnimateDiff，文生视频
    - stability-ai/stable-video-diffusion: SVD，图生视频
    
    Replicate 采用预测 (prediction) 模式，需要轮询获取结果
    """
    
    provider_name = "replicate"
    
    supported_modes = [VideoGenerationMode.TEXT_TO_VIDEO, VideoGenerationMode.IMAGE_TO_VIDEO]
    
    # 模型到版本的映射
    MODEL_VERSIONS = {
        "zeroscope-v2-xl": "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
        "animate-diff": "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
        "stable-video-diffusion": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
    }
    
    SUPPORTED_SIZES = ["1024x576", "576x1024", "512x512", "768x768"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "zeroscope-v2-xl",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.replicate.com/v1"
    
    def _get_model_version(self, model: str) -> str:
        """获取模型的完整版本字符串"""
        return self.MODEL_VERSIONS.get(model, model)
    
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
        """生成视频"""
        model = model or self.default_model
        width, height = self.parse_size(size)
        
        # 获取模型版本
        version = self._get_model_version(model)
        
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 根据模型构建输入参数
            if model == "stable-video-diffusion":
                # SVD 需要图片
                if not image_url:
                    return VideoGenerationResult.fail(
                        "stable-video-diffusion 需要提供图片 (image_url)",
                        self.provider_name
                    )
                input_params = {
                    "input_image": image_url,
                    "motion_bucket_id": kwargs.get("motion_bucket_id", 127),
                    "cond_aug": kwargs.get("cond_aug", 0.02),
                    "decoding_t": kwargs.get("decoding_t", 14),
                    "seed": kwargs.get("seed"),
                }
            elif model == "animate-diff":
                input_params = {
                    "prompt": prompt,
                    "n_prompt": kwargs.get("negative_prompt", ""),
                    "seed": kwargs.get("seed"),
                    "steps": kwargs.get("steps", 25),
                    "guidance_scale": kwargs.get("guidance_scale", 7.5),
                }
            else:
                # Zeroscope V2 等
                input_params = {
                    "prompt": prompt,
                    "negative_prompt": kwargs.get("negative_prompt", ""),
                    "width": width,
                    "height": height,
                    "num_frames": int(duration * fps / 4),  # 约 24 帧
                    "fps": fps,
                    "seed": kwargs.get("seed"),
                }
            
            # 移除 None 值
            input_params = {k: v for k, v in input_params.items() if v is not None}
            
            payload = {
                "version": version.split(":")[-1] if ":" in version else version,
                "input": input_params
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 创建预测
                response = await client.post(
                    f"{self.base_url}/predictions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code not in [200, 201]:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return VideoGenerationResult.fail(f"Replicate API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                prediction_id = data.get("id")
                
                if not prediction_id:
                    return VideoGenerationResult.fail("未获取到预测ID", self.provider_name)
                
                # 轮询获取结果
                return await self._poll_task_result(
                    prediction_id,
                    self._check_task_status,
                    max_attempts=120,
                    interval=5.0
                )
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Replicate video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def _check_task_status(self, prediction_id: str) -> Tuple[bool, Optional[VideoGenerationResult], Optional[str]]:
        """检查预测状态"""
        headers = {
            "Authorization": f"Token {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/predictions/{prediction_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                return False, None, None
            
            data = response.json()
            status = data.get("status")
            
            if status == "succeeded":
                output = data.get("output")
                
                # output 可能是单个 URL 或 URL 列表
                if isinstance(output, str):
                    videos = [output]
                elif isinstance(output, list):
                    videos = output
                else:
                    return True, None, "未知的输出格式"
                
                result = VideoGenerationResult.ok(
                    videos=videos,
                    model=self.default_model,
                    provider=self.provider_name,
                    task_id=prediction_id
                )
                return True, result, None
            
            elif status == "failed":
                error_msg = data.get("error", "预测失败")
                return True, None, error_msg
            
            elif status == "canceled":
                return True, None, "预测已取消"
            
            # starting, processing
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
        return list(self.MODEL_VERSIONS.keys())
