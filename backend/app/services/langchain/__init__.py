"""
LangChain 服务模块
统一的 AI 模型调用抽象层，支持 16 个主流厂商

主要组件：
- config: 厂商配置（16个厂商的 URL、模型、认证方式等）
- chat: Chat Model 工厂和自定义实现
- tools: 插件适配器和工具执行器
- image: 图片生成（9个厂商）
- video: 视频生成（6个厂商）
- service: 统一服务入口
- compat: 兼容性适配器

快速开始：
    >>> from app.services.langchain import LangChainService
    >>> 
    >>> # 创建服务
    >>> service = LangChainService(
    ...     provider="openai",
    ...     model="gpt-4",
    ...     api_key="sk-xxx"
    ... )
    >>> 
    >>> # 简单对话
    >>> response = await service.chat("你好")
    >>> print(response.content)
    >>> 
    >>> # 带工具的对话
    >>> from app.services.plugins.plugins.utilities.calculator import CalculatorPlugin
    >>> from app.services.langchain.tools import create_tool_from_plugin
    >>> 
    >>> calc = CalculatorPlugin()
    >>> tool = create_tool_from_plugin(calc)
    >>> response = await service.chat_with_tools("2+2=?", tools=[tool])

图片生成：
    >>> from app.services.langchain.image import ImageGeneratorFactory, generate_image
    >>> 
    >>> # 使用工厂
    >>> generator = ImageGeneratorFactory.create("openai", api_key="sk-xxx")
    >>> result = await generator.generate("一只可爱的猫咪")
    >>> 
    >>> # 快速调用
    >>> result = await generate_image("openai", "sk-xxx", "一只可爱的猫咪")

视频生成：
    >>> from app.services.langchain.video import VideoGeneratorFactory, generate_video
    >>> 
    >>> # 使用工厂
    >>> generator = VideoGeneratorFactory.create("zhipu", api_key="xxx")
    >>> result = await generator.generate("一只猫在花园里奔跑")
    >>> 
    >>> # 快速调用
    >>> result = await generate_video("zhipu", "xxx", "一只猫在花园里奔跑")

兼容旧接口：
    >>> from app.services.langchain import LangChainAIServiceFactory
    >>> 
    >>> # 与原 AIServiceFactory 用法完全相同
    >>> service = LangChainAIServiceFactory.create_service(
    ...     provider="openai",
    ...     api_key="sk-xxx",
    ...     model_name="gpt-4"
    ... )
    >>> result = await service.generate_text("你好")
"""

# 配置
from .config import (
    PROVIDERS,
    Capability,
    AuthType,
    ProviderConfig,
    get_provider_config,
    get_providers_by_capability,
    get_all_providers,
    get_text_providers,
    get_image_providers,
    get_video_providers,
    get_default_model,
    get_endpoint,
)

# Chat 工厂
from .chat.factory import LangChainChatFactory

# 服务
from .service import (
    LangChainService,
    ChatResponse,
    quick_chat,
    quick_chat_with_plugins,
    get_supported_providers,
    is_provider_supported,
)

# 兼容层
from .compat import (
    LangChainAIService,
    LangChainAIServiceFactory,
    get_ai_service_factory,
)

# 回调监控
from .callbacks import UsageCallbackHandler

# 工具
from .tools import (
    PluginToolAdapter,
    create_tool_from_plugin,
    ToolExecutor,
)

# 图片生成
from .image import (
    ImageGeneratorFactory,
    ImageGeneratorBase,
    ImageGenerationResult,
    ImageGenerationTool,
    generate_image,
    create_image_tool,
)

# 视频生成
from .video import (
    VideoGeneratorFactory,
    VideoGeneratorBase,
    VideoGenerationResult,
    VideoGenerationMode,
    VideoGenerationTool,
    VideoTaskCheckTool,
    generate_video,
    generate_video_from_image,
    create_video_tool,
    create_video_tools,
)

__all__ = [
    # 配置
    "PROVIDERS",
    "Capability",
    "AuthType",
    "ProviderConfig",
    "get_provider_config",
    "get_providers_by_capability",
    "get_all_providers",
    "get_text_providers",
    "get_image_providers",
    "get_video_providers",
    "get_default_model",
    "get_endpoint",
    
    # Chat 工厂
    "LangChainChatFactory",
    
    # 服务
    "LangChainService",
    "ChatResponse",
    "quick_chat",
    "quick_chat_with_plugins",
    "get_supported_providers",
    "is_provider_supported",
    
    # 兼容层
    "LangChainAIService",
    "LangChainAIServiceFactory",
    "get_ai_service_factory",
    
    # 回调监控
    "UsageCallbackHandler",
    
    # 工具
    "PluginToolAdapter",
    "create_tool_from_plugin",
    "ToolExecutor",
    
    # 图片生成
    "ImageGeneratorFactory",
    "ImageGeneratorBase",
    "ImageGenerationResult",
    "ImageGenerationTool",
    "generate_image",
    "create_image_tool",
    
    # 视频生成
    "VideoGeneratorFactory",
    "VideoGeneratorBase",
    "VideoGenerationResult",
    "VideoGenerationMode",
    "VideoGenerationTool",
    "VideoTaskCheckTool",
    "generate_video",
    "generate_video_from_image",
    "create_video_tool",
    "create_video_tools",
]
