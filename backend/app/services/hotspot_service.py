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
    CategoryInfo,
    WritingAngle,
    TopicSuggestResponse,
)

logger = logging.getLogger(__name__)


class HotspotService:
    """热点追踪服务"""
    
    # DailyHotApi 基础 URL（可自部署）
    BASE_URL = "https://apinews.geekaso.com"
    
    # 分类定义
    CATEGORIES = {
        "all": {"name": "全部", "order": 0},
        "social": {"name": "社交媒体", "order": 1},
        "news": {"name": "新闻资讯", "order": 2},
        "tech": {"name": "科技数码", "order": 3},
        "dev": {"name": "开发者", "order": 4},
        "knowledge": {"name": "知识社区", "order": 5},
        "game": {"name": "游戏动漫", "order": 6},
        "entertainment": {"name": "影音娱乐", "order": 7},
        "international": {"name": "国际媒体", "order": 8},
        "other": {"name": "其他", "order": 9},
    }
    
    # 支持的平台列表（约60个）
    PLATFORMS = {
        # === 社交媒体 ===
        "weibo": {"name": "微博", "category": "social", "color": "#E6162D"},
        "douyin": {"name": "抖音", "category": "social", "color": "#000000"},
        "kuaishou": {"name": "快手", "category": "social", "color": "#FF5722"},
        "bilibili": {"name": "B站", "category": "social", "color": "#FB7299"},
        "acfun": {"name": "A站", "category": "social", "color": "#FD4C5D"},
        
        # === 新闻资讯 ===
        # 百度 API 暂时有问题，先注释掉
        # "baidu": {
        #     "name": "百度",
        #     "category": "news",
        #     "color": "#2932E1",
        #     "subtypes": {
        #         "realtime": "热搜",
        #         "car": "汽车",
        #         "game": "游戏",
        #         "movie": "电影",
        #         "novel": "小说",
        #         "teleplay": "电视剧",
        #     }
        # },
        "toutiao": {"name": "头条", "category": "news", "color": "#F85959"},
        "thepaper": {"name": "澎湃新闻", "category": "news", "color": "#1A1A1A"},
        "sina": {"name": "新浪", "category": "news", "color": "#E6162D"},
        "sina-news": {"name": "新浪新闻", "category": "news", "color": "#E6162D"},
        "netease-news": {"name": "网易新闻", "category": "news", "color": "#C4282D"},
        "qq-news": {"name": "腾讯新闻", "category": "news", "color": "#0066FF"},
        
        # === 科技数码 ===
        "36kr": {"name": "36氪", "category": "tech", "color": "#0078FF"},
        "ithome": {"name": "IT之家", "category": "tech", "color": "#D32F2F"},
        "ithome-xijiayi": {"name": "喜加一", "category": "tech", "color": "#4CAF50"},
        "sspai": {"name": "少数派", "category": "tech", "color": "#DA282A"},
        "dgtle": {"name": "数字尾巴", "category": "tech", "color": "#00BCD4"},
        "ifanr": {"name": "爱范儿", "category": "tech", "color": "#E91E63"},
        "geekpark": {"name": "极客公园", "category": "tech", "color": "#00C853"},
        "coolapk": {"name": "酷安", "category": "tech", "color": "#11A96D"},
        
        # === 开发者 ===
        "github": {"name": "GitHub", "category": "dev", "color": "#24292F"},
        "juejin": {"name": "掘金", "category": "dev", "color": "#1E80FF"},
        "csdn": {"name": "CSDN", "category": "dev", "color": "#FC5531"},
        "v2ex": {"name": "V2EX", "category": "dev", "color": "#333333"},
        "nodeseek": {"name": "NodeSeek", "category": "dev", "color": "#5C6BC0"},
        "hostloc": {"name": "全球主机", "category": "dev", "color": "#2196F3"},
        "51cto": {"name": "51CTO", "category": "dev", "color": "#E53935"},
        "hellogithub": {"name": "HelloGitHub", "category": "dev", "color": "#3F51B5"},
        "hackernews": {"name": "HackerNews", "category": "dev", "color": "#FF6600"},
        "producthunt": {"name": "ProductHunt", "category": "dev", "color": "#DA552F"},
        
        # === 知识社区 ===
        "zhihu": {"name": "知乎", "category": "knowledge", "color": "#0084FF"},
        "zhihu-daily": {"name": "知乎日报", "category": "knowledge", "color": "#0084FF"},
        "tieba": {"name": "贴吧", "category": "knowledge", "color": "#4A8FE2"},
        "douban-group": {"name": "豆瓣小组", "category": "knowledge", "color": "#00B51D"},
        "jianshu": {"name": "简书", "category": "knowledge", "color": "#EA6F5A"},
        "guokr": {"name": "果壳", "category": "knowledge", "color": "#87C040"},
        "linuxdo": {"name": "LinuxDo", "category": "knowledge", "color": "#FFA500"},
        "newsmth": {"name": "水木社区", "category": "knowledge", "color": "#006400"},
        
        # === 游戏动漫 ===
        "miyoushe": {"name": "米游社", "category": "game", "color": "#00BFFF"},
        "genshin": {"name": "原神", "category": "game", "color": "#00BFFF"},
        "honkai": {"name": "崩坏3", "category": "game", "color": "#FF6B81"},
        "starrail": {"name": "星穹铁道", "category": "game", "color": "#6B5CE7"},
        "lol": {"name": "英雄联盟", "category": "game", "color": "#C89B3C"},
        "ngabbs": {"name": "NGA", "category": "game", "color": "#7B1FA2"},
        "gameres": {"name": "GameRes", "category": "game", "color": "#FF5722"},
        "yystv": {"name": "游研社", "category": "game", "color": "#FF4081"},
        
        # === 影音娱乐 ===
        "douban-movie": {"name": "豆瓣电影", "category": "entertainment", "color": "#00B51D"},
        "weread": {"name": "微信读书", "category": "entertainment", "color": "#1AAD19"},
        "hupu": {"name": "虎扑", "category": "entertainment", "color": "#E31E26"},
        "smzdm": {"name": "什么值得买", "category": "entertainment", "color": "#E53935"},
        
        # === 国际媒体 ===
        "theverge": {"name": "TheVerge", "category": "international", "color": "#E91E63"},
        "engadget": {"name": "Engadget", "category": "international", "color": "#FF5500"},
        "techcrunch": {"name": "TechCrunch", "category": "international", "color": "#0A9E01"},
        "nytimes": {"name": "纽约时报", "category": "international", "color": "#000000"},
        "theguardian": {"name": "卫报", "category": "international", "color": "#052962"},
        "economist": {"name": "经济学人", "category": "international", "color": "#E3120B"},
        
        # === 其他 ===
        "52pojie": {"name": "吾爱破解", "category": "other", "color": "#1E88E5"},
        "huxiu": {"name": "虎嗅", "category": "other", "color": "#FF9800"},
        "weatheralarm": {"name": "气象预警", "category": "other", "color": "#FF5722"},
        "earthquake": {"name": "地震速报", "category": "other", "color": "#B71C1C"},
        "history": {"name": "历史上的今天", "category": "other", "color": "#795548"},
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
    def get_categories(cls) -> List[CategoryInfo]:
        """获取分类列表"""
        return [
            CategoryInfo(
                code=code,
                name=info["name"],
                order=info["order"],
            )
            for code, info in sorted(cls.CATEGORIES.items(), key=lambda x: x[1]["order"])
        ]
    
    @classmethod
    def get_platforms(cls) -> List[PlatformInfo]:
        """获取支持的平台列表"""
        return [
            PlatformInfo(
                code=code,
                name=info["name"],
                category=info["category"],
                icon=info.get("icon"),
                color=info.get("color"),
                subtypes=info.get("subtypes"),
            )
            for code, info in cls.PLATFORMS.items()
        ]
    
    @classmethod
    async def get_hot_list(
        cls,
        platform: str,
        limit: int = 20,
        subtype: Optional[str] = None,
    ) -> HotspotListResponse:
        """
        获取指定平台的热点列表
        
        Args:
            platform: 平台代码
            limit: 返回数量限制
            subtype: 子类型（如百度的 realtime/car/game 等）
            
        Returns:
            HotspotListResponse
        """
        if platform not in cls.PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}")
        
        # 构建 URL
        url = f"{cls.BASE_URL}/{platform}"
        params = {}
        
        # 百度特殊处理：支持 type 参数
        if platform == "baidu" and subtype:
            params["type"] = subtype
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params if params else None)
                response.raise_for_status()
                data = response.json()
                
                # DailyHotApi 返回格式：{ code: 200, data: [...], update_time: "..." }
                items = []
                raw_items = data.get("data", [])
                
                for idx, item in enumerate(raw_items[:limit]):
                    # 处理热度值
                    hot_value = item.get("hot")
                    if hot_value is not None:
                        try:
                            hot_value = int(hot_value)
                        except (ValueError, TypeError):
                            hot_value = None
                    
                    items.append(HotspotItem(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        hot=hot_value,
                        index=idx + 1,
                        mobile_url=item.get("mobileUrl"),
                    ))
                
                # 获取平台名称（如果有 subtype，添加子类型名称）
                platform_name = cls.PLATFORMS[platform]["name"]
                if platform == "baidu" and subtype:
                    subtypes = cls.PLATFORMS[platform].get("subtypes", {})
                    subtype_name = subtypes.get(subtype, "")
                    if subtype_name:
                        platform_name = f"百度{subtype_name}"
                
                return HotspotListResponse(
                    platform=platform,
                    platform_name=platform_name,
                    update_time=data.get("updateTime") or data.get("update_time"),
                    items=items,
                )
                
        except httpx.TimeoutException:
            logger.error(f"获取 {platform} 热点超时")
            return cls._get_mock_hotlist(platform, limit)
        except httpx.HTTPStatusError as e:
            logger.error(f"获取 {platform} 热点失败: {e}")
            return cls._get_mock_hotlist(platform, limit)
        except Exception as e:
            logger.error(f"获取热点异常: {e}")
            return cls._get_mock_hotlist(platform, limit)
    
    @classmethod
    def _get_mock_hotlist(cls, platform: str, limit: int = 20) -> HotspotListResponse:
        """获取模拟热点数据（API 不可用时的兜底）"""
        mock_data = {
            "weibo": [
                "AI 技术最新突破引发热议",
                "春季养生指南：这些习惯要注意",
                "2024年职场新趋势盘点",
                "新能源汽车销量再创新高",
                "健康饮食：专家推荐的食谱",
                "远程办公效率提升技巧",
                "理财小白入门指南",
                "亲子教育：如何培养孩子的阅读习惯",
                "旅游攻略：小众目的地推荐",
                "科技改变生活：智能家居新品",
            ],
            "zhihu": [
                "如何看待 AI 对就业市场的影响？",
                "有哪些值得推荐的自我提升方法？",
                "年轻人如何做好职业规划？",
                "怎样才能提高工作效率？",
                "如何培养良好的阅读习惯？",
                "有哪些实用的理财建议？",
                "如何平衡工作与生活？",
                "学习一门新技能需要多长时间？",
                "如何提升自己的表达能力？",
                "有哪些值得学习的思维方式？",
            ],
            "douyin": [
                "这个技巧太实用了 #生活小妙招",
                "原来还可以这样做 #美食教程",
                "一分钟学会 #干货分享",
                "太治愈了 #日常vlog",
                "这也太好看了 #穿搭分享",
                "绝绝子 #好物推荐",
                "笑死我了 #搞笑日常",
                "这波操作可以 #技术流",
                "新手必看 #入门教程",
                "真的很有用 #知识分享",
            ],
        }
        
        # 获取对应平台的模拟数据，如果没有则使用微博的
        titles = mock_data.get(platform, mock_data["weibo"])
        
        items = []
        for idx, title in enumerate(titles[:limit]):
            items.append(HotspotItem(
                title=title,
                url="",
                hot=(limit - idx) * 10000,
                index=idx + 1,
                mobile_url=None,
            ))
        
        platform_info = cls.PLATFORMS.get(platform, {"name": platform, "category": "other"})
        
        return HotspotListResponse(
            platform=platform,
            platform_name=platform_info["name"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (模拟数据)",
            items=items,
        )
    
    @classmethod
    async def get_topic_suggestions(
        cls,
        hot_title: str,
        url: Optional[str] = None,
        user_domain: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
        ai_model = None,
        db = None,
    ) -> TopicSuggestResponse:
        """
        根据热点生成选题建议
        
        Args:
            hot_title: 热点标题
            url: 可选的热点链接
            user_domain: 用户领域
            target_platforms: 目标平台
            ai_model: AI 模型实例
            db: 数据库会话
            
        Returns:
            TopicSuggestResponse
        """
        from app.services.langchain import LangChainService
        
        logger.info(f"选题建议请求: title={hot_title}, url={url}")
        
        # 如果有URL，先获取内容
        article_content = ""
        if url:
            # 检查是否是视频平台链接
            video_domains = ['kuaishou', 'douyin', 'bilibili', 'youku', 'iqiyi', 'qq.com/video']
            is_video_url = any(domain in url.lower() for domain in video_domains)
            
            if is_video_url:
                logger.info(f"检测到视频链接，跳过内容抓取: {url}")
                # 视频链接无法直接获取内容，只基于标题生成
                article_content = ""
            else:
                logger.info(f"获取热点文章内容: {url}")
                try:
                    from app.services.plugins.registry import PluginRegistry
                    plugin_class = PluginRegistry.get_class("web_fetch")
                    if plugin_class:
                        plugin = plugin_class()
                        fetch_result = await plugin.execute(url=url)
                        if fetch_result.get("success"):
                            article_content = fetch_result.get("data", {}).get("content", "")
                            content_title = fetch_result.get("data", {}).get("title", "")
                            logger.info(f"成功获取内容: title={content_title}, length={len(article_content)}")
                        else:
                            logger.warning(f"获取内容失败: {fetch_result.get('error')}")
                    else:
                        logger.warning("web_fetch 插件未找到")
                except Exception as e:
                    logger.error(f"获取热点内容失败: {e}")
        
        # 构建提示词
        prompt = cls._build_topic_suggestion_prompt(
            hot_title=hot_title,
            article_content=article_content if article_content else None,
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
        article_content: Optional[str] = None,
        user_domain: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
    ) -> str:
        """构建选题建议提示词"""
        
        domain_text = f"用户领域：{user_domain}" if user_domain else "用户领域：通用"
        platform_text = ""
        if target_platforms:
            platform_names = [cls._get_tool_name(p) for p in target_platforms]
            platform_text = f"目标平台：{', '.join(platform_names)}"
        
        # 如果有文章内容，添加到提示词中
        content_text = ""
        if article_content:
            content_text = f"\n## 热点文章内容\n以下是热点文章的实际内容，请仔细阅读并基于内容进行分析：\n{article_content[:5000]}"
        
        return f"""你是一位资深的新媒体内容策划专家，擅长从热点事件中挖掘创作角度。

## 任务
针对以下热点，分析其背景并提供多个创作角度建议。

## 热点信息
标题：{hot_title}
{domain_text}
{platform_text}
{content_text}

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
    
    @classmethod
    async def extract_keywords(
        cls,
        title: str,
        ai_model = None,
        url: str = None,
    ) -> dict:
        """
        从热点标题中提取关键词，如果有URL则获取内容生成补充说明
        
        Args:
            title: 热点标题
            ai_model: AI 模型实例
            url: 可选的热点链接，用于获取内容生成补充说明
            
        Returns:
            包含 keywords 和 additional_description 的字典
        """
        from app.services.langchain import LangChainService
        
        logger.info(f"开始提取关键词: title={title}, url={url}")
        
        keywords = []
        additional_description = ""
        
        try:
            # 如果有URL，先获取网页内容
            if url:
                # 检查是否是视频平台链接
                video_domains = ['kuaishou', 'douyin', 'bilibili', 'zhihu', 'xiaohongshu', 'weibo', 'toutiao', 'youku', 'iqiyi', 'qq.com/video']
                is_video_url = any(domain in url.lower() for domain in video_domains)
                
                if is_video_url:
                    logger.info(f"检测到视频链接，跳过内容抓取: {url}")
                    content = ""
                else:
                    logger.info(f"获取热点链接内容: {url}")
                    try:
                        from app.services.plugins.registry import PluginRegistry
                        plugin_class = PluginRegistry.get_class("web_fetch")
                        if plugin_class:
                            plugin = plugin_class()
                            fetch_result = await plugin.execute(url=url)
                            if fetch_result.get("success"):
                                content = fetch_result.get("data", {}).get("content", "")
                                content_title = fetch_result.get("data", {}).get("title", "")
                                logger.info(f"成功获取内容: title={content_title}, length={len(content)}")
                            else:
                                content = ""
                                logger.warning(f"获取内容失败: {fetch_result.get('error')}")
                        else:
                            content = ""
                            logger.warning("web_fetch 插件未找到")
                    except Exception as e:
                        content = ""
                        logger.error(f"获取热点内容失败: {e}")
                
                # 如果获取到内容，生成补充说明
                if content:
                    summary_prompt = f"""请阅读以下热点文章内容，然后：
1. 用50-100字总结文章核心内容
2. 提取3-5个与内容主题相关的关键词（每个2-6个字）

文章标题：{content_title}
文章内容：{content[:5000]}

请按以下格式返回：
摘要：<50-100字的摘要>
关键词：关键词1,关键词2,关键词3"""
                    
                    if ai_model:
                        service = LangChainService(
                            provider=ai_model.provider,
                            model=ai_model.model_name or "gpt-4",
                            api_key=ai_model.api_key,
                            api_base=ai_model.base_url,
                        )
                        summary_response = await service.chat(summary_prompt)
                        summary_content = summary_response.content.strip()
                        
                        # 解析摘要和关键词
                        lines = summary_content.split('\n')
                        for line in lines:
                            if line.startswith('摘要：'):
                                additional_description = line[3:].strip()
                            elif line.startswith('关键词：'):
                                kw_text = line[4:].strip()
                                keywords = [k.strip() for k in kw_text.split(',') if k.strip()][:5]
                    
                    # 补充说明包含摘要和原始链接
                    if additional_description:
                        additional_description = f"{additional_description}\n\n参考链接：{url}"
                    else:
                        additional_description = f"参考链接：{url}"
                    
                    logger.info(f"生成补充说明成功: keywords={keywords}, description_length={len(additional_description)}")
            else:
                # 没有URL，只提取关键词
                keywords_prompt = f"""从以下标题中提取3-5个关键词，用于内容创作时的SEO优化。

标题：{title}

要求：
1. 关键词要与标题主题相关
2. 包含核心概念和热点词汇
3. 适合用于搜索引擎优化
4. 每个关键词2-6个字

请直接返回关键词，用英文逗号分隔，不要其他内容。
示例输出格式：关键词1,关键词2,关键词3"""
                
                if ai_model:
                    service = LangChainService(
                        provider=ai_model.provider,
                        model=ai_model.model_name or "gpt-4",
                        api_key=ai_model.api_key,
                        api_base=ai_model.base_url,
                    )
                    response = await service.chat(keywords_prompt)
                    
                    content = response.content.strip()
                    content = content.strip('"\'')
                    keywords = [k.strip() for k in content.split(',') if k.strip()][:5]
                    
                    logger.info(f"提取关键词成功: keywords={keywords}")
            
            # 如果没有AI模型或提取失败，返回空
            if not ai_model:
                logger.warning("没有配置 AI 模型，无法提取关键词")
                
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
        
        return {
            "keywords": keywords[:5] if keywords else [],
            "additional_description": additional_description
        }
