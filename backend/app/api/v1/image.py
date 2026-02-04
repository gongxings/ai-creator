"""
图片生成API
"""
from typing import Optional
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.creation import Creation
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.common import success_response
from app.utils.deps import get_current_user
from pydantic import BaseModel

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
        # 模拟AI图片生成（实际应调用AI服务）
        await asyncio.sleep(2)  # 模拟处理时间
        
        # 生成模拟图片URL
        images = [
            f"https://example.com/generated_{uuid.uuid4().hex[:8]}.png"
            for _ in range(request_data.get("num_images", 1))
        ]
        
        # 更新创作记录
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"images": images}
            creation.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        # 标记任务失败
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


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
            tool_type="image_generation",
            title=f"图片生成: {request.prompt[:50]}",
            input_data={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "width": request.width,
                "height": request.height,
                "num_images": request.num_images,
                "style": request.style
            },
            status="processing",
            task_id=task_id
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
            tool_type="image_variation",
            title="图片变体",
            input_data={
                "image": request.image,
                "num_variations": request.num_variations
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
            tool_type="image_edit",
            title=f"图片编辑: {request.prompt[:50]}",
            input_data={
                "image": request.image,
                "prompt": request.prompt,
                "mask": request.mask
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
            tool_type="image_upscale",
            title=f"图片放大 {request.scale}x",
            input_data={
                "image": request.image,
                "scale": request.scale
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
        creation = db.query(Creation).filter(
            Creation.task_id == task_id,
            Creation.user_id == current_user.id
        ).first()
        
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
