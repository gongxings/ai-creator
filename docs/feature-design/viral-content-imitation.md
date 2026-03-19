# 爆款模仿功能实现方案

## 一、功能概述

**核心目标**：用户输入一个爆款文章的URL，系统自动分析其写作风格、结构特点，并生成具有相似风格但内容原创的新文章。

**用户场景**：
- 自媒体运营者希望学习爆款文章的写作技巧
- 内容创作者需要快速产出类似风格的优质内容
- 企业营销团队需要批量生产高质量营销内容

---

## 二、功能架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        爆款模仿功能                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  1.内容抓取  │ -> │  2.风格分析  │ -> │  3.内容生成  │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│          │                  │                  │                │
│          v                  v                  v                │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  网页解析    │    │  AI分析引擎  │    │  风格迁移    │        │
│   │  正文提取    │    │  结构识别    │    │  原创生成    │        │
│   │  元数据获取  │    │  风格建模    │    │  质量检测    │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、技术实现方案

### 3.1 内容抓取模块

**现有能力**：项目已有 `fetch_url_content` API 和 `WebFetchPlugin` 插件，支持基础的网页抓取。

**增强方案**：

```python
# backend/app/services/content_analyzer.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import re

@dataclass
class ArticleContent:
    """抓取的文章内容"""
    url: str
    title: str
    content: str
    paragraphs: List[str]
    headings: List[Dict[str, str]]  # [{"level": "h2", "text": "..."}]
    word_count: int
    image_count: int
    platform: str  # 识别平台：wechat/xiaohongshu/zhihu/toutiao 等
    publish_date: Optional[str]
    author: Optional[str]
    engagement: Optional[Dict]  # 点赞、评论、转发数

class ArticleFetcher:
    """增强版文章抓取器"""
    
    # 平台特定的选择器配置
    PLATFORM_SELECTORS = {
        "mp.weixin.qq.com": {
            "content": "#js_content",
            "title": "#activity-name",
            "author": "#js_name",
            "date": "#publish_time",
        },
        "xiaohongshu.com": {
            "content": ".note-content",
            "title": ".title",
            "author": ".user-name",
        },
        "zhihu.com": {
            "content": ".RichContent-inner",
            "title": ".QuestionHeader-title",
            "author": ".AuthorInfo-name",
        },
        "toutiao.com": {
            "content": "article",
            "title": "h1",
            "author": ".user-name",
        },
    }
    
    async def fetch(self, url: str) -> ArticleContent:
        """抓取文章内容"""
        # 识别平台
        platform = self._detect_platform(url)
        
        # 获取HTML
        html = await self._fetch_html(url)
        
        # 根据平台使用不同解析策略
        soup = BeautifulSoup(html, 'html.parser')
        selectors = self.PLATFORM_SELECTORS.get(platform, {})
        
        # 提取结构化内容
        content = self._extract_content(soup, selectors)
        
        return ArticleContent(
            url=url,
            title=self._extract_title(soup, selectors),
            content=content,
            paragraphs=self._split_paragraphs(content),
            headings=self._extract_headings(soup),
            word_count=len(content),
            image_count=len(soup.find_all('img')),
            platform=platform,
            publish_date=self._extract_date(soup, selectors),
            author=self._extract_author(soup, selectors),
            engagement=None  # 需要特殊处理
        )
```

### 3.2 文章风格分析模块

这是核心模块，负责分析文章的写作风格和结构特点。

**分析维度**：

| 维度 | 分析内容 | 提取方法 |
|------|----------|----------|
| **结构** | 标题模式、段落数、小标题使用、开篇结尾模式 | 规则+AI |
| **语言** | 句子长度、词汇难度、口语化程度、专业术语密度 | NLP统计 |
| **修辞** | 比喻、排比、设问、感叹等修辞手法 | AI识别 |
| **情感** | 情感基调、情绪变化曲线 | 情感分析 |
| **互动** | 互动引导语、CTA类型、读者称呼 | 规则匹配 |
| **视觉** | emoji使用、符号装饰、列表使用 | 正则统计 |

**风格分析提示词设计**：

