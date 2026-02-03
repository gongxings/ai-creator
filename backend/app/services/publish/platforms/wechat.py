"""
微信公众号平台发布服务
"""
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page
import asyncio

from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class WeChatPublisher(BasePlatformPublisher):
    """微信公众号发布实现"""
    
    def get_platform_name(self) -> str:
        return "微信公众号"
    
    def get_login_url(self) -> str:
        return "https://mp.weixin.qq.com/"
    
    async def validate_cookies(self, account: PlatformAccount) -> bool:
        """验证微信公众号Cookie有效性"""
        cookies = self.get_cookies(account)
        if not cookies:
            return False
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # 设置Cookie
                await context.add_cookies([
                    {"name": k, "value": v, "domain": ".qq.com", "path": "/"}
                    for k, v in cookies.items()
                ])
                
                page = await context.new_page()
                
                # 访问公众号后台首页
                await page.goto("https://mp.weixin.qq.com/", timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # 检查是否跳转到登录页
                current_url = page.url
                is_valid = "login" not in current_url.lower() and "mp.weixin.qq.com" in current_url
                
                await browser.close()
                return is_valid
                
        except Exception as e:
            self.logger.error(f"验证微信公众号Cookie失败: {str(e)}")
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
        创建微信公众号草稿
        
        Args:
            account: 平台账号
            title: 文章标题
            content: 文章内容（HTML格式）
            cover_image: 封面图片URL
            media_urls: 其他图片URLs
            tags: 标签（微信不支持）
            **kwargs: 其他参数（author, digest等）
            
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
                    {"name": k, "value": v, "domain": ".qq.com", "path": "/"}
                    for k, v in cookies.items()
                ])
                
                page = await context.new_page()
                
                # 访问图文消息页面
                await page.goto("https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=&lang=zh_CN", timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # 填写标题
                title_input = await page.wait_for_selector('#js_appmsg_title', timeout=10000)
                await title_input.fill(title)
                
                # 填写作者
                author = kwargs.get('author', '')
                if author:
                    author_input = await page.query_selector('#js_author')
                    if author_input:
                        await author_input.fill(author)
                
                # 填写摘要
                digest = kwargs.get('digest', content[:100])
                digest_input = await page.query_selector('#js_digest')
                if digest_input:
                    await digest_input.fill(digest)
                
                # 上传封面图
                if cover_image:
                    await self._upload_cover(page, cover_image)
                
                # 填写正文内容
                # 微信公众号使用富文本编辑器，需要特殊处理
                await self._fill_content(page, content)
                
                # 点击保存按钮
                save_btn = await page.wait_for_selector('#js_submit', timeout=10000)
                await save_btn.click()
                
                # 等待保存完成
                await asyncio.sleep(3)
                
                # 获取草稿箱链接
                draft_url = "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_list&type=10&action=list&token=&lang=zh_CN"
                
                await browser.close()
                
                return {
                    "success": True,
                    "draft_id": "draft",
                    "draft_url": draft_url,
                    "message": "草稿已保存，请前往微信公众号后台查看并发布"
                }
                
        except Exception as e:
            self.logger.error(f"创建微信公众号草稿失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建草稿失败: {str(e)}"
            }
    
    async def _upload_cover(self, page: Page, cover_url: str) -> None:
        """上传封面图"""
        try:
            # 点击封面上传按钮
            cover_btn = await page.query_selector('#js_cover_img_area')
            if cover_btn:
                await cover_btn.click()
                await asyncio.sleep(1)
                
                # 这里需要处理图片上传
                # 实际实现中需要下载图片并上传
                self.logger.info(f"上传封面: {cover_url}")
                
        except Exception as e:
            self.logger.error(f"上传封面失败: {str(e)}")
    
    async def _fill_content(self, page: Page, content: str) -> None:
        """填写正文内容"""
        try:
            # 微信公众号使用iframe编辑器
            # 需要切换到iframe中操作
            iframe = await page.wait_for_selector('#ueditor_0', timeout=10000)
            frame = await iframe.content_frame()
            
            if frame:
                # 在编辑器中填写内容
                editor = await frame.query_selector('body')
                if editor:
                    # 如果是HTML内容，直接设置innerHTML
                    await frame.evaluate(f'document.body.innerHTML = `{content}`')
                    
        except Exception as e:
            self.logger.error(f"填写内容失败: {str(e)}")
            raise
