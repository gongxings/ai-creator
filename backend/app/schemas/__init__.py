"""
Schemas模块初始化
"""
from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    UserUpdate,
    PasswordChange
)
from app.schemas.ai_model import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelListResponse
)
from app.schemas.creation import (
    CreationGenerate,
    CreationRegenerate,
    CreationOptimize,
    CreationUpdate,
    CreationResponse,
    CreationListItem,
    CreationVersion,
    WritingToolInfo
)
from app.schemas.platform import (
    PlatformBind,
    PlatformUpdate,
    PlatformResponse,
    PublishRequest,
    PublishResponse,
    PublishListItem,
    PlatformInfo
)
from app.schemas.plugin import (
    # 插件市场
    PluginMarketCreate,
    PluginMarketUpdate,
    PluginMarketResponse,
    PluginMarketListItem,
    PluginMarketFilter,
    PluginCategory,
    # 用户插件
    UserPluginInstall,
    UserPluginUpdate,
    UserPluginResponse,
    UserPluginListItem,
    # 插件选择
    PluginSelectionSave,
    PluginSelectionResponse,
    PluginSelectionWithDetails,
    # 插件调用
    PluginInvocationLog,
    # 插件评价
    PluginReviewCreate,
    PluginReviewUpdate,
    PluginReviewResponse,
    # 创作时使用
    PluginForCreation,
    CreationPluginsRequest,
    PluginStats,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    # User
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    # AI Model
    "AIModelCreate",
    "AIModelUpdate",
    "AIModelResponse",
    "AIModelListResponse",
    # Creation
    "CreationGenerate",
    "CreationRegenerate",
    "CreationOptimize",
    "CreationUpdate",
    "CreationResponse",
    "CreationListItem",
    "CreationVersion",
    "WritingToolInfo",
    # Platform
    "PlatformBind",
    "PlatformUpdate",
    "PlatformResponse",
    "PublishRequest",
    "PublishResponse",
    "PublishListItem",
    "PlatformInfo",
    # Plugin Market
    "PluginMarketCreate",
    "PluginMarketUpdate",
    "PluginMarketResponse",
    "PluginMarketListItem",
    "PluginMarketFilter",
    "PluginCategory",
    # User Plugin
    "UserPluginInstall",
    "UserPluginUpdate",
    "UserPluginResponse",
    "UserPluginListItem",
    # Plugin Selection
    "PluginSelectionSave",
    "PluginSelectionResponse",
    "PluginSelectionWithDetails",
    # Plugin Invocation
    "PluginInvocationLog",
    # Plugin Review
    "PluginReviewCreate",
    "PluginReviewUpdate",
    "PluginReviewResponse",
    # Plugin for Creation
    "PluginForCreation",
    "CreationPluginsRequest",
    "PluginStats",
]