```python
# backend/app/services/style_analyzer.py

STYLE_ANALYSIS_PROMPT = """你是一位资深的内容策略分析师，擅长分析爆款文章的写作技巧。

请对以下文章进行深度分析，提取其写作风格特征：

## 原文
{article_content}

## 分析要求

请从以下维度进行分析，输出JSON格式：

```json
{
  "structure": {
    "title_pattern": "标题模式描述，如：数字+痛点+解决方案",
    "opening_hook": "开篇吸引方式，如：提问式/故事式/数据式/直击痛点式",
    "paragraph_count": 段落数量,
    "heading_pattern": "小标题使用模式",
    "closing_cta": "结尾行动召唤类型"
  },
  "language": {
    "tone": "语气基调，如：轻松幽默/专业严谨/温暖治愈/犀利直接",
    "formality": "正式程度 1-5",
    "sentence_style": "句式特点，如：短句为主/长短结合/疑问句多",
    "vocabulary_level": "词汇难度 1-5",
    "colloquial_expressions": ["口语化表达示例"]
  },
  "rhetoric": {
    "techniques": ["使用的修辞手法列表"],
    "examples": ["具体修辞示例"]
  },
  "engagement": {
    "reader_address": "读者称呼方式，如：你/亲/宝子/各位",
    "interaction_triggers": ["互动引导语示例"],
    "emotional_resonance": "情感共鸣点"
  },
  "visual": {
    "emoji_density": "emoji使用密度 1-5",
    "emoji_examples": ["常用emoji"],
    "formatting": "排版特点，如：分点列表/编号/分隔线"
  },
  "unique_features": ["该文章的独特风格特征"],
  "target_audience": "目标读者画像",
  "content_category": "内容分类"
}
```

请确保分析准确、具体，便于后续生成类似风格的文章。"""


class StyleAnalyzer:
    """文章风格分析器"""
    
    async def analyze(self, article: ArticleContent, ai_model) -> Dict:
        """分析文章风格"""
        
        # 1. 基础统计分析（不依赖AI）
        basic_stats = self._compute_basic_stats(article)
        
        # 2. AI深度分析
        prompt = STYLE_ANALYSIS_PROMPT.format(
            article_content=article.content[:8000]  # 限制长度
        )
        
        from app.services.langchain import LangChainService
        service = LangChainService(
            provider=ai_model.provider,
            model=ai_model.model_name,
            api_key=ai_model.api_key,
            api_base=ai_model.base_url
        )
        
        response = await service.chat(prompt)
        ai_analysis = self._parse_json_response(response.content)
        
        # 3. 合并分析结果
        return {
            "basic_stats": basic_stats,
            "style_profile": ai_analysis,
            "article_info": {
                "title": article.title,
                "word_count": article.word_count,
                "platform": article.platform,
            }
        }
    
    def _compute_basic_stats(self, article: ArticleContent) -> Dict:
        """计算基础统计数据"""
        import re
        
        content = article.content
        sentences = re.split(r'[。！？.!?]', content)
        sentences = [s for s in sentences if len(s.strip()) > 0]
        
        return {
            "char_count": len(content),
            "word_count": article.word_count,
            "paragraph_count": len(article.paragraphs),
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(len(s) for s in sentences) / max(len(sentences), 1),
            "heading_count": len(article.headings),
            "emoji_count": len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
            "question_mark_count": content.count('？') + content.count('?'),
            "exclamation_count": content.count('！') + content.count('!'),
            "list_items": len(re.findall(r'^[\d一二三四五六七八九十][\.\、）]', content, re.MULTILINE)),
        }
```

### 3.3 内容生成模块

基于分析结果，生成风格相似但内容原创的新文章。

**风格迁移提示词设计**：

