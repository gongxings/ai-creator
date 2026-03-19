"""
爆款标题生成服务
使用 AI 生成、优化和分析标题
"""
import json
import logging
from typing import List, Optional

from app.schemas.title import (
    TitleStyle,
    PlatformType,
    TitleItem,
    TitleGenerateRequest,
    TitleGenerateResponse,
    TitleOptimizeRequest,
    TitleOptimizeResponse,
    TitleAnalyzeRequest,
    TitleAnalyzeResponse,
)

logger = logging.getLogger(__name__)


class TitleService:
    """爆款标题生成服务"""
    
    # 标题风格说明
    STYLE_DESCRIPTIONS = {
        TitleStyle.CURIOSITY: "好奇心驱动型：利用悬念、未知信息引发好奇",
        TitleStyle.BENEFIT: "利益驱动型：突出读者能获得的好处和价值",
        TitleStyle.EMOTIONAL: "情感驱动型：引发共鸣、触动情感",
        TitleStyle.TRENDING: "热点借势型：结合当前热点话题",
        TitleStyle.LISTICLE: "数字清单型：用数字量化内容价值",
        TitleStyle.QUESTION: "提问式：以问题引发思考和好奇",
        TitleStyle.HOW_TO: "教程式：提供解决方案和方法",
        TitleStyle.CONTRAST: "对比反差型：通过对比制造冲突感",
    }
    
    # 平台特点
    PLATFORM_FEATURES = {
        PlatformType.WECHAT: {
            "name": "微信公众号",
            "max_length": 64,
            "features": "标题可以较长，注重价值感和专业度，适合深度内容",
            "tips": ["可用【】突出关键词", "适合观点输出类标题", "情感共鸣类表现好"],
        },
        PlatformType.XIAOHONGSHU: {
            "name": "小红书",
            "max_length": 20,
            "features": "标题简短有力，大量使用emoji，偏年轻化、生活化",
            "tips": ["必须使用emoji装饰", "口语化表达", "突出「我」的体验", "种草感强"],
        },
        PlatformType.DOUYIN: {
            "name": "抖音",
            "max_length": 30,
            "features": "短平快，强调情绪冲击和话题性",
            "tips": ["制造争议或悬念", "口语化", "突出冲突感"],
        },
        PlatformType.ZHIHU: {
            "name": "知乎",
            "max_length": 50,
            "features": "偏理性、专业，注重信息增量",
            "tips": ["突出专业度", "提供独特视角", "避免标题党"],
        },
        PlatformType.WEIBO: {
            "name": "微博",
            "max_length": 40,
            "features": "热点敏感，话题性强",
            "tips": ["结合热搜话题", "制造讨论点", "适当使用#话题#"],
        },
        PlatformType.TOUTIAO: {
            "name": "今日头条",
            "max_length": 30,
            "features": "信息流分发，需要强吸引力",
            "tips": ["突出新闻价值", "数字和数据吸引眼球", "悬念感强"],
        },
        PlatformType.BILIBILI: {
            "name": "B站",
            "max_length": 80,
            "features": "年轻化，可以较长，注重创意和趣味",
            "tips": ["可以用梗和流行语", "创意标题党", "突出UP主个性"],
        },
    }
    
    # 钩子技巧列表
    HOOK_TECHNIQUES = [
        "数字量化", "悬念设置", "利益承诺", "痛点直击", "情感共鸣",
        "权威背书", "时效性", "对比反差", "提问引导", "争议话题",
        "身份认同", "稀缺性", "具体场景", "否定常识", "解决方案",
    ]
    
    @classmethod
    async def generate_titles(
        cls,
        request: TitleGenerateRequest,
        ai_model=None,
    ) -> TitleGenerateResponse:
        """
        生成爆款标题
        
        Args:
            request: 标题生成请求
            ai_model: AI 模型配置
            
        Returns:
            TitleGenerateResponse
        """
        from app.services.langchain import LangChainService
        
        prompt = cls._build_generate_prompt(request)
        
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
            return cls._parse_generate_response(response.content)
            
        except Exception as e:
            logger.error(f"标题生成失败: {e}")
            return cls._get_fallback_titles(request)
    
    @classmethod
    async def optimize_title(
        cls,
        request: TitleOptimizeRequest,
        ai_model=None,
    ) -> TitleOptimizeResponse:
        """
        优化现有标题
        
        Args:
            request: 标题优化请求
            ai_model: AI 模型配置
            
        Returns:
            TitleOptimizeResponse
        """
        from app.services.langchain import LangChainService
        
        prompt = cls._build_optimize_prompt(request)
        
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
            return cls._parse_optimize_response(request.original_title, response.content)
            
        except Exception as e:
            logger.error(f"标题优化失败: {e}")
            raise Exception(f"标题优化失败: {str(e)}")
    
    @classmethod
    async def analyze_title(
        cls,
        request: TitleAnalyzeRequest,
        ai_model=None,
    ) -> TitleAnalyzeResponse:
        """
        分析标题质量
        
        Args:
            request: 标题分析请求
            ai_model: AI 模型配置
            
        Returns:
            TitleAnalyzeResponse
        """
        from app.services.langchain import LangChainService
        
        prompt = cls._build_analyze_prompt(request)
        
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
            return cls._parse_analyze_response(request.title, response.content)
            
        except Exception as e:
            logger.error(f"标题分析失败: {e}")
            raise Exception(f"标题分析失败: {str(e)}")
    
    @classmethod
    def _build_generate_prompt(cls, request: TitleGenerateRequest) -> str:
        """构建标题生成提示词"""
        platform_info = ""
        if request.platform:
            pf = cls.PLATFORM_FEATURES.get(request.platform, {})
            platform_info = f"""
## 目标平台：{pf.get('name', request.platform.value)}
- 标题长度限制：{pf.get('max_length', 50)}字以内
- 平台特点：{pf.get('features', '')}
- 写作技巧：{', '.join(pf.get('tips', []))}
"""
        
        style_info = ""
        if request.style:
            style_info = f"\n## 要求风格：{cls.STYLE_DESCRIPTIONS.get(request.style, request.style.value)}\n"
        
        keywords_info = ""
        if request.keywords:
            keywords_info = f"\n## 必须包含的关键词：{', '.join(request.keywords)}\n"
        
        tone_info = ""
        if request.tone:
            tone_info = f"\n## 语气要求：{request.tone}\n"
        
        return f"""你是一位顶级的新媒体标题策划专家，擅长撰写高点击率的爆款标题。

## 任务
根据以下内容，生成 {request.count} 个不同风格的爆款标题。

## 内容主题
{request.content}
{platform_info}{style_info}{keywords_info}{tone_info}

## 爆款标题技巧参考
1. **数字量化**：用具体数字增加可信度，如"3个方法"、"90%的人不知道"
2. **悬念设置**：制造好奇心，如"原来是因为..."、"真相竟然是..."
3. **利益承诺**：突出读者收益，如"学会这招，效率提升3倍"
4. **痛点直击**：戳中用户痛点，如"为什么你总是..."
5. **情感共鸣**：引发情感认同，如"看哭了"、"太真实了"
6. **权威背书**：借助权威，如"哈佛研究发现"
7. **对比反差**：制造冲突，如"月薪3千和3万的区别"
8. **提问引导**：引发思考，如"为什么..."、"怎样才能..."

## 评分标准（爆款指数 0-100）
- 90-100：极具爆款潜力，多种钩子组合，情绪价值高
- 70-89：优秀标题，有明确钩子，吸引力强
- 50-69：合格标题，基本满足要求
- 50以下：需要优化

## 输出格式
严格按照以下 JSON 格式输出，不要输出其他内容：
```json
{{
  "titles": [
    {{
      "title": "标题文本",
      "style": "curiosity|benefit|emotional|trending|listicle|question|how_to|contrast",
      "score": 85,
      "hooks": ["使用的钩子技巧1", "钩子技巧2"],
      "explanation": "为什么这个标题有效的简短解释"
    }}
  ],
  "analysis": "整体创作建议，50字以内"
}}
```"""
    
    @classmethod
    def _build_optimize_prompt(cls, request: TitleOptimizeRequest) -> str:
        """构建标题优化提示词"""
        platform_info = ""
        if request.platform:
            pf = cls.PLATFORM_FEATURES.get(request.platform, {})
            platform_info = f"""
## 目标平台：{pf.get('name', request.platform.value)}
- 标题长度限制：{pf.get('max_length', 50)}字以内
- 平台特点：{pf.get('features', '')}
- 写作技巧：{', '.join(pf.get('tips', []))}
"""
        
        goals_info = ""
        if request.optimization_goals:
            goals_info = f"\n## 优化目标：{', '.join(request.optimization_goals)}\n"
        
        return f"""你是一位顶级的新媒体标题策划专家，擅长优化标题以提升点击率。

## 任务
分析并优化以下标题，生成 5 个更具爆款潜力的版本。

## 原标题
{request.original_title}
{platform_info}{goals_info}

## 分析要求
1. 评估原标题的爆款指数（0-100分）
2. 找出原标题的问题和不足
3. 保留原标题的核心信息，优化表达方式
4. 每个优化版本采用不同的钩子技巧

## 输出格式
严格按照以下 JSON 格式输出：
```json
{{
  "original_score": 45,
  "original_issues": ["问题1", "问题2"],
  "optimized_titles": [
    {{
      "title": "优化后的标题",
      "style": "curiosity|benefit|emotional|trending|listicle|question|how_to|contrast",
      "score": 85,
      "hooks": ["使用的钩子技巧"],
      "explanation": "优化说明"
    }}
  ],
  "improvement_tips": ["改进建议1", "改进建议2"]
}}
```"""
    
    @classmethod
    def _build_analyze_prompt(cls, request: TitleAnalyzeRequest) -> str:
        """构建标题分析提示词"""
        platform_info = ""
        if request.platform:
            pf = cls.PLATFORM_FEATURES.get(request.platform, {})
            platform_info = f"""
## 目标平台：{pf.get('name', request.platform.value)}
- 标题长度限制：{pf.get('max_length', 50)}字以内
- 平台特点：{pf.get('features', '')}
"""
        
        return f"""你是一位顶级的新媒体标题策划专家，请深度分析以下标题。

## 待分析标题
{request.title}
{platform_info}

## 分析维度
1. **爆款指数**（0-100分）：综合评估标题的吸引力
2. **风格识别**：判断标题属于哪种风格
3. **优点分析**：这个标题做得好的地方
4. **缺点分析**：这个标题的不足之处
5. **钩子识别**：识别标题使用了哪些钩子技巧
6. **改进建议**：具体可操作的优化方向

## 风格类型
- curiosity: 好奇心驱动型
- benefit: 利益驱动型
- emotional: 情感驱动型
- trending: 热点借势型
- listicle: 数字清单型
- question: 提问式
- how_to: 教程式
- contrast: 对比反差型

## 输出格式
严格按照以下 JSON 格式输出：
```json
{{
  "score": 65,
  "style": "benefit",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "hooks_used": ["数字量化", "利益承诺"],
  "improvement_suggestions": ["建议1", "建议2"],
  "platform_fit": "平台适配度分析（如果指定了平台）"
}}
```"""
    
    @classmethod
    def _parse_generate_response(cls, ai_response: str) -> TitleGenerateResponse:
        """解析标题生成响应"""
        try:
            json_str = cls._extract_json(ai_response)
            data = json.loads(json_str)
            
            titles = []
            for item in data.get("titles", []):
                titles.append(TitleItem(
                    title=item.get("title", ""),
                    style=TitleStyle(item.get("style", "benefit")),
                    score=item.get("score", 70),
                    hooks=item.get("hooks", []),
                    explanation=item.get("explanation", ""),
                ))
            
            return TitleGenerateResponse(
                titles=titles,
                analysis=data.get("analysis", ""),
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"解析标题生成响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
    
    @classmethod
    def _parse_optimize_response(
        cls,
        original_title: str,
        ai_response: str
    ) -> TitleOptimizeResponse:
        """解析标题优化响应"""
        try:
            json_str = cls._extract_json(ai_response)
            data = json.loads(json_str)
            
            optimized = []
            for item in data.get("optimized_titles", []):
                optimized.append(TitleItem(
                    title=item.get("title", ""),
                    style=TitleStyle(item.get("style", "benefit")),
                    score=item.get("score", 70),
                    hooks=item.get("hooks", []),
                    explanation=item.get("explanation", ""),
                ))
            
            return TitleOptimizeResponse(
                original_title=original_title,
                original_score=data.get("original_score", 50),
                original_issues=data.get("original_issues", []),
                optimized_titles=optimized,
                improvement_tips=data.get("improvement_tips", []),
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"解析标题优化响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
    
    @classmethod
    def _parse_analyze_response(
        cls,
        title: str,
        ai_response: str
    ) -> TitleAnalyzeResponse:
        """解析标题分析响应"""
        try:
            json_str = cls._extract_json(ai_response)
            data = json.loads(json_str)
            
            return TitleAnalyzeResponse(
                title=title,
                score=data.get("score", 50),
                style=TitleStyle(data.get("style", "benefit")),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                hooks_used=data.get("hooks_used", []),
                improvement_suggestions=data.get("improvement_suggestions", []),
                platform_fit=data.get("platform_fit"),
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"解析标题分析响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
    
    @classmethod
    def _extract_json(cls, text: str) -> str:
        """从文本中提取 JSON"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        elif "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
    
    @classmethod
    def _get_fallback_titles(cls, request: TitleGenerateRequest) -> TitleGenerateResponse:
        """获取兜底标题（AI 失败时）"""
        content = request.content[:20] if len(request.content) > 20 else request.content
        return TitleGenerateResponse(
            titles=[
                TitleItem(
                    title=f"关于{content}，你必须知道的3件事",
                    style=TitleStyle.LISTICLE,
                    score=65,
                    hooks=["数字量化"],
                    explanation="使用数字清单增加具体感",
                ),
                TitleItem(
                    title=f"为什么{content}如此重要？",
                    style=TitleStyle.QUESTION,
                    score=60,
                    hooks=["提问引导"],
                    explanation="提问式标题引发思考",
                ),
                TitleItem(
                    title=f"{content}的正确打开方式",
                    style=TitleStyle.HOW_TO,
                    score=62,
                    hooks=["解决方案"],
                    explanation="教程式标题承诺价值",
                ),
            ],
            analysis="建议结合热点和目标受众特点进一步优化标题",
        )
