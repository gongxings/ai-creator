# 一键多平台内容转换功能实现方案

## 1. 各平台内容特点分析

### 1.1 微信公众号文章
| 维度 | 特点 |
|------|------|
| **内容长度** | 1500-5000字，支持长文深度阅读 |
| **结构特点** | 标题 + 导语 + 小标题分段 + 正文 + 结尾互动 |
| **语言风格** | 正式或半正式，可深度、可轻松 |
| **排版要求** | 支持富文本、图文混排、代码块、引用 |
| **特殊元素** | 适量emoji、引导关注/转发/在看、原创声明 |
| **SEO要素** | 标题含关键词、摘要优化 |

### 1.2 小红书笔记
| 维度 | 特点 |
|------|------|
| **内容长度** | 300-1000字，精炼为主 |
| **结构特点** | 吸睛标题 + 开头痛点/亮点 + 分点罗列 + 互动引导 |
| **语言风格** | 口语化、真实感、种草感、闺蜜聊天式 |
| **排版要求** | 大量emoji分隔、符号装饰、空行分段 |
| **特殊元素** | #话题标签（5-10个）、@提及、表情符号密集 |
| **标题公式** | 数字+痛点/好处+emoji（如：3招搞定｜学生党必看） |

### 1.3 今日头条文章
| 维度 | 特点 |
|------|------|
| **内容长度** | 800-3000字，中等长度 |
| **结构特点** | 震撼标题 + 导语吸引 + 正文 + 总结 |
| **语言风格** | 通俗易懂、接地气、信息量大 |
| **排版要求** | 段落短小、图文结合、列表清晰 |
| **特殊元素** | 标题党倾向（但不过度）、悬念感、争议性 |
| **算法偏好** | 完读率、停留时长、互动率 |

### 1.4 知乎回答
| 维度 | 特点 |
|------|------|
| **内容长度** | 500-5000字，深度内容更受欢迎 |
| **结构特点** | 先说结论 + 分点论证 + 案例/数据支撑 + 总结 |
| **语言风格** | 专业、理性、有深度、适度幽默 |
| **排版要求** | 逻辑清晰、善用加粗/引用、代码块 |
| **特殊元素** | 「划重点」、引用来源、@专家、相关回答链接 |
| **调性要求** | 有理有据、避免绝对化表述 |

### 1.5 抖音/快手文案
| 维度 | 特点 |
|------|------|
| **内容长度** | 50-300字，极简 |
| **结构特点** | 开头3秒hook + 核心信息 + 行动号召 |
| **语言风格** | 口语化、节奏感、有冲击力 |
| **排版要求** | 短句、换行多、易于配音朗读 |
| **特殊元素** | #话题标签、@账号、争议性观点引发评论 |
| **节奏要求** | 适合15-60秒视频，信息密度高 |

---

## 2. 内容转换规则设计

### 2.1 公众号 → 小红书

```
转换规则：
1. 长度压缩：提取核心观点，压缩至500-800字
2. 标题改造：添加数字+emoji+痛点关键词
3. 结构重组：
   - 开头：直击痛点，1-2句话
   - 正文：3-7个要点，每点1-2句
   - 结尾：互动引导（收藏/点赞）
4. 语言转换：书面语→口语化、亲切感
5. emoji密度：每段添加2-4个相关emoji
6. 标签生成：提取5-10个#话题标签
```

### 2.2 公众号 → 今日头条

```
转换规则：
1. 长度调整：保持或略微压缩至800-2000字
2. 标题改造：增加吸引力、悬念感（不过度标题党）
3. 结构优化：
   - 导语：前100字抓住注意力
   - 正文：短段落、多分点、图文结合提示
   - 结尾：总结+引导评论
4. 语言转换：保持通俗、接地气
5. 删除公众号特有引导语（如"点击关注"）
```

### 2.3 公众号 → 知乎回答

