# AI创作者平台 - 数据库设计文档

## 数据库选型
- **数据库**：MySQL 8.0+
- **字符集**：utf8mb4
- **排序规则**：utf8mb4_unicode_ci

---

## 数据库表设计

### 1. users（用户表）

```sql
CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `role` ENUM('super_admin', 'admin', 'user') DEFAULT 'user' COMMENT '角色',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
  `daily_quota` INT DEFAULT 100 COMMENT '每日配额',
  `used_quota` INT DEFAULT 0 COMMENT '已使用配额',
  `quota_reset_at` DATETIME DEFAULT NULL COMMENT '配额重置时间',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

### 2. ai_models（AI模型配置表）

```sql
CREATE TABLE `ai_models` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '模型ID',
  `name` VARCHAR(100) NOT NULL COMMENT '模型名称',
  `provider` VARCHAR(50) NOT NULL COMMENT '服务提供商：openai/anthropic/stability等',
  `model_type` ENUM('text', 'image', 'video', 'multimodal') NOT NULL COMMENT '模型类型',
  `model_id` VARCHAR(100) NOT NULL COMMENT '模型标识符',
  `api_key` VARCHAR(255) NOT NULL COMMENT 'API密钥（加密存储）',
  `api_base` VARCHAR(255) DEFAULT NULL COMMENT 'API端点',
  `config` JSON DEFAULT NULL COMMENT '模型配置参数',
  `priority` INT DEFAULT 0 COMMENT '优先级：数字越大优先级越高',
  `is_active` TINYINT DEFAULT 1 COMMENT '是否启用：0-禁用，1-启用',
  `max_tokens` INT DEFAULT NULL COMMENT '最大令牌数',
  `temperature` DECIMAL(3,2) DEFAULT NULL COMMENT '温度参数',
  `created_by` BIGINT UNSIGNED NOT NULL COMMENT '创建人ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_provider` (`provider`),
  KEY `idx_model_type` (`model_type`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_priority` (`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI模型配置表';
```

---

### 3. creations（创作记录表）

```sql
CREATE TABLE `creations` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '创作ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `model_id` BIGINT UNSIGNED NOT NULL COMMENT '使用的模型ID',
  `type` VARCHAR(50) NOT NULL COMMENT '创作类型：wechat/xiaohongshu/official/paper/image/video/ppt等',
  `title` VARCHAR(255) DEFAULT NULL COMMENT '标题',
  `prompt` TEXT NOT NULL COMMENT '提示词/输入内容',
  `content` LONGTEXT DEFAULT NULL COMMENT '生成内容',
  `file_path` VARCHAR(500) DEFAULT NULL COMMENT '文件路径（图片/视频/PPT）',
  `metadata` JSON DEFAULT NULL COMMENT '元数据（参数、配置等）',
  `status` ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '状态',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
  `tokens_used` INT DEFAULT 0 COMMENT '使用的令牌数',
  `generation_time` INT DEFAULT 0 COMMENT '生成耗时（秒）',
  `is_favorite` TINYINT DEFAULT 0 COMMENT '是否收藏',
  `tags` VARCHAR(500) DEFAULT NULL COMMENT '标签（逗号分隔）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_model_id` (`model_id`),
  KEY `idx_type` (`type`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_is_favorite` (`is_favorite`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`model_id`) REFERENCES `ai_models`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='创作记录表';
```

---

### 4. creation_versions（创作版本表）

```sql
CREATE TABLE `creation_versions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '版本ID',
  `creation_id` BIGINT UNSIGNED NOT NULL COMMENT '创作ID',
  `version` INT NOT NULL COMMENT '版本号',
  `content` LONGTEXT NOT NULL COMMENT '版本内容',
  `file_path` VARCHAR(500) DEFAULT NULL COMMENT '文件路径',
  `change_note` VARCHAR(500) DEFAULT NULL COMMENT '变更说明',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_creation_id` (`creation_id`),
  KEY `idx_version` (`version`),
  FOREIGN KEY (`creation_id`) REFERENCES `creations`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='创作版本表';
```

---

### 5. platform_accounts（平台账号表）

```sql
CREATE TABLE `platform_accounts` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账号ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `platform` VARCHAR(50) NOT NULL COMMENT '平台：wechat/xiaohongshu/douyin/kuaishou/toutiao/zhihu等',
  `account_name` VARCHAR(100) NOT NULL COMMENT '账号名称',
  `account_id` VARCHAR(100) DEFAULT NULL COMMENT '平台账号ID',
  `access_token` VARCHAR(500) DEFAULT NULL COMMENT '访问令牌（加密存储）',
  `refresh_token` VARCHAR(500) DEFAULT NULL COMMENT '刷新令牌（加密存储）',
  `expires_at` DATETIME DEFAULT NULL COMMENT '令牌过期时间',
  `credentials` JSON DEFAULT NULL COMMENT '其他凭证信息（加密存储）',
  `is_active` TINYINT DEFAULT 1 COMMENT '是否启用：0-禁用，1-启用',
  `last_sync_at` DATETIME DEFAULT NULL COMMENT '最后同步时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_platform` (`platform`),
  KEY `idx_is_active` (`is_active`),
  UNIQUE KEY `uk_user_platform` (`user_id`, `platform`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台账号表';
```

---

### 6. publish_records（发布记录表）

```sql
CREATE TABLE `publish_records` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '发布ID',
  `creation_id` BIGINT UNSIGNED NOT NULL COMMENT '创作ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `platform_account_id` BIGINT UNSIGNED NOT NULL COMMENT '平台账号ID',
  `platform` VARCHAR(50) NOT NULL COMMENT '发布平台',
  `platform_post_id` VARCHAR(200) DEFAULT NULL COMMENT '平台文章ID',
  `platform_url` VARCHAR(500) DEFAULT NULL COMMENT '平台文章URL',
  `title` VARCHAR(255) DEFAULT NULL COMMENT '发布标题',
  `content` LONGTEXT DEFAULT NULL COMMENT '发布内容',
  `cover_image` VARCHAR(500) DEFAULT NULL COMMENT '封面图片',
  `status` ENUM('pending', 'publishing', 'published', 'failed') DEFAULT 'pending' COMMENT '发布状态',
  `scheduled_at` DATETIME DEFAULT NULL COMMENT '定时发布时间',
  `published_at` DATETIME DEFAULT NULL COMMENT '实际发布时间',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
  `view_count` INT DEFAULT 0 COMMENT '浏览量',
  `like_count` INT DEFAULT 0 COMMENT '点赞数',
  `comment_count` INT DEFAULT 0 COMMENT '评论数',
  `share_count` INT DEFAULT 0 COMMENT '分享数',
  `last_sync_at` DATETIME DEFAULT NULL COMMENT '最后同步数据时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_creation_id` (`creation_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_platform_account_id` (`platform_account_id`),
  KEY `idx_platform` (`platform`),
  KEY `idx_status` (`status`),
  KEY `idx_scheduled_at` (`scheduled_at`),
  KEY `idx_published_at` (`published_at`),
  FOREIGN KEY (`creation_id`) REFERENCES `creations`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`platform_account_id`) REFERENCES `platform_accounts`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='发布记录表';
```

---

### 7. system_config（系统配置表）

```sql
CREATE TABLE `system_config` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` TEXT NOT NULL COMMENT '配置值',
  `config_type` VARCHAR(20) DEFAULT 'string' COMMENT '配置类型：string/int/bool/json',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '配置说明',
  `is_public` TINYINT DEFAULT 0 COMMENT '是否公开：0-私有，1-公开',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
```

---

### 8. operation_logs（操作日志表）

```sql
CREATE TABLE `operation_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID',
  `action` VARCHAR(100) NOT NULL COMMENT '操作动作',
  `resource_type` VARCHAR(50) DEFAULT NULL COMMENT '资源类型',
  `resource_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '资源ID',
  `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户代理',
  `request_data` JSON DEFAULT NULL COMMENT '请求数据',
  `response_data` JSON DEFAULT NULL COMMENT '响应数据',
  `status` VARCHAR(20) DEFAULT NULL COMMENT '状态：success/failed',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_resource_type` (`resource_type`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

---

### 9. prompt_templates（提示词模板表）

```sql
CREATE TABLE `prompt_templates` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '模板ID',
  `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
  `type` VARCHAR(50) NOT NULL COMMENT '模板类型：对应创作类型',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '模板描述',
  `template` TEXT NOT NULL COMMENT '提示词模板',
  `variables` JSON DEFAULT NULL COMMENT '模板变量定义',
  `example` TEXT DEFAULT NULL COMMENT '使用示例',
  `is_system` TINYINT DEFAULT 0 COMMENT '是否系统模板：0-用户，1-系统',
  `is_active` TINYINT DEFAULT 1 COMMENT '是否启用',
  `usage_count` INT DEFAULT 0 COMMENT '使用次数',
  `created_by` BIGINT UNSIGNED DEFAULT NULL COMMENT '创建人ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`),
  KEY `idx_is_system` (`is_system`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词模板表';
```

---

## 索引说明

### 主键索引
所有表都使用自增的 `id` 作为主键，类型为 `BIGINT UNSIGNED`。

### 唯一索引
- `users`: username, email（保证用户名和邮箱唯一）
- `platform_accounts`: user_id + platform（一个用户在同一平台只能绑定一个账号）
- `system_config`: config_key（配置键唯一）

### 普通索引
根据查询场景添加了以下索引：
- 状态字段（status, is_active等）
- 时间字段（created_at, updated_at等）
- 外键字段（user_id, model_id等）
- 类型字段（type, platform等）

---

## 外键约束

### CASCADE（级联删除）
- 用户删除时，级联删除其创作记录、平台账号、发布记录
- 创作删除时，级联删除其版本记录和发布记录

### RESTRICT（限制删除）
- AI模型被创作记录引用时，不允许删除
- 平台账号被发布记录引用时，不允许删除

---

## 数据类型说明

### 文本类型
- `VARCHAR`: 用于固定长度或较短的文本（如用户名、邮箱）
- `TEXT`: 用于中等长度的文本（如提示词、错误信息）
- `LONGTEXT`: 用于长文本（如生成的文章内容）

### 数值类型
- `BIGINT UNSIGNED`: 用于ID字段，支持大量数据
- `INT`: 用于计数字段（如配额、使用次数）
- `TINYINT`: 用于布尔值和小范围枚举
- `DECIMAL`: 用于精确小数（如温度参数）

### 时间类型
- `DATETIME`: 用于所有时间字段，精确到秒

### JSON类型
- 用于存储灵活的配置和元数据
- 便于扩展，无需修改表结构

---

## 字符集和排序规则

- **字符集**: utf8mb4（支持完整的Unicode字符，包括emoji）
- **排序规则**: utf8mb4_unicode_ci（不区分大小写，支持多语言）

---

## 安全考虑

### 敏感数据加密
以下字段需要在应用层加密后存储：
- `users.password_hash`: 使用bcrypt加密
- `ai_models.api_key`: 使用AES加密
- `platform_accounts.access_token`: 使用AES加密
- `platform_accounts.refresh_token`: 使用AES加密
- `platform_accounts.credentials`: 使用AES加密

### 软删除
部分表可以考虑添加 `deleted_at` 字段实现软删除，保留历史数据：
- users
- creations
- platform_accounts

---

## 性能优化建议

### 分区策略
对于数据量大的表，可以考虑分区：
- `creations`: 按创建时间分区（按月或按年）
- `operation_logs`: 按创建时间分区（按月）
- `publish_records`: 按发布时间分区（按月）

### 读写分离
- 主库：处理写操作
- 从库：处理读操作（如历史记录查询、统计分析）

### 缓存策略
以下数据适合缓存到Redis：
- 用户信息（users）
- AI模型配置（ai_models）
- 系统配置（system_config）
- 提示词模板（prompt_templates）

---

## 初始化数据

### 系统配置初始数据
```sql
INSERT INTO `system_config` (`config_key`, `config_value`, `config_type`, `description`, `is_public`) VALUES
('site_name', 'AI创作者平台', 'string', '网站名称', 1),
('site_description', '专业的AI创作工具平台', 'string', '网站描述', 1),
('default_daily_quota', '100', 'int', '默认每日配额', 0),
('max_file_size', '10485760', 'int', '最大文件大小（字节）', 0),
('allowed_file_types', '["jpg","jpeg","png","gif","pdf","docx","pptx"]', 'json', '允许的文件类型', 0);
```

### 默认管理员账号
```sql
INSERT INTO `users` (`username`, `email`, `password_hash`, `role`, `status`, `daily_quota`) VALUES
('admin', 'admin@example.com', '$2b$12$...', 'super_admin', 1, 999999);
```

---

## 数据库维护

### 定期任务
1. **配额重置**: 每日凌晨重置用户配额
2. **日志清理**: 定期清理30天前的操作日志
3. **数据备份**: 每日全量备份，每小时增量备份
4. **统计更新**: 定期更新发布记录的互动数据

### 监控指标
- 数据库连接数
- 慢查询日志
- 表大小和增长趋势
- 索引使用情况

---

## 版本历史

- **v1.0** (2026-01-21): 初始数据库设计
  - 9个核心表
  - 完整的索引和外键约束
  - 安全和性能优化建
