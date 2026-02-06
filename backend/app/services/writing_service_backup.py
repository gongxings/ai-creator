"""
写作服务
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.creation import Creation
from app.models.ai_model import AIModel
from app.schemas.creation import CreationCreate
from app.services.ai import OpenAIService, AnthropicService


class WritingService:
    """写作服务"""
    
    # 写作工具提示词模板
    TOOL_PROMPTS = {
        "wechat_article": """你是一位专业的微信公众号文章写手。请根据以下信息创作一篇高质量的公众号文章：

主题：{topic}
关键词：{keywords}
目标读者：{target_audience}
文章风格：{style}

要求：
1. 标题吸引人，包含关键词
2. 开头引人入胜，快速抓住读者注意力
3. 内容结构清晰，使用小标题分段
4. 语言生动有趣，贴近读者
5. 适当使用emoji表情
6. 结尾有互动引导（点赞、转发、评论）
7. 字数控制在1500-2500字

请直接输出文章内容，包含标题。""",
        
        "xiaohongshu_note": """你是一位小红书爆款笔记创作专家。请根据以下信息创作一篇小红书笔记：

主题：{topic}
关键词：{keywords}
笔记类型：{note_type}

要求：
1. 标题使用数字、emoji、符号等吸引眼球
2. 开头直击痛点或亮点
3. 内容分点呈现，每点简洁有力
4. 大量使用emoji表情
5. 适当添加话题标签#
6. 结尾引导互动（收藏、点赞、关注）
7. 字数控制在500-1000字
8. 语言口语化、真实感强

请直接输出笔记内容。""",
        
        "official_document": """你是一位资深公文写作专家。请根据以下信息撰写一份规范的公文：

公文类型：{doc_type}
主题：{topic}
发文单位：{issuer}
收文单位：{receiver}
主要内容：{content}

要求：
1. 严格遵循公文格式规范
2. 语言正式、准确、简洁
3. 结构完整（标题、主送机关、正文、落款等）
4. 逻辑清晰，层次分明
5. 用词规范，避免口语化

请直接输出公文内容。""",
        
        "academic_paper": """你是一位学术论文写作专家。请根据以下信息撰写学术论文：

论文题目：{title}
研究领域：{field}
研究方法：{method}
核心观点：{main_points}

要求：
1. 包含摘要、关键词、引言、正文、结论、参考文献
2. 语言学术化、严谨
3. 论证充分，逻辑严密
4. 适当引用文献
5. 字数控制在3000-5000字

请直接输出论文内容。""",
        
        "marketing_copy": """你是一位资深营销文案策划。请根据以下信息创作营销文案：

产品/服务：{product}
目标客户：{target_customer}
核心卖点：{selling_points}
营销目标：{goal}

要求：
1. 标题抓眼球，激发兴趣
2. 突出产品核心价值和差异化优势
3. 使用AIDA模型（注意-兴趣-欲望-行动）
4. 语言有感染力和说服力
5. 包含明确的行动号召（CTA）
6. 字数控制在800-1500字

请直接输出文案内容。""",
        
        "news_article": """你是一位专业新闻记者。请根据以下信息撰写新闻稿：

新闻主题：{topic}
新闻类型：{news_type}
关键信息：{key_info}

要求：
1. 标题简洁有力，概括核心信息
2. 导语包含5W1H（何时、何地、何人、何事、为何、如何）
3. 倒金字塔结构，重要信息在前
4. 客观中立，事实准确
5. 语言简洁明了
6. 字数控制在800-1200字

请直接输出新闻稿内容。""",
        
        "video_script": """你是一位短视频脚本创作专家。请根据以下信息创作短视频脚本：

视频主题：{topic}
视频时长：{duration}
目标平台：{platform}
视频风格：{style}

要求：
1. 开头3秒抓住注意力
2. 节奏紧凑，信息密度高
3. 包含画面描述、台词、字幕、音效等
4. 适合竖屏观看
5. 结尾有互动引导
6. 时长控制在{duration}

