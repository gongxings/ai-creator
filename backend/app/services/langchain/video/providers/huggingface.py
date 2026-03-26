"""
Hugging Face 视频生成

通过 Hugging Face Inference API 调用开源视频生成模型，免费使用（有速率限制）。

支持模型：
- stabilityai/stable-video-diffusion-img2vid-xt
- stabilityai/stable-video-diffusion-img2vid
- cerspense/zeroscope_v2_576w

API文档: https://huggingface.co/docs/api-inference/
"""

import asyncio
import logging
import os
from typing import List, Optional

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)



class HuggingFaceVideoGenerator(VideoGeneratorBase):
    """
    Hugging Face 视频生成器
    
    使用 Hugging Face Inference API 调用开源视频生成模型。
    免费使用，有速率限制。
    
    特点：
    - 完全免费
    - 支持图生视频和文生视频
    - 返回视频URL或base64
    """
    
    provider_name = "huggingface"
    
    supported_modes = [VideoGenerationMode.IMAGE_TO_VIDEO, VideoGenerationMode.TEXT_TO_VIDEO]
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "stabilityai/stable-video-diffusion-img2vid-xt",
        "stabilityai/stable-video-diffusion-img2vid",
        "cerspense/zeroscope_v2_576w",
    ]
    
    # 模型对应的模式
    MODEL_MODES = {
        "stabilityai/stable-video-diffusion-img2vid-xt": [VideoGenerationMode.IMAGE_TO_VIDEO],
        "stabilityai/stable-video-diffusion-img2vid": [VideoGenerationMode.IMAGE_TO_VIDEO],
        "cerspense/zeroscope_v2_576w": [VideoGenerationMode.TEXT_TO_VIDEO],
    }
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "stabilityai/stable-video-diffusion-img2vid-xt",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api-inference.huggingface.co/models"
    
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
        """
        生成视频
        
        Args:
            prompt: 视频描述（用于文生视频）或运动描述（用于图生视频）
            image_url: 图片URL（用于图生视频）
            size: 视频尺寸
            duration: 视频时长（秒）
            fps: 帧率
            style: 风格
            model: 模型名称
        """
        model = model or self.default_model
        
        # 确定生成模式
        if model in self.MODEL_MODES:
            supported = self.MODEL_MODES[model]
            if VideoGenerationMode.IMAGE_TO_VIDEO in supported and not image_url:
                return VideoGenerationResult.fail(
                    f"模型 {model} 只支持图生视频，请提供图片",
                    self.provider_name
                )
            if VideoGenerationMode.TEXT_TO_VIDEO in supported and image_url:
                logger.warning(f"模型 {model} 主要支持文生视频，忽略image_url参数")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 视频生成需要更长时间
                # 构建请求体
                if image_url:
                    # 图生视频
                    payload = {
                        "inputs": image_url,
                        "parameters": {
                            "motion_bucket_id": 127,  # 运动程度
                            "noise_aug_strength": 0.1,  # 噪声增强
                        }
                    }
                else:
                    # 文生视频
                    if style:
                        prompt = f"{prompt}, {style} style"
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "num_frames": int(duration * fps),
                            "fps": fps,
                        }
                    }
                
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 503:
                    # 模型正在加载
                    logger.info(f"Hugging Face视频模型 {model} 正在加载，等待...")
                    await asyncio.sleep(30)
                    response = await client.post(
                        f"{self.base_url}/{model}",
                        headers=headers,
                        json=payload
                    )
                
                if response.status_code != 200:
                    error_msg = response.text
                    return VideoGenerationResult.fail(
                        f"Hugging Face API 错误 ({response.status_code}): {error_msg}",
                        self.provider_name
                    )
                
                # 检查返回类型
                content_type = response.headers.get("content-type", "")
                if "video" in content_type:
                    # 返回的是视频数据，需要上传到存储服务获取URL
                    import base64
                    video_base64 = base64.b64encode(response.content).decode("utf-8")
                    return VideoGenerationResult.ok(
                        videos=[f"data:{content_type};base64,{video_base64}"],
                        model=model or self.default_model,
                        provider=self.provider_name,
                        duration=duration,
                        is_base64=True
                    )
                else:
                    # JSON响应
                    try:
                        data = response.json()
                        if isinstance(data, dict) and "video" in data:
                            return VideoGenerationResult.ok(
                                videos=[data["video"]],
                                model=model or self.default_model,
                                provider=self.provider_name,
                                duration=duration
                            )
                        elif isinstance(data, list) and len(data) > 0:
                            return VideoGenerationResult.ok(
                                videos=data,
                                model=model or self.default_model,
                                provider=self.provider_name,
                                duration=duration
                            )
                    except:
                        # 解析失败
                        import base64
                        video_base64 = base64.b64encode(response.content).decode("utf-8")
                        return VideoGenerationResult.ok(
                            videos=[video_base64],
                            model=model or self.default_model,
                            provider=self.provider_name,
                            duration=duration,
                            is_base64=True
                        )
                
                return VideoGenerationResult.fail("未生成任何视频", self.provider_name)
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时（视频生成需要较长时间）", self.provider_name)
        except Exception as e:
            logger.error(f"Hugging Face video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def check_task(self, task_id: str) -> VideoGenerationResult:
        """检查任务状态（Hugging Face为同步模式，此方法不适用）"""
        return VideoGenerationResult.fail("Hugging Face为同步API，不支持任务查询", self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["576x320", "1024x576", "512x512"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
