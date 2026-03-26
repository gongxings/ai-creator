"""
图片生成API
"""
import os
import base64
import uuid
import asyncio
from datetime import datetime
from typing import Optional
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

# 图片存储目录
IMAGE_STORAGE_DIR = "uploads/images"


def save_image_from_url_or_base64(image_data: str, filename: str = None) -> str:
    """
    保存图片到本地存储，返回保存后的URL
    
    Args:
        image_data: 图片URL或base64数据
        filename: 可选的文件名
    
    Returns:
        保存后的URL路径
    """
    os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:12]
    if not filename:
        filename = f"image_{unique_id}.png"
    else:
        # 清理文件名
        filename = f"{unique_id}_{filename.replace('/', '_').replace('\\', '_')}"
    
    filepath = os.path.join(IMAGE_STORAGE_DIR, filename)
    
    if image_data.startswith("data:"):
        # base64 数据
        header, b64data = image_data.split(",", 1)
        # 提取 mime 类型
        mime = header.replace("data:", "").replace(";base64", "")
        ext = "png" if "png" in mime else "jpg"
        filepath = filepath.replace(".png", f".{ext}") if ".png" in filepath else filepath
        filepath = filepath.replace(".jpg", f".{ext}") if ".jpg" in filepath else filepath
        
        img_data = base64.b64decode(b64data)
        with open(filepath, "wb") as f:
            f.write(img_data)
    elif image_data.startswith("http"):
        # URL 下载
        import httpx
        try:
            response = httpx.get(image_data, timeout=30.0)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            raise ValueError(f"下载图片失败: {e}")
    else:
        # 纯base64
        img_data = base64.b64decode(image_data)
        with open(filepath, "wb") as f:
            f.write(img_data)
    
    # 返回相对URL
    return f"/uploads/images/{os.path.basename(filepath)}"


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
async def process_image_generation(db: Session, creation_id: int, request_data: dict, user_id: int):
    """后台处理图片生成任务 - 只使用 AIModel"""
    try:
        logger.info(f"Starting image generation for creation {creation_id}")

        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if not creation:
            logger.error(f"Creation {creation_id} not found")
            return

        logger.info(f"Creation found: user_id={creation.user_id}, status={creation.status}")

        # 使用用户配置的 AIModel
        logger.info("Using AIModel for image generation")
        
        from app.models.ai_model import AIModel
        from app.services.langchain.image.factory import ImageGeneratorFactory

        # 查询用户启用的、具备图片生成能力的 AIModel
        ai_model = db.query(AIModel).filter(
            AIModel.user_id == user_id,
            AIModel.is_active == True,
            AIModel.capabilities.contains(["image"])
        ).first()

        if not ai_model:
            logger.error("No active AI model with image capability found")
            raise ValueError("请先配置支持图片生成的AI模型")

        logger.info(f"Using AI model: {ai_model.name}, provider: {ai_model.provider}, model: {ai_model.model_name}")

        # 构建请求参数
        prompt = request_data.get("prompt", "")
        negative_prompt = request_data.get("negative_prompt")
        style = request_data.get("style")
        size = f"{request_data.get('width', 1024)}x{request_data.get('height', 1024)}"

        logger.info(f"Generating image with AIModel: prompt={prompt}, size={size}, provider={ai_model.provider}")

        try:
            # 使用 ImageGeneratorFactory 创建图片生成器
            generator = ImageGeneratorFactory.create(
                provider=ai_model.provider,
                api_key=ai_model.api_key,
                model=ai_model.model_name,
                api_base=ai_model.base_url,
            )

            # 生成图片
            result = await generator.generate(
                prompt=prompt,
                size=size,
                negative_prompt=negative_prompt,
                style=style,
            )

            logger.info(f"Image generation result: success={result.success}")

            if not result.success:
                error_msg = result.error or "图片生成失败"
                logger.error(f"Image generation error: {error_msg}")
                raise ValueError(error_msg)

            images = result.images or []
            if not images:
                logger.error("No images generated")
                raise ValueError("未生成任何图片")

            # 保存图片到本地存储
            saved_images = []
            for i, img_data in enumerate(images):
                try:
                    saved_url = save_image_from_url_or_base64(img_data, f"generated_{i}")
                    saved_images.append(saved_url)
                    logger.info(f"图片已保存: {saved_url}")
                except Exception as e:
                    logger.error(f"保存第 {i+1} 张图片失败: {e}")
                    # 即使保存失败，也保留原始数据
                    saved_images.append(img_data)

            creation.status = "completed"
            creation.output_data = {"images": saved_images}
            creation.error_message = None
            db.commit()

            logger.info(f"Image generation completed for creation {creation_id}, {len(images)} images generated")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"图片生成失败: {str(e)}")

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
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
    """文本生成图片 - 使用用户配置的AIModel"""
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
                "task_id": task_id,
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
            db, creation.id, request.model_dump(), current_user.id
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