```
转换规则：
1. 长度保持：可保持原长度或扩展
2. 结构重组：
   - 开头：先给结论/核心观点
   - 正文：分点论证、增加数据/案例
   - 结尾：总结+延伸思考
3. 语言转换：增加专业性、理性论证
4. 格式优化：善用引用块、加粗重点
5. 删除营销性质内容
```

### 2.4 长文 → 短视频脚本

```
转换规则：
1. 极致压缩：提取3-5个核心要点
2. 脚本结构：
   【开头hook】0-3秒，吸引停留
   【核心内容】分镜头展示要点
   【结尾CTA】引导点赞/关注/评论
3. 语言转换：
   - 书面语→口语化、可朗读
   - 长句→短句（每句5-15字）
   - 增加节奏感和停顿标记
4. 时长适配：
   - 15秒：1个核心观点
   - 60秒：3-5个要点
   - 3分钟：完整小主题
```

### 2.5 小红书 → 公众号

```
转换规则：
1. 长度扩展：500字→1500-2500字
2. 结构扩展：
   - 为每个要点补充详细说明
   - 增加背景介绍、原理解释
   - 添加案例和故事
3. 语言转换：口语化→半正式书面
4. 格式调整：减少emoji、规范排版
5. 增加引导：订阅、转发、在看
```

---

## 3. 数据库设计

### 3.1 内容转换记录表

```sql
CREATE TABLE content_conversions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    -- 源内容
    source_creation_id BIGINT,  -- 关联原始创作（可选）
    source_content TEXT NOT NULL,
    source_platform VARCHAR(50) NOT NULL,  -- 'wechat', 'xiaohongshu', 'toutiao', 'zhihu', 'douyin', 'kuaishou', 'general'
    
    -- 转换结果
    target_platform VARCHAR(50) NOT NULL,
    converted_content TEXT NOT NULL,
    converted_title VARCHAR(500),
    converted_tags JSON,  -- ["标签1", "标签2"]
    
    -- 转换配置
    conversion_config JSON,  -- {style: "...", length: "...", ...}
    
    -- AI相关
    model_id BIGINT,
    prompt_used TEXT,
    tokens_used INT,
    
    -- 状态
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,
    
    -- 发布关联
    publish_record_id BIGINT,  -- 如果已发布，关联发布记录
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (source_creation_id) REFERENCES creations(id),
    FOREIGN KEY (model_id) REFERENCES ai_models(id),
    FOREIGN KEY (publish_record_id) REFERENCES publish_records(id),
    INDEX idx_user_source (user_id, source_creation_id),
    INDEX idx_platforms (source_platform, target_platform)
);
```

### 3.2 转换模板表

```sql
CREATE TABLE conversion_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    source_platform VARCHAR(50) NOT NULL,
    target_platform VARCHAR(50) NOT NULL,
    
    -- 系统提示词
    system_prompt TEXT NOT NULL,
    
    -- 转换规则配置
    rules JSON,  -- {max_length: 800, emoji_density: "high", ...}
    
    -- 示例（few-shot）
    examples JSON,  -- [{input: "...", output: "..."}, ...]
    
    is_system BOOLEAN DEFAULT TRUE,  -- 系统模板不可删除
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_platforms (source_platform, target_platform, name)
);
```

---

## 4. AI提示词设计

### 4.1 通用转换提示词结构

```python
CONVERSION_PROMPT_TEMPLATE = """
你是一位专业的内容运营专家，精通各平台内容特点和转换技巧。

## 任务
将以下【{source_platform}】内容转换为适合【{target_platform}】发布的内容。

## 源平台特点
{source_platform_features}

## 目标平台特点
{target_platform_features}

## 转换规则
{conversion_rules}

## 原始内容
{original_content}

## 输出要求
请按以下JSON格式输出：
```json
{
    "title": "转换后的标题",
    "content": "转换后的正文内容",
    "tags": ["标签1", "标签2", "标签3"],
    "summary": "一句话摘要（可选）"
}
```

注意：
1. 保持原文核心信息完整
2. 完全适配目标平台风格
3. 不要添加与原文无关的内容
4. 确保输出是有效的JSON格式
"""
```

