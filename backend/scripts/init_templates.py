"""
初始化系统预设文章模板

运行方式:
    cd backend
    python -m scripts.init_templates
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.template import ArticleTemplate


# 5个系统预设模板
SYSTEM_TEMPLATES = [
    {
        "name": "简约黑白",
        "description": "干净专业的黑白配色，适合通用场景，突出内容本身",
        "thumbnail": "/templates/simple-bw.png",
        "styles": {
            "container": {
                "maxWidth": "100%",
                "padding": "20px",
                "backgroundColor": "#ffffff",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            },
            "h1": {
                "fontSize": "24px",
                "fontWeight": "700",
                "color": "#1a1a1a",
                "marginTop": "32px",
                "marginBottom": "16px",
                "paddingBottom": "12px",
                "borderBottom": "2px solid #333333",
                "lineHeight": "1.4"
            },
            "h2": {
                "fontSize": "20px",
                "fontWeight": "600",
                "color": "#2c2c2c",
                "marginTop": "28px",
                "marginBottom": "12px",
                "paddingBottom": "8px",
                "borderBottom": "1px solid #e5e5e5",
                "lineHeight": "1.4"
            },
            "h3": {
                "fontSize": "18px",
                "fontWeight": "600",
                "color": "#333333",
                "marginTop": "24px",
                "marginBottom": "8px",
                "lineHeight": "1.4"
            },
            "p": {
                "fontSize": "16px",
                "lineHeight": "1.8",
                "color": "#333333",
                "marginTop": "16px",
                "marginBottom": "16px",
                "textAlign": "justify"
            },
            "blockquote": {
                "borderLeft": "4px solid #333333",
                "paddingLeft": "16px",
                "paddingTop": "12px",
                "paddingBottom": "12px",
                "backgroundColor": "#f5f5f5",
                "color": "#666666",
                "marginTop": "20px",
                "marginBottom": "20px",
                "fontStyle": "italic"
            },
            "ul": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "ol": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "li": {
                "lineHeight": "1.8",
                "marginTop": "8px",
                "marginBottom": "8px",
                "color": "#333333"
            },
            "code": {
                "backgroundColor": "#f0f0f0",
                "padding": "2px 6px",
                "borderRadius": "3px",
                "fontFamily": "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace",
                "fontSize": "14px",
                "color": "#333333"
            },
            "pre": {
                "backgroundColor": "#282c34",
                "color": "#abb2bf",
                "padding": "16px",
                "borderRadius": "8px",
                "overflow": "auto",
                "fontSize": "14px",
                "lineHeight": "1.6"
            },
            "img": {
                "maxWidth": "100%",
                "borderRadius": "8px",
                "marginTop": "20px",
                "marginBottom": "20px",
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto"
            },
            "a": {
                "color": "#333333",
                "textDecoration": "underline"
            },
            "hr": {
                "border": "none",
                "borderTop": "1px solid #e5e5e5",
                "marginTop": "32px",
                "marginBottom": "32px"
            },
            "strong": {
                "fontWeight": "600",
                "color": "#1a1a1a"
            },
            "em": {
                "fontStyle": "italic"
            }
        }
    },
    {
        "name": "微信绿",
        "description": "微信公众号原生风格，绿色主题，亲和力强",
        "thumbnail": "/templates/wechat-green.png",
        "styles": {
            "container": {
                "maxWidth": "100%",
                "padding": "20px",
                "backgroundColor": "#ffffff",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            },
            "h1": {
                "fontSize": "24px",
                "fontWeight": "700",
                "color": "#07C160",
                "marginTop": "32px",
                "marginBottom": "16px",
                "paddingBottom": "12px",
                "borderBottom": "3px solid #07C160",
                "lineHeight": "1.4",
                "textAlign": "center"
            },
            "h2": {
                "fontSize": "20px",
                "fontWeight": "600",
                "color": "#07C160",
                "marginTop": "28px",
                "marginBottom": "12px",
                "paddingLeft": "12px",
                "borderLeft": "4px solid #07C160",
                "lineHeight": "1.4"
            },
            "h3": {
                "fontSize": "18px",
                "fontWeight": "600",
                "color": "#333333",
                "marginTop": "24px",
                "marginBottom": "8px",
                "lineHeight": "1.4"
            },
            "p": {
                "fontSize": "16px",
                "lineHeight": "2",
                "color": "#3f3f3f",
                "marginTop": "16px",
                "marginBottom": "16px",
                "textIndent": "2em"
            },
            "blockquote": {
                "borderLeft": "4px solid #07C160",
                "paddingLeft": "16px",
                "paddingTop": "12px",
                "paddingBottom": "12px",
                "backgroundColor": "#f0fff4",
                "color": "#666666",
                "marginTop": "20px",
                "marginBottom": "20px"
            },
            "ul": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "ol": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "li": {
                "lineHeight": "2",
                "marginTop": "8px",
                "marginBottom": "8px",
                "color": "#3f3f3f"
            },
            "code": {
                "backgroundColor": "#f0fff4",
                "padding": "2px 6px",
                "borderRadius": "3px",
                "fontFamily": "'SFMono-Regular', Consolas, monospace",
                "fontSize": "14px",
                "color": "#07C160"
            },
            "pre": {
                "backgroundColor": "#1e1e1e",
                "color": "#d4d4d4",
                "padding": "16px",
                "borderRadius": "8px",
                "overflow": "auto",
                "fontSize": "14px",
                "lineHeight": "1.6"
            },
            "img": {
                "maxWidth": "100%",
                "borderRadius": "8px",
                "marginTop": "20px",
                "marginBottom": "20px",
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto",
                "boxShadow": "0 4px 12px rgba(7, 193, 96, 0.15)"
            },
            "a": {
                "color": "#07C160",
                "textDecoration": "none"
            },
            "hr": {
                "border": "none",
                "borderTop": "1px dashed #07C160",
                "marginTop": "32px",
                "marginBottom": "32px"
            },
            "strong": {
                "fontWeight": "600",
                "color": "#07C160"
            },
            "em": {
                "fontStyle": "italic",
                "color": "#07C160"
            }
        }
    },
    {
        "name": "科技蓝",
        "description": "科技感十足的蓝色主题，适合技术、科技类文章",
        "thumbnail": "/templates/tech-blue.png",
        "styles": {
            "container": {
                "maxWidth": "100%",
                "padding": "20px",
                "backgroundColor": "#ffffff",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            },
            "h1": {
                "fontSize": "26px",
                "fontWeight": "700",
                "color": "#1890ff",
                "marginTop": "32px",
                "marginBottom": "16px",
                "paddingBottom": "12px",
                "borderBottom": "3px solid #1890ff",
                "lineHeight": "1.4",
                "background": "linear-gradient(90deg, #1890ff, #40a9ff)",
                "WebkitBackgroundClip": "text",
                "WebkitTextFillColor": "transparent"
            },
            "h2": {
                "fontSize": "20px",
                "fontWeight": "600",
                "color": "#1890ff",
                "marginTop": "28px",
                "marginBottom": "12px",
                "paddingLeft": "12px",
                "borderLeft": "4px solid #1890ff",
                "lineHeight": "1.4",
                "backgroundColor": "#e6f7ff",
                "paddingTop": "8px",
                "paddingBottom": "8px"
            },
            "h3": {
                "fontSize": "18px",
                "fontWeight": "600",
                "color": "#0050b3",
                "marginTop": "24px",
                "marginBottom": "8px",
                "lineHeight": "1.4"
            },
            "p": {
                "fontSize": "16px",
                "lineHeight": "1.8",
                "color": "#333333",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "blockquote": {
                "borderLeft": "4px solid #1890ff",
                "paddingLeft": "16px",
                "paddingTop": "12px",
                "paddingBottom": "12px",
                "backgroundColor": "#e6f7ff",
                "color": "#595959",
                "marginTop": "20px",
                "marginBottom": "20px",
                "borderRadius": "0 8px 8px 0"
            },
            "ul": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "ol": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "li": {
                "lineHeight": "1.8",
                "marginTop": "8px",
                "marginBottom": "8px",
                "color": "#333333"
            },
            "code": {
                "backgroundColor": "#e6f7ff",
                "padding": "2px 6px",
                "borderRadius": "4px",
                "fontFamily": "'SFMono-Regular', Consolas, monospace",
                "fontSize": "14px",
                "color": "#1890ff",
                "border": "1px solid #91d5ff"
            },
            "pre": {
                "backgroundColor": "#0d1117",
                "color": "#c9d1d9",
                "padding": "16px",
                "borderRadius": "8px",
                "overflow": "auto",
                "fontSize": "14px",
                "lineHeight": "1.6",
                "border": "1px solid #1890ff"
            },
            "img": {
                "maxWidth": "100%",
                "borderRadius": "8px",
                "marginTop": "20px",
                "marginBottom": "20px",
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto",
                "boxShadow": "0 4px 16px rgba(24, 144, 255, 0.2)",
                "border": "1px solid #e6f7ff"
            },
            "a": {
                "color": "#1890ff",
                "textDecoration": "none",
                "borderBottom": "1px solid #1890ff"
            },
            "hr": {
                "border": "none",
                "borderTop": "2px solid #e6f7ff",
                "marginTop": "32px",
                "marginBottom": "32px"
            },
            "strong": {
                "fontWeight": "600",
                "color": "#1890ff"
            },
            "em": {
                "fontStyle": "italic",
                "color": "#40a9ff"
            }
        }
    },
    {
        "name": "暖橙活力",
        "description": "活力四射的暖橙色主题，适合营销、活动类文章",
        "thumbnail": "/templates/warm-orange.png",
        "styles": {
            "container": {
                "maxWidth": "100%",
                "padding": "20px",
                "backgroundColor": "#fffaf5",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            },
            "h1": {
                "fontSize": "26px",
                "fontWeight": "700",
                "color": "#ff6a00",
                "marginTop": "32px",
                "marginBottom": "16px",
                "paddingBottom": "12px",
                "lineHeight": "1.4",
                "textAlign": "center",
                "borderBottom": "3px solid #ff6a00"
            },
            "h2": {
                "fontSize": "20px",
                "fontWeight": "600",
                "color": "#ff6a00",
                "marginTop": "28px",
                "marginBottom": "12px",
                "lineHeight": "1.4",
                "backgroundColor": "#fff7e6",
                "padding": "10px 16px",
                "borderRadius": "8px"
            },
            "h3": {
                "fontSize": "18px",
                "fontWeight": "600",
                "color": "#d46b08",
                "marginTop": "24px",
                "marginBottom": "8px",
                "lineHeight": "1.4"
            },
            "p": {
                "fontSize": "16px",
                "lineHeight": "2",
                "color": "#333333",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "blockquote": {
                "borderLeft": "4px solid #ff6a00",
                "paddingLeft": "16px",
                "paddingTop": "12px",
                "paddingBottom": "12px",
                "backgroundColor": "#fff7e6",
                "color": "#666666",
                "marginTop": "20px",
                "marginBottom": "20px",
                "borderRadius": "0 8px 8px 0"
            },
            "ul": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "ol": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "li": {
                "lineHeight": "2",
                "marginTop": "8px",
                "marginBottom": "8px",
                "color": "#333333"
            },
            "code": {
                "backgroundColor": "#fff7e6",
                "padding": "2px 6px",
                "borderRadius": "4px",
                "fontFamily": "'SFMono-Regular', Consolas, monospace",
                "fontSize": "14px",
                "color": "#ff6a00"
            },
            "pre": {
                "backgroundColor": "#282c34",
                "color": "#abb2bf",
                "padding": "16px",
                "borderRadius": "8px",
                "overflow": "auto",
                "fontSize": "14px",
                "lineHeight": "1.6"
            },
            "img": {
                "maxWidth": "100%",
                "borderRadius": "12px",
                "marginTop": "20px",
                "marginBottom": "20px",
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto",
                "boxShadow": "0 4px 16px rgba(255, 106, 0, 0.2)"
            },
            "a": {
                "color": "#ff6a00",
                "textDecoration": "none",
                "fontWeight": "500"
            },
            "hr": {
                "border": "none",
                "borderTop": "2px dashed #ffbb96",
                "marginTop": "32px",
                "marginBottom": "32px"
            },
            "strong": {
                "fontWeight": "700",
                "color": "#ff6a00"
            },
            "em": {
                "fontStyle": "italic",
                "color": "#fa8c16"
            }
        }
    },
    {
        "name": "文艺紫",
        "description": "优雅神秘的紫色主题，适合文化、艺术、情感类文章",
        "thumbnail": "/templates/artistic-purple.png",
        "styles": {
            "container": {
                "maxWidth": "100%",
                "padding": "20px",
                "backgroundColor": "#faf5ff",
                "fontFamily": "'Noto Serif SC', 'Source Han Serif SC', serif"
            },
            "h1": {
                "fontSize": "26px",
                "fontWeight": "700",
                "color": "#722ed1",
                "marginTop": "32px",
                "marginBottom": "20px",
                "paddingBottom": "16px",
                "lineHeight": "1.5",
                "textAlign": "center",
                "borderBottom": "2px solid #d3adf7",
                "letterSpacing": "2px"
            },
            "h2": {
                "fontSize": "20px",
                "fontWeight": "600",
                "color": "#722ed1",
                "marginTop": "28px",
                "marginBottom": "12px",
                "lineHeight": "1.5",
                "paddingLeft": "16px",
                "borderLeft": "4px solid #b37feb",
                "letterSpacing": "1px"
            },
            "h3": {
                "fontSize": "18px",
                "fontWeight": "600",
                "color": "#531dab",
                "marginTop": "24px",
                "marginBottom": "8px",
                "lineHeight": "1.5"
            },
            "p": {
                "fontSize": "16px",
                "lineHeight": "2.2",
                "color": "#333333",
                "marginTop": "20px",
                "marginBottom": "20px",
                "textIndent": "2em",
                "letterSpacing": "0.5px"
            },
            "blockquote": {
                "borderLeft": "4px solid #b37feb",
                "paddingLeft": "20px",
                "paddingTop": "16px",
                "paddingBottom": "16px",
                "backgroundColor": "#f9f0ff",
                "color": "#595959",
                "marginTop": "24px",
                "marginBottom": "24px",
                "fontStyle": "italic",
                "borderRadius": "0 8px 8px 0"
            },
            "ul": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "ol": {
                "paddingLeft": "24px",
                "marginTop": "16px",
                "marginBottom": "16px"
            },
            "li": {
                "lineHeight": "2",
                "marginTop": "10px",
                "marginBottom": "10px",
                "color": "#333333"
            },
            "code": {
                "backgroundColor": "#f9f0ff",
                "padding": "2px 6px",
                "borderRadius": "4px",
                "fontFamily": "'SFMono-Regular', Consolas, monospace",
                "fontSize": "14px",
                "color": "#722ed1"
            },
            "pre": {
                "backgroundColor": "#1e1e2e",
                "color": "#cdd6f4",
                "padding": "16px",
                "borderRadius": "8px",
                "overflow": "auto",
                "fontSize": "14px",
                "lineHeight": "1.6"
            },
            "img": {
                "maxWidth": "100%",
                "borderRadius": "12px",
                "marginTop": "24px",
                "marginBottom": "24px",
                "display": "block",
                "marginLeft": "auto",
                "marginRight": "auto",
                "boxShadow": "0 8px 24px rgba(114, 46, 209, 0.15)"
            },
            "a": {
                "color": "#722ed1",
                "textDecoration": "none",
                "borderBottom": "1px solid #d3adf7"
            },
            "hr": {
                "border": "none",
                "height": "2px",
                "background": "linear-gradient(90deg, transparent, #d3adf7, transparent)",
                "marginTop": "36px",
                "marginBottom": "36px"
            },
            "strong": {
                "fontWeight": "600",
                "color": "#722ed1"
            },
            "em": {
                "fontStyle": "italic",
                "color": "#9254de"
            }
        }
    }
]


def init_templates():
    """初始化系统预设模板"""
    # 确保表已创建
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 检查是否已有系统模板
        existing_count = db.query(ArticleTemplate).filter(
            ArticleTemplate.is_system == True
        ).count()
        
        if existing_count > 0:
            print(f"系统模板已存在 ({existing_count} 个)，跳过初始化")
            
            # 可选：更新现有模板的样式
            update_existing = input("是否更新现有系统模板的样式？(y/n): ").strip().lower()
            if update_existing == 'y':
                for template_data in SYSTEM_TEMPLATES:
                    existing = db.query(ArticleTemplate).filter(
                        ArticleTemplate.name == template_data["name"],
                        ArticleTemplate.is_system == True
                    ).first()
                    
                    if existing:
                        existing.description = template_data["description"]
                        existing.styles = template_data["styles"]
                        print(f"  更新模板: {template_data['name']}")
                    else:
                        # 新模板，添加
                        new_template = ArticleTemplate(
                            name=template_data["name"],
                            description=template_data["description"],
                            thumbnail=template_data["thumbnail"],
                            styles=template_data["styles"],
                            is_system=True,
                            is_public=True,
                            user_id=None
                        )
                        db.add(new_template)
                        print(f"  添加新模板: {template_data['name']}")
                
                db.commit()
                print("系统模板更新完成")
            return
        
        # 创建系统模板
        print("开始初始化系统预设模板...")
        
        for template_data in SYSTEM_TEMPLATES:
            template = ArticleTemplate(
                name=template_data["name"],
                description=template_data["description"],
                thumbnail=template_data["thumbnail"],
                styles=template_data["styles"],
                is_system=True,
                is_public=True,
                user_id=None
            )
            db.add(template)
            print(f"  创建模板: {template_data['name']}")
        
        db.commit()
        print(f"\n成功创建 {len(SYSTEM_TEMPLATES)} 个系统预设模板")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_templates()
