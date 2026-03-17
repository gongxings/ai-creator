"""
插件管理器
"""
import importlib
import pkgutil
import inspect
import time
import json
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.services.plugins.plugin_interface import PluginInterface
from app.services.plugins.registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginManager:
    """
    插件管理器（单例模式）
    
    负责：
    - 发现和加载内置插件
    - 管理用户插件安装/卸载
    - 执行插件并记录日志
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not PluginManager._initialized:
            PluginManager._initialized = True
            logger.info("PluginManager initialized")
    
    def discover_builtin_plugins(self) -> List[Type[PluginInterface]]:
        """
        发现内置插件（自动扫描 plugins 包）
        
        Returns:
            发现的插件类列表
        """
        discovered = []
        
        try:
            # 导入 plugins 包
            import app.services.plugins.plugins as plugins_pkg
            
            # 遍历所有子包
            for importer, modname, ispkg in pkgutil.walk_packages(
                plugins_pkg.__path__, 
                prefix="app.services.plugins.plugins."
            ):
                try:
                    module = importlib.import_module(modname)
                    
                    # 查找所有 PluginInterface 的子类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, PluginInterface) and 
                            obj != PluginInterface and
                            hasattr(obj, 'name') and obj.name):
                            
                            # 检查是否已注册（避免重复注册）
                            if obj.name not in PluginRegistry.list_names():
                                PluginRegistry.register(obj)
                                logger.info(f"Discovered plugin: {obj.name} from {modname}")
                            
                            # 始终添加到发现列表（用于返回）
                            if obj not in discovered:
                                discovered.append(obj)
                            
                except Exception as e:
                    logger.error(f"Failed to load module {modname}: {e}")
                    
        except ImportError as e:
            logger.warning(f"Plugins package not found: {e}")
        
        logger.info(f"Discovered {len(discovered)} builtin plugins")
        return discovered
    
    def sync_to_database(self, db: Session) -> int:
        """
        将已注册的插件同步到数据库 plugin_market 表
        
        Args:
            db: 数据库 session
            
        Returns:
            同步的插件数量
        """
        from app.models.plugin import PluginMarket
        
        synced = 0
        for plugin_class in PluginRegistry.list_all():
            try:
                # 创建临时实例获取信息
                instance = plugin_class()
                info = instance.get_info()
                
                # 查找或创建
                existing = db.query(PluginMarket).filter_by(name=info["name"]).first()
                
                if existing:
                    # 更新现有记录
                    existing.display_name = info["display_name"]
                    existing.description = info["description"]
                    existing.version = info["version"]
                    existing.author = info["author"]
                    existing.category = info["category"]
                    existing.tags = info["tags"]
                    existing.icon = info.get("icon", "")
                    existing.config_schema = info["config_schema"]
                    existing.parameters_schema = info["parameters_schema"]
                    existing.entry_point = f"{plugin_class.__module__}:{plugin_class.__name__}"
                else:
                    # 创建新记录
                    market_plugin = PluginMarket(
                        name=info["name"],
                        display_name=info["display_name"],
                        description=info["description"],
                        short_description=info["description"][:200] if info["description"] else "",
                        version=info["version"],
                        author=info["author"],
                        category=info["category"],
                        tags=info["tags"],
                        icon=info.get("icon", ""),
                        is_official=True,
                        is_approved=True,
                        is_active=True,
                        config_schema=info["config_schema"],
                        parameters_schema=info["parameters_schema"],
                        entry_point=f"{plugin_class.__module__}:{plugin_class.__name__}",
                    )
                    db.add(market_plugin)
                
                synced += 1
                
            except Exception as e:
                logger.error(f"Failed to sync plugin {plugin_class.name}: {e}")
        
        db.commit()
        logger.info(f"Synced {synced} plugins to database")
        return synced
    
    def get_user_plugins(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户已安装的插件列表
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            
        Returns:
            用户插件列表（包含市场信息）
        """
        from app.models.plugin import UserPlugin, PluginMarket
        
        user_plugins = db.query(UserPlugin, PluginMarket).join(
            PluginMarket, UserPlugin.plugin_name == PluginMarket.name
        ).filter(
            UserPlugin.user_id == user_id
        ).all()
        
        result = []
        for up, pm in user_plugins:
            result.append({
                "id": up.id,
                "name": pm.name,
                "display_name": pm.display_name,
                "description": pm.description,
                "category": pm.category,
                "icon": pm.icon,
                "version": pm.version,
                "is_enabled": up.is_enabled,
                "is_auto_use": up.is_auto_use,
                "config": up.config,
                "usage_count": up.usage_count,
                "last_used_at": up.last_used_at,
                "installed_at": up.installed_at,
            })
        
        return result
    
    def install_plugin(
        self, 
        db: Session, 
        user_id: int, 
        plugin_name: str, 
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        为用户安装插件
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_name: 插件名称
            config: 插件配置
            
        Returns:
            安装结果
        """
        from app.models.plugin import UserPlugin, PluginMarket
        
        # 检查插件是否存在于市场
        market_plugin = db.query(PluginMarket).filter_by(
            name=plugin_name, 
            is_active=True
        ).first()
        
        if not market_plugin:
            raise ValueError(f"插件 '{plugin_name}' 不存在或已下架")
        
        # 检查是否已安装
        existing = db.query(UserPlugin).filter_by(
            user_id=user_id,
            plugin_name=plugin_name
        ).first()
        
        if existing:
            raise ValueError(f"插件 '{plugin_name}' 已安装")
        
        # 验证配置
        plugin_class = PluginRegistry.get_class(plugin_name)
        if plugin_class:
            instance = plugin_class()
            if config and not instance.validate_config(config):
                raise ValueError("插件配置无效")
        
        # 创建安装记录
        user_plugin = UserPlugin(
            user_id=user_id,
            plugin_name=plugin_name,
            is_enabled=True,
            config=config or {},
        )
        db.add(user_plugin)
        
        # 更新安装次数
        market_plugin.download_count = (market_plugin.download_count or 0) + 1
        
        db.commit()
        db.refresh(user_plugin)
        
        # 触发安装钩子
        if plugin_class:
            try:
                instance = plugin_class(**(config or {}))
                import asyncio
                asyncio.create_task(instance.on_install(user_id, config or {}))
            except Exception as e:
                logger.warning(f"Plugin on_install hook failed: {e}")
        
        logger.info(f"User {user_id} installed plugin '{plugin_name}'")
        
        return {
            "id": user_plugin.id,
            "plugin_name": plugin_name,
            "installed_at": user_plugin.installed_at,
        }
    
    def uninstall_plugin(self, db: Session, user_id: int, plugin_name: str) -> bool:
        """
        为用户卸载插件
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_name: 插件名称
            
        Returns:
            是否成功卸载
        """
        from app.models.plugin import UserPlugin
        
        user_plugin = db.query(UserPlugin).filter_by(
            user_id=user_id,
            plugin_name=plugin_name
        ).first()
        
        if not user_plugin:
            raise ValueError(f"插件 '{plugin_name}' 未安装")
        
        # 触发卸载钩子
        plugin_class = PluginRegistry.get_class(plugin_name)
        if plugin_class:
            try:
                instance = plugin_class()
                import asyncio
                asyncio.create_task(instance.on_uninstall(user_id))
            except Exception as e:
                logger.warning(f"Plugin on_uninstall hook failed: {e}")
        
        db.delete(user_plugin)
        db.commit()
        
        logger.info(f"User {user_id} uninstalled plugin '{plugin_name}'")
        return True
    
    def update_plugin_config(
        self, 
        db: Session, 
        user_id: int, 
        plugin_name: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新用户的插件配置
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_name: 插件名称
            config: 新配置
            
        Returns:
            更新后的配置
        """
        from app.models.plugin import UserPlugin
        
        user_plugin = db.query(UserPlugin).filter_by(
            user_id=user_id,
            plugin_name=plugin_name
        ).first()
        
        if not user_plugin:
            raise ValueError(f"插件 '{plugin_name}' 未安装")
        
        # 验证配置
        plugin_class = PluginRegistry.get_class(plugin_name)
        if plugin_class:
            instance = plugin_class()
            if not instance.validate_config(config):
                raise ValueError("插件配置无效")
        
        user_plugin.config = config
        db.commit()
        
        return {"plugin_name": plugin_name, "config": config}
    
    def toggle_plugin(
        self, 
        db: Session, 
        user_id: int, 
        plugin_name: str, 
        enabled: bool
    ) -> bool:
        """
        启用/禁用用户的插件
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_name: 插件名称
            enabled: 是否启用
            
        Returns:
            是否成功
        """
        from app.models.plugin import UserPlugin
        
        user_plugin = db.query(UserPlugin).filter_by(
            user_id=user_id,
            plugin_name=plugin_name
        ).first()
        
        if not user_plugin:
            raise ValueError(f"插件 '{plugin_name}' 未安装")
        
        user_plugin.is_enabled = enabled
        db.commit()
        
        return True
    
    def get_user_plugin_selection(
        self, 
        db: Session, 
        user_id: int, 
        tool_type: str
    ) -> List[str]:
        """
        获取用户为指定创作类型选择的插件列表
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            tool_type: 写作类型
            
        Returns:
            插件名称列表
        """
        from app.models.plugin import CreationPluginSelection
        
        selection = db.query(CreationPluginSelection).filter_by(
            user_id=user_id,
            tool_type=tool_type
        ).first()
        
        if selection and selection.selected_plugins:
            return selection.selected_plugins
        return []
    
    def save_user_plugin_selection(
        self, 
        db: Session, 
        user_id: int, 
        tool_type: str, 
        plugin_names: List[str]
    ) -> None:
        """
        保存用户为指定创作类型选择的插件列表
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            tool_type: 写作类型
            plugin_names: 插件名称列表
        """
        from app.models.plugin import CreationPluginSelection
        
        selection = db.query(CreationPluginSelection).filter_by(
            user_id=user_id,
            tool_type=tool_type
        ).first()
        
        if selection:
            selection.selected_plugins = plugin_names
        else:
            selection = CreationPluginSelection(
                user_id=user_id,
                tool_type=tool_type,
                selected_plugins=plugin_names
            )
            db.add(selection)
        
        db.commit()
    
    def create_plugin_instances(
        self, 
        db: Session, 
        user_id: int, 
        plugin_names: List[str]
    ) -> List[PluginInterface]:
        """
        为用户创建插件实例（带用户配置）
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_names: 插件名称列表
            
        Returns:
            插件实例列表
        """
        from app.models.plugin import UserPlugin
        
        instances = []
        
        # 获取用户的插件配置
        user_plugins = db.query(UserPlugin).filter(
            UserPlugin.user_id == user_id,
            UserPlugin.plugin_name.in_(plugin_names),
            UserPlugin.is_enabled == True
        ).all()
        
        user_configs = {up.plugin_name: up.config or {} for up in user_plugins}
        
        for name in plugin_names:
            plugin_class = PluginRegistry.get_class(name)
            if plugin_class:
                try:
                    config = user_configs.get(name, {})
                    instance = plugin_class(**config)
                    instance.set_context(user_id=user_id, db_session=db)
                    instances.append(instance)
                except Exception as e:
                    logger.error(f"Failed to create plugin instance '{name}': {e}")
        
        return instances
    
    async def execute_plugin(
        self, 
        db: Session,
        user_id: int,
        plugin_name: str,
        arguments: Dict[str, Any],
        creation_id: int = None
    ) -> Dict[str, Any]:
        """
        执行插件并记录日志
        
        Args:
            db: 数据库 session
            user_id: 用户 ID
            plugin_name: 插件名称
            arguments: 调用参数
            creation_id: 关联的创作 ID（可选）
            
        Returns:
            执行结果
        """
        from app.models.plugin import PluginInvocation, UserPlugin
        
        start_time = time.time()
        result = None
        error = None
        
        try:
            # 获取用户配置
            user_plugin = db.query(UserPlugin).filter_by(
                user_id=user_id,
                plugin_name=plugin_name,
                is_enabled=True
            ).first()
            
            if not user_plugin:
                raise ValueError(f"插件 '{plugin_name}' 未安装或未启用")
            
            # 创建插件实例
            plugin_class = PluginRegistry.get_class(plugin_name)
            if not plugin_class:
                raise ValueError(f"插件 '{plugin_name}' 未注册")
            
            config = user_plugin.config or {}
            instance = plugin_class(**config)
            instance.set_context(user_id=user_id, db_session=db)
            
            # 执行插件
            result = await instance.execute(**arguments)
            
            # 更新使用统计
            user_plugin.usage_count = (user_plugin.usage_count or 0) + 1
            user_plugin.last_used_at = datetime.utcnow()
            
        except Exception as e:
            error = str(e)
            logger.error(f"Plugin '{plugin_name}' execution failed: {e}")
            result = {"error": error}
        
        # 记录日志
        duration_ms = int((time.time() - start_time) * 1000)
        
        invocation = PluginInvocation(
            user_id=user_id,
            creation_id=creation_id,
            plugin_name=plugin_name,
            arguments=arguments,
            result=result,
            error=error,
            duration_ms=duration_ms,
        )
        db.add(invocation)
        db.commit()
        
        return result


# 全局单例
plugin_manager = PluginManager()
