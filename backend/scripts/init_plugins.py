"""
插件市场初始化脚本

运行方式：
    cd backend
    python -m scripts.init_plugins
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.plugin import PluginMarket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 预置插件数据
PRESET_PLUGINS = [
    {
        "name": "web_search",
        "display_name": "网页搜索",
        "description": """
使用 Bing 搜索引擎搜索互联网上的最新信息。

功能特点：
- 实时搜索最新信息
- 支持中英文搜索
- 返回相关网页摘要和链接

使用场景：
- 获取最新新闻和热点
- 查找特定主题的资料
- 验证事实和数据
        """.strip(),
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
                "api_key": {
                    "type": "string",
                    "title": "Bing Search API Key",
                    "description": "从 Azure Portal 获取的 Bing Search API 密钥"
                },
                "market": {
                    "type": "string",
                    "title": "市场区域",
                    "description": "搜索结果的市场区域",
                    "default": "zh-CN",
                    "enum": ["zh-CN", "en-US", "zh-TW", "ja-JP"]
                }
            },
            "required": ["api_key"]
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询关键词"
                },
                "count": {
                    "type": "integer",
                    "description": "返回结果数量，默认5条",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        "entry_point": "app.services.plugins.plugins.search.web_search.WebSearchPlugin"
    },
    {
        "name": "web_fetch",
        "display_name": "网页抓取",
        "description": """
抓取指定网页的内容，提取正文文本。

功能特点：
- 智能提取网页正文
- 自动清理广告和导航
- 支持各种类型的网页

使用场景：
- 深入阅读搜索结果中的网页
- 提取文章内容进行分析
- 获取网页的详细信息
        """.strip(),
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
                "url": {
                    "type": "string",
                    "description": "要抓取的网页 URL"
                },
                "max_length": {
                    "type": "integer",
                    "description": "返回内容的最大长度（字符数）",
                    "default": 5000
                }
            },
            "required": ["url"]
        },
        "entry_point": "app.services.plugins.plugins.search.web_fetch.WebFetchPlugin"
    },
    {
        "name": "calculator",
        "display_name": "计算器",
        "description": """
计算数学表达式，支持各种数学运算和函数。

支持的运算：
- 基本运算：+、-、*、/、//、%、**
- 数学函数：sin、cos、tan、sqrt、log、log10、exp
- 其他函数：abs、round、ceil、floor、min、max
- 常量：pi、e、tau

