"""
视频生成API
"""
from typing import Optional
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.creation import Creation
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.common import success_response
from app.utils.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    prompt: str
    duration: int = 5
    fps: int = 30
    resolution: str = "1080p"
    platform: Optional[str] = None  # 支持Cookie模式


class TextToVideoRequest(BaseModel):
    """文本转视频请求"""
    text: str
    voice: Optional[str] = None
    background_music: bool = False
    subtitle: bool = True
    platform: Optional[str] = None  # 支持Cookie模式


class ImageToVideoRequest(BaseModel):
    """图片转视频请求"""
    images: list[str]
    transition: str = "fade"
    duration_per_image: int = 3
    platform: Optional[str] = None  # 支持Cookie模式


class VideoTaskResponse(BaseModel):
    """视频任务响应"""
    task_id: str
    status: str
    video_url: Optional[str] = None
    script: Optional[str] = None
    progress: Optional[int] = None


# Background task processing functions
async def process_video_generation(db: Session, creation_id: int, request_data: dict, user_id: int = None, platform: Optional[str] = None):
    """后台处理视频生成任务"""
    try:
        logger.info(f"Starting video generation for creation {creation_id}, platform={platform}")

        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if not creation:
            logger.error(f"Creation {creation_id} not found")
            return

        if platform:
            # Cookie模式
            logger.info(f"Using Cookie mode for platform: {platform}")
            
            from app.models.oauth_account import OAuthAccount
            from app.services.oauth.encryption import decrypt_credentials
            from app.services.ai.video_service import DoubaoVideoService

            # 获取用户的OAuth账号
            oauth_account = db.query(OAuthAccount).filter(
                OAuthAccount.user_id == user_id,
                OAuthAccount.platform == platform,
                OAuthAccount.is_active == True,
                OAuthAccount.is_expired == False
            ).first()

            if not oauth_account:
                logger.error(f"No active OAuth account for platform {platform}")
                creation.status = "failed"
                creation.error_message = f"未找到有效的 {platform} 账号"
                creation.output_data = {"error": f"未找到有效的 {platform} 账号"}
                db.commit()
                return

            # 解密凭证
            try:
                credentials = decrypt_credentials(oauth_account.credentials)
                cookies = credentials.get("cookies", {})
            except Exception as e:
                logger.error(f"Failed to decrypt credentials: {e}")
                creation.status = "failed"
                creation.error_message = f"解密凭证失败: {str(e)}"
                creation.output_data = {"error": f"解密凭证失败: {str(e)}"}
                db.commit()
                return

            # 调用视频生成服务
            if platform == "doubao":
                service = DoubaoVideoService(cookies=cookies)
                
                # 验证Cookie
                is_valid = await service.validate_cookies()
                if not is_valid:
                    logger.warning(f"Cookie validation failed for {platform}")
                    creation.status = "failed"
                    creation.error_message = f"{platform} Cookie已过期"
                    creation.output_data = {"error": f"{platform} Cookie已过期"}
                    db.commit()
                    return
                
                # 生成视频脚本
                result = await service.generate_video(
                    prompt=request_data.get("prompt", ""),
                    duration=request_data.get("duration"),
                )
                
                logger.info(f"Video generation result: {result}")
                
                if "error" in result:
                    creation.status = "failed"
                    creation.error_message = result.get("error", "视频生成失败")
                    creation.output_data = result
                else:
                    creation.status = "completed"
                    creation.output_data = result
                
                db.commit()
            else:
                logger.error(f"Unsupported platform: {platform}")
                creation.status = "failed"
                creation.error_message = f"不支持的平台: {platform}"
                creation.output_data = {"error": f"不支持的平台: {platform}"}
                db.commit()
        else:
            # API Key模式 - 模拟
            await asyncio.sleep(5)
            video_url = f"https://example.com/generated_{uuid.uuid4().hex[:8]}.mp4"
            creation.status = "completed"
            creation.output_data = {"video_url": video_url}
            creation.completed_at = datetime.utcnow()
            db.commit()

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            creation = db.query(Creation).filter(Creation.id == creation_id).first()
            if creation:
                creation.status = "failed"
                creation.error_message = str(e)
                creation.output_data = {"error": str(e)}
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update creation status: {db_error}")


async def process_text_to_video(db: Session, creation_id: int, request_data: dict):
    """后台处理文本转视频任务"""
    try:
        await asyncio.sleep(5)
        
        video_url = f"https://example.com/text_video_{uuid.uuid4().hex[:8]}.mp4"
        
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"video_url": video_url}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


async def process_image_to_video(db: Session, creation_id: int, request_data: dict):
    """后台处理图片转视频任务"""
    try:
        await asyncio.sleep(5)
        
        video_url = f"https://example.com/image_video_{uuid.uuid4().hex[:8]}.mp4"
        
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"video_url": video_url}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


