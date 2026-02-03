"""
初始化OAuth平台配置
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.platform_config import PlatformConfig
from loguru import logger


def init_platforms():
    """初始化平台配置"""
    db = SessionLocal()
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 检查是否已有平台配置
        existing_count = db.query(PlatformConfig).count()
        if existing_count > 0:
            logger.info(f"已存在 {existing_count} 个平台配置，跳过初始化")
            return
        
        # 定义平台配置 - 使用网页聊天版本的URL
        platforms = [
            {
                "platform_id": "qwen",
                "platform_name": "通义千问",
                "description": "阿里云通义千问大模型网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://tongyi.aliyun.com/qianwen/",
                    "login_selectors": {
                        "login_button": "button:has-text('登录')",
                        "scan_qr": ".qrcode-container",
                    },
                    "cookie_names": ["login_aliyunid_ticket", "login_aliyunid_pk", "t"],
                },
                "litellm_config": {
                    "provider": "qwen_web",
                    "api_base": "https://qianwen.biz.aliyun.com/dialog/conversation",
                    "default_model": "qwen-turbo",
                    "available_models": [
                        "qwen-turbo",
                        "qwen-plus",
                        "qwen-max",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "openai",
                "platform_name": "ChatGPT",
                "description": "OpenAI ChatGPT网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://chat.openai.com/",
                    "login_selectors": {
                        "login_button": "button:has-text('Log in')",
                        "email_input": "input[name='username']",
                        "continue_button": "button[type='submit']",
                        "password_input": "input[name='password']",
                        "submit_button": "button[type='submit']",
                    },
                    "cookie_names": ["__Secure-next-auth.session-token", "_cfuvid"],
                },
                "litellm_config": {
                    "provider": "chatgpt_web",
                    "api_base": "https://chatgpt.com/backend-api/conversation",
                    "default_model": "gpt-3.5-turbo",
                    "available_models": [
                        "gpt-3.5-turbo",
                        "gpt-4",
                        "gpt-4-turbo",
                    ],
                },
                "quota_config": {
                    "daily_limit": 500000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "claude",
                "platform_name": "Claude",
                "description": "Anthropic Claude网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://claude.ai/",
                    "login_selectors": {
                        "email_input": "input[type='email']",
                        "continue_button": "button:has-text('Continue with email')",
                        "code_input": "input[placeholder='Enter 6-digit code']",
                    },
                    "cookie_names": ["sessionKey", "__cf_bm", "_cfuvid"],
                },
                "litellm_config": {
                    "provider": "claude_web",
                    "api_base": "https://claude.ai/api",
                    "default_model": "claude-3-sonnet",
                    "available_models": [
                        "claude-3-opus",
                        "claude-3-sonnet",
                        "claude-3-haiku",
                    ],
                },
                "quota_config": {
                    "daily_limit": 500000,
                    "rate_limit": 50,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "baidu",
                "platform_name": "文心一言",
                "description": "百度文心一言网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://yiyan.baidu.com/",
                    "login_selectors": {
                        "login_button": ".login-btn",
                        "qr_code": ".qrcode-img",
                    },
                    "cookie_names": ["BAIDUID", "BDUSS", "BDUSS_BFESS", "STOKEN", "PTOKEN"],
                },
                "litellm_config": {
                    "provider": "yiyan_web",
                    "api_base": "https://yiyan.baidu.com/eb/chat/new",
                    "default_model": "ernie-bot-turbo",
                    "available_models": [
                        "ernie-bot-turbo",
                        "ernie-bot",
                        "ernie-bot-4",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "zhipu",
                "platform_name": "智谱清言",
                "description": "智谱清言网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://chatglm.cn/",
                    "login_selectors": {
                        "login_button": "button:has-text('登录')",
                        "phone_input": "input[placeholder='请输入手机号']",
                        "code_input": "input[placeholder='请输入验证码']",
                        "submit_button": "button:has-text('登录')",
                    },
                    "cookie_names": ["chatglm_token", "chatglm_refresh_token", "chatglm_user_id"],
                },
                "litellm_config": {
                    "provider": "chatglm_web",
                    "api_base": "https://chatglm.cn/chatglm/backend-api/assistant/stream",
                    "default_model": "glm-4-flash",
                    "available_models": [
                        "glm-4-flash",
                        "glm-4",
                        "glm-4v",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "spark",
                "platform_name": "讯飞星火",
                "description": "讯飞星火网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://xinghuo.xfyun.cn/",
                    "login_selectors": {
                        "phone_input": "input[placeholder='手机号']",
                        "code_input": "input[placeholder='验证码']",
                        "submit_button": "button:has-text('登录')",
                    },
                    "cookie_names": ["ssoSessionId", "refreshToken", "accessToken"],
                },
                "litellm_config": {
                    "provider": "spark_web",
                    "api_base": "https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/chat-message",
                    "default_model": "spark-lite",
                    "available_models": [
                        "spark-lite",
                        "spark-pro",
                        "spark-max",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "gemini",
                "platform_name": "Google Gemini",
                "description": "Google Gemini网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://gemini.google.com/",
                    "login_selectors": {
                        "email_input": "input[type='email']",
                        "next_button": "#identifierNext",
                        "password_input": "input[type='password']",
                        "submit_button": "#passwordNext",
                    },
                    "cookie_names": ["SID", "HSID", "SSID", "APISID", "SAPISID", "__Secure-1PSID", "__Secure-3PSID"],
                },
                "litellm_config": {
                    "provider": "gemini_web",
                    "api_base": "https://gemini.google.com/app",
                    "default_model": "gemini-pro",
                    "available_models": [
                        "gemini-pro",
                        "gemini-pro-vision",
                        "gemini-1.5-pro",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
            {
                "platform_id": "doubao",
                "platform_name": "豆包",
                "description": "字节跳动豆包网页版（免费）",
                "oauth_config": {
                    "auth_url": "https://www.doubao.com/",
                    "login_selectors": {
                        "phone_input": "input[placeholder='请输入手机号']",
                        "code_input": "input[placeholder='请输入验证码']",
                        "submit_button": "button[type='submit']",
                    },
                    "cookie_names": ["sessionid", "sessionid_ss", "s_v_web_id", "tt_webid"],
                },
                "litellm_config": {
                    "provider": "doubao_web",
                    "api_base": "https://www.doubao.com/api/chat",
                    "default_model": "doubao-lite-4k",
                    "available_models": [
                        "doubao-lite-4k",
                        "doubao-lite-32k",
                        "doubao-pro-4k",
                        "doubao-pro-32k",
                    ],
                },
                "quota_config": {
                    "daily_limit": 1000000,
                    "rate_limit": 60,
                },
                "is_enabled": True,
            },
        ]
        
        # 插入平台配置
        for platform_data in platforms:
            platform = PlatformConfig(**platform_data)
            db.add(platform)
        
        db.commit()
        logger.info(f"成功初始化 {len(platforms)} 个平台配置")
        
        # 显示已初始化的平台
        for platform in platforms:
            logger.info(f"  - {platform['platform_name']} ({platform['platform_id']})")
        
    except Exception as e:
        logger.error(f"初始化平台配置失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("开始初始化OAuth平台配置...")
    init_platforms()
    logger.info("OAuth平台配置初始化完成")
