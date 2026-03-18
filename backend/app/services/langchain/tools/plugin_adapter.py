"""
Plugin 到 LangChain Tool 适配器

将现有的 PluginInterface 插件转换为 LangChain 兼容的 BaseTool，
实现无缝集成，无需修改现有插件代码。
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Type, Union

from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field, create_model

from app.services.plugins.plugin_interface import PluginInterface

logger = logging.getLogger(__name__)


class PluginToolAdapter(BaseTool):
    """
    将 PluginInterface 适配为 LangChain BaseTool
    
    这个适配器包装现有的插件实例，使其能够被 LangChain Agent 调用。
    保留插件的所有元数据和执行逻辑。
    
    Example:
        >>> from app.services.plugins.plugins.utilities.calculator import CalculatorPlugin
        >>> plugin = CalculatorPlugin()
        >>> tool = PluginToolAdapter(plugin=plugin)
        >>> result = await tool.ainvoke({"expression": "2 + 2"})
    """
    
    # 被包装的插件实例
    plugin: PluginInterface = Field(exclude=True)
    
    # 覆盖 BaseTool 的属性
    name: str = ""
    description: str = ""
    
    # 是否返回直接结果（不经过 Agent 处理）
    return_direct: bool = False
    
    class Config:
        """Pydantic 配置"""
        arbitrary_types_allowed = True
    
    def __init__(self, plugin: PluginInterface, **kwargs):
        """
        初始化适配器
        
        Args:
            plugin: PluginInterface 插件实例
            **kwargs: 额外参数
        """
        # 从插件获取元数据
        super().__init__(
            plugin=plugin,
            name=plugin.name,
            description=plugin.description,
            **kwargs
        )
    
    @property
    def args_schema(self) -> Optional[Type[BaseModel]]:
        """
        动态生成参数 Schema（从 plugin.parameters_schema 转换）
        
        LangChain 使用 Pydantic 模型定义工具参数，
        而我们的插件使用 JSON Schema。这里进行转换。
        """
        return _json_schema_to_pydantic(
            self.plugin.parameters_schema,
            f"{self.plugin.name.title().replace('_', '')}Args"
        )
    
    def _run(
        self,
        *args,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """
        同步执行（回退到异步）
        
        大多数插件是异步的，这里用 asyncio.run 包装。
        注意：在已有事件循环的环境中可能需要特殊处理。
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已在异步环境中，创建新线程执行
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._arun(*args, run_manager=None, **kwargs)
                    )
                    return future.result()
            else:
                return asyncio.run(self._arun(*args, run_manager=None, **kwargs))
        except RuntimeError:
            # 没有事件循环，直接创建新的
            return asyncio.run(self._arun(*args, run_manager=None, **kwargs))
    
    async def _arun(
        self,
        *args,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """
        异步执行插件
        
        Returns:
            JSON 格式的执行结果字符串
        """
        try:
            logger.debug(f"Executing plugin {self.name} with args: {kwargs}")
            
            # 调用插件的 execute 方法
            result = await self.plugin.execute(**kwargs)
            
            # 将结果转换为字符串（LangChain Tool 返回字符串）
            if isinstance(result, dict):
                # 格式化输出，便于 LLM 理解
                if result.get("success"):
                    data = result.get("data", result)
                    return json.dumps(data, ensure_ascii=False, indent=2)
                else:
                    error = result.get("error", "未知错误")
                    return f"执行失败: {error}"
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Plugin {self.name} execution error: {e}", exc_info=True)
            return f"插件执行错误: {str(e)}"


def create_tool_from_plugin(plugin: PluginInterface) -> PluginToolAdapter:
    """
    从 PluginInterface 创建 LangChain Tool
    
    便捷函数，用于快速转换插件。
    
    Args:
        plugin: PluginInterface 实例
        
    Returns:
        PluginToolAdapter 实例
        
    Example:
        >>> plugin = WebSearchPlugin(api_key="xxx")
        >>> tool = create_tool_from_plugin(plugin)
    """
    return PluginToolAdapter(plugin=plugin)


def create_tools_from_plugins(plugins: List[PluginInterface]) -> List[PluginToolAdapter]:
    """
    批量转换插件为 LangChain Tools
    
    Args:
        plugins: 插件实例列表
        
    Returns:
        PluginToolAdapter 列表
    """
    return [create_tool_from_plugin(p) for p in plugins]


def _json_schema_to_pydantic(
    schema: Dict[str, Any],
    model_name: str = "DynamicModel"
) -> Type[BaseModel]:
    """
    将 JSON Schema 转换为 Pydantic 模型
    
    这是一个简化的转换器，处理常见的 JSON Schema 结构。
    
    Args:
        schema: JSON Schema 字典
        model_name: 生成的模型名称
        
    Returns:
        动态创建的 Pydantic 模型类
    """
    if not schema or schema.get("type") != "object":
        # 空 schema 或非 object 类型，返回空模型
        return create_model(model_name)
    
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    
    # 构建字段定义
    field_definitions = {}
    
    for field_name, field_schema in properties.items():
        field_type = _get_python_type(field_schema)
        field_description = field_schema.get("description", "")
        field_default = field_schema.get("default", ...)
        
        # 如果不是必需字段且没有默认值，设为 None
        if field_name not in required and field_default is ...:
            field_default = None
            if field_type != type(None):
                field_type = Optional[field_type]
        
        field_definitions[field_name] = (
            field_type,
            Field(default=field_default, description=field_description)
        )
    
    return create_model(model_name, **field_definitions)


def _get_python_type(field_schema: Dict[str, Any]) -> Type:
    """
    从 JSON Schema 字段定义获取 Python 类型
    
    Args:
        field_schema: 字段的 JSON Schema
        
    Returns:
        对应的 Python 类型
    """
    json_type = field_schema.get("type", "string")
    
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    
    # 处理联合类型
    if isinstance(json_type, list):
        # 如 ["string", "null"] -> Optional[str]
        types = [type_mapping.get(t, Any) for t in json_type if t != "null"]
        if len(types) == 1:
            return Optional[types[0]]
        return Any
    
    return type_mapping.get(json_type, str)


# ============================================================================
# 工具函数：创建常用工具
# ============================================================================

def create_builtin_tools(
    plugin_configs: Dict[str, Dict[str, Any]] = None
) -> List[BaseTool]:
    """
    创建内置工具列表
    
    根据配置加载并初始化内置插件，转换为 LangChain Tools。
    
    Args:
        plugin_configs: 插件配置字典，格式：
            {
                "web_search": {"api_key": "xxx"},
                "calculator": {}
            }
            
    Returns:
        BaseTool 列表
    """
    from app.services.plugins.registry import PluginRegistry
    
    tools = []
    configs = plugin_configs or {}
    
    # 获取所有已注册的内置插件
    registry = PluginRegistry()
    builtin_plugins = registry.get_builtin_plugins()
    
    for plugin_class in builtin_plugins:
        plugin_name = plugin_class.name
        
        # 获取该插件的配置
        config = configs.get(plugin_name, {})
        
        try:
            # 实例化插件
            plugin = plugin_class(**config)
            
            # 转换为 Tool
            tool = create_tool_from_plugin(plugin)
            tools.append(tool)
            
            logger.debug(f"Created tool from plugin: {plugin_name}")
            
        except Exception as e:
            logger.warning(f"Failed to create tool from {plugin_name}: {e}")
    
    return tools
