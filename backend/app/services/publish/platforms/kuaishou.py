"""
快手平台发布服务（基于Cookie）
"""
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page
from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class KuaishouPublisher(BasePlatformPublisher):
    """快手平台发布器（使用Cookie模拟浏览器操作）"""
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "快手"
    
    def get_login_url(self) -> str:
        """获取登录URL"""
        return "https://cp.kuaishou.com/"
    
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
                await page.goto("https://cp.kuaishou.com/", wait_until="networkidle")
                
                # 检查是否需要登录
                current_url = page.url
                is_valid = "login" not in current_url.lower()
                
                await browser.close()
                return is_valid
                
        except Exception as e:
            self.logger.error(f"验证快手Cookie失败: {str(e)}")
            return False
    
    async def create_draft(
        self,
        account: PlatformAccount,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建快手视频草稿
        
        Args:
            account: 平台账号
            content: 发布内容，包含：
                - title: 视频标题
                - description: 视频描述
                - video_url: 视频文件URL
                - cover_url: 封面图URL（必需）
                - tags: 标签列表（可选）
                - location: 位置信息（可选）
                
        Returns:
            Dict: 包含draft_url的字典
        """
        # 检查Cookie
        self.check_cookies_or_raise(account)
        cookies = self.get_cookies(account)
        
        # 验证必需字段
        if not content.get("video_url"):
            raise ValueError("快手发布需要提供视频URL")
        if not content.get("cover_url"):
            raise ValueError("快手发布需要提供封面图URL")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                
                # 访问发布页面
                await page.goto("https://cp.kuaishou.com/article/publish/video", wait_until="networkidle")
                await page.wait_for_timeout(2000)
                
                # 上传视频文件
                await self._upload_video(page, content["video_url"])
                
                # 等待视频处理
                await page.wait_for_timeout(5000)
                
                # 上传封面图
                await self._upload_cover(page, content["cover_url"])
                
                # 填写标题
                title_input = await page.wait_for_selector('input[placeholder*="标题"]', timeout=10000)
                await title_input.fill(content.get("title", ""))
                
                # 填写描述
                if content.get("description"):
                    desc_textarea = await page.query_selector('textarea[placeholder*="描述"]')
                    if desc_textarea:
                        await desc_textarea.fill(content["description"])
                
                # 添加标签
                if content.get("tags"):
                    await self._add_tags(page, content["tags"])
                
                # 添加位置
                if content.get("location"):
                    location_btn = await page.query_selector('text="添加地理位置"')
                    if location_btn:
                        await location_btn.click()
                        await page.wait_for_timeout(1000)
                        location_input = await page.query_selector('input[placeholder*="搜索"]')
                        if location_input:
                            await location_input.fill(content["location"])
                            await page.wait_for_timeout(1000)
                            # 选择第一个结果
                            first_result = await page.query_selector('.location-list-item:first-child')
                            if first_result:
                                await first_result.click()
                
                # 保存草稿
                draft_btn = await page.wait_for_selector('button:has-text("保存草稿")', timeout=10000)
                await draft_btn.click()
                
                # 等待保存完成
                await page.wait_for_timeout(3000)
                
                await browser.close()
                
                return {
                    "success": True,
                    "draft_url": "https://cp.kuaishou.com/article/manage/video",
                    "message": "草稿已保存到快手创作者中心"
                }
                
        except Exception as e:
            self.logger.error(f"创建快手草稿失败: {str(e)}")
            raise Exception(f"创建快手草稿失败: {str(e)}")
    
    async def _upload_video(self, page: Page, video_url: str):
        """上传视频"""
        import httpx
        import tempfile
        import os
        
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=120.0)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
        
        try:
            # 找到上传按钮并上传
            upload_input = await page.query_selector('input[type="file"][accept*="video"]')
            if upload_input:
                await upload_input.set_input_files(tmp_path)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    async def _upload_cover(self, page: Page, cover_url: str):
        """上传封面图"""
        import httpx
        import tempfile
        import os
        
        async with httpx.AsyncClient() as client:
            response = await client.get(cover_url, timeout=30.0)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
        
        try:
            # 点击封面编辑按钮
            cover_btn = await page.query_selector('text="更换封面"')
            if cover_btn:
                await cover_btn.click()
                await page.wait_for_timeout(1000)
                
                # 上传封面图片
                cover_input = await page.query_selector('input[type="file"][accept*="image"]')
                if cover_input:
                    await cover_input.set_input_files(tmp_path)
                    await page.wait_for_timeout(2000)
                    # 确认封面
                    confirm_btn = await page.query_selector('button:has-text("确定")')
                    if confirm_btn:
                        await confirm_btn.click()
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    async def _add_tags(self, page: Page, tags: List[str]):
        """添加标签"""
        try:
            # 点击添加标签按钮
            tag_btn = await page.query_selector('text="添加标签"')
            if tag_btn:
                await tag_btn.click()
                await page.wait_for_timeout(1000)
                
                # 添加每个标签（最多10个）
                for tag in tags[:10]:
                    tag_input = await page.query_selector('input[placeholder*="搜索标签"]')
                    if tag_input:
                        await tag_input.fill(tag)
                        await page.wait_for_timeout(500)
                        # 选择第一个结果
                        first_result = await page.query_selector('.tag-item:first-child')
                        if first_result:
                            await first_result.click()
                        await page.wait_for_timeout(500)
        except Exception as e:
            self.logger.warning(f"添加标签失败: {str(e)}")
