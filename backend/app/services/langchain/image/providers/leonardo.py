"""
Leonardo AI 图片生成

通过 Leonardo AI API 调用图片生成模型，有免费额度（150积分/天）。

支持模型：
- Leonardo Phoenix
- Leonardo Lightning XL
- Leonardo Kino XL
- Leonardo Diffusion XL

API文档: https://docs.leonardo.ai/reference/creategeneration
"""

import base64
import logging
import asyncio
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class LeonardoImageGenerator(ImageGeneratorBase):
    """
    Leonardo AI 图片生成器
    
    使用 Leonardo AI API 调用图片生成模型。
    免费额度：150积分/天（约15张标准图片）。
    
    特点：
    - 高质量图片生成
    - 多种模型可选
    - 支持多种风格
    """
    
    provider_name = "leonardo"
    
    # 支持的模型
    SUPPORTED_MODELS = [
        "leonardo-phoenix",         # 最新模型，高质量
        "leonardo-lightning-xl",    # 快速生成
        "leonardo-kinexl",          # 电影感风格
        "leonardo-diffusion-xl",    # 稳定扩散XL
        "sd-1.5",                   # Stable Diffusion 1.5
        "playground-v2-5",          # Playground v2.5
    ]
    
    # 模型ID映射
    MODEL_IDS = {
        "leonardo-phoenix": "6b645e3a-dad4-4b58-9b6c-76d1b2c8ccd4",
        "leonardo-lightning-xl": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
        "leonardo-kinexl": "aa77f04e-3eec-4034-9c07-d0f619684628",
        "leonardo-diffusion-xl": "1e60896f-3c26-424c-9b88-7171fb8ca99b",
        "sd-1.5": "b820ea11-02bf-4652-97ae-9ac0cc00593d",
        "playground-v2-5": "8af4b0b2-fcd5-4e8c-8b53-c8c8c7f1c5b4",
    }
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "leonardo-phoenix",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://cloud.leonardo.ai/api/rest/v1"
    
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
            quality: 图片质量（standard/hd）
            style: 图片风格
            n: 生成数量
            model: 模型名称
        """
        model = model or self.default_model
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        # Leonardo要求尺寸为8的倍数
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 构建提示词
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 1. 创建生成任务
                payload = {
                    "prompt": full_prompt,
                    "modelId": self.MODEL_IDS.get(model),
                    "width": width,
                    "height": height,
                    "num_images": min(n, 4),
                    "guidance_scale": 7 if quality == "standard" else 12,
                }
                
                if negative_prompt:
                    payload["negative_prompt"] = negative_prompt
                
                # 如果有预设模型ID，使用预设
                if model in self.MODEL_IDS:
                    payload["modelId"] = self.MODEL_IDS[model]
                else:
                    # 尝试直接使用model作为modelId
                    payload["modelId"] = model
                
                response = await client.post(
                    f"{self.base_url}/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error", response.text)
                    return ImageGenerationResult.fail(
                        f"Leonardo API 错误: {error_msg}",
                        self.provider_name
                    )
                
                data = response.json()
                generation = data.get("sdGenerationJob", {})
                generation_id = generation.get("generationId")
                
                if not generation_id:
                    return ImageGenerationResult.fail("未获取到生成ID", self.provider_name)
                
                # 2. 轮询等待结果
                images = []
                max_attempts = 30
                
                for attempt in range(max_attempts):
                    await asyncio.sleep(2)
                    
                    check_response = await client.get(
                        f"{self.base_url}/generations/{generation_id}",
                        headers=headers
                    )
                    
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        gen_data = check_data.get("generations_by_pk", {})
                        status = gen_data.get("status")
                        
                        if status == "COMPLETE":
                            generated_images = gen_data.get("generated_images", [])
                            for img in generated_images:
                                img_url = img.get("url")
                                if img_url:
                                    images.append(img_url)
                            break
                        elif status == "FAILED":
                            return ImageGenerationResult.fail("图片生成失败", self.provider_name)
                
                if images:
                    return ImageGenerationResult.ok(
                        images=images,
                        model=model,
                        provider=self.provider_name,
                    )
                else:
                    return ImageGenerationResult.fail("图片生成超时", self.provider_name)
                    
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Leonardo image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return ["512x512", "768x768", "1024x1024", "1024x768", "768x1024", "1280x720", "720x1280"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return self.SUPPORTED_MODELS
