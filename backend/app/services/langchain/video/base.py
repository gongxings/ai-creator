"""
视频生成基类

定义视频生成的统一接口，所有厂商的实现都继承此基类。
同时提供 LangChain Tool 包装，便于 Agent 调用视频生成能力。

视频生成特点：
1. 通常为异步任务模式，需要轮询获取结果
2. 支持文生视频 (text-to-video) 和图生视频 (image-to-video)
3. 生成时间较长（通常 30秒 - 几分钟）
4. 结果通常是视频 URL
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VideoSize(str, Enum):
    """标准视频尺寸"""
    # 横屏
    LANDSCAPE_1280_720 = "1280x720"      # 720p
    LANDSCAPE_1920_1080 = "1920x1080"    # 1080p
    LANDSCAPE_1024_576 = "1024x576"      # 常见比例
    # 竖屏
    PORTRAIT_720_1280 = "720x1280"
    PORTRAIT_1080_1920 = "1080x1920"
    PORTRAIT_576_1024 = "576x1024"
    # 方形
    SQUARE_1024 = "1024x1024"
    SQUARE_512 = "512x512"


class VideoQuality(str, Enum):
    """视频质量"""
    STANDARD = "standard"
    HD = "hd"
    ULTRA = "ultra"


class VideoStyle(str, Enum):
    """视频风格"""
    NATURAL = "natural"           # 自然/写实
    CINEMATIC = "cinematic"       # 电影感
    ANIME = "anime"               # 动漫
    ARTISTIC = "artistic"         # 艺术
    DOCUMENTARY = "documentary"   # 纪录片风格
    SLOW_MOTION = "slow_motion"   # 慢动作


class VideoGenerationMode(str, Enum):
    """视频生成模式"""
    TEXT_TO_VIDEO = "text_to_video"     # 文生视频
    IMAGE_TO_VIDEO = "image_to_video"   # 图生视频


@dataclass
class VideoGenerationResult:
    """视频生成结果"""
    success: bool
    videos: List[str] = field(default_factory=list)   # 视频 URL 列表
    is_base64: bool = False                            # 是否为 base64 编码
    model: str = ""                                    # 使用的模型
    provider: str = ""                                 # 厂商
    duration: Optional[float] = None                   # 视频时长（秒）
    task_id: Optional[str] = None                      # 任务ID（用于后续查询）
    error: Optional[str] = None                        # 错误信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "videos": self.videos,
            "is_base64": self.is_base64,
            "model": self.model,
            "provider": self.provider,
            "duration": self.duration,
            "task_id": self.task_id,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def ok(
        cls,
        videos: List[str],
        model: str = "",
        provider: str = "",
        is_base64: bool = False,
        duration: float = None,
        task_id: str = None,
        **metadata
    ) -> "VideoGenerationResult":
        """成功结果"""
        return cls(
            success=True,
            videos=videos,
            is_base64=is_base64,
            model=model,
            provider=provider,
            duration=duration,
            task_id=task_id,
            metadata=metadata
        )
    
    @classmethod
    def pending(cls, task_id: str, provider: str = "") -> "VideoGenerationResult":
        """任务进行中"""
        return cls(
            success=True,
            task_id=task_id,
            provider=provider,
            metadata={"status": "pending"}
        )
    
    @classmethod
    def fail(cls, error: str, provider: str = "") -> "VideoGenerationResult":
        """失败结果"""
        return cls(success=False, error=error, provider=provider)


class VideoGeneratorBase(ABC):
    """
    视频生成器基类
    
    所有厂商的视频生成实现都需要继承此类。
    
    特点：
    1. 大多数厂商使用异步任务模式
    2. 支持 text-to-video 和 image-to-video
    3. 提供任务轮询机制
    
    Example:
        >>> class ZhipuVideoGenerator(VideoGeneratorBase):
        ...     provider_name = "zhipu"
        ...     
        ...     async def generate(self, prompt, **kwargs):
        ...         # 提交任务
        ...         task_id = await self._submit_task(prompt)
        ...         # 轮询结果
        ...         return await self._poll_result(task_id)
    """
    
    # 子类必须定义
    provider_name: str = ""
    
    # 默认支持的模式
    supported_modes: List[VideoGenerationMode] = [VideoGenerationMode.TEXT_TO_VIDEO]
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs
    ):
        """
        初始化生成器
        
        Args:
            api_key: API 密钥
            api_base: 自定义 API 地址
            default_model: 默认模型
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.api_base = api_base
        self.default_model = default_model
        self.extra_config = kwargs
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        size: str = "1280x720",
        duration: float = 4.0,
        fps: int = 24,
        style: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        生成视频
        
        Args:
            prompt: 视频描述提示词
            image_url: 参考图片 URL（图生视频模式）
            size: 视频尺寸 (如 "1280x720")
            duration: 视频时长（秒）
            fps: 帧率
            style: 视频风格
            model: 模型名称（覆盖默认）
            **kwargs: 厂商特定参数
            
        Returns:
            VideoGenerationResult
        """
        pass
    
    async def check_task_status(self, task_id: str) -> VideoGenerationResult:
        """
        检查任务状态（用于异步模式）
        
        子类可重写此方法以支持任务状态查询。
        
        Args:
            task_id: 任务ID
            
        Returns:
            VideoGenerationResult
        """
        return VideoGenerationResult.fail(
            "此厂商不支持任务状态查询",
            self.provider_name
        )
    
    def get_supported_sizes(self) -> List[str]:
        """获取支持的视频尺寸"""
        return ["1280x720", "720x1280", "1024x1024"]
    
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        return []
    
    def get_supported_modes(self) -> List[VideoGenerationMode]:
        """获取支持的生成模式"""
        return self.supported_modes
    
    def supports_image_to_video(self) -> bool:
        """是否支持图生视频"""
        return VideoGenerationMode.IMAGE_TO_VIDEO in self.supported_modes
    
    def validate_size(self, size: str) -> bool:
        """验证尺寸是否支持"""
        return size in self.get_supported_sizes()
    
    def parse_size(self, size: str) -> tuple:
        """解析尺寸字符串为 (width, height)"""
        try:
            parts = size.lower().split("x")
            return int(parts[0]), int(parts[1])
        except:
            return 1280, 720
    
    async def _poll_task_result(
        self,
        task_id: str,
        check_func,
        max_attempts: int = 120,
        interval: float = 5.0
    ) -> VideoGenerationResult:
        """
        通用任务轮询方法
        
        Args:
            task_id: 任务ID
            check_func: 检查函数，返回 (is_done, result_or_none, error_or_none)
            max_attempts: 最大尝试次数
            interval: 轮询间隔（秒）
            
        Returns:
            VideoGenerationResult
        """
        for attempt in range(max_attempts):
            try:
                is_done, result, error = await check_func(task_id)
                
                if error:
                    return VideoGenerationResult.fail(error, self.provider_name)
                
                if is_done and result:
                    return result
                
                logger.debug(f"Task {task_id} still processing, attempt {attempt + 1}/{max_attempts}")
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error polling task {task_id}: {e}")
                await asyncio.sleep(interval)
        
        return VideoGenerationResult.fail(
            f"任务超时（已等待 {max_attempts * interval} 秒）",
            self.provider_name
        )


# ============================================================================
# LangChain Tool 包装
# ============================================================================

class VideoGenerationInput(BaseModel):
    """视频生成工具输入参数"""
    prompt: str = Field(description="视频描述，详细描述想要生成的视频内容、动作、场景等")
    image_url: Optional[str] = Field(
        default=None,
        description="参考图片 URL，用于图生视频模式。如果提供，将基于此图片生成视频"
    )
    size: str = Field(
        default="1280x720",
        description="视频尺寸，如 1280x720（横屏）, 720x1280（竖屏）, 1024x1024（方形）"
    )
    duration: float = Field(
        default=4.0,
        description="视频时长（秒），通常为 2-10 秒",
        ge=1.0,
        le=30.0
    )
    style: Optional[str] = Field(
        default=None,
        description="视频风格，如 cinematic（电影感）, anime（动漫）, natural（自然）等"
    )


class VideoGenerationTool(BaseTool):
    """
    视频生成 LangChain Tool
    
    将视频生成器包装为 LangChain Tool，便于 Agent 调用。
    
    Example:
        >>> generator = ZhipuVideoGenerator(api_key="xxx")
        >>> tool = VideoGenerationTool(generator=generator)
        >>> result = await tool.ainvoke({"prompt": "一只猫在花园里奔跑"})
    """
    
    name: str = "video_generation"
    description: str = """生成视频。根据文字描述生成对应的视频。
