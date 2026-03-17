"""
微信公众号平台发布服务

使用 HTTP 请求方式验证 Cookie 和创建草稿，不依赖 Playwright 浏览器
"""
from typing import Dict, Any, Optional, List
import httpx
import re
import json

from .base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class WeChatPublisher(BasePlatformPublisher):
    """微信公众号发布实现"""
    
    # 微信公众号 API 基础 URL
    BASE_URL = "https://mp.weixin.qq.com"
    
    # 常用请求头
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://mp.weixin.qq.com/",
    }
    
    def get_platform_name(self) -> str:
        return "微信公众号"
    
    def get_login_url(self) -> str:
        return "https://mp.weixin.qq.com/"
    
    async def validate_cookies(self, account: PlatformAccount) -> bool:
        """
        验证微信公众号Cookie有效性
        
        使用 HTTP 请求验证，不依赖 Playwright
        """
        cookies = self.get_cookies(account)
        if not cookies:
            return False
        
        try:
            async with httpx.AsyncClient(
                headers=self.DEFAULT_HEADERS,
                cookies=cookies,
                follow_redirects=False,
                timeout=30.0
            ) as client:
                # 请求微信公众号后台首页
                response = await client.get(f"{self.BASE_URL}/cgi-bin/home")
                
                # 如果返回 302 重定向到登录页，说明 Cookie 无效
                if response.status_code == 302:
                    location = response.headers.get("location", "")
                    if "login" in location.lower() or "scanlogin" in location.lower():
                        self.logger.info("Cookie 无效：重定向到登录页")
                        return False
                
                # 如果返回 200，检查页面内容
                if response.status_code == 200:
                    content = response.text
                    # 检查是否包含登录页面的特征
                    if "请使用微信扫描二维码登录" in content or "扫码登录" in content:
                        self.logger.info("Cookie 无效：页面显示需要登录")
                        return False
                    
                    # 检查是否包含已登录的特征（如后台管理界面元素）
                    if "公众号" in content or "新建群发" in content or "首页" in content:
                        self.logger.info("Cookie 有效")
                        return True
                
                # 其他情况，尝试获取 token
                token = await self._extract_token_internal(client)
                if token:
                    self.logger.info(f"Cookie 有效，获取到 token: {token[:10]}...")
                    return True
                
                self.logger.info(f"Cookie 验证结果不确定，状态码: {response.status_code}")
                return False
                
        except httpx.TimeoutException:
            self.logger.error("验证微信公众号Cookie超时")
            return False
        except Exception as e:
            self.logger.error(f"验证微信公众号Cookie失败: {str(e)}")
            return False
    
    async def _extract_token_internal(self, client: httpx.AsyncClient) -> Optional[str]:
        """内部方法：从已有 client 提取 token"""
        return await self._extract_token_via_redirect(client)
    
    async def _extract_token(self, client: httpx.AsyncClient, cookies: Dict[str, str]) -> Optional[str]:
        """
        从微信公众号后台提取 token
        
        token 是进行后续 API 调用的必要参数
        
        重要：必须先访问根路径 /，让微信服务器重定向到带 token 的 URL
        直接访问 /cgi-bin/home 不会返回 token
        """
        return await self._extract_token_via_redirect(client)
    
    async def _extract_token_via_redirect(self, client: httpx.AsyncClient) -> Optional[str]:
        """
        通过访问根路径获取重定向 URL 中的 token
        
        微信公众号后台的工作流程：
        1. 访问 https://mp.weixin.qq.com/
        2. 服务器检查 Cookie，如果有效则重定向到 /cgi-bin/home?t=home/index&token=XXXXX
        3. 从重定向后的 URL 中提取 token
        """
        try:
            # 第一步：访问根路径，让服务器重定向
            # 注意：这里使用 follow_redirects=True 让 httpx 自动跟随重定向
            response = await client.get(
                f"{self.BASE_URL}/",
                follow_redirects=True
            )
            
            final_url = str(response.url)
            self.logger.info(f"Token extraction - Final URL: {final_url}, Status: {response.status_code}")
            
            # 从最终 URL 中提取 token
            url_token_match = re.search(r'token=(\d+)', final_url)
            if url_token_match:
                token = url_token_match.group(1)
                self.logger.info(f"Successfully extracted token from redirect URL: {token}")
                return token
            
            # 如果 URL 中没有 token，检查响应内容
            if response.status_code == 200:
                content = response.text
                
                # 检查是否是登录页面
                if "扫码登录" in content or "请使用微信扫描" in content or "scanlogin" in final_url.lower():
                    self.logger.warning("Cookie已失效，需要重新登录")
                    return None
                
                # 尝试从页面内容中提取 token
                token = self._parse_token_from_response(response)
                if token:
                    self.logger.info(f"Extracted token from page content: {token}")
                    return token
                
                # 调试：记录页面内容片段
                self.logger.warning(f"无法提取token，最终URL: {final_url}")
                self.logger.debug(f"页面内容片段: {content[:500]}")
            
            return None
        except Exception as e:
            self.logger.error(f"提取 token 失败: {str(e)}")
            return None
    
    def _parse_token_from_response(self, response: httpx.Response) -> Optional[str]:
        """从响应中解析 token"""
        # 从 URL 中提取 token
        url_match = re.search(r'token=(\d+)', str(response.url))
        if url_match:
            self.logger.info(f"Found token in URL: {url_match.group(1)}")
            return url_match.group(1)
        
        content = response.text
        
        # 先检查是否已登录（uin 不为空）
        uin_match = re.search(r'uin:\s*["\']?(\d+)', content)
        if not uin_match or uin_match.group(1) == "0":
            self.logger.warning("Cookie 已失效：uin 为空或为0")
            return None
        
        # 模式1: token=数字 (URL参数格式)
        pattern1 = re.search(r'[?&]token=(\d+)', content)
        if pattern1:
            self.logger.info(f"Found token (pattern1): {pattern1.group(1)}")
            return pattern1.group(1)
        
        # 模式2: "token":"数字" 或 'token':'数字' (JSON格式)
        pattern2 = re.search(r'["\']token["\']\s*:\s*["\']?(\d+)', content)
        if pattern2:
            self.logger.info(f"Found token (pattern2): {pattern2.group(1)}")
            return pattern2.group(1)
        
        # 模式3: token : 数字 或 token: 数字 (JS对象格式)
        pattern3 = re.search(r'\btoken\s*:\s*["\']?(\d+)', content)
        if pattern3:
            self.logger.info(f"Found token (pattern3): {pattern3.group(1)}")
            return pattern3.group(1)
        
        # 模式4: cgiData 中的 token
        pattern4 = re.search(r'cgiData\s*=\s*\{[^}]*?token\s*:\s*["\']?(\d+)', content, re.DOTALL)
        if pattern4:
            self.logger.info(f"Found token (pattern4): {pattern4.group(1)}")
            return pattern4.group(1)
        
        # 模式5: window.wx.cgiData
        pattern5 = re.search(r'window\.wx\.cgiData\s*=\s*\{[^}]*?token\s*:\s*["\']?(\d+)', content, re.DOTALL)
        if pattern5:
            self.logger.info(f"Found token (pattern5): {pattern5.group(1)}")
            return pattern5.group(1)
        
        # 模式6: 任意位置的 token=数字
        pattern6 = re.search(r'token[=:](\d{6,})', content)
        if pattern6:
            self.logger.info(f"Found token (pattern6): {pattern6.group(1)}")
            return pattern6.group(1)
        
        return None
    
    async def create_draft(
        self,
        account: PlatformAccount,
        title: str = None,
        content: str = None,
        cover_image: Optional[str] = None,
        images: Optional[List[str]] = None,
        video_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建微信公众号草稿
        
        Args:
            account: 平台账号
            title: 文章标题
            content: 文章内容（HTML格式）
            cover_image: 封面图片URL
            images: 其他图片URLs
            video_url: 视频URL（不适用）
            tags: 标签（微信不支持）
            location: 位置（不适用）
            **kwargs: 其他参数（author, digest等）
            
        Returns:
            Dict: 草稿信息
        """
        # 检查Cookie
        cookies = await self.check_cookies_or_raise(account)
        
        try:
            async with httpx.AsyncClient(
                headers=self.DEFAULT_HEADERS,
                cookies=cookies,
                follow_redirects=True,
                timeout=60.0
            ) as client:
                # 获取 token
                token = await self._extract_token(client, cookies)
                
                if not token:
                    return {
                        "success": False,
                        "message": "Cookie 已失效，请重新登录微信公众号后台 (https://mp.weixin.qq.com/) 并更新 Cookie"
                    }
                
                # 调试日志：检查 content 是否正确传递
                self.logger.info(f"Creating draft - title: {title}, content length: {len(content) if content else 0}")
                if content:
                    self.logger.debug(f"Content preview: {content[:200]}...")
                
                # 通过 API 创建草稿
                result = await self._create_draft_via_api(
                    client, token, title, content, cover_image, **kwargs
                )
                
                return result
                
        except ValueError as e:
            # Cookie 验证失败
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"创建微信公众号草稿失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建草稿失败: {str(e)}"
            }
    
    async def _create_draft_via_api(
        self,
        client: httpx.AsyncClient,
        token: str,
        title: str,
        content: str,
        cover_image: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通过微信公众号 API 创建草稿
        """
        try:
            # 获取作者和摘要
            author = kwargs.get('author', '')
            digest = kwargs.get('digest', '')
            if not digest and content:
                # 自动生成摘要：去除HTML标签，取前120字
                clean_content = re.sub(r'<[^>]+>', '', content)
                digest = clean_content[:120]
            
            # 构建图文消息数据
            appmsg_data = {
                "token": token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": "1",
                "random": "0.123456789",
                "AppMsgId": "",
                "count": "1",
                "data_seq": "0",
                "operate_from": "Chrome",
                "isnew": "1",
                "articlenum": "1",
                "can_reward": "0",
                "reward_reply_id": "",
                "is_pay_subscribe": "0",
                "pay_fee": "0",
                "pay_preview_percent": "0",
                "appmsgext": "",
                "title0": title or "",
                "author0": author,
                "digest0": digest,
                "content0": content or "",
                "sourceurl0": "",
                "need_open_comment0": "0",
                "only_fans_can_comment0": "0",
            }
            
            # 发送创建请求
            response = await client.post(
                f"{self.BASE_URL}/cgi-bin/operate_appmsg",
                params={
                    "t": "ajax-response",
                    "sub": "create",
                    "type": "10",
                    "token": token,
                    "lang": "zh_CN"
                },
                data=appmsg_data,
                headers={
                    **self.DEFAULT_HEADERS,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                }
            )
            
            self.logger.info(f"Create draft response: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.info(f"API response: {result}")
                    
                    ret_code = result.get("base_resp", {}).get("ret", -1)
                    
                    if ret_code == 0:
                        app_msg_id = result.get("appMsgId", "")
                        return {
                            "success": True,
                            "draft_id": str(app_msg_id),
                            "draft_url": f"{self.BASE_URL}/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&type=10&appmsgid={app_msg_id}&token={token}&lang=zh_CN",
                            "message": "草稿创建成功"
                        }
                    else:
                        error_msg = result.get("base_resp", {}).get("err_msg", "未知错误")
                        self.logger.warning(f"API 创建草稿失败: ret={ret_code}, err_msg={error_msg}")
                        return {
                            "success": False,
                            "message": f"创建草稿失败: {error_msg} (错误码: {ret_code})"
                        }
                        
                except json.JSONDecodeError:
                    self.logger.warning(f"API 返回非 JSON 格式: {response.text[:200]}")
                    return {
                        "success": False,
                        "message": "API 返回格式错误"
                    }
            
            return {
                "success": False,
                "message": f"API 请求失败，状态码: {response.status_code}"
            }
            
        except Exception as e:
            self.logger.error(f"API 创建草稿异常: {str(e)}")
            return {
                "success": False,
                "message": f"创建草稿异常: {str(e)}"
            }
    
    async def upload_image(
        self,
        account: PlatformAccount,
        image_url: str
    ) -> Optional[str]:
        """
        上传图片到微信公众号素材库
        
        Args:
            account: 平台账号
            image_url: 图片URL
            
        Returns:
            上传后的素材 media_id，失败返回 None
        """
        cookies = self.get_cookies(account)
        if not cookies:
            return None
        
        try:
            async with httpx.AsyncClient(
                headers=self.DEFAULT_HEADERS,
                cookies=cookies,
                follow_redirects=True,
                timeout=60.0
            ) as client:
                # 获取 token
                token = await self._extract_token(client, cookies)
                if not token:
                    return None
                
                # 下载图片
                image_response = await client.get(image_url)
                if image_response.status_code != 200:
                    return None
                
                image_data = image_response.content
                
                # 上传到微信
                files = {
                    "file": ("image.jpg", image_data, "image/jpeg")
                }
                
                response = await client.post(
                    f"{self.BASE_URL}/cgi-bin/filetransfer",
                    params={
                        "action": "upload_material",
                        "f": "json",
                        "scene": "1",
                        "writetype": "doublewrite",
                        "groupid": "1",
                        "token": token,
                        "lang": "zh_CN"
                    },
                    files=files
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("base_resp", {}).get("ret") == 0:
                        return result.get("content", "")
                
                return None
                
        except Exception as e:
            self.logger.error(f"上传图片失败: {str(e)}")
            return None