```python
# backend/app/services/content_generator.py

STYLE_IMITATION_PROMPT = """你是一位专业的内容创作者，需要模仿学习一种写作风格，创作全新的原创内容。

## 风格参考（仅学习写作手法，不复制内容）

### 原文风格分析
{style_profile}

### 风格要点
- 标题模式：{title_pattern}
- 开篇方式：{opening_hook}
- 语气基调：{tone}
- 句式特点：{sentence_style}
- 读者称呼：{reader_address}
- 修辞手法：{techniques}
- 视觉风格：{formatting}

## 创作任务

**新文章主题**：{new_topic}
**目标读者**：{target_audience}
**字数要求**：{word_count}字左右
**关键词**：{keywords}

## 重要要求

1. **只学习风格，不复制内容**：
   - 学习参考文章的写作技巧、表达方式、结构安排
   - 内容必须围绕新主题完全原创
   - 不得使用参考文章中的具体案例、数据、故事

2. **风格模仿要点**：
   - 保持相似的语气和节奏
   - 使用类似的开篇吸引方式
   - 采用相似的段落结构
   - 运用类似的修辞手法
   - 保持相似的互动风格

3. **原创性保证**：
   - 使用全新的例子和数据
   - 讲述不同的故事
   - 提供独特的见解
   - 确保通过原创性检测

请直接输出文章内容，包含标题。"""


class StyleImitationGenerator:
    """风格模仿内容生成器"""
    
    async def generate(
        self,
        style_analysis: Dict,
        new_topic: str,
        target_audience: str,
        word_count: int,
        keywords: List[str],
        ai_model,
        additional_requirements: str = ""
    ) -> str:
        """生成风格模仿的新文章"""
        
        style = style_analysis.get("style_profile", {})
        
        prompt = STYLE_IMITATION_PROMPT.format(
            style_profile=json.dumps(style, ensure_ascii=False, indent=2),
            title_pattern=style.get("structure", {}).get("title_pattern", "常规标题"),
            opening_hook=style.get("structure", {}).get("opening_hook", "开门见山"),
            tone=style.get("language", {}).get("tone", "专业"),
            sentence_style=style.get("language", {}).get("sentence_style", "标准"),
            reader_address=style.get("engagement", {}).get("reader_address", "你"),
            techniques=", ".join(style.get("rhetoric", {}).get("techniques", [])),
            formatting=style.get("visual", {}).get("formatting", "标准排版"),
            new_topic=new_topic,
            target_audience=target_audience,
            word_count=word_count,
            keywords=", ".join(keywords)
        )
        
        if additional_requirements:
            prompt += f"\n\n## 额外要求\n{additional_requirements}"
        
        from app.services.langchain import LangChainService
        service = LangChainService(
            provider=ai_model.provider,
            model=ai_model.model_name,
            api_key=ai_model.api_key,
            api_base=ai_model.base_url
        )
        
        response = await service.chat(prompt)
        return response.content
```

---

## 四、避免抄袭/洗稿的法律风险

### 4.1 法律风险分析

| 风险类型 | 描述 | 法律后果 |
|----------|------|----------|
| **著作权侵权** | 直接复制或实质性相似 | 民事赔偿、刑事责任 |
| **不正当竞争** | 系统性洗稿竞争对手内容 | 行政处罚、民事赔偿 |
| **名誉侵权** | 篡改原文含义造成误导 | 民事赔偿、道歉声明 |

### 4.2 技术防护措施

