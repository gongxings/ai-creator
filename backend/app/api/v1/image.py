"""
图片生成API
"""
from typing import Optional
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.creation import Creation, CreationStatus
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.common import success_response
from app.utils.deps import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class ImageGenerateRequest(BaseModel):
    """图片生成请求"""
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    num_images: int = 1
    style: Optional[str] = None


class ImageVariationRequest(BaseModel):
    """图片变体请求"""
    image: str
    num_variations: int = 1


class ImageEditRequest(BaseModel):
    """图片编辑请求"""
    image: str
    prompt: str
    mask: Optional[str] = None


class ImageUpscaleRequest(BaseModel):
    """图片放大请求"""
    image: str
    scale: int = 2


class ImageTaskResponse(BaseModel):
    """图片任务响应"""
    task_id: str
    status: str
    images: Optional[list[str]] = None
    progress: Optional[int] = None


# Background task processing functions
async def process_image_generation(db: Session, creation_id: int, request_data: dict):
    """后台处理图片生成任务"""
    try:
        from app.models.oauth_account import OAuthAccount
        from app.models.platform_config import PlatformConfig
        from app.services.oauth.adapters import PLATFORM_ADAPTERS

        logger.info(f"Starting image generation for creation {creation_id}")

        creation = db.query(Creation).filter(Creation.id == creation_id).first()

        if not creation:
            logger.error(f"Creation {creation_id} not found")
            return

        logger.info(f"Creation found: user_id={creation.user_id}, status={creation.status}")

        # 获取用户可用的 OAuth 账号
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == "doubao"
        ).first()

        if not platform_config:
            logger.error("Doubao platform config not found")
            raise ValueError("平台配置未找到")

        logger.info(f"Platform config found: {platform_config.platform_id}")

        # 获取用户的豆包 OAuth 账号
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == creation.user_id,
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True,
            OAuthAccount.is_expired == False
        ).first()

        if not oauth_account:
            logger.error(f"No active OAuth account for user {creation.user_id}")
            creation.status = "failed"
            creation.error_message = "未找到有效的豆包 OAuth 账号"
            creation.output_data = {"error": "未找到有效的豆包 OAuth 账号"}
            db.commit()
            return

        logger.info(f"OAuth account found: {oauth_account.id}, name={oauth_account.account_name}")

        # 解密凭证
        from app.services.oauth.encryption import decrypt_credentials
        try:
            credentials = decrypt_credentials(oauth_account.credentials)
            cookies = credentials.get("cookies", {})
            logger.info(f"Cookies decrypted: {list(cookies.keys())} cookies")
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            creation.status = "failed"
            creation.error_message = f"解密凭证失败: {str(e)}"
            creation.output_data = {"error": f"解密凭证失败: {str(e)}"}
            db.commit()
            return

        # 获取豆包适配器
        adapter_class = PLATFORM_ADAPTERS.get("doubao")
        if not adapter_class:
            logger.error("Doubao adapter not found")
            raise ValueError("平台适配器未找到")

        adapter = adapter_class("doubao", {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })

        # 调用图片生成
        prompt = request_data.get("prompt", "")
        negative_prompt = request_data.get("negative_prompt")
        style = request_data.get("style")
        size = f"{request_data.get('width', 1024)}x{request_data.get('height', 1024)}"

        logger.info(f"Generating image with doubao adapter: prompt={prompt}, size={size}")

        result = await adapter.generate_image(
            prompt=prompt,
            cookies=cookies,
            negative_prompt=negative_prompt,
            style=style,
            size=size
        )

        logger.info(f"Image generation result: {result}")

        # 处理结果
        if "error" in result:
            error_msg = result.get("error", "图片生成失败")
            logger.error(f"Image generation error: {error_msg}")
            raise ValueError(error_msg)

        images = result.get("images", [])
        logger.info(f"Generated {len(images)} images: {images}")

        if not images:
            logger.error("No images generated")
            raise ValueError("未生成任何图片")

        # 更新创作记录
        creation.status = "completed"
        creation.output_data = {"images": images}
        creation.error_message = None
        db.commit()

        logger.info(f"Image generation completed for creation {creation_id}, {len(images)} images generated")

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # 标记任务失败
        try:
            creation = db.query(Creation).filter(Creation.id == creation_id).first()
            if creation:
                creation.status = "failed"
                creation.error_message = str(e)
                creation.output_data = {"error": str(e)}
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update creation status: {db_error}")


async def process_image_variation(db: Session, creation_id: int, request_data: dict):
    """后台处理图片变体任务"""
    try:
        await asyncio.sleep(2)
        
        images = [
            f"https://example.com/variation_{uuid.uuid4().hex[:8]}.png"
            for _ in range(request_data.get("num_variations", 1))
        ]
        
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"images": images}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


