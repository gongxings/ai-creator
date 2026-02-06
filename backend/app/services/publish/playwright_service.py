"""
Publish platform Playwright automation for cookie capture.
"""
import os
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger


class PublishPlaywrightService:
    def __init__(self) -> None:
        self.headless = os.getenv("PUBLISH_PLAYWRIGHT_HEADLESS", "false").lower() == "true"
        self.timeout = int(os.getenv("PUBLISH_PLAYWRIGHT_TIMEOUT", "300000"))
        self.max_concurrent = int(os.getenv("PUBLISH_PLAYWRIGHT_MAX_CONCURRENT", "2"))
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._browser: Optional[Browser] = None
        self._playwright = None

    async def start(self) -> None:
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            logger.info("Publish Playwright started")

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            logger.info("Publish Playwright stopped")

    async def get_browser(self) -> Browser:
        if not self._playwright:
            await self.start()

        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            logger.info(f"Publish browser launched (headless={self.headless})")
        return self._browser

    async def create_context(self) -> BrowserContext:
        browser = await self.get_browser()
        return await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

    async def authorize_platform(
        self,
        login_url: str,
        success_pattern: Optional[str] = None,
        cookie_domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self._semaphore:
            context: Optional[BrowserContext] = None
            try:
                context = await self.create_context()
                page = await context.new_page()
                page.set_default_timeout(self.timeout)

                await page.goto(login_url)
                logger.info(f"Publish login opened: {login_url}")

                if success_pattern:
                    await page.wait_for_url(success_pattern, timeout=self.timeout)
                else:
                    await self._wait_for_login(page, login_url)

                cookies = await context.cookies()
                filtered = self._filter_cookies(cookies, login_url, cookie_domain)
                if not filtered:
                    raise ValueError("No cookies extracted")

                return {
                    "cookies": filtered,
                    "user_agent": page.context.user_agent,
                }
            finally:
                if context:
                    await context.close()

    async def _wait_for_login(self, page: Page, login_url: str) -> None:
        parsed = urlparse(login_url)
        login_host = parsed.netloc.lower()
        start_url = page.url
        elapsed = 0
        interval = 1000
        while elapsed < self.timeout:
            await page.wait_for_timeout(interval)
            elapsed += interval
            current_url = page.url
            if current_url != start_url and login_host in current_url:
                return
            if "login" not in current_url.lower() and login_host in current_url:
                return

    def _filter_cookies(self, cookies: list, login_url: str, cookie_domain: Optional[str]) -> Dict[str, str]:
        if cookie_domain:
            def keep(domain: str) -> bool:
                return domain.endswith(cookie_domain)
        else:
            parsed = urlparse(login_url)
            host = parsed.netloc.lower()
            parts = host.split(".")
            root = ".".join(parts[-2:]) if len(parts) >= 2 else host
            def keep(domain: str) -> bool:
                return domain.endswith(host) or domain.endswith(root)

        result: Dict[str, str] = {}
        for cookie in cookies:
            domain = cookie.get("domain", "").lstrip(".").lower()
            if keep(domain):
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value is not None:
                    result[name] = value
        return result


publish_playwright_service = PublishPlaywrightService()
