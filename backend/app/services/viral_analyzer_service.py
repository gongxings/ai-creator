"""
爆款模仿服务
分析爆款文章风格并生成类似内容
"""
import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas.viral_analyzer import (
    ContentCategory,
    ViralElement,
    StructureAnalysis,
    AnalyzeRequest,
    AnalyzeResponse,
    ImitateRequest,
    ImitateResponse,
)
from app.models.creation import Creation, CreationType, CreationStatus

logger = logging.getLogger(__name__)


class ViralAnalyzerService:
    """爆款模仿服务"""
    
    # 爆款元素定义
    VIRAL_ELEMENTS = {
        "hook": "开头钩子 - 前3秒/前3句抓住注意力",
        "emotion": "情感共鸣 - 引发读者情感认同",
        "story": "故事性 - 用故事承载观点",
        "conflict": "冲突感 - 制造认知冲突或戏剧冲突",
        "value": "价值感 - 提供实用价值或信息增量",
        "social_proof": "社会认同 - 权威背书、数据支撑",
        "scarcity": "稀缺性 - 独家、限时、少有人知",
        "curiosity": "好奇心 - 悬念、未知、反常识",
        "identity": "身份认同 - 让读者觉得「说的就是我」",
        "cta": "行动召唤 - 引导互动、转发、关注",
    }
    
    @classmethod
    async def analyze(
        cls,
        request: AnalyzeRequest,
        ai_model=None,
    ) -> AnalyzeResponse:
        """
        分析爆款内容
        
        Args:
            request: 分析请求
            ai_model: AI模型配置
            
        Returns:
            AnalyzeResponse
        """
        prompt = cls._build_analyze_prompt(
            content=request.content,
            title=request.title,
            platform=request.platform,
        )
        
        from app.services.langchain import LangChainService
        
        try:
            if ai_model:
                service = LangChainService(
                    provider=ai_model.provider,
                    model=ai_model.model_name or "gpt-4",
                    api_key=ai_model.api_key,
                    api_base=ai_model.base_url,
                )
            else:
                service = LangChainService(
                    provider="openai",
                    model="gpt-3.5-turbo",
                )
            
            response = await service.chat(prompt)
            return cls._parse_analyze_response(response.content, request.title or "")
            
        except Exception as e:
            logger.error(f"爆款分析失败: {e}")
            raise Exception(f"爆款分析失败: {str(e)}")
    
    @classmethod
    async def imitate(
        cls,
        request: ImitateRequest,
        db: Session,
        user_id: int,
        ai_model=None,
    ) -> ImitateResponse:
        """
        模仿爆款生成内容
        
        Args:
            request: 模仿请求
            db: 数据库会话
            user_id: 用户ID
            ai_model: AI模型配置
            
        Returns:
            ImitateResponse
        """
        prompt = cls._build_imitate_prompt(
            reference_content=request.reference_content,
            reference_title=request.reference_title,
            new_topic=request.new_topic,
            platform=request.platform,
            style_strength=request.style_strength,
            keep_structure=request.keep_structure,
            additional_requirements=request.additional_requirements,
        )
        
        from app.services.langchain import LangChainService
        
        try:
            if ai_model:
                service = LangChainService(
                    provider=ai_model.provider,
                    model=ai_model.model_name or "gpt-4",
                    api_key=ai_model.api_key,
                    api_base=ai_model.base_url,
                )
            else:
                service = LangChainService(
                    provider="openai",
                    model="gpt-3.5-turbo",
                )
            
            response = await service.chat(prompt)
            result = cls._parse_imitate_response(response.content)
            
            # 保存为新的创作记录
            new_creation = Creation(
                user_id=user_id,
                creation_type=CreationType.WECHAT_ARTICLE,
                tool_type="viral_imitate",
                title=result.title,
                input_data={
                    "reference_title": request.reference_title,
                    "new_topic": request.new_topic,
                    "platform": request.platform,
                    "style_strength": request.style_strength,
                },
                output_content=result.content,
                status=CreationStatus.COMPLETED,
            )
            db.add(new_creation)
            db.commit()
            db.refresh(new_creation)
            
            result.creation_id = new_creation.id
            return result
            
        except Exception as e:
            logger.error(f"爆款模仿失败: {e}")
            raise Exception(f"爆款模仿失败: {str(e)}")
    
    @classmethod
    def _build_analyze_prompt(
        cls,
        content: str,
        title: Optional[str],
        platform: Optional[str],
    ) -> str:
        """构建分析提示词"""
        
        title_text = f"标题：{title}" if title else "（无标题）"
        platform_text = f"来源平台：{platform}" if platform else ""
        
        elements_desc = "\n".join([f"- {k}: {v}" for k, v in cls.VIRAL_ELEMENTS.items()])
        
        return f"""你是一位资深的爆款内容分析专家，擅长拆解爆款文章的成功要素。

## 任务
深度分析以下内容的爆款元素和写作技巧。

## 待分析内容
{title_text}
{platform_text}

正文：
{content}

## 分析维度

### 1. 爆款元素（每个元素0-100分）
{elements_desc}

### 2. 内容类别
- emotion: 情感共鸣类
- knowledge: 知识干货类
- story: 故事叙事类
- news: 新闻热点类
- tutorial: 教程攻略类
- review: 测评种草类
- opinion: 观点输出类

### 3. 结构分析
- 段落结构
- 开头钩子手法
- 结尾行动召唤
- 过渡风格

## 输出格式
严格按照以下JSON格式输出：
```json
{{
  "title": "文章标题",
  "category": "emotion|knowledge|story|news|tutorial|review|opinion",
  "viral_score": 85,
  "tone": "语气风格描述",
  "target_audience": "目标受众描述",
  "emotional_triggers": ["情感触发点1", "情感触发点2"],
  "viral_elements": [
    {{
      "name": "元素名称",
      "description": "运用说明",
      "score": 90,
      "examples": ["文中示例1"]
    }}
  ],
  "structure": {{
    "sections": ["第一段：xxx", "第二段：xxx"],
    "opening_hook": "开头钩子分析",
    "closing_cta": "结尾CTA分析",
    "transition_style": "过渡风格"
  }},
  "writing_techniques": ["技巧1", "技巧2"],
  "keywords": ["关键词1", "关键词2"],
  "improvement_suggestions": ["改进建议1"]
}}
```"""
    
    @classmethod
    def _build_imitate_prompt(
        cls,
        reference_content: str,
        reference_title: Optional[str],
        new_topic: str,
        platform: Optional[str],
        style_strength: int,
        keep_structure: bool,
        additional_requirements: Optional[str],
    ) -> str:
        """构建模仿提示词"""
        
        title_text = f"参考标题：{reference_title}" if reference_title else ""
        platform_text = f"目标平台：{platform}" if platform else ""
        structure_text = "严格保持与参考文章相同的段落结构和节奏" if keep_structure else "可以调整结构，但保持相似的风格"
        requirements_text = f"额外要求：{additional_requirements}" if additional_requirements else ""
        
        return f"""你是一位资深的爆款内容创作专家，擅长分析和模仿成功的写作风格。

## 任务
参考以下爆款文章的风格，围绕新主题创作类似风格的内容。

## 参考爆款文章
{title_text}

{reference_content}

## 新主题
{new_topic}

## 创作要求
1. 风格模仿强度：{style_strength}%（100%完全模仿，0%完全原创）
2. {structure_text}
3. 保留参考文章的：
   - 语气风格和用词习惯
   - 情感节奏和表达方式
   - 爆款元素的运用手法
   - 开头钩子和结尾CTA的风格
4. 用新主题替换原有的具体内容
{platform_text}
{requirements_text}

## 输出格式
严格按照以下JSON格式输出：
```json
{{
  "title": "生成的标题",
  "content": "生成的正文内容",
  "imitation_notes": ["模仿说明1", "模仿说明2"],
  "elements_applied": ["应用的爆款元素1", "元素2"],
  "word_count": 字数,
  "estimated_viral_score": 预估爆款指数
}}
```"""
    
    @classmethod
    def _parse_analyze_response(cls, ai_response: str, default_title: str) -> AnalyzeResponse:
        """解析分析响应"""
        try:
            json_str = cls._extract_json(ai_response)
            data = json.loads(json_str)
            
            # 解析爆款元素
            viral_elements = []
            for elem in data.get("viral_elements", []):
                viral_elements.append(ViralElement(
                    name=elem.get("name", ""),
                    description=elem.get("description", ""),
                    score=elem.get("score", 0),
                    examples=elem.get("examples", []),
                ))
            
            # 解析结构分析
            struct_data = data.get("structure", {})
            structure = StructureAnalysis(
                sections=struct_data.get("sections", []),
                opening_hook=struct_data.get("opening_hook", ""),
                closing_cta=struct_data.get("closing_cta", ""),
                transition_style=struct_data.get("transition_style", ""),
            )
            
            return AnalyzeResponse(
                title=data.get("title", default_title),
                category=ContentCategory(data.get("category", "knowledge")),
                viral_score=data.get("viral_score", 70),
                tone=data.get("tone", ""),
                target_audience=data.get("target_audience", ""),
                emotional_triggers=data.get("emotional_triggers", []),
                viral_elements=viral_elements,
                structure=structure,
                writing_techniques=data.get("writing_techniques", []),
                keywords=data.get("keywords", []),
                improvement_suggestions=data.get("improvement_suggestions", []),
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"解析分析响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
    
    @classmethod
    def _parse_imitate_response(cls, ai_response: str) -> ImitateResponse:
        """解析模仿响应"""
        try:
            json_str = cls._extract_json(ai_response)
            data = json.loads(json_str)
            
            return ImitateResponse(
                title=data.get("title", ""),
                content=data.get("content", ""),
                imitation_notes=data.get("imitation_notes", []),
                elements_applied=data.get("elements_applied", []),
                word_count=data.get("word_count", 0),
                estimated_viral_score=data.get("estimated_viral_score", 70),
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"解析模仿响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
    
    @classmethod
    def _extract_json(cls, text: str) -> str:
        """从文本中提取JSON"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        elif "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