async def process_image_edit(db: Session, creation_id: int, request_data: dict):
    """后台处理图片编辑任务"""
    try:
        await asyncio.sleep(2)
        
        image_url = f"https://example.com/edited_{uuid.uuid4().hex[:8]}.png"
        
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"images": [image_url]}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


async def process_image_upscale(db: Session, creation_id: int, request_data: dict):
    """后台处理图片放大任务"""
    try:
        await asyncio.sleep(2)
        
        image_url = f"https://example.com/upscaled_{uuid.uuid4().hex[:8]}.png"
        
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"images": [image_url]}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


@router.post("/generate")
async def generate_image(
    request: ImageGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """文本生成图片"""
    try:
        # 计算所需积分（每张图片100积分）
        required_credits = request.num_images * 100
        
        # 检查积分余额
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        # 生成任务ID
        task_id = f"img_{uuid.uuid4().hex[:16]}"
        
        # 创建创作记录
        creation = Creation(
            user_id=current_user.id,
            creation_type="image",
            title=f"图片生成: {request.prompt[:50]}",
            input_data={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "width": request.width,
                "height": request.height,
                "num_images": request.num_images,
                "style": request.style,
                "task_id": task_id
            },
            status="processing"
        )
        db.add(creation)
        
        # 扣除积分
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description=f"图片生成: {request.num_images}张",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        # 添加后台任务处理图片生成
        background_tasks.add_task(
            process_image_generation,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=ImageTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="图片生成任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"图片生成失败: {str(e)}")


@router.post("/variation")
async def create_image_variation(
    request: ImageVariationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建图片变体"""
    try:
        required_credits = request.num_variations * 80
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"var_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            creation_type="image",
            title="图片变体",
            input_data={
                "image": request.image,
                "num_variations": request.num_variations,
                "task_id": task_id
            },
            extra_data={"image_action": "variation"},
            status="processing"
        )
        db.add(creation)
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description=f"图片变体: {request.num_variations}张",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_image_variation,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=ImageTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="图片变体任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"图片变体失败: {str(e)}")


@router.post("/edit")
async def edit_image(
    request: ImageEditRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """编辑图片"""
    try:
        required_credits = 120
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"edit_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            creation_type="image",
            title=f"图片编辑: {request.prompt[:50]}",
            input_data={
                "image": request.image,
                "prompt": request.prompt,
                "mask": request.mask,
                "task_id": task_id
            },
            extra_data={"image_action": "edit"},
            status="processing"
        )
        db.add(creation)
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description="图片编辑",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_image_edit,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=ImageTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="图片编辑任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"图片编辑失败: {str(e)}")


@router.post("/upscale")
async def upscale_image(
    request: ImageUpscaleRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """图片放大"""
    try:
        required_credits = 50 * request.scale
        
        if current_user.credits < required_credits:
            raise HTTPException(status_code=402, detail="积分不足")
        
        task_id = f"upscale_{uuid.uuid4().hex[:16]}"
        
        creation = Creation(
            user_id=current_user.id,
            creation_type="image",
            title=f"图片放大 {request.scale}x",
            input_data={
                "image": request.image,
                "scale": request.scale,
                "task_id": task_id
            },
            extra_data={"image_action": "upscale"},
            status="processing"
        )
        db.add(creation)
        
        current_user.credits -= required_credits
        transaction = CreditTransaction(
            user_id=current_user.id,
            transaction_type=TransactionType.CONSUME,
            amount=-required_credits,
            balance_before=current_user.credits + required_credits,
            balance_after=current_user.credits,
            description=f"图片放大 {request.scale}x",
            related_id=creation.id,
            related_type="creation"
        )
        db.add(transaction)
        db.commit()
        db.refresh(creation)
        
        background_tasks.add_task(
            process_image_upscale,
            db, creation.id, request.dict()
        )
        
        return success_response(
            data=ImageTaskResponse(
                task_id=task_id,
                status="processing",
                progress=0
            ),
            message="图片放大任务已创建"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"图片放大失败: {str(e)}")


@router.get("/task/{task_id}")
async def get_image_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取图片任务状态"""
    try:
        # 从 input_data 中查找包含指定 task_id 的创作记录
        # SQLite JSON 查询需要特殊处理
        all_creations = db.query(Creation).filter(
            Creation.user_id == current_user.id,
            Creation.creation_type == "image"
        ).all()
        
        # 在内存中查找匹配的 task_id
        creation = None
        for c in all_creations:
            if c.input_data and isinstance(c.input_data, dict):
                if c.input_data.get("task_id") == task_id:
                    creation = c
                    break
        
        if not creation:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        images = None
        if creation.status == "completed" and creation.output_data:
            images = creation.output_data.get("images", [])
        
        progress = 100 if creation.status == "completed" else (
            50 if creation.status == "processing" else 0
        )
        
        return success_response(
            data=ImageTaskResponse(
                task_id=task_id,
                status=creation.status,
                images=images,
                progress=progress
            ),
            message="获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
