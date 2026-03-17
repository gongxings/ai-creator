"""
插件接口定义
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PluginInterface(ABC):
    """
    插件接口基类
    
    所有插件必须继承此类并实现抽象方法。
    设计兼容 LangChain Tool，但不强依赖 LangChain。
    """
    
    # ============ 元数据（必须重写）============
    name: str = ""                           # 插件唯一标识符（如 "web_search"）
    display_name: str = ""                   # 显示名称（如 "网页搜索"）
    description: str = ""                    # 描述（用于 AI 理解何时调用）
    version: str = "1.0.0"                   # 版本号
    author: str = "AI Creator"               # 作者
    category: str = "utility"                # 分类：search, writing, media, utility
    tags: List[str] = []                     # 标签（用于搜索/筛选）
    icon: str = ""                           # 图标（emoji 或图标名称）
    
    # ============ 配置（可选）=================
    # config_schema: 用于前端生成配置表单（JSON Schema 格式）
    # 例如：{"type": "object", "properties": {"api_key": {"type": "string", "title": "API Key"}}}
    config_schema: Dict[str, Any] = {}
    
    # parameters_schema: 用于 OpenAI function calling 的参数定义
    # 例如：{"type": "object", "properties": {"query": {"type": "string", "description": "搜索查询"}}}
    parameters_schema: Dict[str, Any] = {}
    
    # ============ 运行时状态 ==================
    _config: Dict[str, Any] = {}             # 用户配置（运行时注入）
    _user_id: Optional[int] = None           # 当前用户 ID
    _db_session: Any = None                  # 数据库 session
    
    def __init__(self, **config):
        """
        初始化插件
        
        Args:
            **config: 用户配置参数（如 api_key 等）
        """
        self._config = config
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_context(self, user_id: int = None, db_session: Any = None):
        """
        设置运行时上下文
        
        Args:
            user_id: 当前用户 ID
            db_session: 数据库 session
        """
        self._user_id = user_id
        self._db_session = db_session
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证用户配置是否有效
        
        Args:
            config: 用户配置字典
            
        Returns:
            True 如果配置有效，否则 False
        """
        # 检查必需字段
        required = self.config_schema.get("required", [])
        for field in required:
            if field not in config or not config[field]:
                return False
        return True
    
    # ============ 生命周期钩子（可选重写）==========
    async def on_install(self, user_id: int, config: Dict[str, Any]):
        """安装时触发（可用于初始化资源）"""
        pass
    
    async def on_uninstall(self, user_id: int):
        """卸载时触发（可用于清理资源）"""
        pass
    
    async def on_enable(self, user_id: int):
        """启用时触发"""
        pass
    
    async def on_disable(self, user_id: int):
        """禁用时触发"""
        pass
    
    # ============ 核心执行方法（必须实现）============
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行插件功能（异步）
        
        Args:
            **kwargs: 调用参数（根据 parameters_schema 定义）
            
        Returns:
            执行结果字典，至少包含 {"success": bool, "data": any} 或 {"error": str}
        """
        pass
    
    def execute_sync(self, **kwargs) -> Dict[str, Any]:
        """
        同步执行（不推荐，仅用于兼容）
        
        默认实现抛出异常，强制使用异步版本
        """
        raise NotImplementedError("请使用异步方法 execute()")
    
    # ============ OpenAI Function Calling 格式转换 ============
    def to_openai_function(self) -> Dict[str, Any]:
        """
        转换为 OpenAI function calling 格式
        
        Returns:
            OpenAI tools 格式的函数定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema or {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    # ============ 插件信息 ============
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息（用于市场展示）
        
        Returns:
            插件元数据字典
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "tags": self.tags,
            "icon": self.icon,
            "config_schema": self.config_schema,
            "parameters_schema": self.parameters_schema,
        }
    
    def __repr__(self):
        return f"<Plugin({self.name} v{self.version})>"


class PluginResult(BaseModel):
    """插件执行结果标准格式"""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def ok(cls, data: Any, metadata: Dict[str, Any] = None) -> "PluginResult":
        """成功结果"""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def fail(cls, error: str, metadata: Dict[str, Any] = None) -> "PluginResult":
        """失败结果"""
        return cls(success=False, error=error, metadata=metadata)