```python
# backend/app/services/plagiarism_checker.py

from typing import Dict, Tuple
import hashlib

class PlagiarismChecker:
    """原创性检测器"""
    
    async def check(
        self, 
        original_content: str, 
        generated_content: str,
        ai_model = None
    ) -> Dict:
        """
        检测生成内容的原创性
        
        Returns:
            {
                "is_safe": bool,
                "similarity_score": float,  # 0-1, 越低越好
                "issues": [str],
                "suggestions": [str]
            }
        """
        issues = []
        suggestions = []
        
        # 1. 文本相似度检测（基于n-gram）
        similarity = self._compute_similarity(original_content, generated_content)
        
        if similarity > 0.3:
            issues.append(f"整体相似度过高: {similarity:.1%}")
            suggestions.append("建议更换更多表达方式和例子")
        
        # 2. 连续相同片段检测
        identical_segments = self._find_identical_segments(
            original_content, 
            generated_content,
            min_length=20
        )
        
        if identical_segments:
            issues.append(f"发现 {len(identical_segments)} 处相同片段")
            suggestions.append("以下片段需要改写：" + str(identical_segments[:3]))
        
        # 3. 关键句子相似度
        key_sentence_sim = self._check_key_sentences(
            original_content, 
            generated_content
        )
        
        if key_sentence_sim > 0.5:
            issues.append("关键句子相似度过高")
            suggestions.append("建议重新组织核心观点的表达")
        
        # 4. AI辅助原创性评估（可选）
        if ai_model and (similarity > 0.2 or identical_segments):
            ai_assessment = await self._ai_originality_check(
                original_content,
                generated_content,
                ai_model
            )
            if not ai_assessment.get("is_original", True):
                issues.extend(ai_assessment.get("issues", []))
                suggestions.extend(ai_assessment.get("suggestions", []))
        
        is_safe = len(issues) == 0 and similarity < 0.2
        
        return {
            "is_safe": is_safe,
            "similarity_score": similarity,
            "identical_segments": identical_segments,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _compute_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """计算n-gram相似度"""
        def get_ngrams(text, n):
            text = text.replace(" ", "").replace("\n", "")
            return set(text[i:i+n] for i in range(len(text)-n+1))
        
        ngrams1 = get_ngrams(text1, n)
        ngrams2 = get_ngrams(text2, n)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = ngrams1 & ngrams2
        union = ngrams1 | ngrams2
        
        return len(intersection) / len(union)
    
    def _find_identical_segments(
        self, 
        text1: str, 
        text2: str, 
        min_length: int = 20
    ) -> List[str]:
        """查找相同的连续片段"""
        identical = []
        
        # 使用滑动窗口查找
        for length in range(min_length, min(len(text1), len(text2)), 5):
            for i in range(len(text2) - length + 1):
                segment = text2[i:i+length]
                if segment in text1:
                    # 尝试扩展匹配
                    expanded = self._expand_match(text1, text2, i, length)
                    if expanded not in identical and len(expanded) >= min_length:
                        identical.append(expanded)
        
        # 去重和排序
        identical = sorted(set(identical), key=len, reverse=True)[:10]
        return identical
    
    async def _ai_originality_check(
        self,
        original: str,
        generated: str,
        ai_model
    ) -> Dict:
        """AI辅助原创性检测"""
        prompt = f"""作为原创性检测专家，请比较以下两段内容，判断第二段是否为原创：

原文（参考）：
{original[:3000]}

生成内容：
{generated[:3000]}

请分析：
1. 生成内容是否存在直接复制原文的情况？
2. 核心观点的表达是否有实质性区别？
3. 案例、数据、故事是否不同？
4. 能否通过原创性检测？

输出JSON：
{{"is_original": true/false, "issues": ["问题1"], "suggestions": ["建议1"]}}"""
        
        # 调用AI进行分析
        from app.services.langchain import LangChainService
        service = LangChainService(...)
        response = await service.chat(prompt)
        
        return self._parse_json_response(response.content)
```

### 4.3 产品层面的风险规避

```python
# 在生成时强制执行的规则

SAFETY_RULES = {
    # 1. 明确用户协议
    "user_agreement": """
    用户使用本功能即表示同意：
    - 仅将生成内容用于学习和参考
    - 发布前需进行原创性检查
    - 不得用于商业侵权用途
    - 因使用不当造成的法律责任由用户承担
    """,
    
    # 2. 功能命名和定位
    "feature_naming": "风格学习" or "写作灵感" (而非 "文章复制"),
    
    # 3. 强制原创性检查
    "mandatory_check": True,
    
    # 4. 保留原文引用
    "citation_prompt": "如需引用原文观点，请注明出处",
    
    # 5. 限制使用频率
    "rate_limit": "每用户每天最多10次",
    
    # 6. 内容水印/标记
    "watermark": "[本文由AI辅助创作，请核实后发布]"
}
```

### 4.4 合规建议

1. **用户协议明确责任**：在用户使用前展示协议，明确告知风险
2. **功能定位为"学习"而非"复制"**：强调学习写作技巧，而非复制内容
3. **强制原创性检查**：生成后自动进行相似度检测
4. **保留操作日志**：记录用户操作，配合潜在调查
5. **举报机制**：提供侵权投诉渠道

---

## 五、竞品分析

### 5.1 主要竞品对比

| 产品 | 功能名称 | 实现方式 | 优点 | 缺点 |
|------|----------|----------|------|------|
| **Copy.ai** | Brand Voice | 分析多篇内容建立品牌声音模型 | 系统化、可复用 | 需要多篇样本 |
| **Jasper** | Tone of Voice | 预设风格+自定义调整 | 简单易用 | 不够精准 |
| **讯飞写作** | 仿写功能 | 直接输入原文仿写 | 简单直接 | 风险较高 |
| **秘塔写作猫** | 改写功能 | 多维度改写 | 保留度可控 | 偏向洗稿 |
| **火山引擎** | 内容理解+生成 | API形式提供 | 技术先进 | 集成成本高 |

### 5.2 最佳实践借鉴

