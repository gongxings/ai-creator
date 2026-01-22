"""
写作服务
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.creation import Creation
from app.models.user import User
from app.services.ai.factory import AIServiceFactory
from app.services.writing.prompts import WRITING_PROMPTS, TOOL_CONFIGS
import json


class WritingService:
    """写作服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_factory = AIServiceFactory()
    
    async def generate_content(
        self,
        user: User,
        tool_type: str,
        params: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None
    ) -> Creation:
        """
        生成写作内容
        
        Args:
            user: 用户对象
            tool_type: 工具类型
            params: 生成参数
            model_config: AI模型配置
            
        Returns:
            Creation: 创作记录
        """
        # 验证工具类型
        if tool_type not in WRITING_PROMPTS:
            raise ValueError(f"不支持的工具类型: {tool_type}")
        
        # 获取提示词模板
        prompt_template = WRITING_PROMPTS[tool_type]
        
        # 填充提示词参数
        try:
            prompt = prompt_template.format(**params)
        except KeyError as e:
            raise ValueError(f"缺少必需参数: {e}")
        
        # 获取AI服务
        ai_service = self.ai_factory.get_service(
            provider=model_config.get("provider", "openai") if model_config else "openai",
            config=model_config
        )
        
        # 调用AI生成内容
        content = await ai_service.generate_text(
            prompt=prompt,
            max_tokens=model_config.get("max_tokens", 2000) if model_config else 2000,
            temperature=model_config.get("temperature", 0.7) if model_config else 0.7
        )
        
        # 创建创作记录
        creation = Creation(
            user_id=user.id,
            tool_type=tool_type,
            title=self._extract_title(content, tool_type),
            content=content,
            params=json.dumps(params, ensure_ascii=False),
            model_config=json.dumps(model_config, ensure_ascii=False) if model_config else None,
            status="completed"
        )
        
        self.db.add(creation)
        self.db.commit()
        self.db.refresh(creation)
        
        return creation
    
    async def regenerate_content(
        self,
        creation: Creation,
        params: Optional[Dict[str, Any]] = None
    ) -> Creation:
        """
        重新生成内容
        
        Args:
            creation: 原创作记录
            params: 新的生成参数（可选）
            
        Returns:
            Creation: 新的创作记录
        """
        # 使用新参数或原参数
        generation_params = params if params else json.loads(creation.params)
        model_config = json.loads(creation.model_config) if creation.model_config else None
        
        # 获取用户
        user = self.db.query(User).filter(User.id == creation.user_id).first()
        
        # 生成新内容
        new_creation = await self.generate_content(
            user=user,
            tool_type=creation.tool_type,
            params=generation_params,
            model_config=model_config
        )
        
        # 设置版本关系
        new_creation.parent_id = creation.id
        new_creation.version = creation.version + 1
        
        self.db.commit()
        self.db.refresh(new_creation)
        
        return new_creation
    
    async def optimize_content(
        self,
        creation: Creation,
        optimization_type: str = "general"
    ) -> Creation:
        """
        优化内容
        
        Args:
            creation: 创作记录
            optimization_type: 优化类型（general/seo/readability）
            
        Returns:
            Creation: 优化后的创作记录
        """
        # 构建优化提示词
        optimization_prompts = {
            "general": "请优化以下内容，使其更加流畅、生动、有吸引力：\n\n{content}",
            "seo": "请从SEO角度优化以下内容，提升关键词密度和搜索排名：\n\n{content}",
            "readability": "请优化以下内容的可读性，使其更易理解、结构更清晰：\n\n{content}"
        }
        
        prompt = optimization_prompts.get(optimization_type, optimization_prompts["general"])
        prompt = prompt.format(content=creation.content)
        
        # 获取AI服务
        model_config = json.loads(creation.model_config) if creation.model_config else None
        ai_service = self.ai_factory.get_service(
            provider=model_config.get("provider", "openai") if model_config else "openai",
            config=model_config
        )
        
        # 生成优化内容
        optimized_content = await ai_service.generate_text(
            prompt=prompt,
            max_tokens=model_config.get("max_tokens", 2000) if model_config else 2000,
            temperature=0.7
        )
        
        # 创建新版本
        new_creation = Creation(
            user_id=creation.user_id,
            tool_type=creation.tool_type,
            title=creation.title,
            content=optimized_content,
            params=creation.params,
            model_config=creation.model_config,
            parent_id=creation.id,
            version=creation.version + 1,
            status="completed"
        )
        
        self.db.add(new_creation)
        self.db.commit()
        self.db.refresh(new_creation)
        
        return new_creation
    
    def get_tool_config(self, tool_type: str) -> Dict[str, Any]:
        """
        获取工具配置
        
        Args:
            tool_type: 工具类型
            
        Returns:
            Dict: 工具配置信息
        """
        if tool_type not in TOOL_CONFIGS:
            raise ValueError(f"不支持的工具类型: {tool_type}")
        
        return TOOL_CONFIGS[tool_type]
    
    def get_all_tools(self) -> list:
        """
        获取所有写作工具列表
        
        Returns:
            list: 工具列表
        """
        return [
            {
                "type": tool_type,
                **config
            }
            for tool_type, config in TOOL_CONFIGS.items()
        ]
    
    def _extract_title(self, content: str, tool_type: str) -> str:
        """
        从内容中提取标题
        
        Args:
            content: 生成的内容
            tool_type: 工具类型
            
        Returns:
            str: 标题
        """
        # 尝试提取第一行作为标题
        lines = content.strip().split('\n')
        if lines:
            title = lines[0].strip()
            # 移除markdown标题标记
            title = title.lstrip('#').strip()
            # 限制标题长度
            if len(title) > 100:
                title = title[:100] + "..."
            return title if title else f"{TOOL_CONFIGS[tool_type]['name']}作品"
        
        return f"{TOOL_CONFIGS[tool_type]['name']}作品"