请按以下格式输出：
【画面】描述
【台词】内容
【字幕】文字
【音效】说明""",
        
        "story_novel": """你是一位优秀的故事作家。请根据以下信息创作故事：

故事类型：{genre}
故事主题：{theme}
主要角色：{characters}
故事背景：{setting}

要求：
1. 情节引人入胜，有起承转合
2. 人物形象鲜明，性格突出
3. 语言生动，富有画面感
4. 适当使用对话和心理描写
5. 结局有意义或有悬念
6. 字数控制在2000-3000字

请直接输出故事内容。""",
        
        "business_plan": """你是一位资深商业顾问。请根据以下信息撰写商业计划书：

项目名称：{project_name}
行业领域：{industry}
商业模式：{business_model}
目标市场：{target_market}

要求：
1. 包含执行摘要、市场分析、产品服务、营销策略、财务预测等
2. 数据支撑，逻辑严密
3. 语言专业、清晰
4. 突出项目优势和可行性
5. 字数控制在3000-5000字

请直接输出商业计划书内容。""",
        
        "work_report": """你是一位专业的工作报告撰写专家。请根据以下信息撰写工作报告：

报告类型：{report_type}
报告周期：{period}
主要工作：{main_work}
工作成果：{achievements}

要求：
1. 结构清晰（工作概述、完成情况、问题分析、下步计划）
2. 数据详实，有理有据
3. 语言简洁、客观
4. 突出重点和亮点
5. 字数控制在1500-2500字

请直接输出工作报告内容。""",
        
        "resume": """你是一位专业的简历撰写顾问。请根据以下信息撰写简历：

姓名：{name}
应聘职位：{position}
工作经验：{experience}
教育背景：{education}
技能特长：{skills}

要求：
1. 格式规范，重点突出
2. 工作经历使用STAR法则描述
3. 量化成果，突出价值
4. 技能与岗位匹配
5. 语言简洁、专业
6. 控制在1-2页

请直接输出简历内容。""",
        
        "rewrite": """你是一位专业的内容改写专家。请根据以下要求改写内容：

原文：{original_text}
改写要求：{rewrite_type}
目标风格：{target_style}

要求：
1. 保持原文核心意思不变
2. 根据要求调整表达方式
3. 优化语言和结构
4. 确保内容流畅自然

请直接输出改写后的内容。""",
        
        "translation": """你是一位专业翻译。请根据以下信息进行翻译：

原文：{source_text}
源语言：{source_lang}
目标语言：{target_lang}
翻译风格：{style}

要求：
1. 准确传达原文意思
2. 符合目标语言习惯
3. 保持原文风格和语气
4. 专业术语准确
5. 语言流畅自然

