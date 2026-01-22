"""
写作服务
处理各种AI写作工具的业务逻辑
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.creation import Creation, CreationVersion
from app.models.ai_model import AIModel
from app.services.ai.factory import AIServiceFactory
from app.core.exceptions import BusinessException
import json


class WritingService:
    """写作服务类"""
    
    # 写作工具配置
    WRITING_TOOLS = {
        "wechat_article": {
            "name": "公众号文章创作",
            "description": "创作适合微信公众号的文章",
            "prompt_template": """请根据以下信息创作一篇微信公众号文章：

主题：{topic}
关键词：{keywords}
目标读者：{target_audience}
文章风格：{style}
字数要求：{word_count}

要求：
1. 标题吸引人，符合公众号特点
2. 开头引人入胜，快速抓住读者注意力
3. 内容结构清晰，使用小标题分段
4. 语言生动有趣，贴近读者
5. 适当使用emoji表情
6. 结尾有互动引导（点赞、转发、评论）
7. 符合微信公众号排版规范

请直接输出文章内容，包含标题。"""
        },
        "xiaohongshu_note": {
            "name": "小红书笔记创作",
            "description": "创作适合小红书的种草笔记",
            "prompt_template": """请根据以下信息创作一篇小红书笔记：

主题：{topic}
产品/内容：{product}
关键词：{keywords}
笔记类型：{note_type}

要求：
1. 标题使用emoji，吸引眼球（不超过20字）
2. 开头直接点明主题，制造悬念
3. 内容真实自然，像朋友分享
4. 多用emoji表情，增加活泼感
5. 分点叙述，条理清晰
6. 包含使用体验、效果对比
7. 结尾引导互动（收藏、点赞）
8. 添加相关话题标签（#话题#）
9. 字数控制在500-1000字

请直接输出笔记内容，包含标题和话题标签。"""
        },
        "official_document": {
            "name": "公文写作",
            "description": "创作正式的公文",
            "prompt_template": """请根据以下信息撰写公文：

公文类型：{doc_type}
标题：{title}
主送机关：{recipient}
主要内容：{content}
发文机关：{sender}

要求：
1. 严格遵守公文格式规范
2. 使用规范的公文用语
3. 结构完整（标题、主送机关、正文、发文机关、日期）
4. 语言准确、简洁、庄重
5. 逻辑清晰，层次分明
6. 符合公文写作标准

请输出完整的公文内容。"""
        },
        "academic_paper": {
            "name": "论文写作",
            "description": "创作学术论文",
            "prompt_template": """请根据以下信息撰写学术论文：

论文题目：{title}
研究领域：{field}
研究方法：{method}
主要观点：{main_points}
字数要求：{word_count}

要求：
1. 包含完整的论文结构（摘要、引言、文献综述、研究方法、结果分析、结论、参考文献）
2. 使用学术规范语言
3. 论证严谨，逻辑清晰
4. 引用相关文献（格式规范）
5. 数据和观点有理有据
6. 符合学术写作规范

请输出完整的论文内容。"""
        },
        "marketing_copy": {
            "name": "营销文案",
            "description": "创作营销推广文案",
            "prompt_template": """请根据以下信息创作营销文案：

产品/服务：{product}
目标客户：{target_customer}
核心卖点：{selling_points}
营销场景：{scenario}
文案类型：{copy_type}

要求：
1. 标题抓眼球，激发兴趣
2. 突出产品核心价值和差异化优势
3. 使用AIDA模型（注意-兴趣-欲望-行动）
4. 语言有感染力，制造紧迫感
5. 包含明确的行动号召（CTA）
6. 适合目标渠道的风格
7. 字数适中，重点突出

请输出完整的营销文案。"""
        },
        "news_article": {
            "name": "新闻稿/软文",
            "description": "创作新闻稿或软文",
            "prompt_template": """请根据以下信息撰写新闻稿/软文：

主题：{topic}
新闻要素：{news_elements}
目标媒体：{target_media}
文章类型：{article_type}
字数要求：{word_count}

要求：
1. 标题新闻性强，概括核心信息
2. 导语简洁有力，包含5W1H
3. 正文结构清晰，倒金字塔结构
4. 客观真实，有新闻价值
5. 引用权威数据或专家观点
6. 软文要自然植入，不生硬
7. 符合新闻写作规范

