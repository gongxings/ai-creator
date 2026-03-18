"""
腾讯混元图片生成

支持混元图像模型
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import List, Optional

import httpx

from ..base import ImageGeneratorBase, ImageGenerationResult

logger = logging.getLogger(__name__)


class HunyuanImageGenerator(ImageGeneratorBase):
    """
    腾讯混元图片生成器
    
    注意：腾讯云使用 Secret ID + Secret Key 双密钥认证
    """
    
    provider_name = "hunyuan"
    
    SUPPORTED_SIZES = ["1024x1024", "768x1024", "1024x768"]
    
    def __init__(
        self,
        api_key: str,  # 这里 api_key 实际是 Secret ID
        api_base: Optional[str] = None,
        default_model: Optional[str] = "hunyuan-image",
        secret_key: str = "",
        **kwargs
    ):
        super().__init__(api_key, api_base, default_model, **kwargs)
        self.secret_id = api_key
        self.secret_key = secret_key
        self.host = "hunyuan.tencentcloudapi.com"
        self.service = "hunyuan"
        self.region = kwargs.get("region", "ap-guangzhou")
    
    def _sign_request(self, payload: dict, action: str) -> dict:
        """生成腾讯云 API 签名"""
        algorithm = "TC3-HMAC-SHA256"
        timestamp = int(time.time())
        date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
        
        # 拼接规范请求串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        content_type = "application/json"
        signed_headers = "content-type;host"
        
        payload_str = json.dumps(payload)
        hashed_payload = hashlib.sha256(payload_str.encode()).hexdigest()
        
        canonical_headers = f"content-type:{content_type}\nhost:{self.host}\n"
        canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
        
        # 拼接待签名字符串
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode()).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # 计算签名
        def hmac_sha256(key, msg):
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()
        
        secret_date = hmac_sha256(f"TC3{self.secret_key}".encode(), date)
        secret_service = hmac_sha256(secret_date, self.service)
        secret_signing = hmac_sha256(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        # 拼接 Authorization
        authorization = (
            f"{algorithm} Credential={self.secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        
        return {
            "Authorization": authorization,
            "Content-Type": content_type,
            "Host": self.host,
            "X-TC-Action": action,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": "2023-09-01",
            "X-TC-Region": self.region,
        }
    
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
        
        # 解析尺寸
        width, height = self.parse_size(size)
        
        try:
            payload = {
                "Prompt": prompt,
                "Resolution": f"{width}:{height}",
            }
            
            if negative_prompt:
                payload["NegativePrompt"] = negative_prompt
            
            headers = self._sign_request(payload, "TextToImage")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"https://{self.host}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    return ImageGenerationResult.fail(f"混元 API 错误: {response.status_code}", self.provider_name)
                
                data = response.json()
                
                if "Response" in data and "Error" in data["Response"]:
                    error = data["Response"]["Error"]
                    return ImageGenerationResult.fail(
                        f"混元 API 错误: {error.get('Message', error.get('Code'))}",
                        self.provider_name
                    )
                
                # 获取结果
                result_image = data.get("Response", {}).get("ResultImage", "")
                
                if not result_image:
                    return ImageGenerationResult.fail("未获取到图片", self.provider_name)
                
                return ImageGenerationResult.ok(
                    images=[result_image],
                    model=model,
                    provider=self.provider_name,
                    is_base64=True
                )
                
        except httpx.TimeoutException:
            return ImageGenerationResult.fail("请求超时", self.provider_name)
        except Exception as e:
            logger.error(f"Hunyuan image generation error: {e}", exc_info=True)
            return ImageGenerationResult.fail(str(e), self.provider_name)
    
    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES
    
    def get_supported_models(self) -> List[str]:
        return ["hunyuan-image"]