### 4.2 具体平台转换提示词

#### 公众号 → 小红书

```python
WECHAT_TO_XIAOHONGSHU_PROMPT = """
你是一位小红书爆款笔记创作专家，同时精通公众号内容。现在需要将公众号文章改编为小红书笔记。

## 公众号文章特点
- 长篇深度内容，1500-5000字
- 正式或半正式语言
- 结构化分段，小标题分隔
- 适量emoji，排版规整

## 小红书笔记特点
- 精炼内容，300-1000字
- 口语化、闺蜜聊天式语言
- 大量emoji装饰（每段2-4个）
- #话题标签 5-10个
- 标题公式：数字+痛点+emoji

## 转换要求
1. **标题改造**：使用小红书爆款标题公式
   - 示例：「3招搞定xxx｜学生党必看✨」
   - 示例：「我后悔没早点知道的xxx🥺」
   - 示例：「xxx保姆级教程｜小白也能学会💪」

2. **内容压缩**：
   - 提取3-7个核心要点
   - 每个要点1-2句话说清楚
   - 删除过于专业/深度的论述

3. **语言转化**：
   - 「您」→「姐妹们/宝子们」
   - 书面语→口语化
   - 增加语气词：真的！绝了！太香了！

4. **排版优化**：
   - 每段开头用emoji
   - 要点前用✅/💡/📌等符号
   - 适当空行，视觉舒适

5. **互动引导**：
   - 结尾加「有用记得收藏💕」
   - 或「有问题评论区见～」

## 原始公众号文章
{original_content}

## 输出格式
```json
{
    "title": "小红书风格标题（含emoji）",
    "content": "转换后的笔记正文（含emoji和排版）",
    "tags": ["#话题1", "#话题2", "#话题3", "#话题4", "#话题5"]
}
```
"""
```

#### 公众号 → 抖音文案

```python
WECHAT_TO_DOUYIN_PROMPT = """
你是一位抖音爆款文案创作专家。现在需要将公众号长文改编为抖音短视频文案/脚本。

## 公众号文章特点
- 长篇深度内容
- 书面语表达
- 完整逻辑论证

## 抖音文案特点
- 极简短小，50-300字
- 口语化，适合朗读
- 前3秒必须抓住注意力
- 节奏感强，信息密度高

## 转换要求
1. **开头hook**（前3秒）：
   - 直接抛出痛点/好奇点/争议点
   - 示例：「你知道吗？90%的人都在犯这个错！」
   - 示例：「一个方法，让我xxx提升了3倍」

2. **核心内容**：
   - 提取1-3个最核心的点
   - 每句话5-15字
   - 用「首先/然后/最后」或「第一/第二/第三」串联

3. **语言转化**：
   - 长句→短句
   - 书面→口语
   - 可直接朗读配音

4. **结尾CTA**：
   - 「点赞收藏，下次还能找到」
   - 「关注我，教你更多xxx」
   - 「评论区告诉我你的xxx」

## 视频时长选择
- 15秒版：1个核心观点
- 60秒版：3个要点快速过
- 3分钟版：完整讲清一个小主题

## 原始公众号文章
{original_content}

## 目标时长
{target_duration}

## 输出格式
```json
{
    "hook": "开头吸引句（3秒内说完）",
    "script": "完整文案（含分段标记）",
    "cta": "结尾行动号召",
    "tags": ["#话题1", "#话题2", "#话题3"],
    "estimated_duration": "预估时长"
}
```
"""
```

#### 公众号 → 知乎回答