请输出完整的新闻稿/软文内容。"""
        },
        "video_script": {
            "name": "短视频脚本",
            "description": "创作短视频脚本",
            "prompt_template": """请根据以下信息创作短视频脚本：

主题：{topic}
视频时长：{duration}
目标平台：{platform}
视频风格：{style}
核心信息：{core_message}

要求：
1. 开头3秒抓住注意力（黄金3秒）
2. 脚本分镜头，标注画面和文案
3. 节奏紧凑，信息密度高
4. 语言口语化，适合配音
5. 包含转折和高潮
6. 结尾有互动引导（关注、点赞、评论）
7. 标注BGM和特效建议
8. 符合平台特点和时长要求

请输出完整的视频脚本，包含分镜表。"""
        },
        "story_novel": {
            "name": "故事/小说创作",
            "description": "创作故事或小说",
            "prompt_template": """请根据以下信息创作故事/小说：

题材：{genre}
主题：{theme}
主要角色：{characters}
故事梗概：{plot}
字数要求：{word_count}

要求：
1. 情节完整，有起承转合
2. 人物形象鲜明，性格突出
3. 对话生动自然
4. 场景描写细腻
5. 节奏把控得当
6. 语言优美流畅
7. 有悬念和冲突
8. 结局合理且有回味

请输出完整的故事/小说内容。"""
        },
        "business_plan": {
            "name": "商业计划书",
            "description": "创作商业计划书",
            "prompt_template": """请根据以下信息撰写商业计划书：

项目名称：{project_name}
行业领域：{industry}
商业模式：{business_model}
目标市场：{target_market}
核心优势：{core_advantages}

要求：
1. 包含完整结构（执行摘要、公司介绍、市场分析、产品服务、营销策略、运营计划、财务预测、风险分析）
2. 数据详实，分析深入
3. 逻辑严密，论证充分
4. 突出项目亮点和竞争优势
5. 财务预测合理可信
6. 语言专业规范
7. 适合投资人阅读

请输出完整的商业计划书。"""
        },
        "work_report": {
            "name": "工作报告",
            "description": "创作工作报告",
            "prompt_template": """请根据以下信息撰写工作报告：

报告类型：{report_type}
报告期间：{period}
主要工作：{main_work}
工作成果：{achievements}
存在问题：{problems}
下步计划：{next_plan}

要求：
1. 结构清晰（工作概述、主要成绩、存在问题、下步打算）
2. 数据准确，用数字说话
3. 重点突出，详略得当
4. 客观真实，不夸大
5. 问题分析深入，措施具体
6. 语言简洁专业
7. 符合公文写作规范

请输出完整的工作报告。"""
        },
        "resume": {
            "name": "简历/求职信",
            "description": "创作个人简历或求职信",
            "prompt_template": """请根据以下信息创作简历/求职信：

文档类型：{doc_type}
应聘职位：{position}
个人信息：{personal_info}
教育背景：{education}
工作经历：{work_experience}
技能特长：{skills}

要求：
1. 格式规范，排版清晰
2. 信息完整准确
3. 突出与岗位匹配的经验和技能
4. 使用动词开头描述工作成果
5. 量化工作成绩
6. 简历控制在1-2页
7. 求职信表达求职动机和优势
8. 语言专业得体

请输出完整的简历/求职信内容。"""
        },
        "lesson_plan": {
            "name": "教案/课件",
            "description": "创作教学教案或课件",
            "prompt_template": """请根据以下信息创作教案/课件：

课程名称：{course_name}
教学对象：{students}
教学目标：{objectives}
教学内容：{content}
课时安排：{duration}

要求：
1. 包含完整结构（教学目标、教学重难点、教学过程、板书设计、作业布置）
2. 教学目标明确具体
3. 教学方法多样有效
4. 教学过程详细清晰
5. 重难点突出
6. 互动环节设计合理
7. 符合教学规律
8. 语言准确规范

请输出完整的教案/课件内容。"""
        },
        "rewrite": {
            "name": "内容改写/扩写/缩写",
            "description": "对现有内容进行改写、扩写或缩写",
            "prompt_template": """请根据以下要求处理内容：

