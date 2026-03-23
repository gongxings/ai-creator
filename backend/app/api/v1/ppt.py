"""
PPT生成API路由
"""
import logging
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.creation import Creation
from app.models.credit import CreditTransaction, TransactionType
from app.models.user import User
from app.schemas.common import success_response
from app.services.ai.ppt_service import create_local_ppt_service
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
                credentials = decrypt_credentials(oauth_account.encrypted_credentials)
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
            # API Key模式 - 使用AI生成大纲，再用python-pptx生成PPTX
            import os
            import tempfile
            
            topic = request_data.get("topic", "")
            slides_count = request_data.get("slides_count", 10)
            style = request_data.get("style", "")
            
            # 使用AI生成PPT大纲
            outline = None
            try:
                from app.services.writing_service import WritingService
                from app.models.ai_model import AIModel
                
                # 获取用户的默认AI模型
                ai_model = db.query(AIModel).filter(
                    AIModel.user_id == user_id,
                    AIModel.is_active == True
                ).first()
                
                if ai_model:
                    service = WritingService.get_langchain_service(ai_model)
                    
                    style_hint = f"\n风格要求：{style}" if style else ""
                    prompt = f"""请帮我生成一份{slides_count}页的PPT大纲：

标题：{topic}{style_hint}

请严格按照以下格式生成每页的标题和要点：
第1页：标题页
- 主标题：{topic}
- 副标题：...

第2页：概述
- 要点1：...
- 要点2：...
- 要点3：...

第3页：...
...

注意：
1. 每页包含标题和3-5个要点
2. 逻辑清晰，循序渐进
3. 最后一页为总结和展望
"""
                    response = await service.chat(prompt)
                    outline = response.content
            except Exception as e:
                logger.warning(f"AI outline generation failed, using simple outline: {e}")
            
            # 如果AI生成失败，创建简单大纲
            if not outline:
                outline = f"第1页：标题页\n- 主标题：{topic}\n- 副标题：AI生成的演示文稿\n\n"
                for i in range(2, slides_count):
                    outline += f"第{i}页：第{i-1}部分\n- 要点1：待补充\n- 要点2：待补充\n- 要点3：待补充\n\n"
                outline += f"第{slides_count}页：总结\n- 要点1：总结回顾\n- 要点2：展望未来\n"
            
            # 使用LocalPPTService生成PPTX文件
            try:
                local_service = create_local_ppt_service()
                if local_service.available:
                    # 生成文件到临时目录
                    output_dir = os.path.join(tempfile.gettempdir(), "ai_creator_ppts")
                    os.makedirs(output_dir, exist_ok=True)
                    filename = f"ppt_{uuid.uuid4().hex[:8]}.pptx"
                    output_path = os.path.join(output_dir, filename)
                    
                    local_service.create_pptx_from_outline(
                        ppt_title=topic,
                        outline=outline,
                        output_path=output_path
                    )
                    
                    # 生成下载URL（需要配置静态文件服务）
                    ppt_url = f"/api/v1/ppt/files/{filename}"
                    
                    creation.status = "completed"
                    creation.output_content = outline
                    creation.output_data = {
                        "ppt_url": ppt_url,
                        "ppt_file_path": output_path,
                        "outline": outline,
                    }
                    db.commit()
                else:
                    # python-pptx不可用，只返回大纲
                    creation.status = "completed"
                    creation.output_content = outline
                    creation.output_data = {
                        "outline": outline,
                        "message": "python-pptx未安装，仅生成大纲"
                    }
                    db.commit()
            except Exception as e:
                logger.error(f"LocalPPTService failed: {e}")
                # 降级：返回大纲
                creation.status = "completed"
                creation.output_content = outline
                creation.output_data = {
                    "outline": outline,
                    "message": f"PPTX文件生成失败，仅返回大纲: {str(e)}"
                }
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
    import os
    
    creation = db.query(Creation).filter(
        Creation.id == ppt_id,
        Creation.user_id == current_user.id
    ).first()

    if not creation:
        raise HTTPException(status_code=404, detail="PPT不存在")

    data = creation.output_data or {}
    file_path = data.get("ppt_file_path")
    
    # 如果有实际文件，直接返回文件
    if file_path and os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=f"{creation.title or 'presentation'}.pptx"
        )
    
    # 降级：返回URL
    download_url = data.get("ppt_url")
    if download_url:
        return success_response(
            data={"download_url": download_url},
            message="success"
        )
    
    raise HTTPException(status_code=404, detail="PPT文件不存在，请重新生成")