适合用于：创建短视频、动态演示、视觉化场景等。
输入详细的视频描述，包括场景、动作、氛围等。
视频生成通常需要 30秒到几分钟时间。"""
    
    args_schema: type = VideoGenerationInput
    
    generator: VideoGeneratorBase = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, generator: VideoGeneratorBase, **kwargs):
        super().__init__(generator=generator, **kwargs)
        # 更新 tool 名称以包含厂商信息
        self.name = f"video_generation_{generator.provider_name}"
        
        # 根据厂商能力更新描述
        modes = generator.get_supported_modes()
        mode_desc = []
        if VideoGenerationMode.TEXT_TO_VIDEO in modes:
            mode_desc.append("文生视频")
        if VideoGenerationMode.IMAGE_TO_VIDEO in modes:
            mode_desc.append("图生视频")
        
        self.description = f"使用 {generator.provider_name} 生成视频。支持：{', '.join(mode_desc)}。{self.description}"
    
    def _run(self, **kwargs) -> str:
        """同步执行"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._arun(**kwargs)
                    )
                    return future.result()
            return asyncio.run(self._arun(**kwargs))
        except RuntimeError:
            return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """异步执行"""
        try:
            result = await self.generator.generate(**kwargs)
            
            if result.success:
                if result.videos:
                    # 返回视频信息
                    videos_info = []
                    for i, vid in enumerate(result.videos):
                        if result.is_base64:
                            videos_info.append(f"视频 {i+1}: [Base64 数据]")
                        else:
                            videos_info.append(f"视频 {i+1}: {vid}")
                    
                    output = f"成功生成 {len(result.videos)} 个视频\n"
                    output += "\n".join(videos_info)
                    if result.duration:
                        output += f"\n视频时长: {result.duration} 秒"
                    return output
                elif result.task_id:
                    # 任务进行中
                    return f"视频生成任务已提交，任务ID: {result.task_id}。请稍后查询结果。"
            
            return f"视频生成失败: {result.error}"
                
        except Exception as e:
            logger.error(f"Video generation error: {e}", exc_info=True)
            return f"视频生成错误: {str(e)}"


