"""
统一模型管理服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from app.models import OAuthAccount, AIModel, Creation
from app.schemas.api_key import ModelInfo, AvailableModelsResponse


class ModelService:
    """统一模型管理服务"""
    
    @staticmethod
    def get_available_models(
        db: Session,
        user_id: int,
        scene_type: Optional[str] = None
    ) -> AvailableModelsResponse:
        """
        获取用户可用的所有模型（OAuth + API Key）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            scene_type: 场景类型（可选）
        
        Returns:
            可用模型列表
        """
        models = []
        
        # 1. 获取OAuth账号模型
        oauth_models = ModelService._get_oauth_models(db, user_id)
        models.extend(oauth_models)
        
        # 2. 获取API Key配置的模型
        api_key_models = ModelService._get_api_key_models(db, user_id)
        models.extend(api_key_models)
        
        # 3. 获取用户偏好模型（上次使用的模型）
        preferred_model_id = ModelService._get_preferred_model(db, user_id, scene_type)
        
        # 4. 标记偏好模型
        for model in models:
            if model.model_id == preferred_model_id:
                model.is_preferred = True
        
        # 5. 排序：preferred > oauth(免费) > api_key
        models.sort(key=lambda x: (
            not x.is_preferred,  # 偏好的排在前面
            not x.is_free,       # 免费的排在前面
            x.display_name       # 按名称排序
        ))
        
        return AvailableModelsResponse(
            models=models,
            total=len(models)
        )
    
    @staticmethod
    def _get_oauth_models(db: Session, user_id: int) -> List[ModelInfo]:
        """获取OAuth账号模型"""
        models = []
        
        # 查询用户的OAuth账号
        accounts = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == user_id,
                OAuthAccount.is_active == True
            )
        ).all()
        
        # 平台模型映射
        platform_models = {
            "qwen": [
                {"name": "qwen-max", "display": "通义千问-Max"},
                {"name": "qwen-plus", "display": "通义千问-Plus"},
                {"name": "qwen-turbo", "display": "通义千问-Turbo"},
            ],
            "doubao": [
                {"name": "doubao-pro", "display": "豆包-Pro"},
                {"name": "doubao-lite", "display": "豆包-Lite"},
            ],
            "zhipu": [
                {"name": "glm-4", "display": "智谱GLM-4"},
                {"name": "glm-3-turbo", "display": "智谱GLM-3-Turbo"},
            ],
            "chatgpt": [
                {"name": "gpt-4", "display": "GPT-4"},
                {"name": "gpt-3.5-turbo", "display": "GPT-3.5-Turbo"},
            ],
            "gemini": [
                {"name": "gemini-pro", "display": "Gemini-Pro"},
            ],
            "codex": [
                {"name": "claude-3-opus", "display": "Claude-3-Opus"},
                {"name": "claude-3-sonnet", "display": "Claude-3-Sonnet"},
            ],
        }
        
        for account in accounts:
            platform = account.platform
            account_models = platform_models.get(platform, [])
            
            for model_info in account_models:
                # 判断状态
                status = "active"
                if account.is_expired:
                    status = "expired"
                elif account.quota_limit and account.quota_used >= account.quota_limit:
                    status = "quota_exceeded"
                
                # 计算配额信息
                quota_info = None
                if account.quota_limit:
                    quota_info = {
                        "used": account.quota_used,
                        "total": account.quota_limit,
                        "percentage": round(account.quota_used / account.quota_limit * 100, 2)
                    }
                
                # 只添加可用的模型
                if status == "active":
                    models.append(ModelInfo(
                        model_id=f"oauth_{account.id}_{model_info['name']}",
                        model_name=model_info['name'],
                        display_name=f"{model_info['display']} ({account.account_name or platform})",
                        provider=platform,
                        source_type="oauth",
                        source_id=account.id,
                        is_free=True,
                        is_preferred=False,
                        status=status,
                        quota_info=quota_info
                    ))
        
        return models
    
    @staticmethod
    def _get_api_key_models(db: Session, user_id: int) -> List[ModelInfo]:
        """获取API Key配置的模型"""
        models = []
        
        # 查询用户的AI模型配置
        ai_models = db.query(AIModel).filter(
            and_(
                AIModel.user_id == user_id,
                AIModel.is_active == True
            )
        ).all()
        
        for ai_model in ai_models:
            models.append(ModelInfo(
                model_id=f"ai_model_{ai_model.id}",
                model_name=ai_model.model_name,
                display_name=f"{ai_model.name} ({ai_model.provider})",
                provider=ai_model.provider,
                source_type="api_key",
                source_id=ai_model.id,
                is_free=False,
                is_preferred=False,
                status="active",
                quota_info=None
            ))
        
        return models
    
    @staticmethod
    def _get_preferred_model(
        db: Session,
        user_id: int,
        scene_type: Optional[str] = None
    ) -> Optional[str]:
        """获取用户偏好的模型ID（上次使用的模型）"""
        query = db.query(Creation).filter(
            Creation.user_id == user_id
        )
        
        # 如果指定了场景类型，则筛选
        if scene_type:
            # 将scene_type映射到CreationType
            scene_mapping = {
                "writing": [
                    "wechat_article", "xiaohongshu_note", "official_document",
                    "paper", "marketing_copy", "news_article", "video_script",
                    "story", "business_plan", "work_report", "resume",
                    "lesson_plan", "rewrite", "translation"
                ],
                "image": ["image"],
                "video": ["video"],
                "ppt": ["ppt"]
            }
            
            types = scene_mapping.get(scene_type, [])
            if types:
                query = query.filter(Creation.creation_type.in_(types))
        
        # 获取最近一条记录
        latest_creation = query.order_by(Creation.created_at.desc()).first()
        
        if latest_creation and latest_creation.model_id:
            # 如果model_id是整数，转换为ai_model_格式
            if isinstance(latest_creation.model_id, int):
                return f"ai_model_{latest_creation.model_id}"
            return str(latest_creation.model_id)
        
        return None
    
    @staticmethod
    def parse_model_id(model_id: str) -> Dict[str, Any]:
        """
        解析model_id，返回来源类型和相关信息
        
        Args:
            model_id: 模型ID（oauth_{account_id}_{model_name} 或 ai_model_{model_id}）
        
        Returns:
            解析结果字典
        """
        if model_id.startswith("oauth_"):
            # OAuth模型：oauth_{account_id}_{model_name}
            parts = model_id.split("_", 2)
            if len(parts) >= 3:
                return {
                    "source_type": "oauth",
                    "account_id": int(parts[1]),
                    "model_name": parts[2]
                }
        elif model_id.startswith("ai_model_"):
            # API Key模型：ai_model_{model_id}
            parts = model_id.split("_", 2)
            if len(parts) >= 3:
                return {
                    "source_type": "api_key",
                    "model_id": int(parts[2])
                }
        
        raise ValueError(f"Invalid model_id format: {model_id}")
