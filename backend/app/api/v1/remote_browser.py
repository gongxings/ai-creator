"""
Remote browser WebSocket API
Support realtime screenshot streaming and remote operation
"""
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.models.user import User
from app.models.platform_config import PlatformConfig
from app.models.oauth_account import OAuthAccount
from app.services.oauth.adapters import PLATFORM_ADAPTERS
from app.services.oauth.remote_browser_service import (
    remote_browser_service,
    SessionStatus,
)
from app.services.oauth.encryption import encrypt_credentials

router = APIRouter(tags=["RemoteBrowser"])


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from token"""
    from app.core.security import decode_token
    try:
        payload = decode_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except Exception as e:
        logger.warning(f"Failed to decode token: {e}")
        return None


@router.websocket("/ws/{platform}")
async def remote_browser_websocket(
    websocket: WebSocket,
    platform: str,
    token: str = Query(...),
    account_name: str = Query(default="default"),
):
    """
    Remote browser WebSocket endpoint
    """
    await websocket.accept()
    
    db = SessionLocal()
    session_id = None
    
    try:
        # 验证用户
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.send_json({"type": "error", "data": {"message": "认证失败"}})
            await websocket.close(code=4001)
            return
        
        user_id = user.id
        session_id = f"{user_id}:{platform}"
        
        logger.info(f"WebSocket connected: {session_id}, account_name: {account_name}")
        
        # 获取平台配置
        platform_config_db = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == platform
        ).first()
        
        if not platform_config_db:
            await websocket.send_json({"type": "error", "data": {"message": f"平台 {platform} 不存在"}})
            await websocket.close(code=4004)
            return
        
        if not platform_config_db.is_enabled:
            await websocket.send_json({"type": "error", "data": {"message": f"平台 {platform} 已禁用"}})
            await websocket.close(code=4004)
            return
        
        # 获取适配器
        adapter_class = PLATFORM_ADAPTERS.get(platform)
        if not adapter_class:
            await websocket.send_json({"type": "error", "data": {"message": f"平台 {platform} 适配器不存在"}})
            await websocket.close(code=4004)
            return
        
        adapter = adapter_class(platform, {
            "oauth_config": platform_config_db.oauth_config,
            "litellm_config": platform_config_db.litellm_config,
            "quota_config": platform_config_db.quota_config,
        })
        
        # 获取 Playwright 配置
        playwright_config = adapter.get_platform_config()
        
        # 定义回调函数
        async def on_screenshot(screenshot_base64: str):
            try:
                await websocket.send_json({
                    "type": "screenshot",
                    "data": screenshot_base64,
                })
            except Exception as e:
                logger.warning(f"Failed to send screenshot: {e}")
        
        async def on_status_change(status: SessionStatus, data: dict):
            try:
                message = {
                    "type": "status",
                    "status": status.value,
                    "data": data,
                }
                
                # 如果是完成状态，发送凭证
                if status == SessionStatus.COMPLETED and "credentials" in data:
                    credentials = data["credentials"]
                    message["type"] = "credentials"
                    message["data"] = {
                        "message": "授权成功！",
                        "cookie_count": len(credentials.get("cookies", {})),
                    }
                    
                    # 保存凭证到数据库
                    await save_credentials(
                        db, user_id, platform, 
                        platform_config_db, adapter,
                        credentials, account_name
                    )
                
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send status: {e}")
        
        # 创建远程浏览器会话
        session = await remote_browser_service.create_session(
            user_id=user_id,
            platform=platform,
            platform_config=playwright_config,
            on_screenshot=on_screenshot,
            on_status_change=on_status_change,
        )
        
        # 更新 session_id
        session_id = session.session_id
        
        # 处理客户端消息
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                if msg_type == "mouse":
                    await remote_browser_service.handle_mouse_event(
                        session_id=session_id,
                        event_type=data.get("event", "click"),
                        x=data.get("x", 0.5),
                        y=data.get("y", 0.5),
                        button=data.get("button", "left"),
                    )
                
                elif msg_type == "keyboard":
                    await remote_browser_service.handle_keyboard_event(
                        session_id=session_id,
                        event_type=data.get("event", "type"),
                        key=data.get("key", ""),
                        text=data.get("text"),
                    )
                
                elif msg_type == "scroll":
                    await remote_browser_service.handle_scroll_event(
                        session_id=session_id,
                        delta_x=data.get("deltaX", 0),
                        delta_y=data.get("deltaY", 0),
                    )
                
                elif msg_type == "close":
                    break
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "data": {"message": str(e)}})
        except:
            pass
    
    finally:
        db.close()
        if session_id:
            try:
                await remote_browser_service.close_session(session_id)
            except:
                pass
        logger.info(f"WebSocket closed: {session_id}")


async def save_credentials(
    db: Session,
    user_id: int,
    platform: str,
    platform_config: PlatformConfig,
    adapter,
    credentials: dict,
    account_name: str = "",
):
    """Save credentials to database"""
    try:
        # 加密凭证
        encrypted_credentials = encrypt_credentials(credentials)
        
        # 如果没有提供 account_name，使用默认名称
        if not account_name or account_name == "default":
            account_name = f"{platform}_account"
        
        # 查找或创建账号
        existing_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user_id,
            OAuthAccount.platform == platform,
        ).first()
        
        if existing_account:
            # 更新现有账号
            existing_account.credentials = encrypted_credentials
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.utcnow()
            logger.info(f"Updated existing account for user {user_id}, platform {platform}")
        else:
            # 创建新账号
            new_account = OAuthAccount(
                user_id=user_id,
                platform=platform,
                account_name=account_name,
                credentials=encrypted_credentials,
                is_active=True,
                is_expired=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(new_account)
            logger.info(f"Created new account for user {user_id}, platform {platform}, account_name {account_name}")
        
        db.commit()
        logger.info(f"Credentials saved for user {user_id}, platform {platform}")
        
    except Exception as e:
        logger.error(f"Failed to save credentials: {e}")
        db.rollback()
        raise
