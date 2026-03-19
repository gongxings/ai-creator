"""
数据库配置
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
    connect_args={
        "charset": "utf8mb4",
        "autocommit": True,
        "init_command": "SET SESSION sql_mode='ALLOW_INVALID_DATES'"
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库
    创建所有表并初始化基础数据
    """
    # 确保所有模型都已导入
    from app.models import (
        User, UserRole, UserStatus,
        AIModel, AIProvider, ModelType,
        Creation, CreationVersion, CreationType, CreationStatus,
        PlatformAccount, PublishRecord, PublishStatus, PlatformStatus,
        CreditTransaction, MembershipOrder, RechargeOrder, CreditPrice, MembershipPrice,
        TransactionType, MembershipType, PaymentStatus,
        Activity, ActivityParticipation, Coupon, UserCoupon, ReferralRecord, OperationStatistics,
        ActivityType, ActivityStatus, CouponType, CouponStatus, ReferralStatus,
        OAuthAccount, OAuthUsageLog, PlatformConfig,
        APIKey, APIKeyUsageLog,
        PluginMarket, UserPlugin, CreationPluginSelection, PluginInvocation, PluginReview,
        ArticleTemplate,
    )
    
    logger.info("开始创建数据库表...")
    
    # 禁用外键检查以避免创建顺序问题
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 重新启用外键检查
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    
    logger.info("数据库表创建完成")
    
    # 初始化基础数据
    _init_base_data()


def _init_base_data() -> None:
    """初始化基础数据（价格配置、系统模板、平台配置等）"""
    from app.models.credit import CreditPrice, MembershipPrice, MembershipType
    from app.models.template import ArticleTemplate
    from app.models.platform_config import PlatformConfig
    
    db = SessionLocal()
    try:
        # 1. 初始化积分价格
        if db.query(CreditPrice).count() == 0:
            logger.info("初始化积分价格配置...")
            credit_prices = [
                CreditPrice(name="10元套餐", amount=10.00, credits=1000, bonus_credits=0, is_active=True, sort_order=1, description="1000积分，适合轻度使用"),
                CreditPrice(name="50元套餐", amount=50.00, credits=5000, bonus_credits=200, is_active=True, sort_order=2, description="5000积分+赠送200积分"),
                CreditPrice(name="100元套餐", amount=100.00, credits=10000, bonus_credits=500, is_active=True, sort_order=3, description="10000积分+赠送500积分，超值推荐"),
                CreditPrice(name="200元套餐", amount=200.00, credits=20000, bonus_credits=1500, is_active=True, sort_order=4, description="20000积分+赠送1500积分，性价比最高"),
            ]
            db.add_all(credit_prices)
            db.commit()
            logger.info(f"成功初始化 {len(credit_prices)} 个积分价格套餐")
        
        # 2. 初始化会员价格
        if db.query(MembershipPrice).count() == 0:
            logger.info("初始化会员价格配置...")
            membership_prices = [
                MembershipPrice(name="月度会员", membership_type=MembershipType.MONTHLY, amount=29.00, original_amount=39.00, duration_days=30, is_active=True, sort_order=1, description="适合尝试体验", features='["所有AI创作工具不限次数", "不消耗积分", "基础客服支持"]'),
                MembershipPrice(name="季度会员", membership_type=MembershipType.QUARTERLY, amount=79.00, original_amount=117.00, duration_days=90, is_active=True, sort_order=2, description="省38元，性价比之选", features='["所有AI创作工具不限次数", "不消耗积分", "优先客服支持", "新功能优先体验"]'),
                MembershipPrice(name="年度会员", membership_type=MembershipType.YEARLY, amount=299.00, original_amount=468.00, duration_days=365, is_active=True, sort_order=3, description="省169元，长期用户首选", features='["所有AI创作工具不限次数", "不消耗积分", "专属客服经理", "新功能优先体验", "定制化服务支持"]'),
            ]
            db.add_all(membership_prices)
            db.commit()
            logger.info(f"成功初始化 {len(membership_prices)} 个会员价格套餐")
        
        # 3. 初始化系统模板
        if db.query(ArticleTemplate).filter(ArticleTemplate.is_system == True).count() == 0:
            logger.info("初始化系统预设模板...")
            system_templates = _get_system_templates()
            for template_data in system_templates:
                template = ArticleTemplate(**template_data)
                db.add(template)
            db.commit()
            logger.info(f"成功初始化 {len(system_templates)} 个系统预设模板")
        
        # 4. 初始化平台配置
        if db.query(PlatformConfig).count() == 0:
            logger.info("初始化OAuth平台配置...")
            platforms = _get_platform_configs()
            for platform_data in platforms:
                platform = PlatformConfig(**platform_data)
                db.add(platform)
            db.commit()
            logger.info(f"成功初始化 {len(platforms)} 个平台配置")
        
        logger.info("基础数据初始化完成")
        
    except Exception as e:
        logger.error(f"初始化基础数据失败: {e}")
        db.rollback()
    finally:
        db.close()