@router.post("/generate")
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成视频 - 支持Cookie和API Key模式"""
    try:
        # Cookie模式不需要积分
        if not request.platform:
            # 计算所需积分（根据时长和分辨率）
            base_credits = 200
            duration_multiplier = request.duration / 5  # 基准5秒
            resolution_multiplier = {"720p": 1.0, "1080p": 1.5, "4k": 2.5}.get(request.resolution, 1.0)
            required_credits = int(base_credits * duration_multiplier * resolution_multiplier)
            
            if current_user.credits < required_credits:
                raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"video_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            creation_type="video",
            title=f"视频生成: {request.prompt[:50]}",
            input_data={
                "prompt": request.prompt,
                "duration": request.duration,
                "fps": request.fps,
                "resolution": request.resolution,
                "platform": request.platform,
                "task_id": task_id
            },
            status="processing"
        )
        db.add(creation)
        
        # 仅在API Key模式下扣除积分
        if not request.platform:
            base_credits = 200
            duration_multiplier = request.duration / 5
            resolution_multiplier = {"720p": 1.0, "1080p": 1.5, "4k": 2.5}.get(request.resolution, 1.0)
            required_credits = int(base_credits * duration_multiplier * resolution_multiplier)
            
            current_user.credits -= required_credits
            transaction = CreditTransaction(
                user_id=current_user.id,
                transaction_type=TransactionType.CONSUME,
                amount=-required_credits,
                balance_before=current_user.credits + required_credits,
                balance_after=current_user.credits,
                description=f"视频生成: {request.duration}秒 {request.resolution}",
                related_id=creation.id,
                related_type="creation"
            )
            db.add(transaction)
        
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_video_generation,
            db, creation.id, request.dict(), current_user.id, request.platform
        )
        
        return success_response(
            data=VideoTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="视频生成任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"视频生成失败: {str(e)}")


@router.post("/text-to-video")
async def text_to_video(
    request: TextToVideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文本转视频"""
    try:
        required_credits = 150
        if request.background_music:
            required_credits += 30
        if request.subtitle:
            required_credits += 20
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"t2v_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            tool_type="text_to_video",
            title=f"文本转视频: {request.text[:50]}",
            input_data={
                "text": request.text,
                "voice": request.voice,
                "background_music": request.background_music,
                "subtitle": request.subtitle
            },
            status="processing",
            task_id=task_id
        )
        db.add(creation)
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description="文本转视频",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_text_to_video,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=VideoTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="文本转视频任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文本转视频失败: {str(e)}")


@router.post("/image-to-video")
async def image_to_video(
    request: ImageToVideoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """图片转视频"""
    try:
        required_credits = 100 + len(request.images) * 20
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"i2v_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            tool_type="image_to_video",
            title=f"图片转视频: {len(request.images)}张图片",
            input_data={
                "images": request.images,
                "transition": request.transition,
                "duration_per_image": request.duration_per_image
            },
            status="processing",
            task_id=task_id
        )
        db.add(creation)
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description=f"图片转视频: {len(request.images)}张",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_image_to_video,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=VideoTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="图片转视频任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"图片转视频失败: {str(e)}")


@router.get("/task/{task_id}")
async def get_video_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取视频任务状态"""
    try:
        creation = db.query(Creation).filter(
            Creation.task_id == task_id,
            Creation.user_id == current_user.id
        ).first()
        
        if not creation:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        video_url = None
        if creation.status == "completed" and creation.output_data:
            video_url = creation.output_data.get("video_url")
        
        progress = 100 if creation.status == "completed" else (
            50 if creation.status == "processing" else 0
        )
        
        return success_response(
            data=VideoTaskResponse(
                task_id=task_id,
                status=creation.status,
                video_url=video_url,
                progress=progress
            ),
            message="获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.post("/voiceover")
async def generate_voiceover(
    request: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI配音"""
    try:
        text = request.get("text", "")
        voice = request.get("voice", "default")
        
        required_credits = 50
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        # 模拟生成配音
        audio_url = f"https://example.com/voiceover_{uuid.uuid4().hex[:8]}.mp3"
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description="AI配音",
            related_type="voiceover"
        )
        db.add(transaction)
        db.commit()
        
        return success_response(
            data={"audio_url": audio_url},
            message="配音生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"配音生成失败: {str(e)}")


@router.post("/subtitles")
async def generate_subtitles(
    request: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成字幕"""
    try:
        video_url = request.get("video_url", "")
        
        required_credits = 30
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        # 模拟生成字幕
        subtitles = [
            {"start": 0, "end": 2, "text": "示例字幕1"},
            {"start": 2, "end": 4, "text": "示例字幕2"}
        ]
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description="生成字幕",
            related_type="subtitle"
        )
        db.add(transaction)
        db.commit()
        
        return success_response(
            data={"subtitles": subtitles},
            message="字幕生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"字幕生成失败: {str(e)}")
