"""
Schemas模块初始化
"""
from app.schemas.common import Response, PaginationParams, PaginatedResponse
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

__all__ = [
    # Common
    "Response",
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
]
