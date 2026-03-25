"""
Hugging Face 图片生成

通过 Hugging Face Inference API 调用开源图片生成模型，完全免费（有速率限制）。

支持模型：
- stabilityai/stable-diffusion-xl-base-1.0
- stabilityai/stable-diffusion-2-1
- runwayml/stable-diffusion-v1-5
- stabilityai/sdxl-turbo

API文档: https://huggingface.co/docs/api-inference/
"""

import base64
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class HuggingFaceImageGenerator(ImageGeneratorBase):
    """
    Hugging Face 图片生成器
    
    使用 Hugging Face Inference API 调用开源图片生成模型。
    免费使用，有速率限制（约30请求/分钟）。
    
    特点：
    - 完全免费
    - 支持多种开源模型
    - 返回图片URL或base64
    """
    
    provider_name = "huggingface"
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "stabilityai/stable-diffusion-2-1",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
        "stabilityai/sdxl-turbo",
    ]
    
    # 模型对应的推荐尺寸
    MODEL_SIZES = {
        "stabilityai/stable-diffusion-xl-base-1.0": ["1024x1024", "1024x768", "768x1024"],
        "stabilityai/sdxl-turbo": ["1024x1024", "512x512"],
        "stabilityai/stable-diffusion-2-1": ["768x768", "512x512"],
        "runwayml/stable-diffusion-v1-5": ["512x512", "512x768", "768x512"],
        "CompVis/stable-diffusion-v1-4": ["512x512", "256x256"],
    }
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "stabilityai/stable-diffusion-xl-base-1.0",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api-inference.huggingface.co/models"
    
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
            quality: 图片质量（HF不直接支持，通过steps参数控制）
            style: 风格提示词
            n: 生成数量（HF一次只返回一张）
            model: 模型名称
        """
        model = model or self.default_model
        
        # 验证模型
        if model not in self.SUPPORTED_MODELS:
            # 尝试直接使用用户提供的模型
            logger.warning(f"模型 {model} 不在预设列表中，尝试直接使用")
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建提示词
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        # 构建请求体
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "width": width,
                "height": height,
            }
        }
        
        # 添加负面提示词
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        
        # 根据质量调整steps
        if quality == "standard":
            payload["parameters"]["num_inference_steps"] = 25
        elif quality == "hd":
            payload["parameters"]["num_inference_steps"] = 50
        else:
            payload["parameters"]["num_inference_steps"] = 25
        
        images = []
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                # HF API一次只能生成一张图片
                for i in range(min(n, 4)):
                    response = await client.post(
                        f"{self.base_url}/{model}",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 503:
                        # 模型正在加载，等待后重试
                        logger.info(f"模型 {model} 正在加载，等待...")
                        import asyncio
                        await asyncio.sleep(20)
                        response = await client.post(
                            f"{self.base_url}/{model}",
                            headers=headers,
                            json=payload
                        )
                    
                    if response.status_code != 200:
                        error_msg = response.text
                        return ImageGenerationResult.fail(
                            f"Hugging Face API 错误 ({response.status_code}): {error_msg}",
                            self.provider_name
                        )
                    
                    # 检查返回类型
                    content_type = response.headers.get("content-type", "")
                    if "image" in content_type:
                        # 返回的是图片二进制数据
                        img_base64 = base64.b64encode(response.content).decode("utf-8")
                        images.append(f"data:{content_type};base64,{img_base64}")
                    else:
                        # 可能是JSON响应
                        try:
                            data = response.json()
                            if isinstance(data, list) and len(data) > 0:
                                img_data = data[0]
                                if "generated_image" in img_data:
                                    images.append(img_data["generated_image"])
                        except:
                            # 如果解析失败，假设返回的是base64
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
            return ImageGenerationResult.fail("请求超时（Hugging Face模型加载较慢）", self.provider_name)
        except Exception as e:
            logger.error(f"Hugging Face image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["512x512", "768x768", "1024x1024", "1024x768", "768x1024"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
