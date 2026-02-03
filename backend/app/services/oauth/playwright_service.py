"""
Playwright自动化服务
用于OAuth授权流程
"""
import os
import asyncio
from typing import Optional, Dict, Any, Callable
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger


class PlaywrightService:
    """Playwright自动化服务"""
    
    def __init__(self):
        """初始化服务"""
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        self.timeout = int(os.getenv("PLAYWRIGHT_TIMEOUT", "300000"))  # 5分钟
        self.max_concurrent = int(os.getenv("PLAYWRIGHT_MAX_CONCURRENT", "3"))
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    async def start(self):
        """启动Playwright"""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            logger.info("Playwright started")
    
    async def stop(self):
        """停止Playwright"""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            logger.info("Playwright stopped")
    
    async def get_browser(self) -> Browser:
        """获取浏览器实例"""
        if not self._playwright:
            await self.start()
        
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            logger.info(f"Browser launched (headless={self.headless})")
        
        return self._browser
    
    async def create_context(self, **kwargs) -> BrowserContext:
        """
        创建浏览器上下文
        
        Args:
            **kwargs: 传递给new_context的参数
            
        Returns:
            BrowserContext实例
        """
        browser = await self.get_browser()
        
        # 默认配置
        default_config = {
            'viewport': {'width': 1280, 'height': 720},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }
        
        # 合并配置
        config = {**default_config, **kwargs}
        
        context = await browser.new_context(**config)
        logger.info("Browser context created")
        
        return context
    
    async def authorize_platform(
        self,
        platform_config: Dict[str, Any],
        on_progress: Optional[Callable[[str, Any], None]] = None
    ) -> Dict[str, Any]:
        """
        执行平台OAuth授权
        
        Args:
            platform_config: 平台配置
            on_progress: 进度回调函数
            
        Returns:
            包含凭证的字典
        """
        async with self._semaphore:
            context = None
            try:
                # 发送进度：开始授权
                if on_progress:
                    on_progress("starting", {"message": "正在启动浏览器..."})
                
                # 创建浏览器上下文
                context = await self.create_context()
                page = await context.new_page()
                
                # 设置超时
                page.set_default_timeout(self.timeout)
                
                # 发送进度：打开登录页
                if on_progress:
                    on_progress("navigating", {"message": "正在打开登录页面..."})
                
                # 导航到OAuth URL
                oauth_url = platform_config.get("oauth_url")
                if not oauth_url:
                    raise ValueError("oauth_url not found in platform config")
                
                await page.goto(oauth_url)
                logger.info(f"Navigated to {oauth_url}")
                
                # 发送进度：等待用户登录
                if on_progress:
                    on_progress("waiting_login", {
                        "message": "请在浏览器中完成登录...",
                        "url": oauth_url
                    })
                
                # 等待登录成功（URL变化）
                success_pattern = platform_config.get("success_pattern", "**/console/**")
                await page.wait_for_url(success_pattern, timeout=self.timeout)
                logger.info("Login successful, URL changed")
                
                # 发送进度：提取凭证
                if on_progress:
                    on_progress("extracting", {"message": "正在提取凭证..."})
                
                # 提取Cookie
                cookies = await context.cookies()
                
                # 过滤需要的Cookie
                cookie_names = platform_config.get("cookie_names", [])
                filtered_cookies = {}
                
                if cookie_names:
                    for cookie in cookies:
                        if cookie['name'] in cookie_names:
                            filtered_cookies[cookie['name']] = cookie['value']
                else:
                    # 如果没有指定，保存所有Cookie
                    for cookie in cookies:
                        filtered_cookies[cookie['name']] = cookie['value']
                
                if not filtered_cookies:
                    raise ValueError("No cookies extracted")
                
                logger.info(f"Extracted {len(filtered_cookies)} cookies")
                
                # 尝试提取Token（如果有）
                tokens = {}
                try:
                    # 从localStorage提取
                    local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
                    for key, value in local_storage.items():
                        if 'token' in key.lower() or 'auth' in key.lower():
                            tokens[key] = value
                except Exception as e:
                    logger.warning(f"Failed to extract tokens from localStorage: {e}")
                
                # 构建凭证
                credentials = {
                    "cookies": filtered_cookies,
                    "tokens": tokens,
                    "user_agent": page.context.user_agent,
                }
                
                # 发送进度：完成
                if on_progress:
                    on_progress("completed", {
                        "message": "授权成功！",
                        "credentials": credentials
                    })
                
                return credentials
                
            except asyncio.TimeoutError:
                logger.error("Authorization timeout")
                if on_progress:
                    on_progress("error", {"message": "授权超时，请重试"})
                raise ValueError("Authorization timeout")
                
            except Exception as e:
                logger.error(f"Authorization failed: {e}")
                if on_progress:
                    on_progress("error", {"message": f"授权失败: {str(e)}"})
                raise
                
            finally:
                # 清理
                if context:
                    await context.close()
                    logger.info("Browser context closed")
    
    async def check_credentials_validity(
        self,
        platform_config: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> bool:
        """
        检查凭证是否有效
        
        Args:
            platform_config: 平台配置
            credentials: 凭证信息
            
        Returns:
            是否有效
        """
        context = None
        try:
            # 创建浏览器上下文
            context = await self.create_context()
            
            # 设置Cookie
            cookies = credentials.get("cookies", {})
            cookie_list = []
            for name, value in cookies.items():
                cookie_list.append({
                    "name": name,
                    "value": value,
                    "domain": platform_config.get("cookie_domain", ".aliyun.com"),
                    "path": "/",
                })
            
            await context.add_cookies(cookie_list)
            
            # 访问验证URL
            page = await context.new_page()
            check_url = platform_config.get("check_url")
            if not check_url:
                logger.warning("No check_url in platform config, skipping validation")
                return True
            
            await page.goto(check_url, timeout=30000)
            
            # 检查是否需要重新登录
            current_url = page.url
            if "login" in current_url.lower():
                logger.info("Credentials expired, login required")
                return False
            
            logger.info("Credentials are valid")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check credentials: {e}")
            return False
            
        finally:
            if context:
                await context.close()


# 全局Playwright服务实例
playwright_service = PlaywrightService()
