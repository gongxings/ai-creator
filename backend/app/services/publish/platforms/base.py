"""
平台发布器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.publish import PlatformAccount


class BasePlatformPublisher(ABC):
    """平台发布器基类"""
    
    @abstractmethod
    async def publish(
        self,
        account: PlatformAccount,
        content: Dict[str, Any],
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        发布内容到平台
        
        Args:
            account: 平台账号
            content: 发布内容
            config: 发布配置
            
        Returns:
            Dict: 发布结果，包含post_id和url
        """
        pass
    
    @abstractmethod
    async def check_status(
        self,
        account: PlatformAccount,
        post_id: str
    ) -> Dict[str, Any]:
        """
        检查发布状态
        
        Args:
            account: 平台账号
            post_id: 文章ID
            
        Returns:
            Dict: 状态信息
        """
        pass
    
    def _get_credentials(self, account: PlatformAccount) -> Dict[str, Any]:
        """获取平台凭证"""
        import json
        return json.loads(account.credentials)
