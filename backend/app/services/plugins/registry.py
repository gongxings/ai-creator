"""
插件注册中心
"""
from typing import Dict, List, Optional, Type
import logging

from app.services.plugins.plugin_interface import PluginInterface

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    插件注册中心（单例模式）
    
    负责管理所有已注册的插件类和实例。
    """
    
    # 已注册的插件类（name -> Plugin Class）
    _plugin_classes: Dict[str, Type[PluginInterface]] = {}
    
    # 已实例化的插件（name -> Plugin Instance）
    _plugin_instances: Dict[str, PluginInterface] = {}
    
    @classmethod
    def register(cls, plugin_class: Type[PluginInterface]) -> None:
        """
        注册插件类
        
        Args:
            plugin_class: 插件类（继承自 PluginInterface）
        """
        if not issubclass(plugin_class, PluginInterface):
            raise TypeError(f"{plugin_class.__name__} must be subclass of PluginInterface")
        
        name = plugin_class.name
        if not name:
            raise ValueError(f"Plugin class {plugin_class.__name__} must have a 'name' attribute")
        
        if name in cls._plugin_classes:
            logger.warning(f"Plugin '{name}' is already registered, overwriting...")
        
        cls._plugin_classes[name] = plugin_class
        logger.info(f"Registered plugin: {name} ({plugin_class.__name__})")
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        取消注册插件
        
        Args:
            name: 插件名称
            
        Returns:
            是否成功取消注册
        """
        if name in cls._plugin_classes:
            del cls._plugin_classes[name]
            if name in cls._plugin_instances:
                del cls._plugin_instances[name]
            logger.info(f"Unregistered plugin: {name}")
            return True
        return False
    
    @classmethod
    def get_class(cls, name: str) -> Optional[Type[PluginInterface]]:
        """
        获取插件类
        
        Args:
            name: 插件名称
            
        Returns:
            插件类或 None
        """
        return cls._plugin_classes.get(name)
    
    @classmethod
    def get_instance(cls, name: str, **config) -> Optional[PluginInterface]:
        """
        获取插件实例（带配置）
        
        Args:
            name: 插件名称
            **config: 插件配置
            
        Returns:
            插件实例或 None
        """
        plugin_class = cls._plugin_classes.get(name)
        if not plugin_class:
            return None
        
        # 每次创建新实例（因为配置可能不同）
        try:
            instance = plugin_class(**config)
            return instance
        except Exception as e:
            logger.error(f"Failed to create plugin instance '{name}': {e}")
            return None
    
    @classmethod
    def list_all(cls) -> List[Type[PluginInterface]]:
        """
        列出所有已注册的插件类
        
        Returns:
            插件类列表
        """
        return list(cls._plugin_classes.values())
    
    @classmethod
    def list_names(cls) -> List[str]:
        """
        列出所有已注册的插件名称
        
        Returns:
            插件名称列表
        """
        return list(cls._plugin_classes.keys())
    
    @classmethod
    def list_by_category(cls, category: str) -> List[Type[PluginInterface]]:
        """
        按分类列出插件
        
        Args:
            category: 分类名称
            
        Returns:
            该分类下的插件类列表
        """
        return [
            p for p in cls._plugin_classes.values()
            if p.category == category
        ]
    
    @classmethod
    def get_info_all(cls) -> List[Dict]:
        """
        获取所有插件的信息
        
        Returns:
            插件信息列表
        """
        result = []
        for plugin_class in cls._plugin_classes.values():
            try:
                # 创建临时实例获取信息
                instance = plugin_class()
                result.append(instance.get_info())
            except Exception as e:
                logger.error(f"Failed to get info for plugin {plugin_class.name}: {e}")
        return result
    
    @classmethod
    def to_openai_functions(cls, plugin_names: List[str]) -> List[Dict]:
        """
        将指定插件转换为 OpenAI function calling 格式
        
        Args:
            plugin_names: 插件名称列表
            
        Returns:
            OpenAI tools 格式的函数定义列表
        """
        functions = []
        for name in plugin_names:
            plugin_class = cls._plugin_classes.get(name)
            if plugin_class:
                try:
                    instance = plugin_class()
                    functions.append(instance.to_openai_function())
                except Exception as e:
                    logger.error(f"Failed to convert plugin '{name}' to OpenAI function: {e}")
        return functions
    
    @classmethod
    def create_instances(cls, plugin_names: List[str], configs: Dict[str, Dict] = None) -> List[PluginInterface]:
        """
        批量创建插件实例
        
        Args:
            plugin_names: 插件名称列表
            configs: 每个插件的配置 {"plugin_name": {"key": "value"}}
            
        Returns:
            插件实例列表
        """
        configs = configs or {}
        instances = []
        
        for name in plugin_names:
            plugin_class = cls._plugin_classes.get(name)
            if plugin_class:
                try:
                    config = configs.get(name, {})
                    instance = plugin_class(**config)
                    instances.append(instance)
                except Exception as e:
                    logger.error(f"Failed to create plugin instance '{name}': {e}")
        
        return instances
    
    @classmethod
    def clear(cls) -> None:
        """清空所有注册的插件（用于测试）"""
        cls._plugin_classes.clear()
        cls._plugin_instances.clear()
        logger.info("Cleared all registered plugins")


# 装饰器：用于自动注册插件
def register_plugin(cls: Type[PluginInterface]) -> Type[PluginInterface]:
    """
    插件注册装饰器
    
    Usage:
        @register_plugin
        class MyPlugin(PluginInterface):
            name = "my_plugin"
            ...
    """
    PluginRegistry.register(cls)
    return cls


# 全局单例实例（方便导入使用）
plugin_registry = PluginRegistry
