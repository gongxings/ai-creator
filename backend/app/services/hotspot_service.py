"""
热点追踪服务
接入 DailyHotApi 获取多平台热搜数据，并提供 AI 选题分析
"""
import httpx
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.schemas.hotspot import (
    HotspotItem,
    HotspotListResponse,
    PlatformInfo,
    WritingAngle,
    TopicSuggestResponse,
)

logger = logging.getLogger(__name__)


class HotspotService:
    """热点追踪服务"""
    
    # DailyHotApi 基础 URL（可自部署）
    BASE_URL = "https://api-hot.imsyy.top"
    
    # 支持的平台列表
    PLATFORMS = {
        "weibo": {
            "name": "微博热搜",
            "icon": "weibo",
            "color": "#E6162D",
        },
        "baidu": {
            "name": "百度热搜",
            "icon": "baidu",
            "color": "#2932E1",
        },
        "zhihu": {
            "name": "知乎热榜",
            "icon": "zhihu",
            "color": "#0084FF",
        },
        "douyin": {
            "name": "抖音热搜",
            "icon": "douyin",
            "color": "#000000",
        },
        "bilibili": {
            "name": "B站热搜",
            "icon": "bilibili",
            "color": "#FB7299",
        },
        "toutiao": {
            "name": "头条热榜",
            "icon": "toutiao",
            "color": "#F85959",
        },
        "36kr": {
            "name": "36氪热榜",
            "icon": "36kr",
            "color": "#0078FF",
        },
        "sspai": {
            "name": "少数派",
            "icon": "sspai",
            "color": "#DA282A",
        },
        "juejin": {
            "name": "掘金热榜",
            "icon": "juejin",
            "color": "#1E80FF",
        },
        "tieba": {
            "name": "百度贴吧",
            "icon": "tieba",
            "color": "#4A8FE2",
        },
    }
    
    # 写作工具与热点类型的匹配关系
    TOOL_RECOMMENDATIONS = {
        "weibo": ["wechat_article", "xiaohongshu_note", "video_script"],
        "baidu": ["wechat_article", "news_article", "video_script"],
        "zhihu": ["wechat_article", "academic_paper"],
        "douyin": ["video_script", "xiaohongshu_note"],
        "bilibili": ["video_script", "wechat_article"],
        "toutiao": ["wechat_article", "news_article"],
        "36kr": ["wechat_article", "news_article", "business_plan"],
        "sspai": ["wechat_article", "xiaohongshu_note"],
        "juejin": ["wechat_article"],
        "tieba": ["xiaohongshu_note", "video_script"],
    }
    
    @classmethod
    def get_platforms(cls) -> List[PlatformInfo]:
        """获取支持的平台列表"""
        return [
            PlatformInfo(
                code=code,
                name=info["name"],
                icon=info.get("icon"),
                color=info.get("color"),
            )
            for code, info in cls.PLATFORMS.items()
        ]
    
    @classmethod
    async def get_hot_list(
        cls,
        platform: str,
        limit: int = 20
    ) -> HotspotListResponse:
        """
        获取指定平台的热点列表
        
        Args:
            platform: 平台代码
            limit: 返回数量限制
            
        Returns:
            HotspotListResponse
        """
        if platform not in cls.PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}")
        
        url = f"{cls.BASE_URL}/{platform}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # DailyHotApi 返回格式：{ code: 200, data: [...], update_time: "..." }
                items = []
                raw_items = data.get("data", [])
                
                for idx, item in enumerate(raw_items[:limit]):
                    items.append(HotspotItem(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        hot=item.get("hot"),
                        index=idx + 1,
                        mobile_url=item.get("mobileUrl"),
                    ))
                
                return HotspotListResponse(
                    platform=platform,
                    platform_name=cls.PLATFORMS[platform]["name"],
                    update_time=data.get("update_time"),
                    items=items,
                )
                
        except httpx.TimeoutException:
            logger.error(f"获取 {platform} 热点超时")
            raise Exception(f"获取 {platform} 热点超时，请稍后重试")
        except httpx.HTTPStatusError as e:
            logger.error(f"获取 {platform} 热点失败: {e}")
            raise Exception(f"获取 {platform} 热点失败")
        except Exception as e:
            logger.error(f"获取热点异常: {e}")
            raise Exception(f"获取热点失败: {str(e)}")
    
    @classmethod
    async def get_topic_suggestions(
        cls,
        hot_title: str,
        user_domain: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
        ai_model = None,
        db = None,
    ) -> TopicSuggestResponse:
        """
        根据热点生成选题建议
        
        Args:
            hot_title: 热点标题
            user_domain: 用户领域
            target_platforms: 目标平台
            ai_model: AI 模型实例
            db: 数据库会话
            
        Returns:
            TopicSuggestResponse
        """
        from app.services.langchain import LangChainService
        
        # 构建提示词
        prompt = cls._build_topic_suggestion_prompt(
            hot_title=hot_title,
            user_domain=user_domain,
            target_platforms=target_platforms,
        )
        
        try:
            # 使用 LangChain 服务调用 AI
            if ai_model:
                service = LangChainService(
                    provider=ai_model.provider,
                    model=ai_model.model_name or "gpt-4",
                    api_key=ai_model.api_key,
                    api_base=ai_model.base_url,
                )
            else:
                # 使用默认配置（需要在环境变量中配置）
                service = LangChainService(
                    provider="openai",
                    model="gpt-3.5-turbo",
                )
            
            response = await service.chat(prompt)
            
            # 解析 AI 响应
            return cls._parse_topic_suggestions(hot_title, response.content)
            
        except Exception as e:
            logger.error(f"AI 选题分析失败: {e}")
            # 返回默认建议
            return cls._get_default_suggestions(hot_title, target_platforms)
    
    @classmethod
    def _build_topic_suggestion_prompt(
        cls,
        hot_title: str,
        user_domain: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
    ) -> str:
        """构建选题建议提示词"""
        
        domain_text = f"用户领域：{user_domain}" if user_domain else "用户领域：通用"
        platform_text = ""
        if target_platforms:
            platform_names = [cls._get_tool_name(p) for p in target_platforms]
            platform_text = f"目标平台：{', '.join(platform_names)}"
        
        return f"""你是一位资深的新媒体内容策划专家，擅长从热点事件中挖掘创作角度。

## 任务
针对以下热点，分析其背景并提供多个创作角度建议。

## 热点信息
标题：{hot_title}
{domain_text}
{platform_text}

## 请提供以下内容

1. **热点背景分析**（50-100字）
   - 简要说明这个热点的背景和为什么受关注

2. **创作角度**（提供3-5个不同角度）
   每个角度包含：
   - 角度描述：用一句话描述这个创作角度
   - 标题建议：给出一个吸引人的标题示例
   - 内容方向：简要说明内容应该怎么写
   - 推荐工具：从以下工具中选择最适合的1-2个
     * wechat_article（公众号文章）- 适合深度分析、观点输出
     * xiaohongshu_note（小红书笔记）- 适合生活化、种草、攻略
     * video_script（短视频脚本）- 适合热点速评、趣味内容
     * news_article（新闻稿）- 适合正式报道、企业宣传
     * marketing_copy（营销文案）- 适合品牌借势、产品推广
   - 目标受众：这个角度适合什么样的读者

3. **相关关键词**（5-10个）
   - 与这个热点相关的搜索关键词

## 输出格式
请严格按照以下 JSON 格式输出，不要输出其他内容：
```json
{{
  "background": "热点背景分析...",
  "angles": [
    {{
      "angle": "角度描述",
      "title_suggestion": "标题建议",
      "content_direction": "内容方向",
      "recommended_tools": ["wechat_article", "video_script"],
      "target_audience": "目标受众"
    }}
  ],
  "keywords": ["关键词1", "关键词2"]
}}
```"""
    
    @classmethod
    def _parse_topic_suggestions(
        cls,
        hot_title: str,
        ai_response: str
    ) -> TopicSuggestResponse:
        """解析 AI 返回的选题建议"""
        try:
            # 尝试提取 JSON
            json_str = ai_response
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0]
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0]
            
            data = json.loads(json_str.strip())
            
            angles = []
            for angle_data in data.get("angles", []):
                angles.append(WritingAngle(
                    angle=angle_data.get("angle", ""),
                    title_suggestion=angle_data.get("title_suggestion", ""),
                    content_direction=angle_data.get("content_direction", ""),
                    recommended_tools=angle_data.get("recommended_tools", ["wechat_article"]),
                    target_audience=angle_data.get("target_audience", ""),
                ))
            
            return TopicSuggestResponse(
                hot_title=hot_title,
                background=data.get("background", ""),
                angles=angles,
                keywords=data.get("keywords", []),
            )
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"解析 AI 响应失败: {e}, 使用默认建议")
            return cls._get_default_suggestions(hot_title)
    
    @classmethod
    def _get_default_suggestions(
        cls,
        hot_title: str,
        target_platforms: Optional[List[str]] = None,
    ) -> TopicSuggestResponse:
        """获取默认选题建议（AI 失败时的兜底）"""
        default_tools = target_platforms or ["wechat_article", "xiaohongshu_note", "video_script"]
        
        return TopicSuggestResponse(
            hot_title=hot_title,
            background=f"「{hot_title}」是当前的热门话题，引起了广泛关注。",
            angles=[
                WritingAngle(
                    angle="深度解读",
                    title_suggestion=f"深度解读：{hot_title}背后的真相",
                    content_direction="从专业角度分析事件的来龙去脉，提供独到见解",
                    recommended_tools=["wechat_article"],
                    target_audience="关注时事、喜欢深度内容的读者",
                ),
                WritingAngle(
                    angle="观点评论",
                    title_suggestion=f"关于{hot_title}，我有话说",
                    content_direction="发表个人观点，引发读者共鸣和讨论",
                    recommended_tools=["wechat_article", "xiaohongshu_note"],
                    target_audience="喜欢表达观点、参与讨论的用户",
                ),
                WritingAngle(
                    angle="趣味盘点",
                    title_suggestion=f"{hot_title}引发的那些神评论",
                    content_direction="收集有趣的网友评论和反应，轻松娱乐向",
                    recommended_tools=["xiaohongshu_note", "video_script"],
                    target_audience="喜欢轻松娱乐内容的年轻用户",
                ),
            ],
            keywords=[hot_title, "热点", "热搜", "最新消息"],
        )
    
    @classmethod
    def _get_tool_name(cls, tool_type: str) -> str:
        """获取工具中文名"""
        tool_names = {
            "wechat_article": "公众号文章",
            "xiaohongshu_note": "小红书笔记",
            "video_script": "短视频脚本",
            "news_article": "新闻稿",
            "marketing_copy": "营销文案",
            "official_document": "公文写作",
            "academic_paper": "论文写作",
        }
        return tool_names.get(tool_type, tool_type)
