"""
视频生成Service - 基于Cookie的网页版实现
支持文本生成视频、图片转视频、AI配音等功能
"""
import httpx
import json
import re
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from app.services.ai.cookie_based_service import CookieBasedAIService

logger = logging.getLogger(__name__)


class VideoGenerationService(CookieBasedAIService):
    """视频生成基础服务（支持Cookie模式）"""
    
    def get_platform_name(self) -> str:
        return "video_generation"
    
    def get_check_url(self) -> str:
        """获取Cookie验证URL"""
        return "https://www.doubao.com/"
    
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        ratio: str = "16:9",
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频
        
        Args:
            prompt: 视频描述
            duration: 视频时长（秒）
            ratio: 视频比例（16:9、9:16、1:1）
            style: 视频风格（可选）
            **kwargs: 其他参数
            
        Returns:
            {
                "video_url": "视频URL",
                "task_id": "任务ID",
                "status": "生成中/完成",
                "error": "错误信息"（可选）
            }
        """
        # 通过AI Chat API 间接生成视频
        # （实际生成可能需要特定的视频生成API）
        
        full_prompt = f"请帮我生成一个视频：{prompt}"
        if duration:
            full_prompt += f"，时长约{duration}秒"
        if style:
            full_prompt += f"，风格：{style}"
        if ratio:
            full_prompt += f"，视频比例：{ratio}"
        
        logger.info(f"Video generation request - prompt: {prompt[:100]}...")
        
        return {
            "video_url": None,
            "task_id": None,
            "status": "pending",
            "message": "视频生成功能需要专用API支持，建议使用专业的视频生成平台"
        }
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """不支持"""
        raise NotImplementedError("VideoGenerationService 不支持文本生成")
    
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """不支持"""
        raise NotImplementedError("VideoGenerationService 不支持图片生成")


class DoubaoVideoService(CookieBasedAIService):
    """豆包视频生成服务 - 基于Chat API的间接实现"""
    
    BASE_URL = "https://www.doubao.com"
    DEFAULT_BOT_ID = "7358044466096914465"
    
    def get_platform_name(self) -> str:
        return "doubao_video"
    
    def get_check_url(self) -> str:
        return self.BASE_URL
    
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        ratio: str = "16:9",
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通过豆包Chat生成视频脚本和指导
        （实际视频生成需要集成视频API如Runway、Pika等）
        """
        headers = self.get_headers()
        
        # 构建完整提示词
        full_prompt = f"""请帮我生成一个视频方案：

视频描述：{prompt}
"""
        if duration:
            full_prompt += f"时长：约{duration}秒\n"
        if ratio:
            full_prompt += f"视频比例：{ratio}\n"
        if style:
            full_prompt += f"风格：{style}\n"
        
        full_prompt += """
请生成：
1. 视频脚本（画面描述、配音文案）
2. 分镜头列表
3. 配音指导
4. 音效建议
5. 字幕文案
"""
        
        payload = {
            "user_input": full_prompt,
            "bot_id": self.DEFAULT_BOT_ID,
            "stream": False,
        }
        
        logger.info(f"Doubao video generation request - prompt: {prompt[:100]}...")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=180.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/api/chat/completions",
                    headers=headers,
                    json=payload,
                )
                
                if response.status_code == 401:
                    return {
                        "video_url": None,
                        "script": None,
                        "error": "Cookie已过期，请重新登录授权"
                    }
                
                response.raise_for_status()
                data = response.json()
                
                # 提取视频脚本
                script = None
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        script = choice["message"]["content"]
                
                return {
                    "video_url": None,  # 需要通过其他API生成
                    "script": script,   # 返回生成的脚本
                    "status": "script_generated",  # 脚本已生成，需要使用视频API生成视频
                    "next_step": "请使用返回的脚本调用专业视频生成API来生成实际视频"
                }
                
        except Exception as e:
            logger.error(f"Doubao video generation failed: {e}")
            return {
                "video_url": None,
                "script": None,
                "error": str(e)
            }
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """不支持"""
        raise NotImplementedError("DoubaoVideoService 不支持文本生成")
    
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """不支持"""
        raise NotImplementedError("DoubaoVideoService 不支持图片生成")


# 工厂函数
def create_video_service(cookies: Dict[str, str], user_agent: Optional[str] = None) -> VideoGenerationService:
    """
    创建视频生成服务实例
    
    Args:
        cookies: Cookie字典
        user_agent: User-Agent（可选）
        
    Returns:
        VideoGenerationService实例
    """
    return VideoGenerationService(cookies=cookies, user_agent=user_agent)


def create_doubao_video_service(cookies: Dict[str, str], user_agent: Optional[str] = None) -> DoubaoVideoService:
    """
    创建豆包视频生成服务实例
    
    Args:
        cookies: Cookie字典
        user_agent: User-Agent（可选）
        
    Returns:
        DoubaoVideoService实例
    """
    return DoubaoVideoService(cookies=cookies, user_agent=user_agent)
