"""
数据库初始化一键脚本

整合所有初始化操作，一次性完成数据库搭建：
1. 创建数据库
2. 创建所有表
3. 初始化插件数据
4. 初始化价格配置
5. 初始化文章模板
6. 初始化OAuth平台配置
7. 添加模型能力字段
8. 初始化管理员用户

运行方式:
    cd backend
    python -m scripts.initdb
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def step_create_database():
    """步骤1: 创建数据库"""
    logger.info("=" * 50)
    logger.info("[1/8] 创建数据库...")
    logger.info("=" * 50)

    from sqlalchemy import create_engine, text
    from app.core.config import settings
    from app.core.database import get_sync_database_url

    db_url = get_sync_database_url(settings.DATABASE_URL)
    db_name = db_url.split('/')[-1].split('?')[0]  # 处理可能的查询参数
    base_url = db_url.rsplit('/', 1)[0]

    engine = create_engine(base_url)

    try:
        with engine.connect() as conn:
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            logger.success(f"数据库 '{db_name}' 创建成功")
    except Exception as e:
        logger.warning(f"创建数据库时出现问题 (可能已存在): {e}")
    finally:
        engine.dispose()


def step_create_tables():
    """步骤2: 创建所有表"""
    logger.info("=" * 50)
    logger.info("[2/8] 创建数据库表...")
    logger.info("=" * 50)

    from app.core.database import engine, Base
    from sqlalchemy import text

    # 导入所有模型以确保它们被注册到 Base.metadata
    from app.models.user import User
    from app.models.ai_model import AIModel
    from app.models.creation import Creation, CreationVersion
    from app.models.publish import PlatformAccount, PublishRecord
    from app.models.credit import CreditTransaction, MembershipOrder, RechargeOrder, CreditPrice, MembershipPrice
    from app.models.operation import Activity, ActivityParticipation, Coupon, UserCoupon, ReferralRecord, \
        OperationStatistics
    from app.models.oauth_account import OAuthAccount
    from app.models.oauth_usage_log import OAuthUsageLog
    from app.models.model_usage_log import AIModelUsageLog
    from app.models.platform_config import PlatformConfig
    from app.models.plugin import PluginMarket, UserPlugin, CreationPluginSelection, PluginInvocation, PluginReview
    from app.models.template import ArticleTemplate

    # 禁用外键约束检查
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.success("所有数据库表创建成功")

    # 重新启用外键约束检查
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


def step_init_plugins():
    """步骤3: 初始化插件数据"""
    logger.info("=" * 50)
    logger.info("[3/8] 初始化插件数据...")
    logger.info("=" * 50)

    from app.core.database import SessionLocal, engine
    from app.models.plugin import PluginMarket
    from sqlalchemy import text

    # 插件表SQL (确保表存在)
    create_table_sqls = [
        """
        CREATE TABLE IF NOT EXISTS `plugin_market` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '插件ID',
            `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '插件唯一标识符',
            `display_name` VARCHAR(200) NOT NULL COMMENT '显示名称',
            `description` TEXT COMMENT '详细描述',
            `short_description` VARCHAR(500) COMMENT '简短描述',
            `version` VARCHAR(50) DEFAULT '1.0.0' COMMENT '版本号',
            `author` VARCHAR(100) DEFAULT 'AI Creator' COMMENT '作者/组织',
            `author_url` VARCHAR(500) COMMENT '作者链接',
            `category` VARCHAR(50) NOT NULL COMMENT '分类',
            `icon` VARCHAR(100) COMMENT '图标',
            `icon_url` VARCHAR(500) COMMENT '图标URL',
            `screenshot_urls` JSON COMMENT '截图展示',
            `tags` JSON COMMENT '标签列表',
            `is_official` BOOLEAN DEFAULT TRUE COMMENT '是否官方插件',
            `is_approved` BOOLEAN DEFAULT TRUE COMMENT '是否审核通过',
            `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否可用',
            `download_count` INT DEFAULT 0 COMMENT '安装次数',
            `rating` DECIMAL(3, 2) DEFAULT 0 COMMENT '评分',
            `review_count` INT DEFAULT 0 COMMENT '评价数',
            `config_schema` JSON COMMENT '配置参数',
            `parameters_schema` JSON COMMENT '插件参数',
            `entry_point` VARCHAR(200) NOT NULL COMMENT 'Python入口路径',
            `requirements` JSON COMMENT '依赖要求',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_name` (`name`),
            INDEX `idx_category` (`category`),
            INDEX `idx_is_active` (`is_active`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS `user_plugins` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
            `user_id` BIGINT NOT NULL,
            `plugin_name` VARCHAR(100) NOT NULL,
            `is_enabled` BOOLEAN DEFAULT TRUE,
            `config` JSON,
            `is_auto_use` BOOLEAN DEFAULT FALSE,
            `usage_count` INT DEFAULT 0,
            `last_used_at` DATETIME,
            `installed_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_plugin` (`user_id`, `plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS `creation_plugin_selections` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
            `user_id` BIGINT NOT NULL,
            `tool_type` VARCHAR(50) NOT NULL,
            `selected_plugins` JSON NOT NULL,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_tool` (`user_id`, `tool_type`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS `plugin_invocations` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
            `user_id` BIGINT NOT NULL,
            `creation_id` BIGINT,
            `plugin_name` VARCHAR(100) NOT NULL,
            `arguments` JSON,
            `result` JSON,
            `error` TEXT,
            `duration_ms` INT,
            `invoked_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX `idx_user_id` (`user_id`),
            INDEX `idx_creation_id` (`creation_id`),
            INDEX `idx_plugin_name` (`plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS `plugin_reviews` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
            `user_id` BIGINT NOT NULL,
            `plugin_name` VARCHAR(100) NOT NULL,
            `rating` INT NOT NULL,
            `comment` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_plugin_review` (`user_id`, `plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]

    with engine.connect() as conn:
        for sql in create_table_sqls:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"SQL警告: {e}")

    # 预置插件数据
    PRESET_PLUGINS = [
        {
            "name": "web_search",
            "display_name": "网页搜索",
            "description": "使用 Bing 搜索引擎搜索互联网上的最新信息。",
            "short_description": "使用 Bing 搜索引擎获取最新信息",
            "version": "1.0.0",
            "author": "AI Creator",
            "category": "search",
            "icon": "Search",
            "tags": ["搜索", "Bing", "实时信息"],
            "is_official": True,
            "config_schema": {
                "type": "object",
                "properties": {
                    "api_key": {"type": "string", "title": "Bing Search API Key"},
                    "market": {"type": "string", "title": "市场区域", "default": "zh-CN"}
                },
                "required": ["api_key"]
            },
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询关键词"},
                    "count": {"type": "integer", "description": "返回结果数量", "default": 5}
                },
                "required": ["query"]
            },
            "entry_point": "app.services.plugins.plugins.search.web_search.WebSearchPlugin"
        },
        {
            "name": "web_fetch",
            "display_name": "网页抓取",
            "description": "抓取指定网页的内容，提取正文文本。",
            "short_description": "抓取并提取网页正文内容",
            "version": "1.0.0",
            "author": "AI Creator",
            "category": "search",
            "icon": "Globe",
            "tags": ["网页", "抓取", "提取"],
            "is_official": True,
            "config_schema": {},
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要抓取的网页 URL"},
                    "max_length": {"type": "integer", "description": "最大长度", "default": 5000}
                },
                "required": ["url"]
            },
            "entry_point": "app.services.plugins.plugins.search.web_fetch.WebFetchPlugin"
        },
        {
            "name": "calculator",
            "display_name": "计算器",
            "description": "计算数学表达式，支持各种数学运算和函数。",
            "short_description": "计算数学表达式，支持各种运算和函数",
            "version": "1.0.0",
            "author": "AI Creator",
            "category": "utility",
            "icon": "Calculator",
            "tags": ["计算", "数学", "工具"],
            "is_official": True,
            "config_schema": {},
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            },
            "entry_point": "app.services.plugins.plugins.utilities.calculator.CalculatorPlugin"
        }
    ]

    db = SessionLocal()
    try:
        for plugin_data in PRESET_PLUGINS:
            existing = db.query(PluginMarket).filter(PluginMarket.name == plugin_data["name"]).first()
            if existing:
                for key, value in plugin_data.items():
                    setattr(existing, key, value)
                logger.info(f"  更新插件: {plugin_data['name']}")
            else:
                plugin = PluginMarket(**plugin_data)
                db.add(plugin)
                logger.info(f"  创建插件: {plugin_data['name']}")
        db.commit()
        logger.success(f"插件数据初始化完成 ({len(PRESET_PLUGINS)} 个)")
    finally:
        db.close()


def step_init_prices():
    """步骤4: 初始化价格配置"""
    logger.info("=" * 50)
    logger.info("[4/8] 初始化价格配置...")
    logger.info("=" * 50)

    from app.core.database import SessionLocal
    from app.models.credit import CreditPrice, MembershipPrice, MembershipType

    db = SessionLocal()
    try:
        # 积分价格
        if db.query(CreditPrice).count() == 0:
            credit_prices = [
                {"name": "10元套餐", "amount": 10.00, "credits": 1000, "bonus_credits": 0, "is_active": True,
                 "sort_order": 1, "description": "1000积分"},
                {"name": "50元套餐", "amount": 50.00, "credits": 5000, "bonus_credits": 200, "is_active": True,
                 "sort_order": 2, "description": "5000积分+赠送200"},
                {"name": "100元套餐", "amount": 100.00, "credits": 10000, "bonus_credits": 500, "is_active": True,
                 "sort_order": 3, "description": "10000积分+赠送500"},
                {"name": "200元套餐", "amount": 200.00, "credits": 20000, "bonus_credits": 1500, "is_active": True,
                 "sort_order": 4, "description": "20000积分+赠送1500"},
            ]
            for data in credit_prices:
                db.add(CreditPrice(**data))
            logger.info(f"  创建 {len(credit_prices)} 个积分套餐")
        else:
            logger.info("  积分套餐已存在，跳过")

        # 会员价格
        if db.query(MembershipPrice).count() == 0:
            membership_prices = [
                {"name": "月度会员", "membership_type": MembershipType.MONTHLY, "amount": 29.00,
                 "original_amount": 39.00, "duration_days": 30, "is_active": True, "sort_order": 1,
                 "description": "月度会员", "features": '["所有AI创作工具不限次数", "不消耗积分"]'},
                {"name": "季度会员", "membership_type": MembershipType.QUARTERLY, "amount": 79.00,
                 "original_amount": 117.00, "duration_days": 90, "is_active": True, "sort_order": 2,
                 "description": "季度会员", "features": '["所有AI创作工具不限次数", "优先客服支持"]'},
                {"name": "年度会员", "membership_type": MembershipType.YEARLY, "amount": 299.00,
                 "original_amount": 468.00, "duration_days": 365, "is_active": True, "sort_order": 3,
                 "description": "年度会员", "features": '["所有AI创作工具不限次数", "专属客服经理"]'},
            ]
            for data in membership_prices:
                db.add(MembershipPrice(**data))
            logger.info(f"  创建 {len(membership_prices)} 个会员套餐")
        else:
            logger.info("  会员套餐已存在，跳过")

        db.commit()
        logger.success("价格配置初始化完成")
    finally:
        db.close()


def step_init_templates():
    """步骤5: 初始化文章模板"""
    logger.info("=" * 50)
    logger.info("[5/8] 初始化文章模板...")
    logger.info("=" * 50)

    from app.core.database import SessionLocal
    from app.models.template import ArticleTemplate

    db = SessionLocal()
    try:
        existing_count = db.query(ArticleTemplate).filter(ArticleTemplate.is_system == True).count()
        if existing_count > 0:
            logger.info(f"  系统模板已存在 ({existing_count} 个)，跳过")
        else:
            # 简化的模板数据
            templates = [
                {"name": "简约黑白", "description": "干净专业的黑白配色", "thumbnail": "/templates/simple-bw.png",
                 "styles": {"container": {"padding": "20px"}, "h1": {"color": "#1a1a1a"}, "p": {"color": "#333333"}},
                 "is_system": True, "is_public": True},
                {"name": "微信绿", "description": "微信公众号原生风格", "thumbnail": "/templates/wechat-green.png",
                 "styles": {"container": {"padding": "20px"}, "h1": {"color": "#07C160"}, "p": {"color": "#3f3f3f"}},
                 "is_system": True, "is_public": True},
                {"name": "科技蓝", "description": "科技感十足的蓝色主题", "thumbnail": "/templates/tech-blue.png",
                 "styles": {"container": {"padding": "20px"}, "h1": {"color": "#1890ff"}, "p": {"color": "#333333"}},
                 "is_system": True, "is_public": True},
                {"name": "暖橙活力", "description": "活力四射的暖橙色主题", "thumbnail": "/templates/warm-orange.png",
                 "styles": {"container": {"padding": "20px"}, "h1": {"color": "#ff6a00"}, "p": {"color": "#333333"}},
                 "is_system": True, "is_public": True},
                {"name": "文艺紫", "description": "优雅神秘的紫色主题", "thumbnail": "/templates/artistic-purple.png",
                 "styles": {"container": {"padding": "20px"}, "h1": {"color": "#722ed1"}, "p": {"color": "#333333"}},
                 "is_system": True, "is_public": True},
            ]
            for data in templates:
                db.add(ArticleTemplate(**data))
            logger.info(f"  创建 {len(templates)} 个系统模板")

        db.commit()
        logger.success("文章模板初始化完成")
    finally:
        db.close()


def step_init_oauth_platforms():
    """步骤6: 初始化OAuth平台配置"""
    logger.info("=" * 50)
    logger.info("[6/8] 初始化OAuth平台配置...")
    logger.info("=" * 50)

    from app.core.database import SessionLocal
    from app.models.platform_config import PlatformConfig

    db = SessionLocal()
    try:
        if db.query(PlatformConfig).count() > 0:
            logger.info("  平台配置已存在，跳过")
        else:
            platforms = [
                {"platform_id": "qwen", "platform_name": "通义千问",
                 "platform_icon": "https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1O0zuCC7osS_!!6000000001644-55-tps-83-82.svg",
                 "priority": 1, "oauth_config": {}, "litellm_config": {"provider": "qwen_web"},
                 "quota_config": {"daily_limit": 1000000}, "is_enabled": True},
                {"platform_id": "openai", "platform_name": "ChatGPT",
                 "platform_icon": "https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e898.png",
                 "priority": 2, "oauth_config": {}, "litellm_config": {"provider": "chatgpt_web"},
                 "quota_config": {"daily_limit": 500000}, "is_enabled": True},
                {"platform_id": "claude", "platform_name": "Claude",
                 "platform_icon": "https://claude.ai/images/claude_app_icon.png", "priority": 3, "oauth_config": {},
                 "litellm_config": {"provider": "claude_web"}, "quota_config": {"daily_limit": 500000},
                 "is_enabled": True},
                {"platform_id": "baidu", "platform_name": "文心一言",
                 "platform_icon": "https://nlp-eb.cdn.bcebos.com/logo/favicon.ico", "priority": 4, "oauth_config": {},
                 "litellm_config": {"provider": "yiyan_web"}, "quota_config": {"daily_limit": 1000000},
                 "is_enabled": True},
                {"platform_id": "zhipu", "platform_name": "智谱清言", "platform_icon": "https://chatglm.cn/favicon.ico",
                 "priority": 5, "oauth_config": {}, "litellm_config": {"provider": "chatglm_web"},
                 "quota_config": {"daily_limit": 1000000}, "is_enabled": True},
                {"platform_id": "doubao", "platform_name": "豆包",
                 "platform_icon": "https://lf-flow-web-cdn.doubao.com/obj/flow-doubao/doubao/web/logo-icon.png",
                 "priority": 8, "oauth_config": {}, "litellm_config": {"provider": "doubao_web"},
                 "quota_config": {"daily_limit": 1000000}, "is_enabled": True},
            ]
            for data in platforms:
                db.add(PlatformConfig(**data))
            logger.info(f"  创建 {len(platforms)} 个平台配置")

        db.commit()
        logger.success("OAuth平台配置初始化完成")
    finally:
        db.close()


def step_add_capabilities_column():
    """步骤7: 添加模型能力字段"""
    logger.info("=" * 50)
    logger.info("[7/8] 添加模型能力字段...")
    logger.info("=" * 50)

    from sqlalchemy import text
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        # 检查列是否已存在
        result = db.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'ai_models' 
            AND column_name = 'capabilities'
        """))
        row = result.fetchone()

        if row and row[0] > 0:
            logger.info("  capabilities 列已存在，跳过")
        else:
            try:
                db.execute(text("""
                    ALTER TABLE ai_models 
                    ADD COLUMN capabilities JSON NULL 
                    COMMENT '模型能力列表'
                """))
                db.commit()
                logger.info("  添加 capabilities 列成功")
            except Exception as e:
                if "doesn't exist" in str(e).lower():
                    logger.info("  ai_models 表不存在，跳过")
                else:
                    raise

        # 更新默认值
        try:
            db.execute(text("UPDATE ai_models SET capabilities = '[\"text\"]' WHERE capabilities IS NULL"))
            db.commit()
        except:
            pass

        logger.success("模型能力字段处理完成")
    finally:
        db.close()


def step_init_admin_user():
    """步骤8: 初始化管理员用户"""
    logger.info("=" * 50)
    logger.info("[8/8] 初始化管理员用户...")
    logger.info("=" * 50)

    from app.core.database import SessionLocal
    from app.models.user import User, UserRole, UserStatus
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # 检查 admin 用户是否已存在
        existing_admin = db.query(User).filter(
            (User.username == "admin") | (User.role == UserRole.ADMIN)
        ).first()

        if existing_admin:
            logger.info(f"  管理员用户已存在: {existing_admin.username}，跳过")
        else:
            admin_user = User(
                username="admin",
                email="admin@ai-creator.com",
                password_hash=get_password_hash("Admin@123456"),
                nickname="管理员",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                credits=10000,
                daily_quota=999999,
            )
            db.add(admin_user)
            db.commit()
            logger.success("  管理员用户创建成功")
            logger.info("    用户名: admin")
            logger.info("    密码: Admin@123456")
            logger.info("    邮箱: admin@ai-creator.com")
            logger.info("    积分: 10000")
            logger.warning("    ⚠️  请登录后立即修改密码！")

        logger.success("管理员用户初始化完成")
    except Exception as e:
        logger.error(f"初始化管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数 - 执行所有初始化步骤"""
    logger.info("")
    logger.info("*" * 50)
    logger.info("*     AI Creator 数据库初始化工具")
    logger.info("*" * 50)
    logger.info("")

    try:
        step_create_database()
        step_create_tables()
        step_init_plugins()
        step_init_prices()
        step_init_templates()
        step_init_oauth_platforms()
        step_add_capabilities_column()
        step_init_admin_user()

        logger.info("")
        logger.info("=" * 50)
        logger.success("所有初始化步骤完成!")
        logger.info("=" * 50)
        logger.info("")
        logger.info("管理员账号信息:")
        logger.info("  用户名: admin")
        logger.info("  密码: Admin@123456")
        logger.info("")

    except Exception as e:
        logger.error(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
