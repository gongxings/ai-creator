"""
发布平台远程浏览器控制 WebSocket API
支持实时截图流和远程操作
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
from app.models.publish import PlatformAccount
from app.services.publish.platforms import get_platform, PLATFORM_REGISTRY
from app.services.oauth.remote_browser_service import (
    remote_browser_service,
    SessionStatus,
)

router = APIRouter(tags=["PublishRemoteBrowser"])


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """从 token 获取用户"""
    from app.utils.security import decode_access_token
    try:
        payload = decode_access_token(token)
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
async def publish_remote_browser_websocket(
    websocket: WebSocket,
    platform: str,
    token: str = Query(...),
    account_name: str = Query(default="default"),
):
    """
    发布平台远程浏览器 WebSocket 端点
    
    消息格式与 OAuth 远程浏览器相同
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
        session_id = f"publish:{user_id}:{platform}"
        
        logger.info(f"Publish WebSocket connected: {session_id}")
        
        # 检查平台是否存在
        if platform not in PLATFORM_REGISTRY:
            await websocket.send_json({"type": "error", "data": {"message": f"平台 {platform} 不存在"}})
            await websocket.close(code=4004)
            return
        
        # 获取平台发布器
        try:
            publisher = get_platform(platform)
        except Exception as e:
            await websocket.send_json({"type": "error", "data": {"message": str(e)}})
            await websocket.close(code=4004)
            return
        
        # 构建 Playwright 配置
        platform_config = {
            "oauth_url": publisher.get_login_url(),
            "success_pattern": "WAIT_FOR_LOGIN",  # 使用轮询检测登录状态
            "cookie_names": [],  # 保存所有 Cookie
        }
        
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
                
                # 如果是完成状态，保存凭证
                if status == SessionStatus.COMPLETED and "credentials" in data:
                    credentials = data["credentials"]
                    message["type"] = "credentials"
                    message["data"] = {
                        "message": "授权成功！",
                        "cookie_count": len(credentials.get("cookies", {})),
                    }
                    
                    # 保存 Cookie 到发布平台账号
                    await save_publish_credentials(
                        db, user_id, platform, account_name,
                        publisher, credentials
                    )
                
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send status: {e}")
        
        # 创建远程浏览器会话
        session = await remote_browser_service.create_session(
            user_id=user_id,
            platform=f"publish_{platform}",  # 加前缀避免与 OAuth 会话冲突
            platform_config=platform_config,
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
            logger.info(f"Publish WebSocket disconnected: {session_id}")
        
    except Exception as e:
        logger.error(f"Publish WebSocket error: {e}")
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
        logger.info(f"Publish WebSocket closed: {session_id}")


async def save_publish_credentials(
    db: Session,
    user_id: int,
    platform: str,
    account_name: str,
    publisher,
    credentials: dict,
):
    """保存凭证到发布平台账号"""
    try:
        cookies = credentials.get("cookies", {})
        
        # 查找或创建账号
        account = db.query(PlatformAccount).filter(
            PlatformAccount.user_id == user_id,
            PlatformAccount.platform == platform,
            PlatformAccount.account_name == account_name,
        ).first()
        
        if not account:
            account = PlatformAccount(
                user_id=user_id,
                platform=platform,
                account_name=account_name,
                cookies_valid="unknown",
                is_active="active",
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        
        # 使用发布器的 set_cookies 方法保存 Cookie
        publisher.set_cookies(account, cookies)
        account.cookies_valid = "valid"
        account.cookies_updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Publish credentials saved for user {user_id}, platform {platform}")
        
    except Exception as e:
        logger.error(f"Failed to save publish credentials: {e}")
        db.rollback()
        raise