@router.get("/templates")
async def get_ppt_templates(db: Session = Depends(get_db)):
    """获取PPT模板列表"""
    try:
        from app.models.ppt_template import PPTTemplate
        
        # 获取系统预设模板
        system_templates = db.query(PPTTemplate).filter(
            PPTTemplate.is_system == True
        ).all()
        
        templates = []
        for t in system_templates:
            templates.append({
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "style": t.style,
                "description": t.description,
                "thumbnail": t.thumbnail,
            })
        
        # 如果没有预设模板，返回默认模板
        if not templates:
            templates = [
                {"id": "default", "name": "默认模板", "category": "general", "style": "简约"},
                {"id": "business", "name": "商务模板", "category": "business", "style": "商务"},
                {"id": "simple", "name": "简约模板", "category": "general", "style": "简约"}
            ]
        
        return success_response(data=templates, message="success")
    except Exception as e:
        logger.error(f"Get templates failed: {e}")
        return success_response(data=[], message="success")


@router.get("/templates/{template_id}")
async def get_ppt_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取PPT模板详情（包含布局元数据）"""
    try:
        from app.models.ppt_template import PPTTemplate
        
        template = db.query(PPTTemplate).filter(PPTTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return success_response(
            data={
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "style": template.style,
                "description": template.description,
                "thumbnail": template.thumbnail,
                "file_path": template.file_path,
                "layout_metadata": template.layout_metadata,
            },
            message="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.post("/generate-outline")
async def generate_ppt_outline(
    request: PPTGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成PPT大纲（用于前端编辑器）
    
    返回结构化的大纲数据，前端可直接转换为PPTist格式
    扣除10积分，保存历史记录
    """
    from app.services.writing_service import WritingService
    from app.services.credit_service import CreditService
    from app.models.ai_model import AIModel
    import json
    
    topic = request.topic
    slides_count = request.slides_count or 10
    style = request.style or "business"
    language = request.language or "zh-CN"
    
    # 检查并扣减积分（会员不扣积分）
    credits_required = 10  # 每次生成需要10积分
    
    try:
        CreditService.check_and_consume_credits(
            db=db,
            user_id=current_user.id,
            amount=credits_required,
            description=f"PPT大纲生成 - {topic[:20]}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=402,
            detail=str(e),
        )
    
    # 获取用户的AI模型
    ai_model = db.query(AIModel).filter(
        AIModel.user_id == current_user.id,
        AIModel.is_active == True
    ).first()
    
    if not ai_model:
        # 退还积分
        CreditService.add_credits(
            db=db,
            user_id=current_user.id,
            amount=credits_required,
            transaction_type=TransactionType.REFUND,
            description="PPT大纲生成失败退款 - 未找到AI模型"
        )
        raise HTTPException(status_code=400, detail="未找到可用的AI模型，请先在设置中添加")
    
    # 使用WritingService的方式调用LangChain
    service = WritingService.get_langchain_service(ai_model)
    
    # 构建提示词
    style_descriptions = {
        "business": "商务专业风格，语言正式，逻辑清晰",
        "modern": "现代简约风格，内容简洁有力",
        "minimal": "极简风格，要点精炼，留白较多",
        "creative": "创意风格，语言生动，有吸引力"
    }
    style_hint = style_descriptions.get(style, "")
    
    prompt = f"""请为"{topic}"生成一份PPT大纲，共{slides_count}页。

风格要求：{style_hint}

请严格按照以下JSON格式返回，不要添加任何其他内容：

```json
{{
  "title": "PPT主标题",
  "subtitle": "PPT副标题",
  "slides": [
    {{
      "slide_type": "content",
      "title": "页面标题",
      "bullets": ["要点1", "要点2", "要点3"],
      "notes": "演讲者备注（可选）"
    }}
  ]
}}
```

要求：
1. slide_type 只能是 "title"、"content"、"section"、"ending" 中的一种
2. 第一页通常是封面（title类型），最后一页是结尾（ending类型）
3. 每页content类型要有3-5个要点
4. 可以适当添加section类型作为章节过渡
5. 总页数控制在{slides_count}页左右

请直接返回JSON，不要包含其他说明文字。"""
    
    try:
        # 调用LangChain生成大纲
        response = await service.chat(prompt)
        ai_response = response.content
        
        # 解析AI返回的JSON
        outline_data = None
        try:
            # 尝试提取JSON部分
            json_match = ai_response.strip()
            if "```json" in json_match:
                json_match = json_match.split("```json")[1].split("```")[0].strip()
            elif "```" in json_match:
                json_match = json_match.split("```")[1].split("```")[0].strip()
            
            outline_data = json.loads(json_match)
            
            # 验证数据结构
            if "title" not in outline_data:
                outline_data["title"] = topic
            if "slides" not in outline_data:
                outline_data["slides"] = []
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，创建简单的大纲
            logger.warning(f"Failed to parse AI response as JSON, creating simple outline")
            
            outline_data = {
                "title": topic,
                "subtitle": f"{style}风格演示",
                "slides": [
                    {
                        "slide_type": "content",
                        "title": f"第{i+1}部分",
                        "bullets": ["要点1", "要点2", "要点3"],
                        "notes": ""
                    }
                    for i in range(slides_count - 2)
                ]
            }
            # 添加结尾页
            outline_data["slides"].append({
                "slide_type": "ending",
                "title": "总结",
                "bullets": [],
                "notes": ""
            })
        
        # 保存历史记录
        creation = Creation(
            user_id=current_user.id,
            creation_type="ppt",
            tool_type="ppt_outline",
            title=f"PPT大纲: {topic[:50]}",
            input_data={
                "topic": topic,
                "slides_count": slides_count,
                "style": style,
                "language": language,
            },
            output_content=json.dumps(outline_data, ensure_ascii=False),
            output_data=outline_data,
            model_id=ai_model.id,
            status="completed",
        )
        db.add(creation)
        db.commit()
        db.refresh(creation)
        
        # 返回结果，包含creation_id
        outline_data["creation_id"] = creation.id
        outline_data["created_at"] = str(creation.created_at)
        
        return success_response(
            data=outline_data,
            message="大纲生成成功"
        )
        
    except HTTPException:
        # 退还积分
        CreditService.add_credits(
            db=db,
            user_id=current_user.id,
            amount=credits_required,
            transaction_type=TransactionType.REFUND,
            description="PPT大纲生成失败退款"
        )
        raise
    except Exception as e:
        logger.error(f"Generate outline failed: {e}")
        # 退还积分
        CreditService.add_credits(
            db=db,
            user_id=current_user.id,
            amount=credits_required,
            transaction_type=TransactionType.REFUND,
            description="PPT大纲生成失败退款"
        )
        raise HTTPException(status_code=500, detail=f"生成大纲失败: {str(e)}")


