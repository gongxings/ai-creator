"""
平台发布服务包
"""
from .base import BasePlatform
from .wechat import WechatPlatform
from .xiaohongshu import XiaohongshuPlatform
from .douyin import DouyinPlatform
from .kuaishou import KuaishouPlatform
from .toutiao import ToutiaoPlatform

# 平台注册表
PLATFORM_REGISTRY = {
    "wechat": WechatPlatform,
    "xiaohongshu": XiaohongshuPlatform,
    "douyin": DouyinPlatform,
    "kuaishou": KuaishouPlatform,
    "toutiao": ToutiaoPlatform,
}


def get_platform(platform_name: str) -> BasePlatform:
    """
    获取平台实例
    
    Args:
        platform_name: 平台名称
        
    Returns:
        BasePlatform: 平台实例
        
    Raises:
        ValueError: 不支持的平台
    """
    platform_class = PLATFORM_REGISTRY.get(platform_name)
    if not platform_class:
        raise ValueError(f"不支持的平台: {platform_name}")
    return platform_class()


__all__ = [
    "BasePlatform",
    "WechatPlatform",
    "XiaohongshuPlatform",
    "DouyinPlatform",
    "KuaishouPlatform",
    "ToutiaoPlatform",
    "PLATFORM_REGISTRY",
    "get_platform",
]
