-- ==========================================
-- 插件系统数据库表 SQL
-- 用于手动创建表或 CI/CD 中使用
-- ==========================================

-- 插件市场表
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件市场表';

-- 用户已安装插件表
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
    UNIQUE KEY `uk_user_plugin` (`user_id`, `plugin_name`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`plugin_name`) REFERENCES `plugin_market`(`name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户已安装插件表';

-- 用户创作插件选择记录表
CREATE TABLE IF NOT EXISTS `creation_plugin_selections` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `tool_type` VARCHAR(50) NOT NULL COMMENT '写作类型（wechat_article等）',
    `selected_plugins` JSON NOT NULL COMMENT '选择的插件列表',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    UNIQUE KEY `uk_user_tool` (`user_id`, `tool_type`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户创作插件选择记录表';

-- 插件调用日志表
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
    INDEX `idx_user_plugin` (`user_id`, `plugin_name`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`creation_id`) REFERENCES `creations`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件调用日志表';

-- 插件评价表
CREATE TABLE IF NOT EXISTS `plugin_reviews` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `plugin_name` VARCHAR(100) NOT NULL COMMENT '插件名称',
    `rating` INT NOT NULL COMMENT '评分（1-5）',
    `comment` TEXT COMMENT '评论内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    UNIQUE KEY `uk_user_plugin_review` (`user_id`, `plugin_name`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`plugin_name`) REFERENCES `plugin_market`(`name`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='插件评价表';