@router.get("/outlines")
async def get_ppt_outlines(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取PPT大纲历史记录"""
    query = db.query(Creation).filter(
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_outline"
    )
    
    total = query.count()
    creations = query.order_by(Creation.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for c in creations:
        items.append({
            "id": c.id,
            "title": c.title,
            "topic": (c.input_data or {}).get("topic", ""),
            "slides_count": (c.input_data or {}).get("slides_count", 10),
            "style": (c.input_data or {}).get("style", ""),
            "created_at": str(c.created_at),
            "status": c.status,
        })
    
    return success_response(
        data={"total": total, "items": items},
        message="success"
    )


@router.get("/outlines/{outline_id}")
async def get_ppt_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取PPT大纲详情"""
    creation = db.query(Creation).filter(
        Creation.id == outline_id,
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_outline"
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    outline_data = creation.output_data or {}
    outline_data["creation_id"] = creation.id
    outline_data["created_at"] = str(creation.created_at)
    
    return success_response(
        data=outline_data,
        message="success"
    )


@router.delete("/outlines/{outline_id}")
async def delete_ppt_outline(
    outline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除PPT大纲"""
    creation = db.query(Creation).filter(
        Creation.id == outline_id,
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_outline"
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    db.delete(creation)
    db.commit()
    
    return success_response(message="删除成功")


class EnrichSlideRequest(BaseModel):
    model_id: int
    title: str
    bullets: List[str]
    style: Optional[str] = None


@router.post("/enrich-slide")
async def enrich_slide(
    request: EnrichSlideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    使用AI丰富幻灯片内容
    
    为每个要点生成标题和详细内容
    """
    from app.services.writing_service import WritingService
    from app.models.ai_model import AIModel
    
    # 获取AI模型
    ai_model = db.query(AIModel).filter(
        AIModel.id == request.model_id,
        AIModel.user_id == current_user.id
    ).first()
    
    if not ai_model:
        raise HTTPException(status_code=400, detail="AI模型不存在")
    
    # 构建提示词
    bullets_text = "\n".join([f"- {b}" for b in request.bullets])
    style_hint = f"风格要求：{request.style}" if request.style else ""
    
    prompt = f"""请为以下PPT页面生成丰富的内容。

页面标题：{request.title}
{style_hint}

当前要点：
{bullets_text}

请为每个要点生成：
1. 一个简短的标题（5-10字）
2. 一段详细的说明文字（30-50字）

要求：
1. 标题要简洁有力，概括要点
2. 说明文字要专业、有吸引力
3. 内容要与页面主题相关

请直接返回JSON格式：
```json
{{
  "items": [
    {{"title": "要点标题1", "text": "详细说明1"}},
    {{"title": "要点标题2", "text": "详细说明2"}},
    ...
  ]
}}
```

只返回JSON，不要其他内容。"""
    
    try:
        service = WritingService.get_langchain_service(ai_model)
        response = await service.chat(prompt)
        ai_response = response.content
        
        # 解析JSON
        import json
        json_match = ai_response.strip()
        if "```json" in json_match:
            json_match = json_match.split("```json")[1].split("```")[0].strip()
        elif "```" in json_match:
            json_match = json_match.split("```")[1].split("```")[0].strip()
        
        result = json.loads(json_match)
        
        return success_response(
            data={"items": result.get("items", [])},
            message="success"
        )
    except Exception as e:
        logger.error(f"Enrich slide failed: {e}")
        # 返回原始要点
        items = [{"title": f"要点 {i+1}", "text": b} for i, b in enumerate(request.bullets)]
        return success_response(
            data={"items": items},
            message="success"
        )


class SavePPTRequest(BaseModel):
    title: str
    slides: List[dict]
    template_id: Optional[str] = None
    outline_id: Optional[int] = None


@router.post("/save")
async def save_ppt(
    request: SavePPTRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    保存PPT到数据库
    """
    import json
    
    try:
        # 创建创作记录（不使用output_content，只使用output_data）
        creation = Creation(
            user_id=current_user.id,
            creation_type="ppt",
            tool_type="ppt_editor",
            title=request.title[:200],
            input_data={
                "template_id": request.template_id,
                "outline_id": request.outline_id,
            },
            output_content=None,  # PPT数据太大，不存储到output_content
            output_data={
                "slides": request.slides,
                "template_id": request.template_id,
            },
            status="completed",
        )
        db.add(creation)
        db.commit()
        db.refresh(creation)
        
        return success_response(
            data={
                "id": creation.id,
                "title": creation.title,
                "created_at": str(creation.created_at),
            },
            message="保存成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Save PPT failed: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/saved")
async def get_saved_ppts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取已保存的PPT列表"""
    query = db.query(Creation).filter(
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_editor"
    )
    
    total = query.count()
    creations = query.order_by(Creation.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for c in creations:
        items.append({
            "id": c.id,
            "title": c.title,
            "created_at": str(c.created_at),
            "status": c.status,
        })
    
    return success_response(
        data={"total": total, "items": items},
        message="success"
    )


@router.get("/saved/{ppt_id}")
async def get_saved_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取已保存的PPT详情"""
    creation = db.query(Creation).filter(
        Creation.id == ppt_id,
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_editor"
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="PPT不存在")
    
    slides = []
    if creation.output_data and "slides" in creation.output_data:
        slides = creation.output_data["slides"]
    
    return success_response(
        data={
            "id": creation.id,
            "title": creation.title,
            "slides": slides,
            "template_id": (creation.output_data or {}).get("template_id"),
            "created_at": str(creation.created_at),
        },
        message="success"
    )


@router.delete("/saved/{ppt_id}")
async def delete_saved_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除已保存的PPT"""
    creation = db.query(Creation).filter(
        Creation.id == ppt_id,
        Creation.user_id == current_user.id,
        Creation.tool_type == "ppt_editor"
    ).first()
    
    if not creation:
        raise HTTPException(status_code=404, detail="PPT不存在")
    
    db.delete(creation)
    db.commit()
    
    return success_response(message="删除成功")
