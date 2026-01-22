"""
阿里通义千问(Qwen)服务
"""
import httpx
from typing import Optional, Dict, Any
from .base import AIServiceBase


class QwenService(AIServiceBase):
    """阿里通义千问服务"""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-turbo",
        base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    ):
        """
        初始化Qwen服务
        
        Args:
            api_key: API密钥
            model_name: 模型名称，如 qwen-turbo, qwen-plus, qwen-max
            base_url: API基础URL
        """
        super().__init__(api_key)
        self.model_name = model_name
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大令牌数
            temperature: 温度参数(0-2)
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        # 构建请求参数
        data = {
            "model": self.model_name,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {}
        }
        
        # 添加可选参数
        if max_tokens:
            data["parameters"]["max_tokens"] = max_tokens
        if temperature is not None:
            data["parameters"]["temperature"] = temperature
        
        # 添加其他参数
        if kwargs.get("top_p"):
            data["parameters"]["top_p"] = kwargs["top_p"]
        if kwargs.get("top_k"):
            data["parameters"]["top_k"] = kwargs["top_k"]
        if kwargs.get("repetition_penalty"):
            data["parameters"]["repetition_penalty"] = kwargs["repetition_penalty"]
        if kwargs.get("enable_search"):
            data["parameters"]["enable_search"] = kwargs["enable_search"]
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 检查响应状态
            if result.get("code"):
                raise Exception(f"Qwen API错误: {result.get('message', '未知错误')}")
            
            # 提取生成的文本
            output = result.get("output", {})
            text = output.get("text", "")
            
            return text
    
    async def generate_image(
        self,
        prompt: str,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成图片（使用通义万相）
        
        Args:
            prompt: 提示词
            size: 图片尺寸，如 "1024*1024", "720*1280", "1280*720"
            quality: 图片质量（暂不支持）
            **kwargs: 其他参数
            
        Returns:
            图片URL
        """
        url = f"{self.base_url}/services/aigc/text2image/image-synthesis"
        
        # 构建请求参数
        data = {
            "model": kwargs.get("image_model", "wanx-v1"),
            "input": {
                "prompt": prompt
            },
            "parameters": {}
        }
        
        # 添加可选参数
        if size:
            data["parameters"]["size"] = size
        if kwargs.get("n"):
            data["parameters"]["n"] = kwargs["n"]
        if kwargs.get("style"):
            data["parameters"]["style"] = kwargs["style"]
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 检查响应状态
            if result.get("code"):
                raise Exception(f"Qwen API错误: {result.get('message', '未知错误')}")
            
            # 提取图片URL
            output = result.get("output", {})
            results = output.get("results", [])
            if results:
                return results[0].get("url", "")
            
            return ""
    
    async def check_health(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            是否健康
        """
        try:
            # 发送一个简单的请求测试
            await self.generate_text("你好", max_tokens=10)
            return True
        except Exception:
            return False
    
    async def generate_text_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """
        流式生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大令牌数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        # 构建请求参数
        data = {
            "model": self.model_name,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "incremental_output": True  # 启用增量输出
            }
        }
        
        # 添加可选参数
        if max_tokens:
            data["parameters"]["max_tokens"] = max_tokens
        if temperature is not None:
            data["parameters"]["temperature"] = temperature
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                headers={**self.headers, "X-DashScope-SSE": "enable"},
                json=data
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            import json
                            data = json.loads(line[5:].strip())
                            
                            if data.get("code"):
                                raise Exception(f"Qwen API错误: {data.get('message', '未知错误')}")
                            
                            output = data.get("output", {})
                            text = output.get("text", "")
                            
                            if text:
                                yield text
                        except json.JSONDecodeError:
                            continue
