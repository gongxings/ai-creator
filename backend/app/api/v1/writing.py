"""
AI写作相关API路由
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.creation import Creation
from app.models.creation_version import CreationVersion
from app.schemas.writing import (
    WritingToolInfo,
    WritingGenerateRequest,
    WritingGenerateResponse,
    CreationResponse,
    CreationListResponse,
)
from app.services.writing_service import WritingService
from app.services.credit_service import CreditService

router = APIRouter()


@router.get("/tools", response_model=List[WritingToolInfo])
def get_writing_tools() -> Any:
    """
    获取所有写作工具列表
    """
    tools = [
        {
            "id": "wechat_article",
            "name": "公众号文章",
            "description": "创作适合微信公众号的文章，自动优化排版和SEO",
            "icon": "📱",
            "category": "social_media",
        },
        {
            "id": "xiaohongshu_note",
            "name": "小红书笔记",
            "description": "创作吸引人的小红书笔记，包含标题、正文和标签",
            "icon": "📔",
            "category": "social_media",
        },
        {
            "id": "official_document",
            "name": "公文写作",
            "description": "撰写规范的公文，包括通知、报告、函等",
            "icon": "📄",
            "category": "professional",
        },
        {
            "id": "academic_paper",
            "name": "论文写作",
            "description": "撰写学术论文，包含摘要、正文、参考文献",
            "icon": "🎓",
            "category": "academic",
        },
        {
            "id": "marketing_copy",
            "name": "营销文案",
            "description": "创作吸引人的营销文案，提升转化率",
            "icon": "💰",
            "category": "marketing",
        },
        {
            "id": "press_release",
            "name": "新闻稿/软文",
            "description": "撰写专业的新闻稿或软文",
            "icon": "📰",
            "category": "media",
        },
        {
            "id": "video_script",
            "name": "短视频脚本",
            "description": "创作短视频脚本，包含场景、台词、镜头",
            "icon": "🎬",
            "category": "media",
        },
        {
            "id": "story_novel",
            "name": "故事/小说",
            "description": "创作引人入胜的故事或小说",
            "icon": "📖",
            "category": "creative",
        },
        {
            "id": "business_plan",
            "name": "商业计划书",
            "description": "撰写完整的商业计划书",
            "icon": "💼",
            "category": "business",
        },
        {
            "id": "work_report",
            "name": "工作报告",
            "description": "撰写工作总结、述职报告等",
            "icon": "📊",
            "category": "professional",
        },
        {
            "id": "resume_cover_letter",
            "name": "简历/求职信",
            "description": "创作专业的简历和求职信",
            "icon": "👔",
            "category": "career",
        },
        {
            "id": "lesson_plan",
            "name": "教案/课件",
            "description": "制作教学教案和课件内容",
            "icon": "👨‍🏫",
            "category": "education",
        },
        {
            "id": "content_rewrite",
            "name": "内容改写/扩写/缩写",
            "description": "对现有内容进行改写、扩写或缩写",
            "icon": "✏️",
            "category": "editing",
        },
        {
            "id": "translation",
            "name": "多语言翻译",
            "description": "将内容翻译成多种语言",
            "icon": "🌐",
            "category": "language",
        },
    ]
    return tools


@router.post("/generate", response_model=WritingGenerateResponse)
async def generate_content(
    request: WritingGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    生成AI写作内容
    """
    # 检查并扣减积分（会员不扣积分）
    credit_service = CreditService(db)
    credits_required = 10  # 每次生成需要10积分
    
    try:
        await credit_service.check_and_consume_credits(
            user_id=current_user.id,
            credits=credits_required,
            description=f"AI写作 - {request.tool_type}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e),
        )
    
    # 创建写作服务实例
    writing_service = WritingService(db)
    
    try:
        # 生成内容
        result = await writing_service.generate_content(
            user_id=current_user.id,
            tool_type=request.tool_type,
            input_data=request.input_data,
            ai_model_id=request.ai_model_id,
        )
        
        return result
        
    except Exception as e:
        # 生成失败，退还积分
        if not current_user.is_member:
            await credit_service.add_credits(
                user_id=current_user.id,
                credits=credits_required,
                transaction_type="REFUND",
                description=f"AI写作失败退款 - {request.tool_type}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成内容失败: {str(e)}",
        )


@router.get("/creations", response_model=CreationListResponse)
def get_creations(
    skip: int = 0,
    limit: int = 20,
    tool_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取创作列表
    """
    query = db.query(Creation).filter(Creation.user_id == current_user.id)
    
    if tool_type:
        query = query.filter(Creation.tool_type == tool_type)
    
    total = query.count()
    creations = query.order_by(Creation.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": creations,
    }


@router.get("/creations/{creation_id}", response_model=CreationResponse)
def get_creation(
    creation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取创作详情
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在",
        )
    
    return creation


@router.put("/creations/{creation_id}", response_model=CreationResponse)
def update_creation(
    creation_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    更新创作内容
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在",
        )
    
    # 保存版本历史
    if content and content != creation.content:
        version = CreationVersion(
            creation_id=creation.id,
            version_number=creation.version + 1,
            content=creation.content,
            metadata=creation.metadata,
        )
        db.add(version)
        creation.version += 1
    
    # 更新内容
    if title:
        creation.title = title
    if content:
        creation.content = content
    
    db.commit()
    db.refresh(creation)
    
    return creation


@router.delete("/creations/{creation_id}")
def delete_creation(
    creation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    删除创作
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在",
        )
    
    db.delete(creation)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/creations/{creation_id}/versions")
def get_creation_versions(
    creation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取创作版本历史
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在",
        )
    
    versions = db.query(CreationVersion).filter(
        CreationVersion.creation_id == creation_id
    ).order_by(CreationVersion.version_number.desc()).all()
    
    return versions


@router.post("/creations/{creation_id}/regenerate", response_model=WritingGenerateResponse)
async def regenerate_content(
    creation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    重新生成内容
    """
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
    ).first()
    
    if not creation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="创作不存在",
        )
    
    # 检查并扣减积分（会员不扣积分）
    credit_service = CreditService(db)
    credits_required = 10  # 每次生成需要10积分
    
    try:
        await credit_service.check_and_consume_credits(
            user_id=current_user.id,
            credits=credits_required,
            description=f"AI写作重新生成 - {creation.tool_type}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e),
        )
    
    writing_service = WritingService(db)
    
    try:
        # 使用原始输入数据重新生成
        result = await writing_service.generate_content(
            user_id=current_user.id,
            tool_type=creation.tool_type,
            input_data=creation.metadata.get("input_data", {}),
            ai_model_id=creation.ai_model_id,
        )
        
        return result
        
    except Exception as e:
        # 生成失败，退还积分
        if not current_user.is_member:
            await credit_service.add_credits(
                user_id=current_user.id,
                credits=credits_required,
                transaction_type="REFUND",
                description=f"AI写作重新生成失败退款 - {creation.tool_type}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新生成失败: {str(e)}",
        )