请直接输出翻译内容。"""
    }
    
    @staticmethod
    def get_ai_service(ai_model: AIModel):
        """根据AI模型配置获取对应的服务实例"""
        if ai_model.provider == "openai":
            return OpenAIService(
                api_key=ai_model.api_key,
                model=ai_model.model_name
            )
        elif ai_model.provider == "anthropic":
            return AnthropicService(
                api_key=ai_model.api_key,
                model=ai_model.model_name
            )
        else:
            raise ValueError(f"不支持的AI服务提供商: {ai_model.provider}")
    
    @classmethod
    async def generate_content(
        cls,
        db: Session,
        tool_type: str,
        user_input: Dict[str, Any],
        ai_model: AIModel
    ) -> str:
        """生成内容"""
        # 获取提示词模板
        if tool_type not in cls.TOOL_PROMPTS:
            raise ValueError(f"不支持的写作工具类型: {tool_type}")
        
        prompt_template = cls.TOOL_PROMPTS[tool_type]
        
        # 填充提示词
        try:
            prompt = prompt_template.format(**user_input)
        except KeyError as e:
            raise ValueError(f"缺少必需的输入参数: {str(e)}")
        
        # 调用AI服务生成内容
        ai_service = cls.get_ai_service(ai_model)
        content = await ai_service.generate_text(prompt)
        
        return content
    
    @classmethod
    async def optimize_content(
        cls,
        db: Session,
        content: str,
        optimization_type: str,
        ai_model: AIModel
    ) -> str:
        """优化内容"""
        optimization_prompts = {
            "seo": f"请对以下内容进行SEO优化，提高搜索引擎友好度：\n\n{content}",
            "readability": f"请优化以下内容的可读性，使其更易理解：\n\n{content}",
            "engagement": f"请优化以下内容，提高用户参与度和互动性：\n\n{content}",
            "concise": f"请精简以下内容，保留核心信息：\n\n{content}",
            "expand": f"请扩展以下内容，增加细节和深度：\n\n{content}"
        }
        
        if optimization_type not in optimization_prompts:
            raise ValueError(f"不支持的优化类型: {optimization_type}")
        
        prompt = optimization_prompts[optimization_type]
        
        # 调用AI服务优化内容
        ai_service = cls.get_ai_service(ai_model)
        optimized_content = await ai_service.generate_text(prompt)
        
        return optimized_content
    
    @staticmethod
    def get_available_tools() -> List[Dict[str, Any]]:
        """获取所有可用的写作工具列表"""
        tools = [
            {
                "type": "wechat_article",
                "name": "公众号文章",
                "description": "创作高质量的微信公众号文章",
                "icon": "📱",
                "required_fields": ["topic", "keywords", "target_audience", "style"]
            },
            {
                "type": "xiaohongshu_note",
                "name": "小红书笔记",
                "description": "创作爆款小红书笔记",
                "icon": "📔",
                "required_fields": ["topic", "keywords", "note_type"]
            },
            {
                "type": "official_document",
                "name": "公文写作",
                "description": "撰写规范的公文",
                "icon": "📄",
                "required_fields": ["doc_type", "topic", "issuer", "receiver", "content"]
            },
            {
                "type": "academic_paper",
                "name": "论文写作",
                "description": "撰写学术论文",
                "icon": "🎓",
                "required_fields": ["title", "field", "method", "main_points"]
            },
            {
                "type": "marketing_copy",
                "name": "营销文案",
                "description": "创作有说服力的营销文案",
                "icon": "💼",
                "required_fields": ["product", "target_customer", "selling_points", "goal"]
            },
            {
                "type": "news_article",
                "name": "新闻稿",
                "description": "撰写专业的新闻稿",
                "icon": "📰",
                "required_fields": ["topic", "news_type", "key_info"]
            },
            {
                "type": "video_script",
                "name": "短视频脚本",
                "description": "创作短视频脚本",
                "icon": "🎬",
                "required_fields": ["topic", "duration", "platform", "style"]
            },
            {
                "type": "story_novel",
                "name": "故事创作",
                "description": "创作引人入胜的故事",
                "icon": "📖",
                "required_fields": ["genre", "theme", "characters", "setting"]
            },
            {
                "type": "business_plan",
                "name": "商业计划书",
                "description": "撰写商业计划书",
                "icon": "💡",
                "required_fields": ["project_name", "industry", "business_model", "target_market"]
            },
            {
                "type": "work_report",
                "name": "工作报告",
                "description": "撰写工作报告",
                "icon": "📊",
                "required_fields": ["report_type", "period", "main_work", "achievements"]
            },
            {
                "type": "resume",
                "name": "简历",
                "description": "撰写专业简历",
                "icon": "👔",
                "required_fields": ["name", "position", "experience", "education", "skills"]
            },
            {
                "type": "rewrite",
                "name": "内容改写",
                "description": "改写和优化内容",
                "icon": "✏️",
                "required_fields": ["original_text", "rewrite_type", "target_style"]
            },
            {
                "type": "translation",
                "name": "多语言翻译",
                "description": "专业多语言翻译",
                "icon": "🌐",
                "required_fields": ["source_text", "source_lang", "target_lang", "style"]
            }
        ]
        return tools
