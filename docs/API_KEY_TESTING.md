# API Key功能测试文档

## 测试环境准备

1. 启动后端服务：
```bash
cd backend
python3 run.py
```

2. 确保数据库已迁移：
```bash
python3 backend/scripts/add_api_key_tables.py
```

## 测试步骤

### 1. 用户登录获取Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
  }
}
```

将获取的`access_token`保存为环境变量：
```bash
export TOKEN="eyJhbGc..."
```

### 2. 获取可用模型列表

```bash
curl -X GET "http://localhost:8000/api/v1/models/available" \
  -H "Authorization: Bearer $TOKEN"
```

响应示例：
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

### 3. 创建API Key

```bash
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "测试API Key",
    "expires_days": 30,
    "rate_limit": 60,
    "allowed_models": ["oauth_1_qwen-max"]
  }'
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "api_key": "sk-abc123def456...",
    "key_name": "测试API Key",
    "expires_at": "2026-03-06T14:30:00"
  }
}
```

**重要**：保存返回的`api_key`，这是唯一一次可以看到完整Key的机会！

```bash
export API_KEY="sk-abc123def456..."
```

### 4. 获取API Key列表

```bash
curl -X GET http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer $TOKEN"
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_keys": [
      {
        "id": 1,
        "key_name": "测试API Key",
        "masked_key": "sk-****...****456",
        "is_active": true,
        "total_requests": 0,
        "total_tokens": 0,
        "last_used_at": null,
        "expires_at": "2026-03-06T14:30:00",
        "created_at": "2026-02-04T14:30:00"
      }
    ]
  }
}
```

### 5. 获取API Key详情

```bash
curl -X GET http://localhost:8000/api/v1/api-keys/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 6. 使用统一AI接口调用模型

```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "oauth_1_qwen-max",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下你自己"}
    ],
    "stream": false
  }'
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "你好！我是通义千问...",
    "model": "qwen-max",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 50,
      "total_tokens": 60
    }
  }
}
```

### 7. 测试OpenAPI代理 - 获取模型列表

```bash
curl -X GET http://localhost:8000/v1/models \
  -H "Authorization: Bearer $API_KEY"
```

响应示例（OpenAI兼容格式）：
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

### 8. 测试OpenAPI代理 - 聊天完成（非流式）

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "oauth_1_qwen-max",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

响应示例（OpenAI兼容格式）：
```json
{
  "id": "chatcmpl-1738656000",
  "object": "chat.completion",
  "created": 1738656000,
  "model": "oauth_1_qwen-max",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么我可以帮助你的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 15,
    "total_tokens": 20
  }
}
```

### 9. 测试OpenAPI代理 - 聊天完成（流式）

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "oauth_1_qwen-max",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "stream": true
  }'
```

响应示例（SSE流式）：
```
data: {"id":"chatcmpl-1738656000","object":"chat.completion.chunk","created":1738656000,"model":"oauth_1_qwen-max","choices":[{"index":0,"delta":{"content":"你"},"finish
