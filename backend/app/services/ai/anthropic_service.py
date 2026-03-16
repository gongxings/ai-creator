"""
Anthropic Claude AI服务
"""
from typing import Dict, Any, Optional
import anthropic
from .base import AIServiceBase


class AnthropicService(AIServiceBase):
    """Anthropic Claude AI服务"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, {"model": model})
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or 4000,
                temperature=temperature or 0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API调用失败: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """Claude不支持图片生成"""
        raise NotImplementedError("Claude不支持图片生成功能")
    
    async def generate_video(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Claude不支持视频生成"""
        raise NotImplementedError("Claude不支持视频生成功能")
    
    async def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            # 简单测试API是否可用
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Hi"}
                ]
            )
            return True
        except Exception:
            return False
