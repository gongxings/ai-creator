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
    返回所有PPT类型的模板（系统+用户上传）
    注意：不返回ppt_layout大字段，只返回基本信息
    """
    from sqlalchemy import select
    
    # 只查询需要的字段，避免加载ppt_layout大字段
    query = select(
        ContentTemplate.id,
        ContentTemplate.name,
        ContentTemplate.description,
        ContentTemplate.thumbnail,
        ContentTemplate.category,
        ContentTemplate.style,
        ContentTemplate.is_system,
        ContentTemplate.user_id,
        ContentTemplate.use_count,
        ContentTemplate.created_at,
    ).filter(
        ContentTemplate.platform == "ppt"
    ).order_by(
        ContentTemplate.is_system.desc(),
        ContentTemplate.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = db.execute(query)
    templates = result.all()
    
    # 获取总数
    from sqlalchemy import func
    total = db.query(func.count(ContentTemplate.id)).filter(
        ContentTemplate.platform == "ppt"
    ).scalar()
    
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
            "user_id": t.user_id,
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
    layout_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传PPTX模板
    前端使用pptxtojson解析为JSON后上传
    JSON存储为文件，数据库只存储基本信息
    """
    import json
    
    try:
        # 验证文件类型
        if not pptx_file.filename.endswith('.pptx'):
            raise HTTPException(status_code=400, detail="只支持.pptx文件")
        
        logger.info(f"收到PPT模板上传请求: name={name}, filename={pptx_file.filename}")
        
        # 确保存储目录存在
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        
        # 生成唯一文件名
        unique_id = uuid.uuid4().hex
        
        # 保存PPTX文件
        pptx_filename = f"{unique_id}.pptx"
        pptx_path = os.path.join(TEMPLATE_DIR, pptx_filename)
        
        with open(pptx_path, 'wb') as f:
            content = await pptx_file.read()
            f.write(content)
        
        # 保存布局JSON为文件（而不是存数据库）
        layout_content = await layout_file.read()
        logger.info(f"layout_file大小: {len(layout_content)} bytes")
        
        # 验证JSON格式
        try:
            ppt_layout = json.loads(layout_content.decode('utf-8'))
            logger.info(f"JSON解析成功，slides数量: {len(ppt_layout.get('slides', []))}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise HTTPException(status_code=400, detail=f"布局JSON格式错误: {str(e)}")
        
        # 保存JSON文件
        layout_filename = f"{unique_id}.json"
        layout_path = os.path.join(TEMPLATE_DIR, layout_filename)
        
        with open(layout_path, 'w', encoding='utf-8') as f:
            json.dump(ppt_layout, f, ensure_ascii=False)
        
        # 处理缩略图
        thumbnail_path = None
        if thumbnail and thumbnail.startswith('data:image'):
            # 将base64缩略图保存为文件
            thumbnail_dir = os.path.join(TEMPLATE_DIR, "thumbnails")
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_name = f"{unique_id}.png"
            thumbnail_file_path = os.path.join(thumbnail_dir, thumbnail_name)
            
            # 解码base64
            thumbnail_data = thumbnail.split(',')[1] if ',' in thumbnail else thumbnail
            with open(thumbnail_file_path, 'wb') as f:
                f.write(base64.b64decode(thumbnail_data))
            
            thumbnail_path = f"/api/v1/ppt-templates/thumbnails/{thumbnail_name}"
        
        # 从JSON中提取主题色
        theme_colors = ppt_layout.get('themeColors', [])
        
        # 创建模板记录（不存储ppt_layout大字段，只存储文件路径）
        template = ContentTemplate(
            name=name[:100],
            description=description[:500] if description else None,
            platform="ppt",
            category="custom",
            style="custom",
            styles={"themeColors": theme_colors},  # 保存主题色
            file_path=pptx_path,  # PPTX文件路径
            ppt_layout={"layout_file": layout_path},  # 只存储JSON文件路径，不存储完整内容
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


def convert_ppt_layout_to_pptist_format(ppt_layout: dict) -> dict:
    """将pptxtojson生成的布局转换为PPTist兼容格式（简化版：只添加顶层字段）"""
    import uuid
    
    if not ppt_layout:
        return ppt_layout
    
    slides = ppt_layout.get('slides', [])
    if not slides:
        return ppt_layout
    
    # 获取尺寸
    size = ppt_layout.get('size', {})
    width = size.get('width', 960) if size else 960
    height = size.get('height', 540) if size else 540
    
    # 获取主题色
    theme_colors = ppt_layout.get('themeColors', [])
    
    # 构建theme对象
    theme = {
        "themeColors": theme_colors if theme_colors else ["#1677ff"],
        "fontColor": "#333333",
        "fontName": "Microsoft YaHei",
        "backgroundColor": "#ffffff",
        "shadow": {"h": 3, "v": 3, "blur": 2, "color": "#808080"},
        "outline": {"width": 2, "color": "#525252", "style": "solid"}
    }
    
    # 简单处理：为每个slide和element添加ID
    converted_slides = []
    for slide in slides:
        slide_id = slide.get('id') or f"slide_{uuid.uuid4().hex[:8]}"
        
        # 处理elements
        elements = slide.get('elements', [])
        converted_elements = []
        
        for el in elements:
            el_id = el.get('id') or f"el_{uuid.uuid4().hex[:8]}"
            
            # 复制原始element，添加必要字段
            converted_el = dict(el)
            converted_el["id"] = el_id
            
            # 确保shape有fill
            if el.get('type') == 'shape':
                if 'fill' not in converted_el:
                    converted_el["fill"] = "#cccccc"
                if 'viewBox' not in converted_el:
                    converted_el["viewBox"] = [200, 200]
                if 'path' not in converted_el:
                    converted_el["path"] = "M 0 0 L 200 0 L 200 200 L 0 200 Z"
                if 'fixedRatio' not in converted_el:
                    converted_el["fixedRatio"] = False
            
            converted_elements.append(converted_el)
        
        converted_slide = dict(slide)
        converted_slide["id"] = slide_id
        converted_slide["elements"] = converted_elements
        
        converted_slides.append(converted_slide)
    
    # 返回添加了顶层字段的格式
    return {
        "title": ppt_layout.get('title', '未命名演示文稿'),
        "width": width,
        "height": height,
        "theme": theme,
        "slides": converted_slides
    }


@router.get("/ppt-templates/{template_id}")
async def get_ppt_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取PPT模板详情（包含布局数据）"""
    import json
    
    template = db.query(ContentTemplate).filter(
        ContentTemplate.id == template_id,
        ContentTemplate.platform == "ppt"
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 从文件读取布局数据
    ppt_layout = None
    if template.ppt_layout:
        logger.info(f"ppt_layout类型: {type(template.ppt_layout)}")
        
        # 检查是否是文件路径格式
        if isinstance(template.ppt_layout, dict) and "layout_file" in template.ppt_layout:
            layout_file_path = template.ppt_layout["layout_file"]
            logger.info(f"从文件读取布局数据: {layout_file_path}")
            if os.path.exists(layout_file_path):
                try:
                    with open(layout_file_path, 'r', encoding='utf-8') as f:
                        ppt_layout = json.load(f)
                    logger.info(f"成功读取布局文件，slides数量: {len(ppt_layout.get('slides', []))}")
                except Exception as e:
                    logger.error(f"读取布局文件失败: {e}")
            else:
                logger.error(f"布局文件不存在: {layout_file_path}")
        else:
            # 兼容旧格式：直接存储在数据库中
            logger.info("使用数据库中直接存储的布局数据")
            ppt_layout = template.ppt_layout
    
    # 转换布局格式为PPTist兼容格式（仅对旧模板生效，新模板已由前端转换好）
    if ppt_layout and "theme" not in ppt_layout:
        ppt_layout = convert_ppt_layout_to_pptist_format(ppt_layout)
    
    logger.info(f"返回ppt_layout: {ppt_layout is not None}, slides: {len(ppt_layout.get('slides', [])) if ppt_layout else 0}")
    
    return success_response(
        data={
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "thumbnail": template.thumbnail,
            "category": template.category,
            "style": template.style,
            "ppt_layout": ppt_layout,
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
    """删除PPT模板（只能删除自己上传的，不能删除系统预置模板）"""
    template = db.query(ContentTemplate).filter(
        ContentTemplate.id == template_id,
        ContentTemplate.platform == "ppt",
        ContentTemplate.is_system == False,
        ContentTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在或无权删除")
    
    try:
        # 删除PPTX文件
        if template.file_path and os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        # 删除布局JSON文件
        if template.ppt_layout and isinstance(template.ppt_layout, dict):
            layout_file = template.ppt_layout.get("layout_file")
            if layout_file and os.path.exists(layout_file):
                os.remove(layout_file)
        
        # 删除缩略图文件
        if template.thumbnail:
            thumbnail_path = None
            if template.thumbnail.startswith('/api/v1/ppt-templates/thumbnails/'):
                thumbnail_filename = template.thumbnail.split('/')[-1]
                thumbnail_path = os.path.join(TEMPLATE_DIR, "thumbnails", thumbnail_filename)
            elif os.path.isabs(template.thumbnail):
                thumbnail_path = template.thumbnail
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
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
