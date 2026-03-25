"""
ModelScope 视频生成

通过 ModelScope Inference API 调用开源视频生成模型，免费使用（有速率限制）。

支持模型：
- iic/text-to-video-synthesis
- iic/VideoComposer
- AI-ModelScope/video-crafter

API文档: https://modelscope.cn/docs/model-service/API-Inference/intro
"""

import asyncio
import logging
from typing import List, Optional

import httpx

from ..base import VideoGeneratorBase, VideoGenerationResult, VideoGenerationMode

logger = logging.getLogger(__name__)


class ModelScopeVideoGenerator(VideoGeneratorBase):
    """
    ModelScope 视频生成器
    
    使用 ModelScope Inference API 调用开源视频生成模型。
    免费使用，有速率限制。
    
    特点：
    - 完全免费
    - 国内服务，访问稳定
    - 支持文生视频和图生视频
    """
    
    provider_name = "modelscope"
    
    supported_modes = [VideoGenerationMode.TEXT_TO_VIDEO, VideoGenerationMode.IMAGE_TO_VIDEO]
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "iic/text-to-video-synthesis",
        "iic/VideoComposer",
        "AI-ModelScope/video-crafter",
    ]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "iic/text-to-video-synthesis",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api-inference.modelscope.cn/v1"
    
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
            prompt: 视频描述
            image_url: 图片URL（用于图生视频）
            size: 视频尺寸
            duration: 视频时长（秒）
            fps: 帧率
            style: 风格
            model: 模型名称
        """
        model = model or self.default_model
        
        # 构建提示词
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 视频生成需要更长时间
                # 构建请求体
                payload = {
                    "model": model,
                    "input": {
                        "prompt": full_prompt,
                        "negative_prompt": kwargs.get("negative_prompt", "低质量,模糊,失真"),
                        "num_frames": int(duration * fps),
                        "fps": fps,
                    }
                }
                
                if image_url:
                    payload["input"]["image_url"] = image_url
                
                response = await client.post(
                    f"{self.base_url}/models/{model}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 503:
                    # 模型正在加载
                    logger.info(f"ModelScope视频模型 {model} 正在加载，等待...")
                    await asyncio.sleep(30)
                    response = await client.post(
                        f"{self.base_url}/models/{model}",
                        headers=headers,
                        json=payload
                    )
                
                if response.status_code != 200:
                    error_msg = response.text
                    return VideoGenerationResult.fail(
                        f"ModelScope API 错误 ({response.status_code}): {error_msg}",
                        self.provider_name
                    )
                
                # 检查返回类型
                content_type = response.headers.get("content-type", "")
                if "video" in content_type:
                    # 返回的是视频数据
                    import base64
                    video_base64 = base64.b64encode(response.content).decode("utf-8")
                    return VideoGenerationResult.ok(
                        videos=[f"data:{content_type};base64,{video_base64}"],
                        model=model,
                        provider=self.provider_name,
                        duration=duration,
                        is_base64=True
                    )
                else:
                    # JSON响应
                    try:
                        data = response.json()
                        output = data.get("output", data)
                        
                        # 检查不同的响应格式
                        if isinstance(output, dict):
                            if "video_url" in output:
                                return VideoGenerationResult.ok(
                                    videos=[output["video_url"]],
                                    model=model,
                                    provider=self.provider_name,
                                    duration=duration
                                )
                            elif "videos" in output:
                                return VideoGenerationResult.ok(
                                    videos=output["videos"],
                                    model=model,
                                    provider=self.provider_name,
                                    duration=duration
                                )
                        elif isinstance(output, list) and len(output) > 0:
                            return VideoGenerationResult.ok(
                                videos=output,
                                model=model,
                                provider=self.provider_name,
                                duration=duration
                            )
                    except Exception as e:
                        logger.error(f"解析ModelScope响应失败: {e}")
                        if response.content:
                            import base64
                            video_base64 = base64.b64encode(response.content).decode("utf-8")
                            return VideoGenerationResult.ok(
                                videos=[video_base64],
                                model=model,
                                provider=self.provider_name,
                                duration=duration,
                                is_base64=True
                            )
                
                return VideoGenerationResult.fail("未生成任何视频", self.provider_name)
                
        except httpx.TimeoutException:
            return VideoGenerationResult.fail("请求超时（视频生成需要较长时间）", self.provider_name)
        except Exception as e:
            logger.error(f"ModelScope video generation error: {e}", exc_info=True)
            return VideoGenerationResult.fail(str(e), self.provider_name)
    
    async def check_task(self, task_id: str) -> VideoGenerationResult:
        """检查任务状态（ModelScope为同步模式，此方法不适用）"""
        return VideoGenerationResult.fail("ModelScope为同步API，不支持任务查询", self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["512x512", "576x320", "1024x576"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
