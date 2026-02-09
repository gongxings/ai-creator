"""
远程浏览器控制服务
支持实时截图流 + 远程鼠标/键盘操作
"""
import asyncio
import base64
import json
from typing import Dict, Any, Optional, Callable, Set
from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page
from dataclasses import dataclass, field
from enum import Enum

from app.services.oauth.playwright_service import playwright_service


class SessionStatus(str, Enum):
    """会话状态"""
    STARTING = "starting"
    NAVIGATING = "navigating"
    WAITING_LOGIN = "waiting_login"
    LOGGED_IN = "logged_in"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class RemoteBrowserSession:
    """远程浏览器会话"""
    session_id: str
    user_id: int
    platform: str
    platform_config: Dict[str, Any]
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None
    status: SessionStatus = SessionStatus.STARTING
    error_message: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    # 截图相关
    screenshot_interval: float = 0.5  # 截图间隔（秒）
    screenshot_quality: int = 60  # JPEG 质量
    viewport_width: int = 1280
    viewport_height: int = 720
    # 回调
    on_screenshot: Optional[Callable[[str], Any]] = None
    on_status_change: Optional[Callable[[SessionStatus, Dict[str, Any]], Any]] = None
    # 控制
    _screenshot_task: Optional[asyncio.Task] = None
    _login_check_task: Optional[asyncio.Task] = None
    _running: bool = False


