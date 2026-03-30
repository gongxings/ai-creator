"""
OpenAI DALL-E 图片生成

支持 DALL-E 2 和 DALL-E 3 模型
同时支持 OpenRouter 等第三方 API 的图片生成
"""

import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class OpenAIImageGenerator(ImageGeneratorBase):
    """
    OpenAI DALL-E 图片生成器
    
    支持模型：
    - dall-e-3: 更高质量，支持 1024x1024, 1024x1792, 1792x1024
    - dall-e-2: 支持 256x256, 512x512, 1024x1024
    - OpenRouter: 通过 chat completions 端点生成图片
    """
    
    provider_name = "openai"
    
    # DALL-E 3 支持的尺寸
    DALLE3_SIZES = ["1024x1024", "1024x1792", "1792x1024"]
    # DALL-E 2 支持的尺寸
    DALLE2_SIZES = ["256x256", "512x512", "1024x1024"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "dall-e-3",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://api.openai.com/v1"
    
    def _is_openrouter(self) -> bool:
        """判断是否使用 OpenRouter"""
        return "openrouter.ai" in self.base_url if self.base_url else False
    
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
            negative_prompt: 负面提示词（DALL-E 不直接支持，会合并到 prompt）
            size: 图片尺寸
            quality: 图片质量 (standard/hd)，仅 DALL-E 3 支持 hd
            style: 风格 (vivid/natural)，仅 DALL-E 3 支持
            n: 生成数量，DALL-E 3 只支持 n=1
            model: 模型名称
        """
        model = model or self.default_model
        
        # OpenRouter 使用 chat completions 端点生成图片
        if self._is_openrouter():
            return await self._generate_via_openrouter(prompt, negative_prompt, model)
        
        # 标准 OpenAI DALL-E 生成
        return await self._generate_via_openai(prompt, negative_prompt, size, quality, style, n, model)
    
    async def _generate_via_openrouter(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "bytedance-seed/seedream-4.5",
        **kwargs
    ) -> ImageGenerationResult:
        """通过 OpenRouter 的 chat completions 端点生成图片"""
        # 默认负面提示词
        default_negative = "low quality, blurry, distorted, deformed, ugly, bad anatomy, watermark, text, logo, signature, out of frame, cropped, lowres, jpeg artifacts, duplicate, error"
        
        # 合并用户负面提示词
        negative_parts = [default_negative]
        if negative_prompt:
            negative_parts.append(negative_prompt)
        
        full_prompt = f"{prompt}\n\nAvoid: {', '.join(negative_parts)}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "modalities": ["image"]
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        if response.content:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", error_msg)
                    except Exception:
                        pass
                    return ImageGenerationResult.fail(f"OpenRouter API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                images = []
                
                choices = data.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    # 处理 images 数组格式
                    for img in message.get("images", []):
                        if isinstance(img, dict):
                            url = img.get("image_url", {}).get("url", "")
                            if url:
                                images.append(url)
                        elif isinstance(img, str):
                            images.append(img)
                    
                    # 处理 content 中的图片（某些模型可能返回在 content 中）
                    content = message.get("content", "")
                    if content and not images:
                        if content.startswith("data:") or content.startswith("http"):
                            images.append(content)
                
                if not images:
                    return ImageGenerationResult.fail("未获取到生成的图片", self.provider_name)
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"OpenRouter image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    async def _generate_via_openai(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        n: int = 1,
        model: str = "dall-e-3",
        **kwargs
    ) -> ImageGenerationResult:
        """通过标准 OpenAI DALL-E 端点生成图片"""
        # 验证参数
        if model == "dall-e-3":
            if size not in self.DALLE3_SIZES:
                size = "1024x1024"
            n = 1  # DALL-E 3 只支持 n=1
        else:
            if size not in self.DALLE2_SIZES:
                size = "1024x1024"
            quality = "standard"  # DALL-E 2 不支持 hd
            style = None
        
        # 默认负面提示词
        default_negative = "low quality, blurry, distorted, deformed, ugly, bad anatomy, watermark, text, logo, signature, out of frame, cropped, lowres, jpeg artifacts, duplicate, error"
        
        # 合并用户负面提示词
        negative_parts = [default_negative]
        if negative_prompt:
            negative_parts.append(negative_prompt)
        
        full_prompt = f"{prompt}. Avoid: {', '.join(negative_parts)}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "n": n,
                "size": size,
                "quality": quality,
            }
            
            if style and model == "dall-e-3":
                payload["style"] = style
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        if response.content:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", error_msg)
                    except Exception:
                        pass
                    return ImageGenerationResult.fail(f"OpenAI API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                
                images = []
                revised_prompt = None
                
                for item in data.get("data", []):
                    if "url" in item:
                        images.append(item["url"])
                    elif "b64_json" in item:
                        images.append(item["b64_json"])
                    
                    # DALL-E 3 会返回优化后的提示词
                    if "revised_prompt" in item and not revised_prompt:
                        revised_prompt = item["revised_prompt"]
                
                return ImageGenerationResult.ok(
                    images=images,
                    model=model,
                    provider=self.provider_name,
                    revised_prompt=revised_prompt
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"OpenAI image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的尺寸"""
        return list(set(self.DALLE3_SIZES + self.DALLE2_SIZES))
    
    def get_supported_models(self) -> List[str]:
        return ["dall-e-3", "dall-e-2"]