```python
WECHAT_TO_ZHIHU_PROMPT = """
你是一位知乎高赞回答创作专家。现在需要将公众号文章改编为知乎回答风格。

## 公众号文章特点
- 可能有营销导向
- 软性表达较多
- 有公众号特有引导语

## 知乎回答特点
- 先说结论，再展开论证
- 理性、专业、有深度
- 数据和案例支撑
- 「划重点」「敲黑板」等特色表达
- 适度幽默，但不浮夸

## 转换要求
1. **结构重组**：
   - 开头：直接给出结论/核心观点
   - 正文：分点论证（用加粗标记要点）
   - 结尾：总结+延伸思考

2. **内容强化**：
   - 补充数据来源（如有）
   - 增加「为什么」的解释
   - 适当增加案例佐证

3. **语言调整**：
   - 删除营销性内容
   - 「我认为」→「从xxx角度来看」
   - 避免绝对化表述，增加「相对/通常/一般而言」

4. **格式优化**：
   - 使用引用块强调重点
   - **加粗**关键词
   - 适当使用分割线

5. **知乎特色**：
   - 开头可用「谢邀」（可选）
   - 可用「利益相关：xxx」声明
   - 结尾可用「以上，希望对你有帮助」

## 原始公众号文章
{original_content}

## 输出格式
```json
{
    "title": "如果需要拟标题（知乎问题格式）",
    "content": "转换后的知乎回答",
    "summary": "一句话核心观点"
}
```
"""
```

#### 公众号 → 今日头条

```python
WECHAT_TO_TOUTIAO_PROMPT = """
你是一位今日头条爆文创作专家。现在需要将公众号文章改编为头条文章。

## 公众号文章特点
- 可能较为深度学术化
- 有公众号特有元素
- 目标读者可能较固定

## 今日头条特点
- 标题吸引力强（但不过度标题党）
- 内容通俗易懂，面向大众
- 段落短小，阅读轻松
- 追求完读率和互动

## 转换要求
1. **标题改造**：
   - 增加吸引力和悬念感
   - 可适当使用数字、疑问
   - 示例：「为什么xxx？真相让人意外」
   - 示例：「xxx的3个秘密，第2个最关键」

2. **内容优化**：
   - 段落控制在3-5行
   - 增加小标题分隔
   - 开头100字内抓住注意力

3. **语言调整**：
   - 专业术语→通俗解释
   - 保持口语化、接地气
   - 增加与读者的对话感

4. **删除/替换**：
   - 删除「点击关注公众号」等引导
   - 删除过于专业深奥的内容
   - 替换为「点赞+评论」引导

## 原始公众号文章
{original_content}

## 输出格式
```json
{
    "title": "今日头条风格标题",
    "content": "转换后的文章正文",
    "summary": "文章摘要（100字内）"
}
```
"""
```

### 4.3 批量转换提示词

```python
BATCH_CONVERSION_PROMPT = """
你是一位全平台内容运营专家，精通各平台内容特点。现在需要将一篇内容同时转换为多个平台版本。

## 原始内容
{original_content}

## 源平台
{source_platform}

## 需要转换的目标平台
{target_platforms}

## 各平台特点速查
- **小红书**：口语化、emoji密集、#标签、300-1000字
- **抖音**：极简、hook式开头、50-300字
- **知乎**：专业理性、先说结论、数据支撑
- **头条**：通俗易懂、短段落、标题吸引
- **快手**：接地气、真实感、老铁文化

## 输出要求
为每个目标平台输出适配的内容版本。

```json
{
    "conversions": [
        {
            "platform": "xiaohongshu",
            "title": "...",
            "content": "...",
            "tags": [...]
        },
        {
            "platform": "douyin",
            "title": "...",
            "content": "...",
            "tags": [...]
        }
        // ... 其他平台
    ]
}
```
"""
```

---

## 5. 后端实现设计

### 5.1 目录结构

```
backend/app/
├── services/
│   └── conversion/
│       ├── __init__.py
│       ├── converter.py          # 核心转换服务
│       ├── prompts.py            # 提示词模板
│       ├── rules.py              # 转换规则配置
│       └── platforms/
│           ├── __init__.py
│           ├── base.py           # 平台适配器基类
│           ├── wechat.py
│           ├── xiaohongshu.py
│           ├── douyin.py
│           ├── toutiao.py
│           ├── zhihu.py
│           └── kuaishou.py
├── models/
│   └── conversion.py             # 转换记录模型
├── schemas/
│   └── conversion.py             # 请求/响应Schema
└── api/v1/
    └── conversion.py             # API接口
```