def _get_system_templates():
    """返回系统预设模板数据"""
    return [
        {
            "name": "简约黑白",
            "description": "干净专业的黑白配色，适合通用场景",
            "is_system": True,
            "is_public": True,
            "styles": {
                "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#ffffff"},
                "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#1a1a1a", "borderBottom": "2px solid #333333"},
                "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#2c2c2c", "borderLeft": "4px solid #333333", "paddingLeft": "12px"},
                "p": {"fontSize": "16px", "lineHeight": "1.8", "color": "#333333"},
                "blockquote": {"borderLeft": "4px solid #333333", "backgroundColor": "#f5f5f5", "padding": "12px 16px"},
            }
        },
        {
            "name": "微信绿",
            "description": "微信公众号原生风格，绿色主题",
            "is_system": True,
            "is_public": True,
            "styles": {
                "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#ffffff"},
                "h1": {"fontSize": "24px", "fontWeight": "700", "color": "#07C160", "borderBottom": "3px solid #07C160"},
                "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#07C160", "borderLeft": "4px solid #07C160", "paddingLeft": "12px"},
                "p": {"fontSize": "16px", "lineHeight": "2", "color": "#3f3f3f", "textIndent": "2em"},
                "blockquote": {"borderLeft": "4px solid #07C160", "backgroundColor": "#f0fff4", "padding": "12px 16px"},
            }
        },
        {
            "name": "科技蓝",
            "description": "科技感蓝色主题，适合技术文章",
            "is_system": True,
            "is_public": True,
            "styles": {
                "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#ffffff"},
                "h1": {"fontSize": "26px", "fontWeight": "700", "color": "#1890ff", "borderBottom": "3px solid #1890ff"},
                "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#1890ff", "borderLeft": "4px solid #1890ff", "paddingLeft": "12px"},
                "p": {"fontSize": "16px", "lineHeight": "1.8", "color": "#333333"},
                "blockquote": {"borderLeft": "4px solid #1890ff", "backgroundColor": "#e6f7ff", "padding": "12px 16px"},
            }
        },
        {
            "name": "暖橙活力",
            "description": "活力橙色主题，适合营销推广",
            "is_system": True,
            "is_public": True,
            "styles": {
                "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#fffaf5"},
                "h1": {"fontSize": "26px", "fontWeight": "700", "color": "#ff6a00", "borderBottom": "3px solid #ff6a00"},
                "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#ff6a00", "backgroundColor": "#fff7e6", "padding": "10px 16px"},
                "p": {"fontSize": "16px", "lineHeight": "2", "color": "#333333"},
                "blockquote": {"borderLeft": "4px solid #ff6a00", "backgroundColor": "#fff7e6", "padding": "12px 16px"},
            }
        },
        {
            "name": "文艺紫",
            "description": "优雅紫色主题，适合文化艺术",
            "is_system": True,
            "is_public": True,
            "styles": {
                "container": {"maxWidth": "100%", "padding": "20px", "backgroundColor": "#faf5ff"},
                "h1": {"fontSize": "26px", "fontWeight": "700", "color": "#722ed1", "borderBottom": "2px solid #d3adf7"},
                "h2": {"fontSize": "20px", "fontWeight": "600", "color": "#722ed1", "borderLeft": "4px solid #b37feb", "paddingLeft": "16px"},
                "p": {"fontSize": "16px", "lineHeight": "2.2", "color": "#333333", "textIndent": "2em"},
                "blockquote": {"borderLeft": "4px solid #b37feb", "backgroundColor": "#f9f0ff", "padding": "16px 20px"},
            }
        },
    ]


def _get_platform_configs():
    """返回OAuth平台配置数据"""
    return [
        {
            "platform_id": "qwen",
            "platform_name": "通义千问",
            "platform_icon": "https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1O0zuCC7osS_!!6000000001644-55-tps-83-82.svg",
            "priority": 1,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://tongyi.aliyun.com/qianwen/"},
            "litellm_config": {"provider": "qwen_web", "default_model": "qwen-turbo"},
            "quota_config": {"daily_limit": 1000000, "rate_limit": 60},
        },
        {
            "platform_id": "openai",
            "platform_name": "ChatGPT",
            "platform_icon": "https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e898.png",
            "priority": 2,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://chat.openai.com/"},
            "litellm_config": {"provider": "chatgpt_web", "default_model": "gpt-3.5-turbo"},
            "quota_config": {"daily_limit": 500000, "rate_limit": 60},
        },
        {
            "platform_id": "claude",
            "platform_name": "Claude",
            "platform_icon": "https://claude.ai/images/claude_app_icon.png",
            "priority": 3,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://claude.ai/"},
            "litellm_config": {"provider": "claude_web", "default_model": "claude-3-sonnet"},
            "quota_config": {"daily_limit": 500000, "rate_limit": 50},
        },
        {
            "platform_id": "baidu",
            "platform_name": "文心一言",
            "platform_icon": "https://nlp-eb.cdn.bcebos.com/logo/favicon.ico",
            "priority": 4,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://yiyan.baidu.com/"},
            "litellm_config": {"provider": "yiyan_web", "default_model": "ernie-bot-turbo"},
            "quota_config": {"daily_limit": 1000000, "rate_limit": 60},
        },
        {
            "platform_id": "zhipu",
            "platform_name": "智谱清言",
            "platform_icon": "https://chatglm.cn/favicon.ico",
            "priority": 5,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://chatglm.cn/"},
            "litellm_config": {"provider": "chatglm_web", "default_model": "glm-4-flash"},
            "quota_config": {"daily_limit": 1000000, "rate_limit": 60},
        },
        {
            "platform_id": "doubao",
            "platform_name": "豆包",
            "platform_icon": "https://lf-flow-web-cdn.doubao.com/obj/flow-doubao/doubao/web/logo-icon.png",
            "priority": 6,
            "is_enabled": True,
            "oauth_config": {"auth_url": "https://www.doubao.com/"},
            "litellm_config": {"provider": "doubao_web", "default_model": "doubao-lite-4k"},
            "quota_config": {"daily_limit": 1000000, "rate_limit": 60},
        },
    ]