"""
OAuth授权会话管理
支持分步授权流程（开始授权 -> 获取二维码 -> 检查状态 -> 完成授权）
"""
import asyncio
import base64
from typing import Dict, Any, Optional
from loguru import logger
from playwright.async_api import Page, BrowserContext

from app.services.oauth.playwright_service import playwright_service


class OAuthSession:
    """OAuth授权会话"""
    
    def __init__(self, user_id: int, platform: str, platform_config: Dict[str, Any]):
        """
        初始化授权会话
        
        Args:
            user_id: 用户ID
            platform: 平台ID
            platform_config: 平台配置
        """
        self.user_id = user_id
        self.platform = platform
        self.platform_config = platform_config
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.credentials: Optional[Dict[str, Any]] = None
    
    async def start(self):
        """开始授权流程"""
        # 创建浏览器上下文
        self.context = await playwright_service.create_context()
        self.page = await self.context.new_page()
        
        # 设置超时
        self.page.set_default_timeout(playwright_service.timeout)
        
        # 导航到OAuth URL
        oauth_url = self.platform_config.get("oauth_url")
        if not oauth_url:
            raise ValueError("oauth_url not found in platform config")
        
        await self.page.goto(oauth_url)
        logger.info(f"Session {self.user_id}-{self.platform}: Navigated to {oauth_url}")
        
        # 尝试点击登录按钮
        await playwright_service._click_login_button(self.page)
        logger.info(f"Session {self.user_id}-{self.platform}: Login button clicked")
    
    async def get_qr_code(self) -> Optional[str]:
        """
        获取二维码图片（base64编码）
        
        Returns:
            base64编码的图片，如果找不到二维码返回None
        """
        try:
            # 获取二维码选择器
            from app.services.oauth.adapters import get_adapter
            adapter = get_adapter(self.platform, {
                "oauth_config": self.platform_config,
                "litellm_config": {},
                "quota_config": {},
            })
            
            if not adapter or not hasattr(adapter, "get_qr_code_selector"):
                return None
            
            qr_selector = adapter.get_qr_code_selector()
            if not qr_selector:
                return None
            
            # 等待二维码元素出现
            qr_element = await self.page.wait_for_selector(qr_selector, timeout=5000)
            if not qr_element:
                return None
            
            # 截取二维码
            screenshot = await qr_element.screenshot(type="png")
            # 转换为base64
            base64_image = base64.b64encode(screenshot).decode("utf-8")
            
            logger.info(f"Session {self.user_id}-{self.platform}: QR code captured")
            return base64_image
        except Exception as e:
            logger.warning(f"Session {self.user_id}-{self.platform}: Failed to capture QR code: {e}")
            return None
    
    async def check_login_status(self) -> bool:
        """
        检查登录状态
        
        Returns:
            是否已登录
        """
        self.is_logged_in = await playwright_service._check_login_status(self.page)
        return self.is_logged_in
    
    async def extract_credentials(self) -> Dict[str, Any]:
        """
        提取登录凭证
        
        Returns:
            凭证字典
        """
        if not self.is_logged_in:
            raise ValueError("Not logged in")
        
        # 提取Cookie
        cookies = await self.context.cookies()
        logger.info(f"Session {self.user_id}-{self.platform}: Total cookies found: {len(cookies)}")
        
        # 过滤需要的Cookie
        cookie_names = self.platform_config.get("cookie_names", [])
        filtered_cookies = {}
        
        if cookie_names:
            for cookie in cookies:
                if cookie['name'] in cookie_names:
                    filtered_cookies[cookie['name']] = cookie['value']
                    logger.info(f"Session {self.user_id}-{self.platform}: Found required cookie: {cookie['name']}")
        else:
            # 如果没有指定，保存所有Cookie
            for cookie in cookies:
                filtered_cookies[cookie['name']] = cookie['value']
        
        if not filtered_cookies:
            logger.error(f"Session {self.user_id}-{self.platform}: No cookies extracted!")
            raise ValueError("No cookies extracted")
        
        logger.info(f"Session {self.user_id}-{self.platform}: Extracted {len(filtered_cookies)} cookies: {list(filtered_cookies.keys())}")
        
        # 尝试提取Token（如果有）
        tokens = {}
        try:
            # 从localStorage提取
            local_storage = await self.page.evaluate("() => Object.assign({}, window.localStorage)")
            for key, value in local_storage.items():
                if 'token' in key.lower() or 'auth' in key.lower():
                    tokens[key] = value
        except Exception as e:
            logger.warning(f"Session {self.user_id}-{self.platform}: Failed to extract tokens from localStorage: {e}")
        
        # 构建凭证
        self.credentials = {
            "cookies": filtered_cookies,
            "tokens": tokens,
            "user_agent": await self.page.evaluate("() => navigator.userAgent"),
        }
        
        logger.info(f"Session {self.user_id}-{self.platform}: Credentials extracted")
        return self.credentials
    
    async def close(self):
        """关闭会话"""
        if self.context:
            await self.context.close()
            logger.info(f"Session {self.user_id}-{self.platform}: Closed")


# 全局会话管理器
class OAuthSessionManager:
    """OAuth会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, OAuthSession] = {}
        self._lock = asyncio.Lock()
    
    def _get_session_key(self, user_id: int, platform: str) -> str:
        """获取会话键"""
        return f"{user_id}:{platform}"
    
    async def create_session(self, user_id: int, platform: str, platform_config: Dict[str, Any]) -> OAuthSession:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            platform: 平台ID
            platform_config: 平台配置
            
        Returns:
            OAuth会话对象
        """
        async with self._lock:
            session_key = self._get_session_key(user_id, platform)
            
            # 如果已存在会话，先关闭
            if session_key in self.sessions:
                await self.sessions[session_key].close()
            
            # 创建新会话
            session = OAuthSession(user_id, platform, platform_config)
            await session.start()
            
            self.sessions[session_key] = session
            logger.info(f"Session created: {session_key}")
            
            return session
    
    async def get_session(self, user_id: int, platform: str) -> Optional[OAuthSession]:
        """
        获取会话
        
        Args:
            user_id: 用户ID
            platform: 平台ID
            
        Returns:
            OAuth会话对象，如果不存在返回None
        """
        session_key = self._get_session_key(user_id, platform)
        return self.sessions.get(session_key)
    
    async def remove_session(self, user_id: int, platform: str):
        """
        移除会话
        
        Args:
            user_id: 用户ID
            platform: 平台ID
        """
        async with self._lock:
            session_key = self._get_session_key(user_id, platform)
            
            if session_key in self.sessions:
                await self.sessions[session_key].close()
                del self.sessions[session_key]
                logger.info(f"Session removed: {session_key}")


# 全局会话管理器实例
oauth_session_manager = OAuthSessionManager()