### 5.2 核心服务实现

```python
# backend/app/services/conversion/converter.py

from typing import Dict, Any, List, Optional
from enum import Enum
import json
import logging
from sqlalchemy.orm import Session

from app.models.conversion import ContentConversion
from app.models.ai_model import AIModel
from app.services.langchain import LangChainService
from .prompts import ConversionPrompts
from .rules import PLATFORM_RULES

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    """支持的平台"""
    WECHAT = "wechat"           # 微信公众号
    XIAOHONGSHU = "xiaohongshu" # 小红书
    TOUTIAO = "toutiao"         # 今日头条
    ZHIHU = "zhihu"             # 知乎
    DOUYIN = "douyin"           # 抖音
    KUAISHOU = "kuaishou"       # 快手
    GENERAL = "general"         # 通用/其他


class ContentConverterService:
    """内容转换服务"""
    
    # 平台特点描述
    PLATFORM_FEATURES = {
        Platform.WECHAT: """
- 长篇深度内容（1500-5000字）
- 正式或半正式语言风格
- 小标题分段，结构化排版
- 适量emoji，引导关注/转发
""",
        Platform.XIAOHONGSHU: """
- 精炼内容（300-1000字）
- 口语化、闺蜜聊天式
- 大量emoji装饰
- #话题标签 5-10个
- 标题公式：数字+痛点+emoji
""",
        Platform.DOUYIN: """
- 极简短小（50-300字）
- 前3秒hook抓注意力
- 口语化，适合朗读配音
- 节奏感强，短句为主
""",
        Platform.TOUTIAO: """
- 中等长度（800-2000字）
- 标题吸引力强
- 段落短小，通俗易懂
- 追求完读率和互动
""",
        Platform.ZHIHU: """
- 深度内容优先
- 先说结论，分点论证
- 理性专业，数据支撑
- 善用引用和加粗
""",
        Platform.KUAISHOU: """
- 接地气、真实感
- 口语化、老铁文化
- 短视频文案为主
- 情感共鸣强
"""
    }
    
    def __init__(self, db: Session, ai_model: AIModel):
        self.db = db
        self.ai_model = ai_model
        self.langchain_service = LangChainService(
            provider=ai_model.provider,
            model=ai_model.model_name,
            api_key=ai_model.api_key,
            api_base=ai_model.base_url,
        )
    
    async def convert(
        self,
        user_id: int,
        source_content: str,
        source_platform: Platform,
        target_platform: Platform,
        source_creation_id: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        转换内容到目标平台
        
        Args:
            user_id: 用户ID
            source_content: 源内容
            source_platform: 源平台
            target_platform: 目标平台
            source_creation_id: 源创作ID（可选）
            config: 额外配置（如视频时长等）
            
        Returns:
            转换结果
        """
        # 构建转换提示词
        prompt = self._build_conversion_prompt(
            source_content=source_content,
            source_platform=source_platform,
            target_platform=target_platform,
            config=config
        )
        
        # 调用AI进行转换
        response = await self.langchain_service.chat(prompt)
        
        # 解析响应
        result = self._parse_response(response.content)
        
        # 保存转换记录
        conversion = ContentConversion(
            user_id=user_id,
            source_creation_id=source_creation_id,
            source_content=source_content,
            source_platform=source_platform.value,
            target_platform=target_platform.value,
            converted_content=result.get("content", ""),
            converted_title=result.get("title"),
            converted_tags=result.get("tags"),
            conversion_config=config,
            model_id=self.ai_model.id,
            prompt_used=prompt,
            status="completed"
        )
        self.db.add(conversion)
        self.db.commit()
        
        return {
            "conversion_id": conversion.id,
            **result
        }
    
    async def batch_convert(
        self,
        user_id: int,
        source_content: str,
        source_platform: Platform,
        target_platforms: List[Platform],
        source_creation_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        批量转换到多个平台
        """
        results = []
        
        # 可以优化为并行处理
        for target in target_platforms:
            result = await self.convert(
                user_id=user_id,
                source_content=source_content,
                source_platform=source_platform,
                target_platform=target,
                source_creation_id=source_creation_id
            )
            results.append(result)
        
        return results
    
    def _build_conversion_prompt(
        self,
        source_content: str,
        source_platform: Platform,
        target_platform: Platform,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建转换提示词"""
        
        # 获取特定平台组合的提示词
        specific_prompt = ConversionPrompts.get_prompt(
            source_platform, target_platform
        )
        
        if specific_prompt:
            return specific_prompt.format(
                original_content=source_content,
                **(config or {})
            )
        
        # 使用通用提示词
        conversion_rules = PLATFORM_RULES.get(
            (source_platform, target_platform),
            self._get_generic_rules(source_platform, target_platform)
        )
        
        return ConversionPrompts.GENERIC_TEMPLATE.format(
            source_platform=source_platform.value,
            target_platform=target_platform.value,
            source_platform_features=self.PLATFORM_FEATURES.get(source_platform, ""),
            target_platform_features=self.PLATFORM_FEATURES.get(target_platform, ""),
            conversion_rules=conversion_rules,
            original_content=source_content
        )
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 解析失败，返回原始内容
            return {
                "content": response,
                "title": None,
                "tags": []
            }
    
    def _get_generic_rules(
        self,
        source: Platform,
        target: Platform
    ) -> str:
        """获取通用转换规则"""
        rules = []
        
        # 长度调整规则
        length_map = {
            Platform.WECHAT: 2500,
            Platform.XIAOHONGSHU: 600,
            Platform.DOUYIN: 150,
            Platform.TOUTIAO: 1200,
            Platform.ZHIHU: 2000,
            Platform.KUAISHOU: 150
        }
        
        source_len = length_map.get(source, 1500)
        target_len = length_map.get(target, 1500)
        
        if target_len < source_len * 0.5:
            rules.append(f"大幅压缩内容至{target_len}字左右")
        elif target_len > source_len * 1.5:
            rules.append(f"扩展内容至{target_len}字左右")
        
        # 风格调整规则
        if target == Platform.XIAOHONGSHU:
            rules.extend([
                "添加大量emoji表情",
                "语言改为口语化、闺蜜聊天式",
                "生成5-10个相关#话题标签"
            ])
        elif target == Platform.DOUYIN:
            rules.extend([
                "开头3秒必须有吸引力",
                "使用短句，每句5-15字",
                "适合朗读配音"
            ])
        elif target == Platform.ZHIHU:
            rules.extend([
                "开头先给结论",
                "增加专业性和数据支撑",
                "使用引用块和加粗"
            ])
        
        return "\n".join(f"- {r}" for r in rules)
```

