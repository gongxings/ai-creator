"""
微信公众号发布器
"""
from typing import Dict, Any
import httpx
from app.services.publish.platforms.base import BasePlatformPublisher
from app.models.publish import PlatformAccount


class WeChatPublisher(BasePlatformPublisher):
    """微信公众号发布器"""
    
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    
    async def publish(
        self,
        account: PlatformAccount,
        content: Dict[str, Any],
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        发布到微信公众号
        
        Args:
            account: 平台账号
            content: 发布内容
            config: 发布配置
            
        Returns:
            Dict: 发布结果
        """
        credentials = self._get_credentials(account)
        access_token = await self._get_access_token(credentials)
        
        # 构建素材
        article = {
            "title": content["title"],
            "author": content.get("author", ""),
            "digest": content.get("digest", ""),
            "content": content["content"],
            "thumb_media_id": content.get("thumb_media_id", ""),
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        
        # 上传图文素材
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/material/add_news",
                params={"access_token": access_token},
                json={"articles": [article]}
            )
            result = response.json()
            
            if result.get("errcode") and result["errcode"] != 0:
                raise Exception(f"微信发布失败: {result.get('errmsg')}")
            
            media_id = result["media_id"]
            
            # 群发图文消息（可选）
            if config and config.get("send_to_all"):
                send_result = await self._send_to_all(access_token, media_id)
                return {
                    "post_id": send_result["msg_id"],
                    "url": f"https://mp.weixin.qq.com/s/{send_result['msg_data_id']}"
                }
            
            return {
                "post_id": media_id,
                "url": f"https://mp.weixin.qq.com"
            }
    
    async def check_status(
        self,
        account: PlatformAccount,
        post_id: str
    ) -> Dict[str, Any]:
        """检查发布状态"""
        return {
            "status": "success",
            "post_id": post_id
        }
    
    async def _get_access_token(self, credentials: Dict[str, Any]) -> str:
        """获取access_token"""
        appid = credentials["appid"]
        secret = credentials["secret"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/token",
                params={
                    "grant_type": "client_credential",
                    "appid": appid,
                    "secret": secret
                }
            )
            result = response.json()
            
            if "access_token" not in result:
                raise Exception(f"获取access_token失败: {result.get('errmsg')}")
            
            return result["access_token"]
    
    async def _send_to_all(self, access_token: str, media_id: str) -> Dict[str, Any]:
        """群发消息"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/message/mass/sendall",
                params={"access_token": access_token},
                json={
                    "filter": {"is_to_all": True},
                    "mpnews": {"media_id": media_id},
                    "msgtype": "mpnews",
                    "send_ignore_reprint": 0
                }
            )
            return response.json()
