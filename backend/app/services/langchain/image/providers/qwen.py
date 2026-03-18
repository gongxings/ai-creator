"""
阿里通义 Wanx 图片生成

支持通义万相系列模型
"""

import asyncio
import logging
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class QwenImageGenerator(ImageGeneratorBase):
    """
    阿里通义万相图片生成器
    
    支持模型：
    - wanx2.1-t2i-turbo: 快速版
    - wanx2.1-t2i-plus: 高质量版
    - wanx-v1: 基础版
    """
    
    provider_name = "qwen"
    
    SUPPORTED_SIZES = ["1024x1024", "720x1280", "1280x720"]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = "wanx2.1-t2i-turbo",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.base_url = api_base or "https://dashscope.aliyuncs.com/api/v1"
    
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
        """生成图片（异步任务模式）"""
        model = model or self.default_model
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"  # 异步模式
            }
            
            payload = {
                "model": model,
                "input": {
                    "prompt": prompt,
                },
                "parameters": {
                    "size": f"{width}*{height}",
                    "n": min(n, 4),
                }
            }
            
            if negative_prompt:
                payload["input"]["negative_prompt"] = negative_prompt
            
            if style:
                payload["parameters"]["style"] = style
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 提交任务
                response = await client.post(
                    f"{self.base_url}/services/aigc/text2image/image-synthesis",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", str(response.status_code))
                    except:
                        error_msg = response.text or str(response.status_code)
                    return ImageGenerationResult.fail(f"通义 API 错误: {error_msg}", self.provider_name)
                
                data = response.json()
                task_id = data.get("output", {}).get("task_id")
                
                if not task_id:
                    return ImageGenerationResult.fail("未获取到任务ID", self.provider_name)
                
                # 轮询获取结果
                return await self._poll_task_result(task_id, model)
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Qwen image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    async def _poll_task_result(
        self,
        task_id: str,
        model: str,
        max_attempts: int = 60,
        interval: float = 2.0
    ) -> ImageGenerationResult:
        """轮询任务结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(max_attempts):
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    await asyncio.sleep(interval)
                    continue
                
                data = response.json()
                status = data.get("output", {}).get("task_status")
                
                if status == "SUCCEEDED":
                    results = data.get("output", {}).get("results", [])
                    images = [r.get("url") for r in results if r.get("url")]
                    
                    return ImageGenerationResult.ok(
                        images=images,
                        model=model,
                        provider=self.provider_name
                    )
                
                elif status == "FAILED":
                    error_msg = data.get("output", {}).get("message", "任务失败")
                    return ImageGenerationResult.fail(error_msg, self.provider_name)
                
                await asyncio.sleep(interval)
        
        return ImageGenerationResult.fail("任务超时", self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["wanx2.1-t2i-turbo", "wanx2.1-t2i-plus", "wanx-v1"]
