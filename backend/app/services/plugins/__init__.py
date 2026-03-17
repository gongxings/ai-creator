"""
插件系统
"""
from app.services.plugins.plugin_interface import PluginInterface
from app.services.plugins.registry import PluginRegistry, plugin_registry, register_plugin
from app.services.plugins.plugin_manager import PluginManager

__all__ = [
    "PluginInterface",
    "PluginRegistry",
    "plugin_registry",
    "register_plugin",
    "PluginManager",
]