**Copy.ai 的 Brand Voice 方案**：
- 不是单篇模仿，而是多篇学习建立声音模型
- 用户可以保存和复用风格配置
- 分析维度包括：语气、词汇、句式、人格特征

**Jasper 的 Templates + Tone**：
- 预置多种内容模板
- 用户可选择语气倾向（专业/友好/幽默等）
- 支持自定义品牌指南

### 5.3 差异化建议

我们的"爆款模仿"功能可以结合：
1. **单篇快速分析** + **风格库积累**：既支持临时分析，也支持保存为可复用的风格模板
2. **平台感知**：针对微信、小红书等平台优化分析维度
3. **合规优先**：内置原创性检测，降低法律风险

---

## 六、数据库设计

```sql
-- 风格分析结果表
CREATE TABLE style_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,  -- 风格名称
    source_url VARCHAR(500),      -- 来源URL
    source_title VARCHAR(200),    -- 来源标题
    source_platform VARCHAR(50),  -- 来源平台
    style_data JSONB NOT NULL,    -- 风格分析JSON
    is_public BOOLEAN DEFAULT FALSE,  -- 是否公开
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 爆款模仿生成记录
CREATE TABLE style_imitations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    style_profile_id INTEGER REFERENCES style_profiles(id),
    original_url VARCHAR(500),
    new_topic VARCHAR(200),
    generated_content TEXT,
    plagiarism_check JSONB,  -- 原创性检测结果
    ai_model_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_style_profiles_user ON style_profiles(user_id);
CREATE INDEX idx_style_profiles_public ON style_profiles(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_imitations_user ON style_imitations(user_id);
```

---

## 七、API 设计

```python
# backend/app/api/v1/style_imitation.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/style-imitation", tags=["风格模仿"])


class StyleAnalysisRequest(BaseModel):
    """风格分析请求"""
    url: str
    save_as_profile: bool = False
    profile_name: Optional[str] = None


class StyleAnalysisResponse(BaseModel):
    """风格分析响应"""
    success: bool
    article_title: str
    article_platform: str
    style_profile: dict
    profile_id: Optional[int] = None  # 如果保存了


class StyleImitationRequest(BaseModel):
    """风格模仿生成请求"""
    # 方式1: 使用已保存的风格
    profile_id: Optional[int] = None
    # 方式2: 直接提供URL即时分析
    source_url: Optional[str] = None
    
    # 新文章参数
    new_topic: str
    target_audience: str = "普通读者"
    word_count: int = 1500
    keywords: List[str] = []
    additional_requirements: str = ""
    
    # AI模型
    ai_model_id: Optional[int] = None


class StyleImitationResponse(BaseModel):
    """风格模仿生成响应"""
    success: bool
    content: str
    title: str
    plagiarism_check: dict
    warnings: List[str] = []


@router.post("/analyze", response_model=StyleAnalysisResponse)
async def analyze_style(request: StyleAnalysisRequest):
    """分析文章风格"""
    pass


@router.post("/generate", response_model=StyleImitationResponse)
async def generate_imitation(request: StyleImitationRequest):
    """生成风格模仿文章"""
    pass


@router.get("/profiles", response_model=List[dict])
async def list_style_profiles():
    """获取用户保存的风格模板列表"""
    pass


@router.get("/profiles/public", response_model=List[dict])
async def list_public_profiles():
    """获取公开的风格模板"""
    pass


@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int):
    """删除风格模板"""
    pass
```

---

## 八、前端界面设计

### 8.1 功能入口

在写作工具列表中新增"风格模仿"工具卡片。

