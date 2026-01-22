"""
小红书平台发布服务
"""
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio

from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class XiaohongshuPublisher(BasePlatformPublisher):
    """小红书平台发布实现"""
    
    def get_platform_name(self) -> str:
        return "小红书"
    
    def get_login_url(self) -> str:
        return "https://creator.xiaohongshu.com/login"
    
    async def validate_cookies(self, account: PlatformAccount) -> bool:
        """验证小红书Cookie有效性"""
        cookies = self.get_cookies(account)
        if not cookies:
            return False
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # 设置Cookie
                await context.add_cookies([
                    {"name": k, "value": v, "domain": ".xiaohongshu.com", "path": "/"}
                    for k, v in cookies.items()
                ])
                
                page = await context.new_page()
                
                # 访问创作者中心，检查是否需要登录
                await page.goto("https://creator.xiaohongshu.com/creator/home", timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # 检查是否跳转到登录页
                current_url = page.url
                is_valid = "login" not in current_url.lower()
                
                await browser.close()
                return is_valid
                
        except Exception as e:
            self.logger.error(f"验证小红书Cookie失败: {str(e)}")
            return False
    
    async def create_draft(
        self,
        account: PlatformAccount,
        title: str,
        content: str,
        cover_image: Optional[str] = None,
        media_urls: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建小红书草稿
        
        Args:
            account: 平台账号
            title: 笔记标题
            content: 笔记内容
            cover_image: 封面图片URL
            media_urls: 图片URLs（小红书最多9张）
            tags: 标签列表
            **kwargs: 其他参数
            
        Returns:
            Dict: 草稿信息
        """
        # 检查Cookie
        cookies = await self.check_cookies_or_raise(account)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                # 设置Cookie
                await context.add_cookies([
                    {"name": k, "value": v, "domain": ".xiaohongshu.com", "path": "/"}
                    for k, v in cookies.items()
                ])
                
                page = await context.new_page()
                
                # 访问发布页面
                await page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # 等待页面加载
                await asyncio.sleep(2)
                
                # 上传图片（如果有）
                if media_urls:
                    await self._upload_images(page, media_urls[:9])  # 最多9张
                elif cover_image:
                    await self._upload_images(page, [cover_image])
                
                # 填写标题
                title_input = await page.wait_for_selector('input[placeholder*="填写标题"]', timeout=10000)
                await title_input.fill(title)
                
                # 填写内容
                content_input = await page.wait_for_selector('textarea[placeholder*="填写正文"]', timeout=10000)
                await content_input.fill(content)
                
                # 添加标签（如果有）
                if tags:
                    await self._add_tags(page, tags)
                
                # 点击"保存草稿"按钮
                save_draft_btn = await page.wait_for_selector('button:has-text("保存草稿")', timeout=10000)
                await save_draft_btn.click()
                
                # 等待保存完成
                await asyncio.sleep(3)
                
                # 获取草稿链接
                draft_url = "https://creator.xiaohongshu.com/creator/post-manage"
                
                await browser.close()
                
                return {
                    "success": True,
                    "draft_id": "draft",  # 小红书不返回具体ID
                    "draft_url": draft_url,
                    "message": "草稿已保存，请前往小红书创作者中心查看并发布"
                }
                
        except Exception as e:
            self.logger.error(f"创建小红书草稿失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建草稿失败: {str(e)}"
            }
    
    async def _upload_images(self, page: Page, image_urls: List[str]) -> None:
        """上传图片到小红书"""
        try:
            # 查找上传按钮
            upload_input = await page.wait_for_selector('input[type="file"]', timeout=10000)
            
            # 下载图片并上传
            for image_url in image_urls:
                # 这里需要先下载图片到本地，然后上传
                # 实际实现中需要处理图片下载和临时文件
                self.logger.info(f"上传图片: {image_url}")
                # await upload_input.set_input_files(local_image_path)
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"上传图片失败: {str(e)}")
            raise
    
    async def _add_tags(self, page: Page, tags: List[str]) -> None:
        """添加标签"""
        try:
            for tag in tags[:10]:  # 小红书最多10个标签
                # 查找标签输入框
                tag_input = await page.query_selector('input[placeholder*="标签"]')
                if tag_input:
                    await tag_input.fill(f"#{tag}")
                    await asyncio.sleep(0.5)
                    # 按回车确认
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            self.logger.error(f"添加标签失败: {str(e)}")
