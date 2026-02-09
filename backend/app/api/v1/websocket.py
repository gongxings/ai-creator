"""Playwright WebSocket API"""
import asyncio
import base64
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.oauth import pw_service as pw_service
from app.services.oauth.oauth_service import oauth_service
from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Playwright WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}, total: {len(self.active_connections)}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}, total: {len(self.active_connections)}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        for session_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {session_id}: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

async def log_handler(session_id: str, level: str, message: str, data: Optional[Dict] = None):
    await manager.send_message(session_id, {
        "type": "log",
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "data": data
    })

async def screenshot_handler(session_id: str, image_data: str, url: str):
    await manager.send_message(session_id, {
        "type": "screenshot",
        "timestamp": datetime.now().isoformat(),
        "image": image_data,
        "url": url
    })

@router.websocket("/ws/playwright/{platform}")
async def playwright_websocket(
    websocket: WebSocket,
    platform: str,
    user_id: int = Query(...),
    session_token: Optional[str] = Query(None)
):
    session_id = f"{user_id}:{platform}"
    await manager.connect(websocket, session_id)
    
    await log_handler(session_id, "info", f"已连接到 {platform} Playwright会话", {"session_id": session_id})
    
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            params = data.get("params", {})
            
            await log_handler(session_id, "debug", f"收到命令: {command}", params)
            
            if command == "screenshot":
                image_data = await pw_service.capture_screenshot(platform)
                if image_data:
                    await screenshot_handler(session_id, image_data, "")
                    
            elif command == "navigate":
                url = params.get("url")
                if url:
                    await pw_service.navigate_to(platform, url)
                    await log_handler(session_id, "info", f"导航到: {url}")
                    
            elif command == "click":
                selector = params.get("selector")
                if selector:
                    await pw_service.click_element(platform, selector)
                    await log_handler(session_id, "info", f"点击元素: {selector}")
                    
            elif command == "input":
                selector = params.get("selector")
                text = params.get("text")
                if selector and text:
                    await pw_service.input_text(platform, selector, text)
                    await log_handler(session_id, "info", f"输入文本到 {selector}: {text[:50]}...")
                    
            elif command == "wait":
                timeout = params.get("timeout", 3000)
                await asyncio.sleep(timeout / 1000)
                await log_handler(session_id, "info", f"等待完成: {timeout}ms")
                
            elif command == "execute":
                script = params.get("script")
                if script:
                    result = await pw_service.execute_script(platform, script)
                    await manager.send_message(session_id, {
                        "type": "script_result",
                        "result": result
                    })
                    
            elif command == "start_streaming":
                interval = params.get("interval", 2000)
                await pw_service.start_screenshot_stream(
                    platform, 
                    lambda img: asyncio.create_task(screenshot_handler(session_id, img, "")),
                    interval
                )
                await log_handler(session_id, "info", f"开始截图流，间隔: {interval}ms")
                
            elif command == "stop_streaming":
                await pw_service.stop_screenshot_stream(platform)
                await log_handler(session_id, "info", "停止截图流")
                
            elif command == "get_url":
                url = await pw_service.get_current_url(platform)
                await manager.send_message(session_id, {
                    "type": "url",
                    "url": url
                })
                
            elif command == "start_auth":
                # 启动授权流程
                account_name = params.get("account_name", platform)
                await log_handler(session_id, "info", f"开始授权流程，账号: {account_name}")
                
                # 获取平台配置
                db = next(get_db())
                from app.models.platform_config import PlatformConfig
                platform_config = db.query(PlatformConfig).filter(
                    PlatformConfig.platform_id == platform
                ).first()
                
                if not platform_config:
                    await log_handler(session_id, "error", f"未找到平台配置: {platform}")
                    continue
                
                # 构建平台配置
                adapter = None
                try:
                    from app.services.oauth.adapters import get_adapter
                    adapter = get_adapter(platform, {
                        "oauth_config": platform_config.oauth_config,
                        "litellm_config": platform_config.litellm_config,
                        "quota_config": platform_config.quota_config,
                    })
                except Exception as e:
                    await log_handler(session_id, "error", f"获取适配器失败: {e}")
                    continue
                
                if not adapter:
                    await log_handler(session_id, "error", f"未找到适配器: {platform}")
                    continue
                
                platform_meta = adapter.get_platform_config()
                
                # 启动授权流程
                async def progress_callback(status: str, data: Dict[str, Any]):
                    await manager.send_message(session_id, {
                        "type": "log",
                        "level": "info",
                        "message": data.get("message", status),
                        "data": data
                    })
                    
                    if status == "completed":
                        # 授权完成，保存凭证
                        credentials = data.get("credentials", {})
                        try:
                            # 加密凭证
                            from app.services.oauth.encryption import encrypt_credentials
                            encrypted = encrypt_credentials(credentials)
                            
                            # 保存到数据库
                            from app.models.oauth_account import OAuthAccount
                            from sqlalchemy import and_
                            
                            existing = db.query(OAuthAccount).filter(
                                and_(
                                    OAuthAccount.user_id == user_id,
                                    OAuthAccount.platform == platform
                                )
                            ).first()
                            
                            if existing:
                                existing.credentials = encrypted
                                existing.is_active = True
                                existing.is_expired = False
                            else:
                                new_account = OAuthAccount(
                                    user_id=user_id,
                                    platform=platform,
                                    account_name=account_name,
                                    credentials=encrypted,
                                    is_active=True,
                                    is_expired=False
                                )
                                db.add(new_account)
                            
                            db.commit()
                            
                            await manager.send_message(session_id, {
                                "type": "credentials_saved",
                                "message": "凭证已保存",
                                "account_name": account_name,
                                "platform": platform
                            })
                            
                        except Exception as e:
                            await manager.send_message(session_id, {
                                "type": "error",
                                "message": f"保存凭证失败: {str(e)}"
                            })
                
                try:
                    credentials = await pw_service.authorize_platform(
                        platform_meta,
                        progress_callback
                    )
                except Exception as e:
                    await log_handler(session_id, "error", f"授权失败: {e}")
                
            else:
                await log_handler(session_id, "warning", f"未知命令: {command}")
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        await log_handler(session_id, "info", "WebSocket连接已关闭")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await log_handler(session_id, "error", f"错误: {str(e)}")
        manager.disconnect(session_id)
