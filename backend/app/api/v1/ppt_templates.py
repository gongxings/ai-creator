"""
PPT模板管理API
支持PPTX导入、模板管理
"""
import os
import uuid
import logging
import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.template import ContentTemplate
from app.schemas.common import success_response

logger = logging.getLogger(__name__)
router = APIRouter()

# 模板存储目录
TEMPLATE_DIR = "storage/ppt_templates"


@router.get("/ppt-templates")
async def get_ppt_templates(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取PPT模板列表
    返回系统预置模板 + 用户上传的模板
    """
    query = db.query(ContentTemplate).filter(
        ContentTemplate.platform == "ppt",
        or_(
            ContentTemplate.is_system == True,
            ContentTemplate.user_id == current_user.id
        )
    )
    
    total = query.count()
    templates = query.order_by(
        ContentTemplate.is_system.desc(),
        ContentTemplate.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    items = []
    for t in templates:
        items.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "thumbnail": t.thumbnail,
            "category": t.category,
            "style": t.style,
            "is_system": t.is_system,
            "use_count": t.use_count,
            "created_at": str(t.created_at),
        })
    
    return success_response(
        data={"total": total, "items": items},
        message="success"
    )


@router.post("/ppt-templates/upload")
async def upload_ppt_template(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    pptx_file: UploadFile = File(...),
    thumbnail: Optional[str] = Form(None),
    layout_json: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传PPTX模板
    前端使用pptxtojson解析为JSON后上传
    """
    import json
    
    try:
        # 验证文件类型
        if not pptx_file.filename.endswith('.pptx'):
            raise HTTPException(status_code=400, detail="只支持.pptx文件")
        
        # 确保存储目录存在
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        
        # 保存PPTX文件
        file_ext = '.pptx'
        file_name = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(TEMPLATE_DIR, file_name)
        
        with open(file_path, 'wb') as f:
            content = await pptx_file.read()
            f.write(content)
        
        # 解析布局JSON
        try:
            ppt_layout = json.loads(layout_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="布局JSON格式错误")
        
        # 处理缩略图
        thumbnail_path = None
        if thumbnail and thumbnail.startswith('data:image'):
            # 将base64缩略图保存为文件
            thumbnail_dir = os.path.join(TEMPLATE_DIR, "thumbnails")
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_name = f"{uuid.uuid4().hex}.png"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)
            
            # 解码base64
            thumbnail_data = thumbnail.split(',')[1] if ',' in thumbnail else thumbnail
            with open(thumbnail_path, 'wb') as f:
                f.write(base64.b64decode(thumbnail_data))
            
            thumbnail_path = f"/api/v1/ppt-templates/thumbnails/{thumbnail_name}"
        
        # 从JSON中提取主题色
        theme_colors = ppt_layout.get('themeColors', [])
        
        # 创建模板记录
        template = ContentTemplate(
            name=name[:100],
            description=description[:500] if description else None,
            platform="ppt",
            category="custom",
            style="custom",
            styles={"themeColors": theme_colors},  # 保存主题色
            file_path=file_path,
            ppt_layout=ppt_layout,  # 保存PPTist JSON
            thumbnail=thumbnail_path,
            is_system=False,
            is_public=False,
            user_id=current_user.id,
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return success_response(
            data={
                "id": template.id,
                "name": template.name,
                "thumbnail": template.thumbnail,
            },
            message="模板上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Upload PPT template failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/ppt-templates/{template_id}")
async def get_ppt_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取PPT模板详情（包含布局数据）"""
    template = db.query(ContentTemplate).filter(
        ContentTemplate.id == template_id,
        ContentTemplate.platform == "ppt",
        or_(
            ContentTemplate.is_system == True,
            ContentTemplate.user_id == current_user.id
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return success_response(
        data={
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "thumbnail": template.thumbnail,
            "category": template.category,
            "style": template.style,
            "ppt_layout": template.ppt_layout,
            "is_system": template.is_system,
            "use_count": template.use_count,
            "created_at": str(template.created_at),
        },
        message="success"
    )


@router.delete("/ppt-templates/{template_id}")
async def delete_ppt_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除PPT模板（只能删除自己上传的）"""
    template = db.query(ContentTemplate).filter(
        ContentTemplate.id == template_id,
        ContentTemplate.platform == "ppt",
        ContentTemplate.user_id == current_user.id,
        ContentTemplate.is_system == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在或无权删除")
    
    try:
        # 删除文件
        if template.file_path and os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        # 删除数据库记录
        db.delete(template)
        db.commit()
        
        return success_response(message="删除成功")
    except Exception as e:
        db.rollback()
        logger.error(f"Delete PPT template failed: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/ppt-templates/thumbnails/{filename}")
async def get_template_thumbnail(filename: str):
    """获取模板缩略图"""
    from fastapi.responses import FileResponse
    
    thumbnail_path = os.path.join(TEMPLATE_DIR, "thumbnails", filename)
    
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="缩略图不存在")
    
    return FileResponse(thumbnail_path, media_type="image/png")