class RemoteBrowserService:
    """远程浏览器控制服务"""
    
    def __init__(self):
        self.sessions: Dict[str, RemoteBrowserSession] = {}
        self._lock = asyncio.Lock()
    
    async def create_session(
        self,
        user_id: int,
        platform: str,
        platform_config: Dict[str, Any],
        on_screenshot: Optional[Callable[[str], Any]] = None,
        on_status_change: Optional[Callable[[SessionStatus, Dict[str, Any]], Any]] = None,
    ) -> RemoteBrowserSession:
        """
        创建远程浏览器会话
        
        Args:
            user_id: 用户ID
            platform: 平台ID
            platform_config: 平台配置
            on_screenshot: 截图回调
            on_status_change: 状态变化回调
            
        Returns:
            远程浏览器会话
        """
        session_id = f"{user_id}:{platform}"
        
        async with self._lock:
            # 如果已存在会话，先关闭
            if session_id in self.sessions:
                await self._close_session_internal(session_id)
            
            session = RemoteBrowserSession(
                session_id=session_id,
                user_id=user_id,
                platform=platform,
                platform_config=platform_config,
                on_screenshot=on_screenshot,
                on_status_change=on_status_change,
            )
            
            self.sessions[session_id] = session
            logger.info(f"RemoteBrowser session created: {session_id}")
        
        # 启动浏览器会话
        try:
            await self._start_session(session)
        except Exception as e:
            session.status = SessionStatus.ERROR
            session.error_message = str(e)
            if session.on_status_change:
                await self._call_async(session.on_status_change, session.status, {"error": str(e)})
            raise
        
        return session
    
    async def _start_session(self, session: RemoteBrowserSession):
        """启动浏览器会话"""
        # 更新状态
        session.status = SessionStatus.STARTING
        if session.on_status_change:
            await self._call_async(session.on_status_change, session.status, {"message": "正在启动浏览器..."})
        
        # 创建浏览器上下文（使用 headless 模式，因为我们通过截图显示）
        session.context = await playwright_service.create_context(
            viewport={"width": session.viewport_width, "height": session.viewport_height}
        )
        session.page = await session.context.new_page()
        
        # 更新状态 - 导航
        session.status = SessionStatus.NAVIGATING
        if session.on_status_change:
            await self._call_async(session.on_status_change, session.status, {"message": "正在打开登录页面..."})
        
        # 导航到 OAuth URL
        oauth_url = session.platform_config.get("oauth_url")
        if not oauth_url:
            raise ValueError("oauth_url not found in platform config")
        
        await session.page.goto(oauth_url)
        logger.info(f"Session {session.session_id}: Navigated to {oauth_url}")
        
        # 尝试点击登录按钮
        await playwright_service._click_login_button(session.page)
        
        # 更新状态 - 等待登录
        session.status = SessionStatus.WAITING_LOGIN
        if session.on_status_change:
            await self._call_async(session.on_status_change, session.status, {"message": "请在页面中完成登录..."})
        
        # 启动截图任务
        session._running = True
        session._screenshot_task = asyncio.create_task(self._screenshot_loop(session))
        
        # 启动登录检查任务
        session._login_check_task = asyncio.create_task(self._login_check_loop(session))
    
    async def _screenshot_loop(self, session: RemoteBrowserSession):
        """截图循环"""
        while session._running and session.page and not session.page.is_closed():
            try:
                # 截图
                screenshot_bytes = await session.page.screenshot(
                    type="jpeg",
                    quality=session.screenshot_quality,
                    full_page=False,
                )
                
                # 转换为 base64
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                
                # 发送截图
                if session.on_screenshot:
                    await self._call_async(session.on_screenshot, screenshot_base64)
                
            except Exception as e:
                if "closed" not in str(e).lower():
                    logger.warning(f"Session {session.session_id}: Screenshot error: {e}")
            
            await asyncio.sleep(session.screenshot_interval)
    
    async def _login_check_loop(self, session: RemoteBrowserSession):
        """登录状态检查循环"""
        check_interval = 2.0  # 每2秒检查一次
        
        while session._running and session.status == SessionStatus.WAITING_LOGIN:
            try:
                if session.page and not session.page.is_closed():
                    is_logged_in = await playwright_service._check_login_status(session.page)
                    
                    if is_logged_in:
                        logger.info(f"Session {session.session_id}: Login detected!")
                        await self._handle_login_success(session)
                        break
            except Exception as e:
                if "closed" not in str(e).lower():
                    logger.warning(f"Session {session.session_id}: Login check error: {e}")
            
            await asyncio.sleep(check_interval)
    
    async def _handle_login_success(self, session: RemoteBrowserSession):
        """处理登录成功"""
        session.status = SessionStatus.LOGGED_IN
        if session.on_status_change:
            await self._call_async(session.on_status_change, session.status, {"message": "登录成功！正在提取凭证..."})
        
        # 等待一下让页面完全加载
        await asyncio.sleep(2)
        
        # 提取凭证
        session.status = SessionStatus.EXTRACTING
        if session.on_status_change:
            await self._call_async(session.on_status_change, session.status, {"message": "正在提取Cookie..."})
        
        try:
            credentials = await self._extract_credentials(session)
            session.credentials = credentials
            session.status = SessionStatus.COMPLETED
            
            if session.on_status_change:
                await self._call_async(session.on_status_change, session.status, {
                    "message": "授权完成！",
                    "credentials": credentials,
                })
            
            logger.info(f"Session {session.session_id}: Credentials extracted, {len(credentials.get('cookies', {}))} cookies")
            
            # 延迟2秒后自动关闭浏览器（给用户时间看到成功消息）
            await asyncio.sleep(2)
            logger.info(f"Session {session.session_id}: Auto-closing browser after successful extraction")
            # 关闭浏览器上下文
            if session.context:
                try:
                    await session.context.close()
                    logger.info(f"Session {session.session_id}: Browser context closed")
                except Exception as e:
                    logger.warning(f"Session {session.session_id}: Error closing context: {e}")
            
        except Exception as e:
            session.status = SessionStatus.ERROR
            session.error_message = str(e)
            if session.on_status_change:
                await self._call_async(session.on_status_change, session.status, {"error": str(e)})
            logger.error(f"Session {session.session_id}: Failed to extract credentials: {e}")
    
    async def _extract_credentials(self, session: RemoteBrowserSession) -> Dict[str, Any]:
        """提取凭证"""
        if not session.context:
            raise ValueError("No browser context")
        
        # 提取 Cookie
        cookies = await session.context.cookies()
        logger.info(f"Session {session.session_id}: Total cookies found: {len(cookies)}")
        
        # 过滤需要的 Cookie
        cookie_names = session.platform_config.get("cookie_names", [])
        filtered_cookies = {}
        
        if cookie_names:
            for cookie in cookies:
                if cookie.get("name") in cookie_names:
                    filtered_cookies[cookie["name"]] = cookie["value"]
                    logger.info(f"Session {session.session_id}: Found required cookie: {cookie['name']}")
        else:
            # 如果没有指定，保存所有 Cookie
            for cookie in cookies:
                if cookie.get("name") and cookie.get("value"):
                    filtered_cookies[cookie["name"]] = cookie["value"]
        
        if not filtered_cookies:
            raise ValueError("No cookies extracted")
        
        # 尝试提取 Token（如果有）
        tokens = {}
        try:
            if session.page and not session.page.is_closed():
                local_storage = await session.page.evaluate("() => Object.assign({}, window.localStorage)")
                for key, value in local_storage.items():
                    if "token" in key.lower() or "auth" in key.lower():
                        tokens[key] = value
        except Exception as e:
            logger.warning(f"Session {session.session_id}: Failed to extract tokens: {e}")
        
        # 获取 User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        try:
            if session.page and not session.page.is_closed():
                user_agent = await session.page.evaluate("() => navigator.userAgent")
        except:
            pass
        
        return {
            "cookies": filtered_cookies,
            "tokens": tokens,
            "user_agent": user_agent,
        }
    
    async def handle_mouse_event(
        self,
        session_id: str,
        event_type: str,
        x: float,
        y: float,
        button: str = "left",
    ):
        """
        处理鼠标事件
        
        Args:
            session_id: 会话ID
            event_type: 事件类型 (click, dblclick, move, down, up)
            x: X坐标（相对于视口的百分比 0-1）
            y: Y坐标（相对于视口的百分比 0-1）
            button: 鼠标按钮 (left, right, middle)
        """
        session = self.sessions.get(session_id)
        if not session or not session.page or session.page.is_closed():
            logger.warning(f"Session {session_id}: Cannot handle mouse event, page not available")
            return
        
        # 转换坐标（从百分比转换为实际像素）
        actual_x = x * session.viewport_width
        actual_y = y * session.viewport_height
        
        try:
            if event_type == "click":
                await session.page.mouse.click(actual_x, actual_y, button=button)
                logger.debug(f"Session {session_id}: Click at ({actual_x}, {actual_y})")
            elif event_type == "dblclick":
                await session.page.mouse.dblclick(actual_x, actual_y, button=button)
                logger.debug(f"Session {session_id}: Double click at ({actual_x}, {actual_y})")
            elif event_type == "move":
                await session.page.mouse.move(actual_x, actual_y)
            elif event_type == "down":
                await session.page.mouse.down(button=button)
            elif event_type == "up":
                await session.page.mouse.up(button=button)
        except Exception as e:
            logger.warning(f"Session {session_id}: Mouse event error: {e}")
    
    async def handle_keyboard_event(
        self,
        session_id: str,
        event_type: str,
        key: str,
        text: Optional[str] = None,
    ):
        """
        处理键盘事件
        
        Args:
            session_id: 会话ID
            event_type: 事件类型 (type, press, down, up)
            key: 按键
            text: 输入文本（用于 type 事件）
        """
        session = self.sessions.get(session_id)
        if not session or not session.page or session.page.is_closed():
            logger.warning(f"Session {session_id}: Cannot handle keyboard event, page not available")
            return
        
        try:
            if event_type == "type" and text:
                await session.page.keyboard.type(text)
                logger.debug(f"Session {session_id}: Typed text")
            elif event_type == "press":
                await session.page.keyboard.press(key)
                logger.debug(f"Session {session_id}: Pressed {key}")
            elif event_type == "down":
                await session.page.keyboard.down(key)
            elif event_type == "up":
                await session.page.keyboard.up(key)
        except Exception as e:
            logger.warning(f"Session {session_id}: Keyboard event error: {e}")
    
    async def handle_scroll_event(
        self,
        session_id: str,
        delta_x: float,
        delta_y: float,
    ):
        """
        处理滚动事件
        
        Args:
            session_id: 会话ID
            delta_x: X方向滚动量
            delta_y: Y方向滚动量
        """
        session = self.sessions.get(session_id)
        if not session or not session.page or session.page.is_closed():
            return
        
        try:
            await session.page.mouse.wheel(delta_x, delta_y)
        except Exception as e:
            logger.warning(f"Session {session_id}: Scroll event error: {e}")
    
    async def get_session(self, session_id: str) -> Optional[RemoteBrowserSession]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        async with self._lock:
            await self._close_session_internal(session_id)
    
    async def _close_session_internal(self, session_id: str):
        """内部关闭会话方法"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        session._running = False
        session.status = SessionStatus.CLOSED
        
        # 取消任务
        if session._screenshot_task:
            session._screenshot_task.cancel()
            try:
                await session._screenshot_task
            except asyncio.CancelledError:
                pass
        
        if session._login_check_task:
            session._login_check_task.cancel()
            try:
                await session._login_check_task
            except asyncio.CancelledError:
                pass
        
        # 关闭浏览器上下文
        if session.context:
            try:
                await session.context.close()
            except Exception as e:
                logger.warning(f"Session {session_id}: Error closing context: {e}")
        
        del self.sessions[session_id]
        logger.info(f"Session {session_id}: Closed")
    
    async def _call_async(self, func: Callable, *args):
        """调用回调函数（支持同步和异步）"""
        if asyncio.iscoroutinefunction(func):
            await func(*args)
        else:
            func(*args)


# 全局服务实例
remote_browser_service = RemoteBrowserService()