### 5.3 API接口设计

```python
# backend/app/api/v1/conversion.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.ai_model import AIModel
from app.services.conversion import ContentConverterService, Platform

router = APIRouter(prefix="/conversion", tags=["内容转换"])


class ConversionRequest(BaseModel):
    """转换请求"""
    source_content: str
    source_platform: Platform
    target_platform: Platform
    source_creation_id: Optional[int] = None
    config: Optional[dict] = None
    model_id: Optional[int] = None


class BatchConversionRequest(BaseModel):
    """批量转换请求"""
    source_content: str
    source_platform: Platform
    target_platforms: List[Platform]
    source_creation_id: Optional[int] = None
    model_id: Optional[int] = None


class ConversionResponse(BaseModel):
    """转换响应"""
    conversion_id: int
    title: Optional[str]
    content: str
    tags: Optional[List[str]]
    target_platform: str


@router.post("/convert", response_model=ConversionResponse)
async def convert_content(
    request: ConversionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """单平台转换"""
    # 获取AI模型
    model_id = request.model_id
    if not model_id:
        ai_model = db.query(AIModel).filter(AIModel.is_default == True).first()
    else:
        ai_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    
    if not ai_model:
        raise HTTPException(status_code=400, detail="请先配置AI模型")
    
    service = ContentConverterService(db, ai_model)
    
    result = await service.convert(
        user_id=current_user.id,
        source_content=request.source_content,
        source_platform=request.source_platform,
        target_platform=request.target_platform,
        source_creation_id=request.source_creation_id,
        config=request.config
    )
    
    return ConversionResponse(
        conversion_id=result["conversion_id"],
        title=result.get("title"),
        content=result["content"],
        tags=result.get("tags"),
        target_platform=request.target_platform.value
    )


@router.post("/batch-convert", response_model=List[ConversionResponse])
async def batch_convert_content(
    request: BatchConversionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量多平台转换"""
    # 获取AI模型
    ai_model = db.query(AIModel).filter(
        AIModel.id == request.model_id if request.model_id else AIModel.is_default == True
    ).first()
    
    if not ai_model:
        raise HTTPException(status_code=400, detail="请先配置AI模型")
    
    service = ContentConverterService(db, ai_model)
    
    results = await service.batch_convert(
        user_id=current_user.id,
        source_content=request.source_content,
        source_platform=request.source_platform,
        target_platforms=request.target_platforms,
        source_creation_id=request.source_creation_id
    )
    
    return [
        ConversionResponse(
            conversion_id=r["conversion_id"],
            title=r.get("title"),
            content=r["content"],
            tags=r.get("tags"),
            target_platform=platform.value
        )
        for r, platform in zip(results, request.target_platforms)
    ]


@router.get("/history")
async def get_conversion_history(
    source_creation_id: Optional[int] = None,
    target_platform: Optional[Platform] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取转换历史"""
    from app.models.conversion import ContentConversion
    
    query = db.query(ContentConversion).filter(
        ContentConversion.user_id == current_user.id
    )
    
    if source_creation_id:
        query = query.filter(ContentConversion.source_creation_id == source_creation_id)
    if target_platform:
        query = query.filter(ContentConversion.target_platform == target_platform.value)
    
    total = query.count()
    items = query.order_by(ContentConversion.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/platforms")
async def get_supported_platforms():
    """获取支持的平台列表"""
    return [
        {"value": p.value, "label": PLATFORM_LABELS[p]}
        for p in Platform
    ]


PLATFORM_LABELS = {
    Platform.WECHAT: "微信公众号",
    Platform.XIAOHONGSHU: "小红书",
    Platform.TOUTIAO: "今日头条",
    Platform.ZHIHU: "知乎",
    Platform.DOUYIN: "抖音",
    Platform.KUAISHOU: "快手",
    Platform.GENERAL: "通用"
}
```