使用场景：
- 精确计算数值
- 进行复杂数学运算
- 验证计算结果
        """.strip(),
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
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如：'2 + 3 * 4'、'sqrt(16)'、'sin(pi/2)'"
                }
            },
            "required": ["expression"]
        },
        "entry_point": "app.services.plugins.plugins.utilities.calculator.CalculatorPlugin"
    }
]


def init_plugin_tables():
    """创建插件相关的数据库表（不使用外键约束，避免权限问题）"""
    from sqlalchemy import text

    logger.info("Creating plugin tables...")

    # 使用原生 SQL 创建表（不含外键约束，兼容权限受限的数据库用户）
    create_table_sqls = [
        # plugin_market 表
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
            `category` VARCHAR(50) NOT NULL COMMENT '分类：writing, search, media, utility',
            `icon` VARCHAR(100) COMMENT '图标（emoji或图标名称）',
            `icon_url` VARCHAR(500) COMMENT '图标URL',
            `screenshot_urls` JSON COMMENT '截图展示 URL 列表',
            `tags` JSON COMMENT '标签列表',
            `is_official` BOOLEAN DEFAULT TRUE COMMENT '是否官方插件',
            `is_approved` BOOLEAN DEFAULT TRUE COMMENT '是否审核通过',
            `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否可用',
            `download_count` INT DEFAULT 0 COMMENT '安装次数',
            `rating` DECIMAL(3, 2) DEFAULT 0 COMMENT '评分（0-5）',
            `review_count` INT DEFAULT 0 COMMENT '评价数',
            `config_schema` JSON COMMENT '配置参数 JSON Schema',
            `parameters_schema` JSON COMMENT '插件参数 Schema（OpenAI function format）',
            `entry_point` VARCHAR(200) NOT NULL COMMENT 'Python入口路径',
            `requirements` JSON COMMENT '依赖要求',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_name` (`name`),
            INDEX `idx_category` (`category`),
            INDEX `idx_is_active` (`is_active`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件市场表'
        """,
        # user_plugins 表（不含外键）
        """
        CREATE TABLE IF NOT EXISTS `user_plugins` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
            `user_id` BIGINT NOT NULL COMMENT '用户ID',
            `plugin_name` VARCHAR(100) NOT NULL COMMENT '插件名称',
            `is_enabled` BOOLEAN DEFAULT TRUE COMMENT '用户是否启用',
            `config` JSON COMMENT '用户配置（API key、参数等）',
            `is_auto_use` BOOLEAN DEFAULT FALSE COMMENT '是否自动加入创作',
            `usage_count` INT DEFAULT 0 COMMENT '使用次数',
            `last_used_at` DATETIME COMMENT '最后使用时间',
            `installed_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '安装时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_plugin` (`user_id`, `plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户已安装插件表'
        """,
        # creation_plugin_selections 表（不含外键）
        """
        CREATE TABLE IF NOT EXISTS `creation_plugin_selections` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
            `user_id` BIGINT NOT NULL COMMENT '用户ID',
            `tool_type` VARCHAR(50) NOT NULL COMMENT '写作类型（wechat_article等）',
            `selected_plugins` JSON NOT NULL COMMENT '选择的插件列表',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_tool` (`user_id`, `tool_type`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户创作插件选择记录表'
        """,
        # plugin_invocations 表（不含外键）
        """
        CREATE TABLE IF NOT EXISTS `plugin_invocations` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
            `user_id` BIGINT NOT NULL COMMENT '用户ID',
            `creation_id` BIGINT COMMENT '关联创作记录',
            `plugin_name` VARCHAR(100) NOT NULL COMMENT '调用的插件',
            `arguments` JSON COMMENT '调用参数',
            `result` JSON COMMENT '返回结果',
            `error` TEXT COMMENT '错误信息',
            `duration_ms` INT COMMENT '执行耗时（毫秒）',
            `invoked_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
            INDEX `idx_user_id` (`user_id`),
            INDEX `idx_creation_id` (`creation_id`),
            INDEX `idx_plugin_name` (`plugin_name`),
            INDEX `idx_user_plugin` (`user_id`, `plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件调用日志表'
        """,
        # plugin_reviews 表（不含外键）
        """
        CREATE TABLE IF NOT EXISTS `plugin_reviews` (
            `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
            `user_id` BIGINT NOT NULL COMMENT '用户ID',
            `plugin_name` VARCHAR(100) NOT NULL COMMENT '插件名称',
            `rating` INT NOT NULL COMMENT '评分（1-5）',
            `comment` TEXT COMMENT '评论内容',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_user_id` (`user_id`),
            UNIQUE KEY `uk_user_plugin_review` (`user_id`, `plugin_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件评价表'
        """
    ]

    with engine.connect() as conn:
        for sql in create_table_sqls:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                # 表已存在则跳过
                if "already exists" in str(e).lower():
                    logger.info(f"Table already exists, skipping...")
                else:
                    logger.warning(f"SQL execution warning: {e}")

    logger.info("Plugin tables created successfully")


def init_preset_plugins(db: Session):
    """初始化预置插件"""
    logger.info("Initializing preset plugins...")

    for plugin_data in PRESET_PLUGINS:
        # 检查是否已存在
        existing = db.query(PluginMarket).filter(
            PluginMarket.name == plugin_data["name"]
        ).first()

        if existing:
            # 更新现有记录
            logger.info(f"Updating plugin: {plugin_data['name']}")
            for key, value in plugin_data.items():
                setattr(existing, key, value)
        else:
            # 创建新记录
            logger.info(f"Creating plugin: {plugin_data['name']}")
            plugin = PluginMarket(**plugin_data)
            db.add(plugin)

    db.commit()
    logger.info(f"Initialized {len(PRESET_PLUGINS)} plugins")


def main():
    """主函数"""
    # 创建表
    init_plugin_tables()

    # 初始化数据
    db = SessionLocal()
    try:
        init_preset_plugins(db)
    finally:
        db.close()

    logger.info("Plugin initialization completed!")


if __name__ == "__main__":
    main()
