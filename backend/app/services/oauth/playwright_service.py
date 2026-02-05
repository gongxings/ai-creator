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
        # 默认使用非 headless 模式，让用户能看到浏览器登录
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
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
    
    async def _click_login_button(self, page: Page):
        """
        点击登录按钮，显示登录界面
        
        Args:
            page: 页面对象
        """
        try:
            # 等待页面加载
            await page.wait_for_load_state("networkidle", timeout=5000)
            
            # 豆包登录按钮的选择器
            login_selectors = [
                "button:has-text('登录')",
                "a:has-text('登录')",
                ".login-btn",
                "[class*='login']",
            ]
            
            for selector in login_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    await page.click(selector)
                    logger.info(f"Clicked login button with selector: {selector}")
                    await page.wait_for_timeout(2000)
                    return
                except:
                    continue
            
            logger.info("No login button found, login form might already be visible")
        except Exception as e:
            logger.warning(f"Failed to click login button: {e}")
    
    async def _check_login_status(self, page: Page) -> bool:
        """
        检查是否登录成功

        Args:
            page: 页面对象

        Returns:
            是否登录成功
        """
        try:
            # 检查 page 是否已关闭
            if not page or page.is_closed():
                raise Exception("Page is closed")

            # 检查 localStorage 中是否有用户信息或登录相关数据
            try:
                local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
                logger.info(f"localStorage keys: {list(local_storage.keys())}")

                # 检查常见的登录相关键
                login_keys = ['user_info', 'token', 'auth', 'session', 'user', 'userId', 'userInfo']
                for key in login_keys:
                    if key in local_storage and local_storage[key]:
                        logger.info(f"Found login indicator in localStorage: {key}")
                        return True
            except Exception as e:
                logger.warning(f"Failed to check localStorage: {e}")

            # 检查是否有登录后的用户元素
            user_selectors = [
                ".user-avatar",
                ".user-info",
                "[data-testid='user-avatar']",
                "img[alt*='头像']",
                "[class*='avatar']",
                "[class*='user']",
            ]

            for selector in user_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.info(f"Found login indicator: {selector}")
                        return True
                except:
                    continue

            # 检查 URL 是否包含用户相关路径
            current_url = page.url
            if "user" in current_url or "console" in current_url or "home" in current_url:
                logger.info(f"URL indicates login: {current_url}")
                return True

            return False
        except Exception as e:
            # 如果是页面/上下文关闭的异常，重新抛出让外层捕获
            error_str = str(e)
            if any(keyword in error_str for keyword in ["closed", "Target page", "Target context", "Target browser"]):
                logger.info(f"Browser context closed detected: {e}")
                raise
            logger.warning(f"Failed to check login status: {e}")
            return False
    
    async def _auto_login(
        self,
        page: Page,
        username: str,
        password: str,
        on_progress: Optional[Callable[[str, Any], None]] = None
    ):
        """
        自动登录
        
        Args:
            page: 页面对象
            username: 用户名
            password: 密码
            on_progress: 进度回调
        """
        # 等待页面加载
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # 尝试查找登录按钮并点击
        login_selectors = [
            "button:has-text('登录')",
            "a:has-text('登录')",
            ".login-button",
            "[data-testid='login-button']",
            "#login-btn",
        ]
        
        login_clicked = False
        for selector in login_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                await page.click(selector)
                logger.info(f"Clicked login button with selector: {selector}")
                login_clicked = True
                break
            except:
                continue
        
        if login_clicked:
            # 等待登录表单出现
            await page.wait_for_timeout(2000)
            
            # 输入用户名
            username_selectors = [
                "input[type='text']",
                "input[name='username']",
                "input[name='phone']",
                "input[name='email']",
                "#username",
                "#phone",
                ".username-input",
            ]
            
            for selector in username_selectors:
                try:
                    await page.fill(selector, username)
                    logger.info(f"Filled username with selector: {selector}")
                    break
                except:
                    continue
            
            # 输入密码
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "#password",
                ".password-input",
            ]
            
            for selector in password_selectors:
                try:
                    await page.fill(selector, password)
                    logger.info(f"Filled password with selector: {selector}")
                    break
                except:
                    continue
            
            # 点击登录/提交按钮
            submit_selectors = [
                "button:has-text('登录')",
                "button:has-text('提交')",
                "button[type='submit']",
                ".submit-button",
                "#submit-btn",
            ]
            
            for selector in submit_selectors:
                try:
                    await page.click(selector)
                    logger.info(f"Clicked submit button with selector: {selector}")
                    break
                except:
                    continue
            
            # 等待登录完成
            await page.wait_for_timeout(3000)
    
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
                
                # 尝试点击登录按钮（让用户看到登录界面）
                await self._click_login_button(page)
                
                # 尝试自动登录（如果有预置账号密码）
                username = platform_config.get("username")
                password = platform_config.get("password")
                
                if username and password:
                    logger.info(f"Attempting auto-login with username: {username}")
                    try:
                        await self._auto_login(page, username, password, on_progress)
                        logger.info("Auto-login completed successfully")
                    except Exception as e:
                        logger.warning(f"Auto-login failed: {e}, will wait for manual login")
                else:
                    logger.info("No pre-configured credentials, waiting for manual login")
                
                # 发送进度：等待用户登录
                if on_progress:
                    on_progress("waiting_login", {
                        "message": "请在浏览器中完成登录...",
                        "url": oauth_url
                    })
                
                # 等待登录成功（URL变化或特定元素）
                success_pattern = platform_config.get("success_pattern", "**/console/**")
                
                # 特殊处理：对于需要等待固定时间的平台
                if success_pattern == "WAIT_FOR_LOGIN":
                    if not self.headless:
                        logger.info("=" * 60)
                        logger.info("请打开浏览器窗口，完成登录！")
                        logger.info(f"超时时间: {self.timeout / 1000} 秒")
                        logger.info("支持扫码登录或账号密码登录")
                        logger.info("=" * 60)
                    
                    # 轮询检测登录状态
                    check_interval = 2000  # 每2秒检查一次
                    max_attempts = self.timeout // check_interval
                    attempt = 0

                    logger.info(f"Polling for login status (timeout: {self.timeout}ms, interval: {check_interval}ms)...")

                    while attempt < max_attempts:
                        try:
                            if await self._check_login_status(page):
                                logger.info("Login successful! Extracting credentials...")
                                break
                        except Exception as e:
                            error_str = str(e)
                            if "closed" in error_str or "Target page" in error_str or "Target context" in error_str:
                                logger.info("Page closed detected (possibly due to refresh), waiting for new page...")
                                # 等待新页面加载
                                await asyncio.sleep(2)
                                # 获取新页面
                                pages = context.pages
                                if pages:
                                    page = pages[-1]  # 获取最新的页面
                                    logger.info(f"Got new page, URL: {page.url}")
                                    # 继续检查登录状态
                                    attempt -= 1  # 不增加 attempt，继续当前检查
                                else:
                                    logger.info("Browser context closed by user, attempting to extract cookies...")
                                    break
                            else:
                                logger.warning(f"Error checking login status: {e}")

                        attempt += 1
                        if attempt < max_attempts:
                            await asyncio.sleep(check_interval / 1000)
                    else:
                        logger.warning(f"Login timeout after {max_attempts * check_interval / 1000} seconds")
                        raise ValueError("Login timeout")
                else:
                    # 正常模式：等待URL变化到success_pattern
                    logger.info(f"Waiting for URL to match pattern: {success_pattern}")
                    await page.wait_for_url(success_pattern, timeout=self.timeout)
                    logger.info(f"URL matched pattern: {page.url}")

                # 提取Cookie（无论浏览器是否关闭）
                if on_progress:
                    on_progress("extracting", {"message": "正在提取凭证..."})

                # 检查 context 是否可用
                if context and not context.pages:
                    logger.warning("Browser context has no pages, attempting to extract cookies from closed context")

                # 提取Cookie
                cookies = []
                max_retries = 3
                for i in range(max_retries):
                    try:
                        cookies = await context.cookies()
                        logger.info(f"Total cookies found: {len(cookies)}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to extract cookies (attempt {i+1}/{max_retries}): {e}")
                        if i < max_retries - 1:
                            await asyncio.sleep(1)
                        else:
                            logger.error(f"All {max_retries} attempts to extract cookies failed")
                
                # 过滤需要的Cookie
                cookie_names = platform_config.get("cookie_names", [])
                filtered_cookies = {}
                
                if cookies:
                    if cookie_names:
                        for cookie in cookies:
                            if 'name' in cookie and 'value' in cookie and cookie['name'] in cookie_names:
                                filtered_cookies[cookie['name']] = cookie['value']
                                logger.info(f"Found required cookie: {cookie['name']}")
                    else:
                        # 如果没有指定，保存所有Cookie
                        for cookie in cookies:
                            if 'name' in cookie and 'value' in cookie:
                                filtered_cookies[cookie['name']] = cookie['value']
                
                if not filtered_cookies:
                    logger.error("No cookies extracted!")
                    raise ValueError("No cookies extracted")
                
                logger.info(f"Extracted {len(filtered_cookies)} cookies: {list(filtered_cookies.keys())}")
                
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
                
                # 获取User-Agent
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                try:
                    user_agent = await page.evaluate("() => navigator.userAgent")
                except Exception as e:
                    logger.warning(f"Failed to extract user agent: {e}")
                
                # 构建凭证
                credentials = {
                    "cookies": filtered_cookies,
                    "tokens": tokens,
                    "user_agent": user_agent,
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
                    try:
                        await context.close()
                        logger.info("Browser context closed")
                    except Exception as e:
                        logger.warning(f"Error closing browser context: {e}")
    
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
        browser = None
        try:
            # 获取浏览器（使用 headless 模式验证）
            browser = await self.get_browser()

            # 创建浏览器上下文（使用 headless 模式）
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )

            # 设置Cookie
            cookies = credentials.get("cookies", {})
            cookie_list = []
            for name, value in cookies.items():
                cookie_list.append({
                    "name": name,
                    "value": value,
                    "domain": platform_config.get("cookie_domain", ".doubao.com"),
                    "path": "/",
                })

            await context.add_cookies(cookie_list)

            # 访问验证URL
            page = await context.new_page()
            check_url = platform_config.get("check_url")
            if not check_url:
                logger.warning("No check_url in platform config, skipping validation")
                return True

            logger.info(f"Checking credentials by visiting: {check_url}")
            await page.goto(check_url, timeout=30000)

            # 检查是否需要重新登录
            current_url = page.url
            logger.info(f"Current URL after check: {current_url}")

            if "login" in current_url.lower():
                logger.info("Credentials expired, login required")
                return False

            # 检查页面内容，看是否有错误提示
            try:
                page_content = await page.content()
                if "登录" in page_content and "请先登录" in page_content:
                    logger.info("Page shows login required message")
                    return False
            except Exception as e:
                logger.warning(f"Failed to check page content: {e}")

            logger.info("Credentials are valid")
            return True

        except Exception as e:
            logger.error(f"Failed to check credentials: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if context:
                await context.close()


# 全局Playwright服务实例
playwright_service = PlaywrightService()
