"""
插件系统 Schemas
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# ==================== 插件市场 ====================

class PluginMarketBase(BaseModel):
    """插件市场基础 Schema"""
    name: str = Field(..., description="插件唯一标识符")
    display_name: str = Field(..., description="显示名称")
    description: Optional[str] = Field(None, description="详细描述")
    short_description: Optional[str] = Field(None, description="简短描述")
    version: str = Field("1.0.0", description="版本号")
    author: str = Field("AI Creator", description="作者")
    author_url: Optional[str] = Field(None, description="作者链接")
    category: str = Field(..., description="分类：search, writing, media, utility")
    icon: Optional[str] = Field(None, description="图标")
    icon_url: Optional[str] = Field(None, description="图标URL")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class PluginMarketCreate(PluginMarketBase):
    """创建插件市场条目"""
    config_schema: Dict[str, Any] = Field(default_factory=dict, description="配置参数 JSON Schema")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="插件参数 Schema")
    entry_point: str = Field(..., description="Python入口路径")
    requirements: List[str] = Field(default_factory=list, description="依赖要求")
    screenshot_urls: List[str] = Field(default_factory=list, description="截图URL列表")
    is_official: bool = Field(True, description="是否官方插件")


class PluginMarketUpdate(BaseModel):
    """更新插件市场条目"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    version: Optional[str] = None
    icon: Optional[str] = None
    icon_url: Optional[str] = None
    tags: Optional[List[str]] = None
    config_schema: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PluginMarketResponse(PluginMarketBase):
    """插件市场响应"""
    id: int
    screenshot_urls: List[str] = Field(default_factory=list)
    is_official: bool = True
    is_approved: bool = True
    is_active: bool = True
    download_count: int = 0
    rating: float = 0
    review_count: int = 0
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    # 用户相关状态（可选）
    is_installed: bool = Field(False, description="当前用户是否已安装")
    user_config: Optional[Dict[str, Any]] = Field(None, description="用户配置")
    
    class Config:
        from_attributes = True


class PluginMarketListItem(BaseModel):
    """插件市场列表项（精简版）"""
    id: int
    name: str
    display_name: str
    short_description: Optional[str]
    category: str
    icon: Optional[str]
    tags: List[str] = []
    is_official: bool = True
    download_count: int = 0
    rating: float = 0
    review_count: int = 0
    is_installed: bool = False
    
    class Config:
        from_attributes = True


# ==================== 用户插件 ====================

class UserPluginInstall(BaseModel):
    """安装插件请求"""
    plugin_name: str = Field(..., description="插件名称")
    config: Dict[str, Any] = Field(default_factory=dict, description="用户配置")


class UserPluginUpdate(BaseModel):
    """更新用户插件配置"""
    config: Optional[Dict[str, Any]] = Field(None, description="用户配置")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    is_auto_use: Optional[bool] = Field(None, description="是否自动使用")


class UserPluginResponse(BaseModel):
    """用户插件响应"""
    id: int
    plugin_name: str
    is_enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    is_auto_use: bool = False
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    installed_at: datetime
    
    # 插件信息（关联）
    display_name: str
    description: Optional[str] = None
    category: str
    icon: Optional[str] = None
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class UserPluginListItem(BaseModel):
    """用户插件列表项"""
    id: int
    plugin_name: str
    display_name: str
    category: str
    icon: Optional[str] = None
    is_enabled: bool = True
    is_auto_use: bool = False
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== 插件选择 ====================

class PluginSelectionSave(BaseModel):
    """保存插件选择请求"""
    tool_type: str = Field(..., description="写作类型")
    selected_plugins: List[str] = Field(..., description="选中的插件列表")


class PluginSelectionResponse(BaseModel):
    """插件选择响应"""
    tool_type: str
    selected_plugins: List[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PluginSelectionWithDetails(BaseModel):
    """带插件详情的选择响应"""
    tool_type: str
    selected_plugins: List[str]
    plugins: List[UserPluginListItem]
    updated_at: datetime


# ==================== 插件调用 ====================

class PluginInvocationLog(BaseModel):
    """插件调用日志"""
    id: int
    plugin_name: str
    arguments: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    invoked_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 插件评价 ====================

class PluginReviewCreate(BaseModel):
    """创建插件评价"""
    plugin_name: str = Field(..., description="插件名称")
    rating: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: Optional[str] = Field(None, description="评论内容")


class PluginReviewUpdate(BaseModel):
    """更新插件评价"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class PluginReviewResponse(BaseModel):
    """插件评价响应"""
    id: int
    user_id: int
    plugin_name: str
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    # 用户信息（可选）
    username: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== 分类和筛选 ====================

class PluginCategory(BaseModel):
    """插件分类"""
    key: str
    name: str
    description: str
    count: int = 0


class PluginMarketFilter(BaseModel):
    """插件市场筛选条件"""
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_official: Optional[bool] = None
    search: Optional[str] = None
    sort_by: str = Field("download_count", description="排序：download_count, rating, created_at")
    sort_order: str = Field("desc", description="排序方向：asc, desc")


# ==================== 创作时使用 ====================

class PluginForCreation(BaseModel):
    """创作时可用的插件"""
    name: str
    display_name: str
    description: str
    icon: Optional[str] = None
    is_enabled: bool = True
    is_selected: bool = False


class CreationPluginsRequest(BaseModel):
    """创作请求中的插件参数"""
    enabled_plugins: List[str] = Field(default_factory=list, description="启用的插件列表")
    save_selection: bool = Field(True, description="是否保存选择")


# ==================== 统计 ====================

class PluginStats(BaseModel):
    """插件使用统计"""
    plugin_name: str
    display_name: str
    total_calls: int = 0
    success_calls: int = 0
    failed_calls: int = 0
    avg_duration_ms: Optional[float] = None
    last_used_at: Optional[datetime] = None
