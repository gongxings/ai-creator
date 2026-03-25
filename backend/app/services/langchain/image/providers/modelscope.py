"""
ModelScope 图片生成

通过 ModelScope Inference API 调用开源图片生成模型，免费使用（有速率限制）。

支持模型：
- stabilityai/stable-diffusion-xl-base-1.0
- AI-ModelScope/dreamshaper-xl-v2-turbo
- iic/Colorize-SD

API文档: https://modelscope.cn/docs/model-service/API-Inference/intro
"""

import base64
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class ModelScopeImageGenerator(ImageGeneratorBase):
    """
    ModelScope 图片生成器
    
    使用 ModelScope Inference API 调用开源图片生成模型。
    免费使用，有速率限制。
    
    特点：
    - 完全免费
    - 国内服务，访问稳定
    - 支持多种开源模型
    """
    
    provider_name = "modelscope"
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "AI-ModelScope/dreamshaper-xl-v2-turbo",
        "iic/Colorize-SD",
        "iic/GroundingDINO_SwinT",
    ]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "stabilityai/stable-diffusion-xl-base-1.0",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api-inference.modelscope.cn/v1"
    
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
        """
        生成图片
        
        Args:
            prompt: 图片描述
            negative_prompt: 负面提示词
            size: 图片尺寸
            quality: 图片质量（通过steps控制）
            style: 风格提示词
            n: 生成数量
            model: 模型名称
        """
        model = model or self.default_model
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        # 构建提示词
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 根据质量调整steps
        if quality == "standard":
            num_steps = 25
        elif quality == "hd":
            num_steps = 50
        else:
            num_steps = 25
        
        images = []
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                for i in range(min(n, 4)):
                    payload = {
                        "model": model,
                        "input": {
                            "prompt": full_prompt,
                            "negative_prompt": negative_prompt or "",
                            "width": width,
                            "height": height,
                            "num_inference_steps": num_steps,
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/models/{model}",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 503:
                        # 模型正在加载
                        logger.info(f"ModelScope模型 {model} 正在加载，等待...")
                        import asyncio
                        await asyncio.sleep(15)
                        response = await client.post(
                            f"{self.base_url}/models/{model}",
                            headers=headers,
                            json=payload
                        )
                    
                    if response.status_code != 200:
                        error_msg = response.text
                        return ImageGenerationResult.fail(
                            f"ModelScope API 错误 ({response.status_code}): {error_msg}",
                            self.provider_name
                        )
                    
                    # 解析响应
                    content_type = response.headers.get("content-type", "")
                    if "image" in content_type:
                        # 返回的是图片二进制数据
                        img_base64 = base64.b64encode(response.content).decode("utf-8")
                        images.append(f"data:{content_type};base64,{img_base64}")
                    else:
                        # JSON响应
                        try:
                            data = response.json()
                            output = data.get("output", data)
                            
                            # 检查不同的响应格式
                            if isinstance(output, dict):
                                if "image_url" in output:
                                    images.append(output["image_url"])
                                elif "images" in output:
                                    images.extend(output["images"])
                                elif "generated_image" in output:
                                    images.append(output["generated_image"])
                            elif isinstance(output, list):
                                images.extend(output)
                        except Exception as e:
                            logger.error(f"解析ModelScope响应失败: {e}")
                            if response.content:
                                img_base64 = base64.b64encode(response.content).decode("utf-8")
                                images.append(img_base64)
                
                if images:
                    return ImageGenerationResult.ok(
                        images=images,
                        model=model,
                        provider=self.provider_name,
                        is_base64=True
                    )
                else:
                    return ImageGenerationResult.fail("未生成任何图片", self.provider_name)
                    
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"ModelScope image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["512x512", "768x768", "1024x1024", "1024x768", "768x1024"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