---

## 6. 前端实现设计

### 6.1 新增组件

```
frontend/src/
├── views/
│   └── conversion/
│       └── ContentConverter.vue    # 内容转换页面
├── components/
│   └── conversion/
│       ├── PlatformSelector.vue    # 平台选择器
│       ├── ContentPreview.vue      # 转换预览
│       └── ConversionHistory.vue   # 转换历史
├── api/
│   └── conversion.ts               # 转换API
└── types/
    └── conversion.ts               # 类型定义
```

### 6.2 核心页面设计

```vue
<!-- ContentConverter.vue -->
<template>
  <div class="content-converter">
    <!-- 左侧：源内容 -->
    <div class="source-panel">
      <div class="panel-header">
        <h3>源内容</h3>
        <PlatformSelector v-model="sourcePlatform" label="来源平台" />
      </div>
      
      <!-- 可选：从历史记录选择 -->
      <div class="source-selector">
        <el-button @click="selectFromHistory">从创作历史选择</el-button>
        <el-button @click="fetchFromUrl">从URL抓取</el-button>
      </div>
      
      <el-input
        v-model="sourceContent"
        type="textarea"
        :rows="15"
        placeholder="粘贴需要转换的内容..."
      />
    </div>
    
    <!-- 中间：转换控制 -->
    <div class="control-panel">
      <h3>转换到</h3>
      
      <!-- 目标平台多选 -->
      <div class="target-platforms">
        <el-checkbox-group v-model="targetPlatforms">
          <el-checkbox v-for="p in platforms" :key="p.value" :label="p.value">
            <span class="platform-icon">{{ p.icon }}</span>
            {{ p.label }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      
      <!-- 快捷操作 -->
      <div class="quick-actions">
        <el-button @click="selectAll">全选</el-button>
        <el-button @click="selectNone">清空</el-button>
      </div>
      
      <!-- 转换按钮 -->
      <el-button 
        type="primary" 
        size="large"
        :loading="converting"
        @click="doConvert"
      >
        一键转换
      </el-button>
    </div>
    
    <!-- 右侧：转换结果 -->
    <div class="result-panel">
      <el-tabs v-model="activeTab">
        <el-tab-pane 
          v-for="result in conversionResults" 
          :key="result.platform"
          :label="getPlatformLabel(result.platform)"
          :name="result.platform"
        >
          <ContentPreview
            :title="result.title"
            :content="result.content"
            :tags="result.tags"
            :platform="result.platform"
            @copy="copyContent(result)"
            @publish="publishContent(result)"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>
```

