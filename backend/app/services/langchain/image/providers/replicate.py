"""
Replicate 图片生成

支持 Replicate 平台上的各种图片生成模型
"""

import asyncio
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class ReplicateImageGenerator(ImageGeneratorBase):
    """
    Replicate 图片生成器
    
    支持模型：
    - stability-ai/sdxl
    - black-forest-labs/flux-schnell
    - black-forest-labs/flux-dev
    """
    
    provider_name = "replicate"
    
    SUPPORTED_SIZES = ["1024x1024", "1024x768", "768x1024", "1280x720", "720x1280"]
    
    # 模型版本映射
    MODEL_VERSIONS = {
        "stability-ai/sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        "black-forest-labs/flux-schnell": "black-forest-labs/flux-schnell",
        "black-forest-labs/flux-dev": "black-forest-labs/flux-dev",
    }
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "black-forest-labs/flux-schnell",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.replicate.com/v1"
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        n: int = 1,
        model: Optional[str] = None,
        **kwargs
    ) -> ImageGenerationResult:
        """生成图片"""
        model = model or self.default_model
        
        # 获取完整模型版本
        model_version = self.MODEL_VERSIONS.get(model, model)
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建输入参数（不同模型参数略有不同）
            input_params = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": min(n, 4),
            }
            
            if negative_prompt:
                input_params["negative_prompt"] = negative_prompt
            
            # Flux 模型特有参数
            if "flux" in model.lower():
                input_params["num_inference_steps"] = 4 if "schnell" in model.lower() else 28
            
            payload = {
                "version": model_version.split(":")[-1] if ":" in model_version else None,
                "input": input_params
            }
            
            # 确定 API 端点
            if ":" in model_version:
                endpoint = f"{self.base_url}/predictions"
            else:
                endpoint = f"{self.base_url}/models/{model_version}/predictions"
                del payload["version"]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code not in [200, 201]:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return ImageGenerationResult.fail(f"Replicate API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                prediction_url = data.get("urls", {}).get("get")
                
                if not prediction_url:
                    return ImageGenerationResult.fail("未获取到预测URL", self.provider_name)
                
                # 轮询获取结果
                return await self._poll_prediction(prediction_url, headers, model)
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Replicate image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    async def _poll_prediction(
        self,
        url: str,
        headers: dict,
        model: str,
        max_attempts: int = 120,
        interval: float = 1.0
    ) -> ImageGenerationResult:
        """轮询预测结果"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(max_attempts):
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    await asyncio.sleep(interval)
                    continue
                
                data = response.json()
                status = data.get("status")
                
                if status == "succeeded":
                    output = data.get("output", [])
                    
                    # 输出可能是单个URL或URL列表
                    if isinstance(output, str):
                        images = [output]
                    elif isinstance(output, list):
                        images = output
                    else:
                        images = []
                    
                    return ImageGenerationResult.ok(
                        images=images,
                        model=model,
                        provider=self.provider_name
                    )
                
                elif status == "failed":
                    error = data.get("error", "预测失败")
                    return ImageGenerationResult.fail(str(error), self.provider_name)
                
                elif status == "canceled":
                    return ImageGenerationResult.fail("预测已取消", self.provider_name)
                
                await asyncio.sleep(interval)
        
        return ImageGenerationResult.fail("预测超时", self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return list(self.MODEL_VERSIONS.keys())
