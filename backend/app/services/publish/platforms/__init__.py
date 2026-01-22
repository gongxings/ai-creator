"""
平台发布服务包
"""
from .base import BasePlatformPublisher
from .wechat import WeChatPublisher
from .xiaohongshu import XiaohongshuPublisher
from .douyin import DouyinPublisher
from .kuaishou import KuaishouPublisher
from .toutiao import ToutiaoPublisher

# 平台注册表
PLATFORM_REGISTRY = {
    "wechat": WeChatPublisher,
    "xiaohongshu": XiaohongshuPublisher,
    "douyin": DouyinPublisher,
    "kuaishou": KuaishouPublisher,
    "toutiao": ToutiaoPublisher,
}


def get_platform(platform_name: str) -> BasePlatformPublisher:
    """
    获取平台实例
    
    Args:
        platform_name: 平台名称
        
    Returns:
        BasePlatformPublisher: 平台实例
        
    Raises:
        ValueError: 不支持的平台
    """
    platform_class = PLATFORM_REGISTRY.get(platform_name)
    if not platform_class:
        raise ValueError(f"不支持的平台: {platform_name}")
    return platform_class()


__all__ = [
    "BasePlatformPublisher",
    "WeChatPublisher",
    "XiaohongshuPublisher",
    "DouyinPublisher",
    "KuaishouPublisher",
    "ToutiaoPublisher",
    "PLATFORM_REGISTRY",
    "get_platform",
]
