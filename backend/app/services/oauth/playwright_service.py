"""
Playwright自动化服务
用于OAuth授权流程，支持WebSocket实时推送截图和日志
"""
import os
import asyncio
import time
import base64
from typing import Optional, Dict, Any, Callable, Awaitable, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError
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

    async def _emit_progress(
        self,
        on_progress: Optional[Callable[[str, Any], Any]],
        status: str,
        payload: Any,
    ):
        if not on_progress:
            return
        result = on_progress(status, payload)
        if asyncio.iscoroutine(result):
            await result

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

    async def _trigger_doubao_image_request(self, page: Page, prompt: str = "自动捕获参数"):
        """
        触发豆包图片生成的请求，以便捕获动态参数
        """
        selectors = [
            "textarea",
            "div[contenteditable='true']",
            "[role='textbox']",
            ".input-area textarea",
            ".chat-input textarea",
        ]
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if not element:
                    continue
                await element.focus()
                tag_name = await element.evaluate("(el) => el.tagName.toLowerCase()")
                if tag_name in ("textarea", "input"):
                    await element.fill(prompt)
                else:
                    await element.evaluate(
                        "(el, text) => { el.textContent = text; el.dispatchEvent(new Event('input', { bubbles: true })); }",
                        prompt,
                    )
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1200)
                # 尝试点击“发送”按钮以确保请求发出
                send_selectors = [
                    "button:has-text('发送')",
                    "button:has-text('生成')",
                    ".send-button",
                    ".submit-button",
                ]
                for send_selector in send_selectors:
                    try:
                        await page.click(send_selector)
                        await page.wait_for_timeout(600)
                        break
                    except:
                        continue
                return True
            except Exception:
                continue
        logger.warning("未找到可用于触发豆包图片请求的输入元素")
        return False
    
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
                    await self._emit_progress(on_progress, "starting", {"message": "正在启动浏览器..."})
                
                # 创建浏览器上下文
                context = await self.create_context()
                page = await context.new_page()
                
                # 设置超时
                page.set_default_timeout(self.timeout)
                
                # 发送进度：打开登录页
                if on_progress:
                    await self._emit_progress(on_progress, "navigating", {"message": "正在打开登录页面..."})
                
                # 导航到OAuth URL
                # ??????????????????
                capture_event = asyncio.Event()
                captured = {
                    "extra_params": {},
                    "extra_headers": {},
                    "referer": None,
                }

                def _maybe_capture(request):
                    try:
                        url = request.url
                        if "/samantha/chat/completion" in url:
                        try:
                            from urllib.parse import urlparse, parse_qs
                            qs = parse_qs(urlparse(url).query)
                                captured["extra_params"] = {k: v[0] if isinstance(v, list) and v else "" for k, v in qs.items()}
                            except Exception:
                                pass
                            try:
                                headers = request.headers
                                extra_headers = {}
                                for key in ["x-flow-trace", "agw-js-conv", "referer"]:
                                    if key in headers:
                                        extra_headers[key] = headers.get(key)
                                captured["extra_headers"] = extra_headers
                                captured["referer"] = headers.get("referer")
                            except Exception:
                                pass
                            capture_event.set()
                            if hasattr(request, "post_data") and request.post_data:
                                captured["body"] = request.post_data
                            elif hasattr(request, "post_data_buffer") and request.post_data_buffer:
                                captured["body"] = request.post_data_buffer.decode("utf-8", errors="ignore")
                    except Exception:
                        pass

                page.on("request", _maybe_capture)

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
                    await self._emit_progress(on_progress, "waiting_login", {
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
                    await self._emit_progress(on_progress, "extracting", {"message": "正在提取凭证..."})
                # ??????????????
                if platform_config.get("platform_id") == "doubao":
                    if on_progress:
                        await self._emit_progress(on_progress, "waiting_capture", {
                            "message": "请在浏览器中打开豆包聊天并触发一次图片生成请求，以便自动抓取参数",
                        })
                    try:
                        await page.goto("https://www.doubao.com/chat/", timeout=30000)
                        await page.wait_for_timeout(1000)
                    except Exception:
                        pass
                    try:
                        triggered = await self._trigger_doubao_image_request(page)
                        if triggered:
                            logger.info("豆包图片请求已自动触发")
                    except Exception as e:
                        logger.warning(f"自动触发豆包图片请求失败: {e}")

                    capture_timeout = platform_config.get("capture_timeout", 120)
                    capture_interval = platform_config.get("capture_interval", 5)
                    start_wait = time.monotonic()
                    while not capture_event.is_set():
                        elapsed = time.monotonic() - start_wait
                        remaining = capture_timeout - elapsed
                        if remaining <= 0:
                            break
                        wait_time = min(remaining, capture_interval)
                        try:
                            await asyncio.wait_for(capture_event.wait(), timeout=wait_time)
                        except asyncio.TimeoutError:
                            logger.info("Still waiting for doubao request capture; user may need to trigger generation in the browser")

                    if capture_event.is_set():
                        logger.info("Captured doubao request params/headers")
                    else:
                        logger.error("No doubao request captured within timeout")
                        raise ValueError("未在规定时间内捕获豆包请求参数，请在浏览器中手动触发一次图片生成后重试")


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
                    logger.debug(f"Available cookies: {[cookie.get('name') for cookie in cookies]}")

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

                if not filtered_cookies and cookies:
                    logger.warning("没有匹配的必须Cookie，尝试保留全部Cookie作为回退")
                    filtered_cookies = {
                        cookie['name']: cookie['value']
                        for cookie in cookies
                        if 'name' in cookie and 'value' in cookie
                    }

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
                    "extra_params": captured.get("extra_params") or {},
                    "extra_headers": captured.get("extra_headers") or {},
                    "referer": captured.get("referer") or page.url,
                    "cookie_string": '; '.join([f"{k}={v}" for k, v in filtered_cookies.items()]),
                    "captured_body": captured.get("body"),
                }                
                # 发送进度：完成
                if on_progress:
                    await self._emit_progress(on_progress, "completed", {
                        "message": "授权成功！",
                        "credentials": credentials
                    })
                
                return credentials
                
            except asyncio.TimeoutError:
                logger.error("Authorization timeout")
                if on_progress:
                    await self._emit_progress(on_progress, "error", {"message": "授权超时，请重试"})
                raise ValueError("Authorization timeout")

            except Exception as e:
                logger.error(f"Authorization failed: {e}")
                if on_progress:
                    await self._emit_progress(on_progress, "error", {"message": f"授权失败: {str(e)}"})
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


class PlaywrightWebSocketService:
    """WebSocket实时服务"""
    
    _instances: Dict[str, 'PlaywrightWebSocketService'] = {}
    
    def __init__(self, user_id: int, platform: str):
        self.user_id = user_id
        self.platform = platform
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self._screenshot_task: Optional[asyncio.Task] = None
        self._screenshot_callback: Optional[Callable] = None
        self._streaming = False
        self._logs: List[Dict[str, Any]] = []
        self._last_screenshot: Optional[str] = None
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
        self.timeout = int(os.getenv("PLAYWRIGHT_TIMEOUT", "300000"))
    
    @classmethod
    def get_instance(cls, user_id: int, platform: str) -> 'PlaywrightWebSocketService':
        key = f"{user_id}:{platform}"
        if key not in cls._instances:
            cls._instances[key] = cls(user_id, platform)
        return cls._instances[key]
    
    @classmethod
    def remove_instance(cls, user_id: int, platform: str):
        key = f"{user_id}:{platform}"
        if key in cls._instances:
            instance = cls._instances[key]
            asyncio.create_task(instance.cleanup())
            del cls._instances[key]
    
    def _add_log(self, level: str, message: str, data: Optional[Dict] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        self._logs.append(log_entry)
        if len(self._logs) > 1000:
            self._logs = self._logs[-500:]
    
    async def start(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self._add_log("info", "Playwright引擎已启动")
    
    async def cleanup(self):
        self._streaming = False
        if self._screenshot_task:
            self._screenshot_task.cancel()
            try:
                await self._screenshot_task
            except asyncio.CancelledError:
                pass
        
        if self._page:
            try:
                await self._page.close()
            except:
                pass
            self._page = None
        
        if self._context:
            try:
                await self._context.close()
            except:
                pass
            self._context = None
        
        if self._browser:
            try:
                await self._browser.close()
            except:
                pass
            self._browser = None
        
        if self._playwright:
            try:
                await self._playwright.stop()
            except:
                pass
            self._playwright = None
        
        self._add_log("info", "Playwright资源已清理")
    
    async def ensure_browser(self):
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
            self._add_log("info", f"浏览器已启动 (headless={self.headless})")
    
    async def create_page(self) -> Page:
        await self.ensure_browser()
        
        if not self._context:
            self._context = await self._browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )
            self._add_log("info", "浏览器上下文已创建")
        
        if not self._page:
            self._page = await self._context.new_page()
            self._page.set_default_timeout(self.timeout)
            self._add_log("info", "新页面已创建")
        
        return self._page
    
    async def navigate_to(self, url: str) -> bool:
        page = await self.create_page()
        try:
            await page.goto(url, wait_until="networkidle")
            self._add_log("info", f"已导航到: {url}", {"current_url": page.url})
            return True
        except Exception as e:
            self._add_log("error", f"导航失败: {str(e)}")
            return False
    
    async def capture_screenshot(self) -> Optional[str]:
        if not self._page:
            return None
        
        try:
            await self._page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
        
        try:
            screenshot_bytes = await self._page.screenshot(type="png", full_page=False)
            image_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            self._last_screenshot = image_base64
            self._add_log("debug", f"截图已捕获 ({len(screenshot_bytes)} bytes)")
            return image_base64
        except Exception as e:
            self._add_log("error", f"截图失败: {str(e)}")
            return None
    
    async def click_element(self, selector: str) -> bool:
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(selector, timeout=5000)
            await self._page.click(selector)
            self._add_log("info", f"已点击元素: {selector}")
            return True
        except Exception as e:
            self._add_log("error", f"点击失败 ({selector}): {str(e)}")
            return False
    
    async def input_text(self, selector: str, text: str) -> bool:
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(selector, timeout=5000)
            await self._page.fill(selector, text)
            self._add_log("info", f"已输入文本到 {selector}: {text[:50]}...")
            return True
        except Exception as e:
            self._add_log("error", f"输入失败 ({selector}): {str(e)}")
            return False
    
    async def execute_script(self, script: str) -> Any:
        if not self._page:
            return None
        
        try:
            result = await self._page.evaluate(script)
            self._add_log("debug", f"脚本执行完成", {"result_type": type(result).__name__})
            return result
        except Exception as e:
            self._add_log("error", f"脚本执行失败: {str(e)}")
            return None
    
    async def get_current_url(self) -> str:
        if self._page:
            return self._page.url
        return ""
    
    async def get_logs(self) -> List[Dict[str, Any]]:
        return self._logs[-100:]
    
    async def start_screenshot_stream(
        self,
        callback: Callable[[str], Awaitable[None]],
        interval_ms: int = 2000
    ):
        if self._streaming:
            await self.stop_screenshot_stream()
        
        self._screenshot_callback = callback
        self._streaming = True
        
        async def screenshot_loop():
            while self._streaming:
                try:
                    image_data = await self.capture_screenshot()
                    if image_data and self._screenshot_callback:
                        await self._screenshot_callback(image_data)
                except Exception as e:
                    self._add_log("error", f"截图流错误: {str(e)}")
                
                await asyncio.sleep(interval_ms / 1000)
        
        self._screenshot_task = asyncio.create_task(screenshot_loop())
        self._add_log("info", f"截图流已开始 (间隔: {interval_ms}ms)")
    
    async def stop_screenshot_stream(self):
        if not self._streaming:
            return
        
        self._streaming = False
        
        if self._screenshot_task:
            self._screenshot_task.cancel()
            try:
                await self._screenshot_task
            except asyncio.CancelledError:
                pass
            self._screenshot_task = None
        
        self._screenshot_callback = None
        self._add_log("info", "截图流已停止")
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            self._add_log("info", f"元素已出现: {selector}")
            return True
        except PlaywrightTimeoutError:
            self._add_log("warning", f"等待元素超时: {selector}")
            return False
        except Exception as e:
            self._add_log("error", f"等待元素失败: {str(e)}")
            return False


playwright_ws_service = PlaywrightWebSocketService


async def get_page_for_websocket(user_id: int, platform: str, url: str = "") -> Page:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    await service.start()
    
    if url:
        await service.navigate_to(url)
    
    return await service.create_page()


async def release_websocket_service(user_id: int, platform: str):
    PlaywrightWebSocketService.remove_instance(user_id, platform)


async def capture_screenshot(platform: str, user_id: int = 1) -> Optional[str]:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    await service.create_page()
    return await service.capture_screenshot()


async def navigate_to(platform: str, url: str, user_id: int = 1) -> bool:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    return await service.navigate_to(url)


async def click_element(platform: str, selector: str, user_id: int = 1) -> bool:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    return await service.click_element(selector)


async def input_text(platform: str, selector: str, text: str, user_id: int = 1) -> bool:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    return await service.input_text(selector, text)


async def execute_script(platform: str, script: str, user_id: int = 1) -> Any:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    return await service.execute_script(script)


async def get_current_url(platform: str, user_id: int = 1) -> str:
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    return await service.get_current_url()


async def start_screenshot_stream(
    platform: str,
    callback: Callable[[str], Awaitable[None]],
    interval_ms: int = 2000,
    user_id: int = 1
):
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    await service.start_screenshot_stream(callback, interval_ms)


async def stop_screenshot_stream(platform: str, user_id: int = 1):
    service = PlaywrightWebSocketService.get_instance(user_id, platform)
    await service.stop_screenshot_stream()


async def generate_image_with_playwright(
    platform_meta: Dict[str, Any],
    prompt: str,
    cookies: Dict[str, str],
    size: str = "1024x1024"
) -> Dict[str, Any]:
    """
    使用Playwright生成图片（模拟真实用户在浏览器中操作）
    
    Args:
        platform_meta: 平台元数据
        prompt: 图片描述
        cookies: Cookie字典
        size: 图片尺寸
    
    Returns:
        生成的图片URL列表
    """
    from loguru import logger
    import asyncio
    
    result = {
        "images": [],
        "prompt": prompt,
        "size": size,
        "method": "playwright"
    }
    
    platform_id = platform_meta.get("platform_id", "doubao")
    
    async with playwright_service._semaphore:
        context = None
        page = None
        
        try:
            context = await playwright_service.create_context()
            
            if cookies:
                cookie_list = [
                    {"name": k, "value": v, "domain": ".doubao.com"}
                    for k, v in cookies.items()
                ]
                await context.add_cookies(cookie_list)
                logger.info(f"Added {len(cookies)} cookies for {platform_id}")
            
            page = await context.new_page()
            page.set_default_timeout(60000)
            
            await page.goto("https://www.doubao.com/chat/")
            logger.info(f"Navigated to https://www.doubao.com/chat/")
            
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            input_selectors = [
                "textarea[placeholder*='输入']",
                "div[contenteditable='true']",
                ".chat-input textarea",
                "textarea.chat-input",
                "[class*='input'] textarea"
            ]
            
            input_box = None
            for selector in input_selectors:
                try:
                    input_box = await page.query_selector(selector)
                    if input_box:
                        logger.info(f"Found input box with selector: {selector}")
                        break
                except:
                    continue
            
            if not input_box:
                logger.error("Could not find input box")
                result["error"] = "无法找到输入框"
                return result
            
            await input_box.fill("")
            await input_box.type(prompt)
            logger.info(f"Entered prompt: {prompt}")
            
            send_selectors = [
                "button[type='submit']",
                "button:has-text('发送')",
                "[class*='send'] button",
                ".chat-send-button",
                "button:has-text('生成')"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = await page.query_selector(selector)
                    if send_button:
                        logger.info(f"Found send button with selector: {selector}")
                        break
                except:
                    continue
            
            if send_button:
                await send_button.click()
                logger.info("Clicked send button")
            else:
                await input_box.press("Enter")
                logger.info("Pressed Enter key")
            
            await asyncio.sleep(5)
            
            image_selectors = [
                "img[src*='byteimg']",
                "[class*='image'] img",
                ".creations img",
                "img[src*='tos-cn']"
            ]
            
            image_urls = []
            for selector in image_selectors:
                try:
                    images = await page.query_selector_all(selector)
                    for img in images:
                        src = await img.get_attribute("src")
                        if src and src not in image_urls:
                            clean_url = src.split("?")[0]
                            if clean_url not in image_urls:
                                image_urls.append(clean_url)
                                logger.info(f"Found image: {clean_url[:80]}...")
                except:
                    continue
            
            if image_urls:
                result["images"] = image_urls
                logger.info(f"Found {len(image_urls)} images")
            else:
                screenshot = await page.screenshot(type="png")
                import base64
                result["screenshot"] = base64.b64encode(screenshot).decode()
                result["error"] = "未找到生成的图片"
                logger.warning("No images found")
            
            return result
            
        except Exception as e:
            logger.error(f"Playwright image generation failed: {e}")
            result["error"] = str(e)
            return result
            
        finally:
            if context:
                try:
                    await context.close()
                    logger.info("Browser context closed")
                except:
                    pass
