"""
初始化多平台系统预设模板

运行方式:
    cd backend
    python -m scripts.init_platform_templates
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.template import ContentTemplate
from app.services.ai.prompt_templates import WECHAT_PROMPTS, XIAOHONGSHU_PROMPTS, TOUTIAO_PROMPTS, PPT_PROMPTS

# 平台预设模板
PLATFORM_TEMPLATES = [
    # ============ 公众号模板 ============
    {
        "name": "情感文艺",
        "platform": "wechat",
        "category": "emotion",
        "style": "文艺",
        "description": "温暖文艺风格，适合情感类文章",
        "ai_prompt": WECHAT_PROMPTS.get("emotion", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "'Noto Serif SC', serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#8B4513", "marginTop": "30px", "marginBottom": "15px", "textAlign": "center", "lineHeight": "1.5"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#8B4513", "marginTop": "25px", "marginBottom": "12px", "paddingLeft": "12px", "borderLeft": "3px solid #8B4513"},
            "p": {"fontSize": "15px", "lineHeight": "1.75", "color": "#333", "marginTop": "15px", "marginBottom": "15px", "textIndent": "2em"},
            "blockquote": {"borderLeft": "3px solid #8B4513", "paddingLeft": "15px", "backgroundColor": "#faf6f0", "color": "#666", "marginTop": "20px", "marginBottom": "20px", "fontStyle": "italic"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 200, "paragraph_spacing": "1.75em"}
    },
    {
        "name": "情感治愈",
        "platform": "wechat",
        "category": "emotion",
        "style": "治愈",
        "description": "清新治愈风格，温暖人心",
        "ai_prompt": WECHAT_PROMPTS.get("emotion", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#2E8B57", "marginTop": "30px", "marginBottom": "15px", "textAlign": "center"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#2E8B57", "marginTop": "25px", "marginBottom": "12px"},
            "p": {"fontSize": "15px", "lineHeight": "1.8", "color": "#333", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #2E8B57", "paddingLeft": "15px", "backgroundColor": "#f0fff4", "color": "#666"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 200}
    },
    {
        "name": "干货专业",
        "platform": "wechat",
        "category": "knowledge",
        "style": "专业",
        "description": "专业简约风格，适合干货分享",
        "ai_prompt": WECHAT_PROMPTS.get("knowledge", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#1a1a1a", "marginTop": "32px", "marginBottom": "16px", "borderBottom": "2px solid #333", "paddingBottom": "10px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#333", "marginTop": "24px", "marginBottom": "12px"},
            "p": {"fontSize": "15px", "lineHeight": "1.75", "color": "#333", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #333", "paddingLeft": "15px", "backgroundColor": "#f5f5f5", "color": "#666"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 150}
    },
    {
        "name": "干货极简",
        "platform": "wechat",
        "category": "knowledge",
        "style": "极简",
        "description": "极简清晰风格，直击要点",
        "ai_prompt": WECHAT_PROMPTS.get("knowledge", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#333", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "17px", "fontWeight": "600", "color": "#444", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.6", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #ddd", "paddingLeft": "12px", "color": "#666"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 120}
    },
    {
        "name": "热点犀利",
        "platform": "wechat",
        "category": "news",
        "style": "犀利",
        "description": "犀利活泼风格，适合热点评论",
        "ai_prompt": WECHAT_PROMPTS.get("news", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#E74C3C", "marginTop": "30px", "marginBottom": "15px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#E74C3C", "marginTop": "24px", "marginBottom": "12px"},
            "p": {"fontSize": "15px", "lineHeight": "1.75", "color": "#333", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #E74C3C", "paddingLeft": "15px", "backgroundColor": "#fff5f5", "color": "#666"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 180}
    },
    {
        "name": "热点轻松",
        "platform": "wechat",
        "category": "news",
        "style": "轻松",
        "description": "轻松幽默风格，易于阅读",
        "ai_prompt": WECHAT_PROMPTS.get("news", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#F39C12", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "17px", "fontWeight": "600", "color": "#F39C12", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.8", "color": "#333", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #F39C12", "paddingLeft": "15px", "backgroundColor": "#fffbf0", "color": "#666"}
        },
        "format_rules": {"title_max_length": 64, "paragraph_max_length": 150}
    },
    
    # ============ 小红书模板 ============
    {
        "name": "清新种草",
        "platform": "xiaohongshu",
        "category": "recommend",
        "style": "清新",
        "description": "清新自然风格，适合种草推荐",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("recommend", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#333", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#333", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.8", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #7bb87b", "paddingLeft": "12px", "backgroundColor": "#f8fff8", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "3-5"}
    },
    {
        "name": "甜美种草",
        "platform": "xiaohongshu",
        "category": "recommend",
        "style": "甜美",
        "description": "甜美可爱风格，少女心满满",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("recommend", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#e91e63", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#e91e63", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.8", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #e91e63", "paddingLeft": "12px", "backgroundColor": "#fff5f8", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "5-8"}
    },
    {
        "name": "实用攻略",
        "platform": "xiaohongshu",
        "category": "guide",
        "style": "实用",
        "description": "实用清晰风格，攻略必备",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("guide", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#333", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#333", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.6", "color": "#333", "marginTop": "10px", "marginBottom": "10px"},
            "blockquote": {"borderLeft": "2px solid #4CAF50", "paddingLeft": "12px", "backgroundColor": "#f8fff8", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "3-5"}
    },
    {
        "name": "可爱攻略",
        "platform": "xiaohongshu",
        "category": "guide",
        "style": "可爱",
        "description": "可爱活泼风格，攻略也能萌萌哒",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("guide", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#ff9800", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#ff9800", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.8", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #ff9800", "paddingLeft": "12px", "backgroundColor": "#fff8f0", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "5-8"}
    },
    {
        "name": "专业测评",
        "platform": "xiaohongshu",
        "category": "review",
        "style": "专业",
        "description": "专业高级风格，测评首选",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("review", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#333", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#333", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.6", "color": "#333", "marginTop": "10px", "marginBottom": "10px"},
            "blockquote": {"borderLeft": "2px solid #333", "paddingLeft": "12px", "backgroundColor": "#f5f5f5", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "3-5"}
    },
    {
        "name": "日常分享",
        "platform": "xiaohongshu",
        "category": "daily",
        "style": "轻松",
        "description": "轻松亲切风格，日常记录",
        "ai_prompt": XIAOHONGSHU_PROMPTS.get("daily", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "16px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "18px", "fontWeight": "700", "color": "#9c27b0", "marginTop": "20px", "marginBottom": "12px"},
            "h2": {"fontSize": "16px", "fontWeight": "600", "color": "#9c27b0", "marginTop": "16px", "marginBottom": "10px"},
            "p": {"fontSize": "14px", "lineHeight": "1.8", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #9c27b0", "paddingLeft": "12px", "backgroundColor": "#faf5fc", "color": "#666"}
        },
        "format_rules": {"title_max_length": 20, "emoji_required": True, "hashtag_count": "5-8"}
    },
    
    # ============ 头条模板 ============
    {
        "name": "新闻严肃",
        "platform": "toutiao",
        "category": "news",
        "style": "严肃",
        "description": "严肃正式风格，新闻资讯首选",
        "ai_prompt": TOUTIAO_PROMPTS.get("news", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#333", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#333", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.6", "color": "#333", "marginTop": "14px", "marginBottom": "14px"},
            "blockquote": {"borderLeft": "3px solid #333", "paddingLeft": "15px", "backgroundColor": "#f5f5f5", "color": "#666"}
        },
        "format_rules": {"title_max_length": 30, "paragraph_max_length": 150}
    },
    {
        "name": "新闻轻松",
        "platform": "toutiao",
        "category": "news",
        "style": "轻松",
        "description": "轻松可读风格，资讯也有趣",
        "ai_prompt": TOUTIAO_PROMPTS.get("news", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "20px", "fontWeight": "700", "color": "#1890ff", "marginTop": "26px", "marginBottom": "12px"},
            "h2": {"fontSize": "17px", "fontWeight": "600", "color": "#1890ff", "marginTop": "20px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.75", "color": "#333", "marginTop": "14px", "marginBottom": "14px"},
            "blockquote": {"borderLeft": "3px solid #1890ff", "paddingLeft": "15px", "backgroundColor": "#e6f7ff", "color": "#666"}
        },
        "format_rules": {"title_max_length": 30, "paragraph_max_length": 120}
    },
    {
        "name": "生活亲切",
        "platform": "toutiao",
        "category": "life",
        "style": "亲切",
        "description": "亲切自然风格，生活百科",
        "ai_prompt": TOUTIAO_PROMPTS.get("life", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "20px", "fontWeight": "700", "color": "#52c41a", "marginTop": "26px", "marginBottom": "12px"},
            "h2": {"fontSize": "17px", "fontWeight": "600", "color": "#52c41a", "marginTop": "20px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.75", "color": "#333", "marginTop": "14px", "marginBottom": "14px"},
            "blockquote": {"borderLeft": "3px solid #52c41a", "paddingLeft": "15px", "backgroundColor": "#f6ffed", "color": "#666"}
        },
        "format_rules": {"title_max_length": 30, "paragraph_max_length": 130}
    },
    {
        "name": "科技专业",
        "platform": "toutiao",
        "category": "tech",
        "style": "专业",
        "description": "专业深度风格，科技数码",
        "ai_prompt": TOUTIAO_PROMPTS.get("tech", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#722ed1", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#722ed1", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.6", "color": "#333", "marginTop": "14px", "marginBottom": "14px"},
            "blockquote": {"borderLeft": "3px solid #722ed1", "paddingLeft": "15px", "backgroundColor": "#f9f0ff", "color": "#666"}
        },
        "format_rules": {"title_max_length": 30, "paragraph_max_length": 150}
    },
    
    # ============ PPT模板 ============
    {
        "name": "商务汇报",
        "platform": "ppt",
        "category": "report",
        "style": "商务",
        "description": "商务专业风格，工作汇报首选",
        "ai_prompt": PPT_PROMPTS.get("report", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#1890ff", "marginTop": "30px", "marginBottom": "15px"},
            "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#1890ff", "marginTop": "25px", "marginBottom": "12px"},
            "p": {"fontSize": "16px", "lineHeight": "1.6", "color": "#333", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #1890ff", "paddingLeft": "15px", "backgroundColor": "#e6f7ff", "color": "#666"}
        },
        "format_rules": {"slide_count_range": [10, 15], "max_bullet_points": 5}
    },
    {
        "name": "简约汇报",
        "platform": "ppt",
        "category": "report",
        "style": "简约",
        "description": "简约清晰风格，一目了然",
        "ai_prompt": PPT_PROMPTS.get("report", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#333", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#333", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.6", "color": "#333", "marginTop": "12px", "marginBottom": "12px"},
            "blockquote": {"borderLeft": "2px solid #ddd", "paddingLeft": "12px", "color": "#666"}
        },
        "format_rules": {"slide_count_range": [8, 12], "max_bullet_points": 4}
    },
    {
        "name": "科技路演",
        "platform": "ppt",
        "category": "roadshow",
        "style": "科技",
        "description": "科技感风格，路演演示",
        "ai_prompt": PPT_PROMPTS.get("roadshow", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#0d1117", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#58a6ff", "marginTop": "30px", "marginBottom": "15px"},
            "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#58a6ff", "marginTop": "25px", "marginBottom": "12px"},
            "p": {"fontSize": "16px", "lineHeight": "1.6", "color": "#c9d1d9", "marginTop": "15px", "marginBottom": "15px"},
            "blockquote": {"borderLeft": "3px solid #58a6ff", "paddingLeft": "15px", "backgroundColor": "#161b22", "color": "#8b949e"}
        },
        "format_rules": {"slide_count_range": [12, 18], "max_bullet_points": 5}
    },
    {
        "name": "教学清晰",
        "platform": "ppt",
        "category": "teaching",
        "style": "清晰",
        "description": "清晰易读风格，教学课件",
        "ai_prompt": PPT_PROMPTS.get("teaching", ""),
        "styles": {
            "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fff", "fontFamily": "-apple-system, sans-serif"},
            "h1": {"fontSize": "22px", "fontWeight": "700", "color": "#52c41a", "marginTop": "28px", "marginBottom": "14px"},
            "h2": {"fontSize": "18px", "fontWeight": "600", "color": "#52c41a", "marginTop": "22px", "marginBottom": "10px"},
            "p": {"fontSize": "15px", "lineHeight": "1.8", "color": "#333", "marginTop": "14px", "marginBottom": "14px"},
            "blockquote": {"borderLeft": "3px solid #52c41a", "paddingLeft": "15px", "backgroundColor": "#f6ffed", "color": "#666"}
        },
        "format_rules": {"slide_count_range": [15, 25], "max_bullet_points": 6}
    }
]


def init_platform_templates():
    """初始化多平台系统预设模板"""
    # 确保表已创建
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 检查是否已有平台模板
        existing_count = db.query(ContentTemplate).filter(
            ContentTemplate.is_system == True,
            ContentTemplate.platform != None
        ).count()
        
        if existing_count > 0:
            print(f"平台模板已存在 ({existing_count} 个)，跳过初始化")
            
            # 可选：更新现有模板
            update_existing = input("是否更新现有平台模板？(y/n): ").strip().lower()
            if update_existing == 'y':
                for template_data in PLATFORM_TEMPLATES:
                    existing = db.query(ContentTemplate).filter(
                        ContentTemplate.name == template_data["name"],
                        ContentTemplate.platform == template_data["platform"],
                        ContentTemplate.is_system == True
                    ).first()
                    
                    if existing:
                        existing.description = template_data.get("description", existing.description)
                        existing.styles = template_data["styles"]
                        existing.format_rules = template_data.get("format_rules")
                        existing.ai_prompt = template_data.get("ai_prompt")
                        print(f"  更新模板: {template_data['platform']}/{template_data['name']}")
                    else:
                        # 新模板，添加
                        new_template = ContentTemplate(
                            name=template_data["name"],
                            description=template_data.get("description"),
                            platform=template_data["platform"],
                            category=template_data.get("category"),
                            style=template_data.get("style"),
                            styles=template_data["styles"],
                            format_rules=template_data.get("format_rules"),
                            ai_prompt=template_data.get("ai_prompt"),
                            is_system=True,
                            is_public=True,
                            user_id=None
                        )
                        db.add(new_template)
                        print(f"  添加新模板: {template_data['platform']}/{template_data['name']}")
                
                db.commit()
                print("平台模板更新完成")
            return
        
        # 创建平台模板
        print("开始初始化多平台系统预设模板...")
        
        for template_data in PLATFORM_TEMPLATES:
            template = ContentTemplate(
                name=template_data["name"],
                description=template_data.get("description"),
                platform=template_data["platform"],
                category=template_data.get("category"),
                style=template_data.get("style"),
                styles=template_data["styles"],
                format_rules=template_data.get("format_rules"),
                ai_prompt=template_data.get("ai_prompt"),
                is_system=True,
                is_public=True,
                user_id=None
            )
            db.add(template)
            print(f"  创建模板: {template_data['platform']}/{template_data['name']}")
        
        db.commit()
        print(f"\n成功创建 {len(PLATFORM_TEMPLATES)} 个平台系统预设模板")
        
        # 统计各平台模板数量
        platform_counts = {}
        for t in PLATFORM_TEMPLATES:
            platform = t["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        print("\n各平台模板数量:")
        for platform, count in platform_counts.items():
            print(f"  {platform}: {count} 个")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_platform_templates()