操作类型：{operation_type}
原始内容：{original_content}
目标字数：{target_word_count}
改写要求：{requirements}

要求：
1. 改写：保持原意，改变表达方式，避免重复
2. 扩写：丰富内容，增加细节和例子，保持逻辑
3. 缩写：提炼核心，删除冗余，保留关键信息
4. 语言流畅自然
5. 符合目标字数要求
6. 保持原文风格（如有要求）

请输出处理后的内容。"""
        },
        "translation": {
            "name": "多语言翻译",
            "description": "进行多语言翻译",
            "prompt_template": """请进行以下翻译：

源语言：{source_language}
目标语言：{target_language}
原文内容：{original_text}
翻译类型：{translation_type}

要求：
1. 准确传达原文意思
2. 符合目标语言习惯
3. 保持原文风格和语气
4. 专业术语翻译准确
5. 语言流畅自然
6. 格式保持一致
7. 根据翻译类型调整（直译/意译/创译）

请输出翻译后的内容。"""
        }
    }
    
    def __init__(self, db: Session):
        """初始化写作服务"""
        self.db = db
    
    def get_tools(self) -> list:
        """获取所有写作工具列表"""
        return [
            {
                "tool_type": tool_type,
                "name": config["name"],
                "description": config["description"]
            }
            for tool_type, config in self.WRITING_TOOLS.items()
        ]
    
    async def generate_content(
        self,
        user_id: int,
        tool_type: str,
        params: Dict[str, Any],
        ai_model_id: Optional[int] = None
    ) -> Creation:
        """
        生成内容
        
        Args:
            user_id: 用户ID
            tool_type: 工具类型
            params: 生成参数
            ai_model_id: AI模型ID（可选，不指定则使用默认模型）
        
        Returns:
            Creation: 创作记录
        """
        # 验证工具类型
        if tool_type not in self.WRITING_TOOLS:
            raise BusinessException(f"不支持的工具类型: {tool_type}")
        
        tool_config = self.WRITING_TOOLS[tool_type]
        
        # 获取AI模型
        if ai_model_id:
            ai_model = self.db.query(AIModel).filter(
                AIModel.id == ai_model_id,
                AIModel.is_active == True
            ).first()
        else:
            ai_model = self.db.query(AIModel).filter(
                AIModel.is_default == True,
                AIModel.is_active == True
            ).first()
        
        if not ai_model:
            raise BusinessException("未找到可用的AI模型")
        
        # 构建提示词
        try:
            prompt = tool_config["prompt_template"].format(**params)
        except KeyError as e:
            raise BusinessException(f"缺少必需参数: {e}")
        
        # 调用AI服务生成内容
        ai_service = AIServiceFactory.create_service(
            ai_model.provider,
            ai_model.api_key,
            ai_model.api_base,
            ai_model.model_name
        )
        
        try:
            content = await ai_service.generate_text(prompt)
        except Exception as e:
            raise BusinessException(f"AI生成失败: {str(e)}")
        
        # 创建创作记录
        creation = Creation(
            user_id=user_id,
            content_type="writing",
            tool_type=tool_type,
            title=self._extract_title(content, tool_type),
            content=content,
            ai_model_id=ai_model.id,
            generation_params=params,
            status="completed"
        )
        
        self.db.add(creation)
        self.db.commit()
        self.db.refresh(creation)
        
        # 创建初始版本
        version = CreationVersion(
            creation_id=creation.id,
            version_number=1,
            content=content,
            change_description="初始生成"
        )
        
        self.db.add(version)
        self.db.commit()
        
        return creation
    
    async def regenerate_content(
        self,
        creation_id: int,
        user_id: int,
        params: Optional[Dict[str, Any]] = None
    ) -> Creation:
        """
        重新生成内容
        
        Args:
            creation_id: 创作ID
            user_id: 用户ID
            params: 新的生成参数（可选）
        
        Returns:
            Creation: 更新后的创作记录
        """
        # 获取创作记录
        creation = self.db.query(Creation).filter(
            Creation.id == creation_id,
            Creation.user_id == user_id
        ).first()
        
        if not creation:
            raise BusinessException("创作记录不存在")
        
        # 使用新参数或原参数
        generation_params = params if params else creation.generation_params
        
        # 获取AI模型
        ai_model = self.db.query(AIModel).filter(
            AIModel.id == creation.ai_model_id
        ).first()
        
        if not ai_model or not ai_model.is_active:
            raise BusinessException("AI模型不可用")
        
        # 构建提示词
        tool_config = self.WRITING_TOOLS[creation.tool_type]
        prompt = tool_config["prompt_template"].format(**generation_params)
        
        # 调用AI服务生成内容
        ai_service = AIServiceFactory.create_service(
            ai_model.provider,
            ai_model.api_key,
            ai_model.api_base,
            ai_model.model_name
        )
        
        try:
            new_content = await ai_service.generate_text(prompt)
        except Exception as e:
            raise BusinessException(f"AI生成失败: {str(e)}")
        
        # 更新创作记录
        creation.content = new_content
        creation.title = self._extract_title(new_content, creation.tool_type)
        creation.generation_params = generation_params
        
        # 创建新版本
        latest_version = self.db.query(CreationVersion).filter(
            CreationVersion.creation_id == creation_id
        ).order_by(CreationVersion.version_number.desc()).first()
        
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = CreationVersion(
            creation_id=creation.id,
            version_number=new_version_number,
            content=new_content,
            change_description="重新生成"
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(creation)
        
        return creation
    
    async def optimize_content(
        self,
        creation_id: int,
        user_id: int,
        optimization_type: str,
        requirements: Optional[str] = None
    ) -> Creation:
        """
        优化内容
        
        Args:
            creation_id: 创作ID
            user_id: 用户ID
            optimization_type: 优化类型（seo/readability/style/grammar）
            requirements: 额外要求
        
        Returns:
            Creation: 更新后的创作记录
        """
        # 获取创作记录
        creation = self.db.query(Creation).filter(
            Creation.id == creation_id,
            Creation.user_id == user_id
        ).first()
        
        if not creation:
            raise BusinessException("创作记录不存在")
        
        # 构建优化提示词
        optimization_prompts = {
            "seo": "请优化以下内容的SEO，包括：1. 优化标题和关键词布局 2. 增加内部链接建议 3. 优化meta描述 4. 提高关键词密度（保持自然）",
            "readability": "请优化以下内容的可读性，包括：1. 简化复杂句子 2. 使用更通俗的表达 3. 优化段落结构 4. 增加小标题和列表",
            "style": "请优化以下内容的文风，使其更加生动有趣、富有感染力",
            "grammar": "请检查并修正以下内容的语法错误、错别字和标点符号问题"
        }
        
        if optimization_type not in optimization_prompts:
            raise BusinessException(f"不支持的优化类型: {optimization_type}")
        
        base_prompt = optimization_prompts[optimization_type]
        if requirements:
            base_prompt += f"\n\n额外要求：{requirements}"
        
        prompt = f"{base_prompt}\n\n原文内容：\n{creation.content}"
        
        # 获取AI模型
        ai_model = self.db.query(AIModel).filter(
            AIModel.id == creation.ai_model_id
        ).first()
        
        if not ai_model or not ai_model.is_active:
            raise BusinessException("AI模型不可用")
        
        # 调用AI服务优化内容
        ai_service = AIServiceFactory.create_service(
            ai_model.provider,
            ai_model.api_key,
            ai_model.api_base,
            ai_model.model_name
        )
        
        try:
            optimized_content = await ai_service.generate_text(prompt)
        except Exception as e:
            raise BusinessException(f"AI优化失败: {str(e)}")
        
        # 更新创作记录
        creation.content = optimized_content
        creation.title = self._extract_title(optimized_content, creation.tool_type)
        
        # 创建新版本
        latest_version = self.db.query(CreationVersion).filter(
            CreationVersion.creation_id == creation_id
        ).order_by(CreationVersion.version_number.desc()).first()
        
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = CreationVersion(
            creation_id=creation.id,
            version_number=new_version_number,
            content=optimized_content,
            change_description=f"{optimization_type}优化"
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(creation)
        
        return creation
    
    def _extract_title(self, content: str, tool_type: str) -> str:
        """
        从内容中提取标题
        
        Args:
            content: 内容
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
            return title if title else f"{self.WRITING_TOOLS[tool_type]['name']}"
        
        return f"{self.WRITING_TOOLS[tool_type]['name']}"