---

## 7. 是否需要保存原文与转换后内容的关联？

### 建议：是的，需要保存关联

#### 7.1 关联关系设计

```
Creation (原始创作)
    │
    ├── ContentConversion (转换记录1) → 小红书版本
    │       └── PublishRecord (发布记录)
    │
    ├── ContentConversion (转换记录2) → 抖音版本
    │       └── PublishRecord (发布记录)
    │
    └── ContentConversion (转换记录3) → 知乎版本
            └── PublishRecord (发布记录)
```

#### 7.2 保存关联的好处

| 好处 | 说明 |
|------|------|
| **内容溯源** | 知道每个平台版本来自哪篇原文 |
| **批量管理** | 一键查看/编辑/删除某篇文章的所有平台版本 |
| **数据分析** | 分析哪类内容在哪个平台表现好 |
| **版本同步** | 原文更新后，可提示重新转换 |
| **避免重复** | 检测是否已转换过，避免重复工作 |

#### 7.3 关联字段设计

```python
class ContentConversion(Base):
    # ... 其他字段
    
    # 源内容关联
    source_creation_id = Column(BigInteger, ForeignKey("creations.id"))
    source_creation = relationship("Creation", backref="conversions")
    
    # 发布关联
    publish_record_id = Column(BigInteger, ForeignKey("publish_records.id"))
    publish_record = relationship("PublishRecord")
```

---

## 8. 实现优先级建议

### Phase 1: 核心功能（1-2周）
- [x] 数据库模型设计
- [ ] 公众号 → 小红书转换
- [ ] 公众号 → 抖音/快手转换
- [ ] 基础API和前端页面

### Phase 2: 扩展平台（1周）
- [ ] 公众号 → 知乎转换
- [ ] 公众号 → 今日头条转换
- [ ] 批量转换功能

### Phase 3: 优化增强（1周）
- [ ] 转换质量优化（Few-shot示例）
- [ ] 一键发布到目标平台
- [ ] 转换历史和统计

### Phase 4: 高级功能（可选）
- [ ] 自定义转换模板
- [ ] A/B测试多版本
- [ ] AI自动评估转换质量

---

## 9. 总结

本方案设计了一个完整的多平台内容转换系统：

1. **平台差异分析**：详细梳理了6个主流平台的内容特点
2. **转换规则设计**：针对各平台组合设计了具体的转换规则
3. **AI提示词设计**：提供了通用模板和平台特定的提示词
4. **数据库设计**：支持转换记录、内容关联、发布追踪
5. **后端架构**：模块化的转换服务设计
6. **前端交互**：一键多平台转换的用户界面
7. **关联存储**：建议保存原文与转换内容的关联关系

该方案可以无缝集成到现有的 ai-creator 项目中，复用已有的 AI 调用、发布等基础设施。
