"""
PPT生成API路由
"""
from typing import Optional, List
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.creation import Creation
from app.schemas.common import success_response
from app.utils.deps import get_current_user

router = APIRouter()


class PPTGenerateRequest(BaseModel):
    topic: str
    slides_count: Optional[int] = 10
    style: Optional[str] = None
    language: Optional[str] = None


class PPTFromOutlineRequest(BaseModel):
    outline: str
    style: Optional[str] = None


class PPTTaskResponse(BaseModel):
    task_id: str
    status: str
    ppt_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    progress: Optional[int] = None


async def process_ppt_generation(db: Session, creation_id: int, request_data: dict):
    """后台处理PPT生成任务"""
    try:
        await asyncio.sleep(2)
        ppt_url = f"https://example.com/ppt_{uuid.uuid4().hex[:8]}.pptx"
        preview_images = [
            f"https://example.com/ppt_preview_{uuid.uuid4().hex[:8]}.png"
            for _ in range(3)
        ]
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "completed"
            creation.output_data = {"ppt_url": ppt_url, "preview_images": preview_images}
            db.commit()
    except Exception as e:
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.output_data = {"error": str(e)}
            db.commit()


@router.post("/generate")
async def generate_ppt(
    request: PPTGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """主题生成PPT"""
    try:
        task_id = f"ppt_{uuid.uuid4().hex[:16]}"
        creation = Creation(
            user_id=current_user.id,
            tool_type="ppt_generate",
            title=f"PPT: {request.topic[:50]}",
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
