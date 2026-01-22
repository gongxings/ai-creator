"""
今日头条平台发布服务（基于Cookie）
"""
from typing import Dict, Any, Optional, List
import os
import tempfile
import httpx
from playwright.async_api import async_playwright, Page
from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class ToutiaoPublisher(BasePlatformPublisher):
    """今日头条平台发布器（使用Cookie模拟浏览器操作）"""
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "今日头条"
    
    def get_login_url(self) -> str:
        """获取登录URL"""
        return "https://mp.toutiao.com/"
    
    async def validate_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        验证Cookie是否有效
        
        Args:
            cookies: Cookie列表
            
        Returns:
            bool: Cookie是否有效
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                
                # 设置Cookie
                await context.add_cookies(cookies)
                
                # 访问创作者中心
                page = await context.new_page()
                await page.goto("https://mp.toutiao.com/", wait_until="networkidle")
                
                # 检查是否需要登录
                current_url = page.url
                is_valid = "login" not in current_url.lower()
                
                await browser.close()
                return is_valid
                
        except Exception as e:
            self.logger.error(f"验证今日头条Cookie失败: {str(e)}")
            return False
    
    async def create_draft(
        self,
        account: PlatformAccount,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建今日头条图文/视频草稿
        
        Args:
            account: 平台账号
            content: 发布内容，包含：
                - title: 标题
                - content: 正文内容（图文）
                - video_url: 视频URL（视频）
                - cover_url: 封面图URL（必需）
                - images: 图片列表（图文，可选）
                - tags: 标签列表（可选）
                - content_type: 内容类型（article/video，默认article）
                
        Returns:
            Dict: 包含draft_url的字典
        """
        # 检查Cookie
        self.check_cookies_or_raise(account)
        cookies = self.get_cookies(account)
        
        # 验证必需字段
        if not content.get("cover_url"):
            raise ValueError("今日头条发布需要提供封面图URL")
        
        content_type = content.get("content_type", "article")
        
        if content_type == "video":
            return await self._create_video_draft(cookies, content)
        else:
            return await self._create_article_draft(cookies, content)
    
    async def _create_article_draft(
        self,
        cookies: List[Dict[str, Any]],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建图文草稿"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                
                # 访问发布页面
                await page.goto("https://mp.toutiao.com/profile_v4/graphic/publish", wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # 填写标题
                title_input = await page.wait_for_selector('input[placeholder*="标题"]', timeout=10000)
                await title_input.fill(content.get("title", ""))
                
                # 填写正文
                if content.get("content"):
                    # 等待富文本编辑器加载
                    await page.wait_for_timeout(2000)
                    editor = await page.query_selector('.ql-editor, .ProseMirror, [contenteditable="true"]')
                    if editor:
                        await editor.fill(content["content"])
                
                # 上传图片（如果有）
                if content.get("images"):
                    await self._upload_images(page, content["images"])
                
                # 上传封面图
                await self._upload_cover(page, content["cover_url"])
                
                # 添加标签
                if content.get("tags"):
                    await self._add_tags(page, content["tags"])
                
                # 保存草稿
                draft_btn = await page.wait_for_selector('button:has-text("存草稿"), button:has-text("保存草稿")', timeout=10000)
                await draft_btn.click()
                
                # 等待保存完成
                await page.wait_for_timeout(3000)
                
                await browser.close()
                
                return {
                    "success": True,
                    "draft_url": "https://mp.toutiao.com/profile_v4/graphic/content-manage",
                    "message": "草稿已保存到今日头条创作者中心"
                }
                
        except Exception as e:
            self.logger.error(f"创建今日头条图文草稿失败: {str(e)}")
            raise Exception(f"创建今日头条图文草稿失败: {str(e)}")
    
    async def _create_video_draft(
        self,
        cookies: List[Dict[str, Any]],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建视频草稿"""
        if not content.get("video_url"):
            raise ValueError("视频发布需要提供视频URL")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                
                # 访问视频发布页面
                await page.goto("https://mp.toutiao.com/profile_v4/xigua/upload-video", wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # 上传视频
                await self._upload_video(page, content["video_url"])
                
                # 等待视频处理
                await page.wait_for_timeout(5000)
                
                # 填写标题
                title_input = await page.wait_for_selector('input[placeholder*="标题"]', timeout=10000)
                await title_input.fill(content.get("title", ""))
                
                # 填写简介
                if content.get("description"):
                    desc_textarea = await page.query_selector('textarea[placeholder*="简介"]')
                    if desc_textarea:
                        await desc_textarea.fill(content["description"])
                
                # 上传封面
                await self._upload_cover(page, content["cover_url"])
                
                # 添加标签
                if content.get("tags"):
                    await self._add_tags(page, content["tags"])
                
                # 保存草稿
                draft_btn = await page.wait_for_selector('button:has-text("存草稿"), button:has-text("保存草稿")', timeout=10000)
                await draft_btn.click()
                
                # 等待保存完成
                await page.wait_for_timeout(3000)
                
                await browser.close()
                
                return {
                    "success": True,
                    "draft_url": "https://mp.toutiao.com/profile_v4/xigua/content-manage",
                    "message": "草稿已保存到今日头条创作者中心"
                }
                
        except Exception as e:
            self.logger.error(f"创建今日头条视频草稿失败: {str(e)}")
            raise Exception(f"创建今日头条视频草稿失败: {str(e)}")
    
    async def _upload_images(self, page: Page, image_urls: List[str]) -> None:
        """
        上传图片到正文
        
        Args:
            page: 页面对象
            image_urls: 图片URL列表
        """
        try:
            for image_url in image_urls[:9]:  # 最多9张图
                # 下载图片
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=30.0)
                    image_data = response.content
                
                # 保存到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(image_data)
                    tmp_path = tmp_file.name
                
                try:
                    # 查找上传按钮
                    upload_btn = await page.query_selector('input[type="file"][accept*="image"]')
                    if upload_btn:
                        await upload_btn.set_input_files(tmp_path)
                        await page.wait_for_timeout(2000)
                finally:
                    # 清理临时文件
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                        
        except Exception as e:
            self.logger.error(f"上传图片失败: {str(e)}")
    
    async def _upload_cover(self, page: Page, cover_url: str) -> None:
        """
        上传封面图
        
        Args:
            page: 页面对象
            cover_url: 封面图URL
        """
        try:
            # 下载封面图
            async with httpx.AsyncClient() as client:
                response = await client.get(cover_url, timeout=30.0)
                cover_data = response.content
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(cover_data)
                tmp_path = tmp_file.name
            
            try:
                # 查找封面上传按钮
                cover_upload = await page.query_selector('input[type="file"][accept*="image"]')
                if not cover_upload:
                    # 尝试点击封面区域触发上传
                    cover_area = await page.query_selector('.cover-upload, [class*="cover"]')
                    if cover_area:
                        await cover_area.click()
                        await page.wait_for_timeout(1000)
                        cover_upload = await page.query_selector('input[type="file"][accept*="image"]')
                
                if cover_upload:
                    await cover_upload.set_input_files(tmp_path)
                    await page.wait_for_timeout(3000)
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            self.logger.error(f"上传封面图失败: {str(e)}")
    
    async def _upload_video(self, page: Page, video_url: str) -> None:
        """
        上传视频文件
        
        Args:
            page: 页面对象
            video_url: 视频URL
        """
        try:
            # 下载视频
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, timeout=120.0)
                video_data = response.content
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(video_data)
                tmp_path = tmp_file.name
            
            try:
                # 查找视频上传按钮
                video_upload = await page.wait_for_selector('input[type="file"][accept*="video"]', timeout=10000)
                await video_upload.set_input_files(tmp_path)
                
                # 等待视频上传和处理
                await page.wait_for_timeout(10000)
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            self.logger.error(f"上传视频失败: {str(e)}")
            raise
    
    async def _add_tags(self, page: Page, tags: List[str]) -> None:
        """
        添加标签
        
        Args:
            page: 页面对象
            tags: 标签列表
        """
        try:
            # 查找标签输入框
            tag_input = await page.query_selector('input[placeholder*="标签"], input[placeholder*="话题"]')
            if tag_input:
                for tag in tags[:5]:  # 最多5个标签
                    await tag_input.fill(tag)
                    await page.wait_for_timeout(500)
                    # 按回车确认
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"添加标签失败: {str(e)}")
