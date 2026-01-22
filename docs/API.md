# AI创作者平台 API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

## 认证相关 API

### 1. 用户注册
**POST** `/auth/register`

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 2. 用户登录
**POST** `/auth/login`

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

### 3. 刷新Token
**POST** `/auth/refresh`

**请求头**:
```
Authorization: Bearer {refresh_token}
```

**响应**:
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
  }
}
```

### 4. 获取当前用户信息
**GET** `/auth/me`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "daily_quota": 100,
    "used_quota": 10,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## AI写作 API

### 1. 获取写作工具列表
**GET** `/writing/tools`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "type": "wechat_article",
      "name": "公众号文章",
      "description": "专业的微信公众号文章创作",
      "icon": "📱"
    },
    {
      "type": "xiaohongshu_note",
      "name": "小红书笔记",
      "description": "吸引人的小红书种草笔记",
      "icon": "📕"
    }
  ]
}
```

### 2. 生成内容
**POST** `/writing/{tool_type}/generate`

**路径参数**:
- `tool_type`: 工具类型（如 wechat_article, xiaohongshu_note 等）

**请求体**:
```json
{
  "topic": "如何提高工作效率",
  "keywords": ["时间管理", "效率工具"],
  "style": "专业",
  "length": "medium",
  "additional_requirements": "需要包含实用案例"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "id": 123,
    "type": "wechat_article",
    "title": "提高工作效率的10个实用技巧",
    "content": "文章内容...",
    "metadata": {
      "word_count": 1500,
      "reading_time": "5分钟"
    },
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 3. 重新生成
**POST** `/writing/{creation_id}/regenerate`

**路径参数**:
- `creation_id`: 创作ID

**请求体**:
```json
{
  "requirements": "增加更多案例，语气更轻松"
}
```

### 4. 优化内容
**POST** `/writing/{creation_id}/optimize`

**请求体**:
```json
{
  "optimization_type": "seo",  // seo, readability, style
  "target_platform": "wechat"
}
```

## 创作记录 API

### 1. 获取创作列表
**GET** `/creations`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `type`: 创作类型（可选）
- `status`: 状态（可选）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 123,
        "type": "wechat_article",
        "title": "文章标题",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 2. 获取创作详情
**GET** `/creations/{id}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 123,
    "type": "wechat_article",
    "title": "文章标题",
    "content": "文章内容...",
    "metadata": {},
    "versions": [
      {
        "version": 1,
        "content": "版本1内容",
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### 3. 更新创作
**PUT** `/creations/{id}`

**请求体**:
```json
{
  "title": "新标题",
  "content": "新内容"
}
```

### 4. 删除创作
**DELETE** `/creations/{id}`

## 图片生成 API

### 1. 文本生成图片
**POST** `/image/generate`

**请求体**:
```json
{
  "prompt": "一只可爱的猫咪在花园里玩耍
