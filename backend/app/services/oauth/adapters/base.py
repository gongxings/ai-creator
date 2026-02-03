"""
平台适配器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger


class PlatformAdapter(ABC):
    """平台适配器基类"""
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            platform_id: 平台ID
            config: 平台配置
        """
        self.platform_id = platform_id
        self.config = config
        self.oauth_config = config.get("oauth_config", {})
        self.litellm_config = config.get("litellm_config", {})
        self.quota_config = config.get("quota_config", {})
    
    @abstractmethod
    def get_oauth_url(self) -> str:
        """
        获取OAuth授权URL
        
        Returns:
            授权URL
        """
        pass
    
    @abstractmethod
    def get_success_pattern(self) -> str:
        """
        获取登录成功的URL模式
        
        Returns:
            URL模式（支持通配符）
        """
        pass
    
    @abstractmethod
    def get_cookie_names(self) -> list:
        """
        获取需要提取的Cookie名称列表
        
        Returns:
            Cookie名称列表
        """
        pass
    
    def get_cookie_domain(self) -> str:
        """
        获取Cookie域名
        
        Returns:
            Cookie域名
        """
        return self.oauth_config.get("cookie_domain", "")
    
    def get_check_url(self) -> Optional[str]:
        """
        获取凭证验证URL
        
        Returns:
            验证URL
        """
        return self.oauth_config.get("check_url")
    
    @abstractmethod
    def build_litellm_config(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建LiteLLM配置
        
        Args:
            credentials: 凭证信息
            
        Returns:
            LiteLLM配置字典
        """
        pass
    
    def get_quota_limit(self) -> Optional[int]:
        """
        获取配额限制
        
        Returns:
            配额限制（tokens数）
        """
        return self.quota_config.get("limit")
    
    def get_rate_limit(self) -> Dict[str, int]:
        """
        获取速率限制
        
        Returns:
            速率限制配置
        """
        return {
            "requests_per_minute": self.quota_config.get("requests_per_minute", 60),
            "tokens_per_minute": self.quota_config.get("tokens_per_minute", 100000),
        }
    
    def get_platform_config(self) -> Dict[str, Any]:
        """
        获取完整的平台配置（用于Playwright）
        
        Returns:
            平台配置字典
        """
        return {
            "platform_id": self.platform_id,
            "oauth_url": self.get_oauth_url(),
            "success_pattern": self.get_success_pattern(),
            "cookie_names": self.get_cookie_names(),
            "cookie_domain": self.get_cookie_domain(),
            "check_url": self.get_check_url(),
        }
    
    def extract_user_info(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        从凭证中提取用户信息（可选）
        
        Args:
            credentials: 凭证信息
            
        Returns:
            用户信息字典
        """
        return {}
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        验证凭证格式是否正确
        
        Args:
            credentials: 凭证信息
            
        Returns:
            是否有效
        """
        if not credentials:
            return False
        
        cookies = credentials.get("cookies", {})
        if not cookies:
            return False
        
        # 检查必需的Cookie是否存在
        required_cookies = self.get_cookie_names()
        for cookie_name in required_cookies:
            if cookie_name not in cookies:
                logger.warning(f"Missing required cookie: {cookie_name}")
                return False
        
        return True
