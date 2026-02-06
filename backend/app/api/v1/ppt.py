"""
PPT生成API路由
"""
from typing import Optional, List
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
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


class PPTGenerateRequest(BaseModel):
    topic: str
    slides_count: Optional[int] = 10
    style: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None  # 支持Cookie模式


class PPTFromOutlineRequest(BaseModel):
    outline: str
    style: Optional[str] = None
    platform: Optional[str] = None  # 支持Cookie模式


class PPTTaskResponse(BaseModel):
    task_id: str
    status: str
    ppt_url: Optional[str] = None
    outline: Optional[str] = None
    preview_images: Optional[List[str]] = None
    progress: Optional[int] = None


async def process_ppt_generation(db: Session, creation_id: int, request_data: dict, user_id: int = None, platform: Optional[str] = None):
    """后台处理PPT生成任务"""
    try:
        logger.info(f"Starting PPT generation for creation {creation_id}, platform={platform}")

        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if not creation:
            logger.error(f"Creation {creation_id} not found")
            return

        if platform:
            # Cookie模式
            logger.info(f"Using Cookie mode for platform: {platform}")
            
            from app.models.oauth_account import OAuthAccount
            from app.services.oauth.encryption import decrypt_credentials
            from app.services.ai.ppt_service import DoubiaoPPTService

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

            # 调用PPT生成服务
            if platform == "doubao":
                service = DoubiaoPPTService(cookies=cookies)
                
                # 验证Cookie
                is_valid = await service.validate_cookies()
                if not is_valid:
                    logger.warning(f"Cookie validation failed for {platform}")
                    creation.status = "failed"
                    creation.error_message = f"{platform} Cookie已过期"
                    creation.output_data = {"error": f"{platform} Cookie已过期"}
                    db.commit()
                    return
                
                # 生成PPT大纲
                result = await service.generate_ppt_outline(
                    title=request_data.get("topic", ""),
                    content="",
                    num_slides=request_data.get("slides_count", 10)
                )
                
                logger.info(f"PPT generation result: {result}")
                
                if "error" in result:
                    creation.status = "failed"
                    creation.error_message = result.get("error", "PPT生成失败")
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
            await asyncio.sleep(2)
            ppt_url = f"https://example.com/ppt_{uuid.uuid4().hex[:8]}.pptx"
            preview_images = [
                f"https://example.com/ppt_preview_{uuid.uuid4().hex[:8]}.png"
                for _ in range(3)
            ]
            creation.status = "completed"
            creation.output_data = {"ppt_url": ppt_url, "preview_images": preview_images}
            db.commit()

    except Exception as e:
        logger.error(f"PPT generation failed: {e}")
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


@router.post("/generate")
async def generate_ppt(
    request: PPTGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """主题生成PPT - 支持Cookie和API Key模式"""
    try:
        # Cookie模式不需要积分
        if not request.platform:
            # API Key模式：计算所需积分
            required_credits = (request.slides_count or 10) * 50
            
            if current_user.credits < required_credits:
                raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"ppt_{uuid.uuid4().hex[:16]}"
        creation = Creation(
            user_id=current_user.id,
            creation_type="ppt",
            title=f"PPT: {request.topic[:50]}",
            input_data={
                **request.dict(),
                "task_id": task_id
            },
            status="processing"
        )
        db.add(creation)
        
        # 仅在API Key模式下扣除积分
        if not request.platform:
            required_credits = (request.slides_count or 10) * 50
            current_user.credits -= required_credits
            transaction = CreditTransaction(
                user_id=current_user.id,
                transaction_type=TransactionType.CONSUME,
                amount=-required_credits,
                balance_before=current_user.credits + required_credits,
                balance_after=current_user.credits,
                description=f"PPT生成: {request.slides_count}页",
                related_id=creation.id,
                related_type="creation"
            )
            db.add(transaction)
        
        db.commit()
        db.refresh(creation)

        background_tasks.add_task(process_ppt_generation, db, creation.id, request.dict(), current_user.id, request.platform)

        return success_response(
            data=PPTTaskResponse(task_id=task_id, status="processing", progress=0),
            message="PPT生成任务已创建"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成PPT失败: {str(e)}")


@router.post("/from-outline")
async def generate_ppt_from_outline(
    request: PPTFromOutlineRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """大纲生成PPT"""
    try:
        task_id = f"ppt_outline_{uuid.uuid4().hex[:16]}"
        creation = Creation(
            user_id=current_user.id,
            tool_type="ppt_outline",
            title="PPT: 大纲生成",
            input_data=request.dict(),
            status="processing",
            task_id=task_id
        )
        db.add(creation)
        db.commit()
        db.refresh(creation)

        background_tasks.add_task(process_ppt_generation, db, creation.id, request.dict())

        return success_response(
            data=PPTTaskResponse(task_id=task_id, status="processing", progress=0),
            message="PPT生成任务已创建"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成PPT失败: {str(e)}")


@router.post("/from-document")
async def generate_ppt_from_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文档转PPT"""
    try:
        task_id = f"ppt_doc_{uuid.uuid4().hex[:16]}"
        creation = Creation(
            user_id=current_user.id,
            tool_type="ppt_document",
            title=f"PPT: {file.filename}",
            input_data={"filename": file.filename},
            status="processing",
            task_id=task_id
        )
        db.add(creation)
        db.commit()
        db.refresh(creation)

        if background_tasks:
            background_tasks.add_task(process_ppt_generation, db, creation.id, {"filename": file.filename})

        return success_response(
            data=PPTTaskResponse(task_id=task_id, status="processing", progress=0),
            message="PPT生成任务已创建"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成PPT失败: {str(e)}")


@router.get("/task/{task_id}")
async def get_ppt_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取PPT任务状态"""
    try:
        creation = db.query(Creation).filter(
            Creation.task_id == task_id,
            Creation.user_id == current_user.id
        ).first()
        if not creation:
            raise HTTPException(status_code=404, detail="任务不存在")

        data = creation.output_data or {}
        progress = 100 if creation.status == "completed" else (
            50 if creation.status == "processing" else 0
        )

        return success_response(
            data=PPTTaskResponse(
                task_id=task_id,
                status=creation.status,
                ppt_url=data.get("ppt_url"),
                preview_images=data.get("preview_images"),
                progress=progress
            ),
            message="获取成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.get("/{ppt_id}/download")
async def download_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载PPT文件"""
    creation = db.query(Creation).filter(
        Creation.id == ppt_id,
        Creation.user_id == current_user.id
    ).first()

    if not creation:
        raise HTTPException(status_code=404, detail="PPT不存在")

    data = creation.output_data or {}
    download_url = data.get("ppt_url") or f"https://example.com/ppt/{ppt_id}.pptx"
    return success_response(
        data={"download_url": download_url},
        message="success"
    )


@router.get("/templates")
async def get_ppt_templates():
    """获取PPT模板列表"""
    return success_response(
        data=[
            {"id": "default", "name": "默认模板"},
            {"id": "business", "name": "商务模板"},
            {"id": "simple", "name": "简约模板"}
        ],
        message="success"
    )