class VideoTaskCheckInput(BaseModel):
    """视频任务状态查询输入"""
    task_id: str = Field(description="视频生成任务ID")


class VideoTaskCheckTool(BaseTool):
    """
    视频任务状态查询 Tool
    
    用于查询异步视频生成任务的状态。
    """
    
    name: str = "video_task_check"
    description: str = "查询视频生成任务的状态。输入任务ID，返回任务进度或最终结果。"
    
    args_schema: type = VideoTaskCheckInput
    
    generator: VideoGeneratorBase = Field(exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, generator: VideoGeneratorBase, **kwargs):
        super().__init__(generator=generator, **kwargs)
        self.name = f"video_task_check_{generator.provider_name}"
    
    def _run(self, task_id: str) -> str:
        """同步执行"""
        import asyncio
        return asyncio.run(self._arun(task_id=task_id))
    
    async def _arun(self, task_id: str) -> str:
        """异步执行"""
        try:
            result = await self.generator.check_task_status(task_id)
            
            if result.success:
                if result.videos:
                    videos_info = [f"视频 {i+1}: {v}" for i, v in enumerate(result.videos)]
                    return f"任务完成！\n" + "\n".join(videos_info)
                else:
                    status = result.metadata.get("status", "processing")
                    progress = result.metadata.get("progress", "")
                    return f"任务状态: {status}" + (f" ({progress})" if progress else "")
            
            return f"查询失败: {result.error}"
            
        except Exception as e:
            return f"查询错误: {str(e)}"


def create_video_tool(generator: VideoGeneratorBase) -> VideoGenerationTool:
    """
    从视频生成器创建 LangChain Tool
    
    Args:
        generator: 视频生成器实例
        
    Returns:
        VideoGenerationTool
    """
    return VideoGenerationTool(generator=generator)


def create_video_tools(generator: VideoGeneratorBase) -> List[BaseTool]:
    """
    从视频生成器创建所有相关的 LangChain Tools
    
    包括：
    - 视频生成 Tool
    - 任务状态查询 Tool
    
    Args:
        generator: 视频生成器实例
        
    Returns:
        List of Tools
    """
    return [
        VideoGenerationTool(generator=generator),
        VideoTaskCheckTool(generator=generator)
    ]
