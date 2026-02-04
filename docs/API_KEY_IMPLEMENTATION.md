# API Key与OpenAPI代理功能实现文档

## 一、实现概述

本次实现完成了OAuth账号对外提供OpenAPI服务的完整方案，包括：

1. **统一模型管理**：整合OAuth账号和API Key配置的模型
2. **API Key管理**：生成、管理和验证用户的API Key
3. **OpenAPI代理**：提供OpenAI兼容的API接口
4. **统一AI调用**：内部统一的模型调用接口

## 二、新增数据库表

### 1. api_keys表
用于管理用户生成的API Key

**字段说明**：
- `id`: 主键
- `user_id`: 用户ID（外键）
- `key_name`: Key名称
- `api_key`: 完整的API Key（仅创建时返回）
- `key_hash`: SHA256哈希值（用于验证）
- `is_active`: 是否激活
- `allowed_models`: 允许使用的模型列表（JSON）
- `rate_limit`: 速率限制（次/分钟）
- `total_requests`: 总请求次数
- `total_tokens`: 总Token使用量
- `last_used_at`: 最后使用时间
- `expires_at`: 过期时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 2. api_key_usage_logs表
记录API Key的使用日志

**字段说明**：
- `id`: 主键
- `api_key_id`: API Key ID（外键）
- `model_id`: 模型ID
- `model_name`: 模型名称
- `endpoint`: 调用的端点
- `prompt_tokens`: 提示Token数
- `completion_tokens`: 完成Token数
- `total_tokens`: 总Token数
- `request_data`: 请求数据（JSON）
- `response_data`: 响应数据（JSON）
- `error_message`: 错误信息
- `ip_address`: IP地址
- `user_agent`: User Agent
- `created_at`: 创建时间

### 3. creations表修改
添加`model_id`字段，记录创作使用的模型

## 三、核心服务实现

### 1. ModelService（模型服务）
**文件**：`backend/app/services/model_service.py`

**主要功能**：
- `get_available_models()`: 获取用户所有可用模型
  - 整合OAuth账号和AI模型
  - 过滤过期和配额用尽的账号
  - 标记用户偏好模型
  - 按优先级排序

- `get_preferred_model()`: 获取用户偏好模型
  - 从历史创作记录中读取
  - 支持按场景类型筛选

- `parse_model_id()`: 解析模型ID
  - OAuth模型：`oauth_{account_id}_{model_name}`
  - AI模型：`ai_model_{model_id}`

### 2. APIKeyService（API Key服务）
**文件**：`backend/app/services/api_key_service.py`

**主要功能**：
- `create_api_key()`: 创建API Key
  - 生成格式：`sk-{32位随机字符}`
  - SHA256哈希存储
  - 设置过期时间和权限

- `verify_api_key()`: 验证API Key
  - 哈希匹配验证
  - 检查激活状态
  - 检查过期时间
  - 速率限制检查（Redis）

- `log_usage()`: 记录使用日志
  - 异步记录到数据库
  - 更新统计信息

- `check_rate_limit()`: 速率限制检查
  - 使用Redis滑动窗口算法
  - 返回限制信息

## 四、API接口实现

### 1. 内部API接口

#### GET /api/v1/models/available
获取可用模型列表

**参数**：
- `scene_type`（可选）：场景类型（writing/image/video）

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "models": [
      {
        "model_id": "oauth_1_qwen-max",
        "model_name": "qwen-max",
        "display_name": "qwen-max (我的通义千问)",
        "provider": "qwen",
        "source_type": "oauth",
        "source_id": 1,
        "is_free": true,
        "is_preferred": false,
        "status": "active",
        "quota_info": {
          "used": 100,
          "total": 1000,
          "percentage": 10
        }
      }
    ]
  }
}
```

#### POST /api/v1/ai/chat
统一AI调用接口

**请求**：
```json
{
  "model_id": "oauth_1_qwen-max",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "scene_type": "writing",
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "你好！有什么我可以帮助你的吗？",
    "model": "qwen-max",
    "usage": {
      "prompt_tokens": 5,
      "completion_tokens": 15,
      "total_tokens": 20
    }
  }
}
```

#### POST /api/v1/api-keys
创建API Key

**请求**：
```json
{
  "key_name": "测试Key",
  "expires_days": 30,
  "rate_limit": 60,
  "allowed_models": ["oauth_1_qwen-max"]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "api_key": "sk-abc123...",
    "key_name": "测试Key",
    "expires_at": "2026-03-06T14:30:00"
  }
}
```

#### GET /api/v1/api-keys
获取API Key列表

#### GET /api/v1/api-keys/{key_id}
获取API Key详情

#### DELETE /api/v1/api-keys/{key_id}
删除API Key

#### GET /api/v1/api-keys/{key_id}/stats
获取API Key使用统计

### 2. OpenAPI代理接口

#### GET /v1/models
获取模型列表（OpenAI兼容）

**认证**：Bearer Token（API Key）

**响应**：
```json
{
  "object": "list",
  "data": [
    {
      "id": "oauth_1_qwen-max",
      "object": "model",
      "created": 1738656000,
      "owned_by": "qwen",
      "permission": [],
      "root": "oauth_1_qwen-max",
      "parent": null
    }
  ]
}
```

#### POST /v1/chat/completions
聊天完