### 8.2 主要界面流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      风格模仿 - 学习爆款写作技巧                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 输入参考文章                                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  文章URL: [                                        ] [分析] │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  或者选择已保存的风格模板:                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  [我的模板 ▼]  小红书种草风  |  公众号干货风  |  知乎专业风    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 2: 风格分析结果（分析后显示）                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  标题: 月薪3000到30000，我用了3年...                         │  │
│  │  平台: 微信公众号                                            │  │
│  │  ──────────────────────────────────────────────────────    │  │
│  │  风格特征:                                                  │  │
│  │  • 标题模式: 数字对比 + 时间跨度 + 悬念                       │  │
│  │  • 开篇方式: 个人故事引入                                    │  │
│  │  • 语气基调: 真诚分享、轻度励志                               │  │
│  │  • 互动风格: 亲切称呼"你"、结尾引导收藏                       │  │
│  │  ──────────────────────────────────────────────────────    │  │
│  │  [保存为模板]                                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 3: 创作新文章                                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  新文章主题: [如何在工作中建立个人品牌              ]         │  │
│  │  目标读者:   [职场新人、有晋升需求的白领            ]         │  │
│  │  关键词:     [个人品牌, 职场, 影响力, 升职          ]         │  │
│  │  字数要求:   [1500 ▼]                                       │  │
│  │  补充说明:   [                                      ]         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│                    [生成文章]                                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 4: 结果与检测                                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  原创性检测: ✅ 通过 (相似度: 8%)                            │  │
│  │  ──────────────────────────────────────────────────────    │  │
│  │  [生成的文章内容...]                                        │  │
│  │                                                            │  │
│  │  ──────────────────────────────────────────────────────    │  │
│  │  [复制] [保存] [重新生成] [编辑]                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 前端表单配置

```typescript
// frontend/src/config/writingToolForms.ts

// 新增风格模仿工具配置
style_imitation: {
  toolType: 'style_imitation',
  name: '风格模仿',
  description: '学习爆款文章的写作技巧，生成类似风格的原创内容',
  fields: [
    {
      name: 'source_url',
      label: '参考文章URL',
      type: 'url_fetch',
      required: false,
      placeholder: '输入爆款文章的URL，系统会分析其写作风格',
      urlFetchConfig: {
        contentField: '_preview',  // 用于预览
        analyzeStyle: true,        // 触发风格分析
      },
    },
    {
      name: 'profile_id',
      label: '或选择已保存的风格',
      type: 'style_profile_select',
      required: false,
      placeholder: '从已保存的风格模板中选择',
    },
    {
      name: 'new_topic',
      label: '新文章主题',
      type: 'input',
      required: true,
      placeholder: '输入你想创作的新文章主题',
      maxLength: 100,
    },
    {
      name: 'target_audience',
      label: '目标读者',
      type: 'input',
      required: false,
      placeholder: '如：职场新人、宝妈群体',
      defaultValue: '普通读者',
    },
    {
      name: 'keywords',
      label: '关键词',
      type: 'input',
      required: false,
      placeholder: '多个关键词用逗号分隔',
    },
    {
      name: 'word_count',
      label: '字数要求',
      type: 'select',
      required: false,
      defaultValue: '1500',
      options: [
        { label: '500字（短文）', value: '500' },
        { label: '1000字', value: '1000' },
        { label: '1500字', value: '1500' },
        { label: '2000字', value: '2000' },
        { label: '3000字（长文）', value: '3000' },
      ],
    },
    additionalDescriptionField,
  ],
}
```

---

## 九、实施计划

### Phase 1: MVP版本（2周）

| 任务 | 时间 | 说明 |
|------|------|------|
| 内容抓取增强 | 2天 | 支持微信、小红书、知乎等主流平台 |
| 风格分析核心 | 3天 | 实现AI风格分析，输出结构化结果 |
| 内容生成 | 2天 | 实现基于风格的内容生成 |
| 原创性检测 | 2天 | 基础相似度检测 |
| 前端界面 | 3天 | 完成基础交互流程 |
| 测试调优 | 2天 | 提示词调优，边界case处理 |

### Phase 2: 增强版本（2周）

- 风格模板保存和管理
- 公开风格库
- AI辅助原创性检测
- 批量生成能力
- 使用数据分析

### Phase 3: 高级功能（待定）

- 多篇文章综合学习
- 风格融合（A+B风格）
- 自动风格推荐
- 与其他写作工具联动

---

## 十、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 抓取被封禁 | 无法获取内容 | 使用代理池、降低频率、支持手动粘贴 |
| 生成内容质量不稳定 | 用户体验差 | 多模型支持、提示词持续优化 |
| 法律合规风险 | 平台下架 | 强化原创性检测、明确用户协议 |
| AI成本过高 | 运营压力 | 限制免费次数、优化token使用 |

---

## 十一、总结

"爆款模仿"功能的核心价值在于**帮助用户学习优秀的写作技巧**，而非简单的内容复制。通过：

1. **深度风格分析**：提取可学习的写作元素
2. **原创内容生成**：基于风格生成全新内容
3. **合规性保障**：内置检测降低法律风险

我们可以为用户提供一个既实用又安全的内容创作辅助工具。
