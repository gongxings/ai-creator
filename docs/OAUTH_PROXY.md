# OAuth代理功能文档

## 功能概述

OAuth代理功能允许用户通过OAuth2.0授权登录各大AI平台（通义千问、OpenAI、Claude等），使用平台的免费额度在本项目中调用AI模型，无需自己申请和管理API密钥。

## 支持的平台

目前支持以下8个AI平台：

1. **通义千问 (Qwen)** - 阿里云通义千问大模型
2. **OpenAI** - GPT系列模型
3. **Claude** - Anthropic Claude系列模型
4. **文心一言 (Baidu)** - 百度文心大模型
5. **智谱AI (Zhipu)** - GLM系列模型
6. **讯飞星火 (Spark)** - 讯飞星火认知大模型
7. **Google Gemini** - Google Gemini系列模型
8. **豆包 (Doubao)** - 字节跳动豆包大模型

## 核心特性

### 1. 浏览器自动化登录
- 使用Playwright自动化浏览器
- 支持多种登录方式（账号密码、手机验证码、邮箱验证码）
- 自动处理验证码和二次验证
- 支持Cookie持久化

### 2. 统一的LiteLLM接口
- 所有平台统一使用LiteLLM标准接口
- 自动转换不同平台的API格式
- 支持流式和非流式响应
- 自动处理错误和重试

### 3. 配额管理
- 自动追踪每个账号的使用量
- 支持每日配额限制
- 支持请求频率限制
- 配额用尽自动切换账号

### 4. 多账号管理
- 支持同一平台绑定多个账号
- 自动负载均衡
- 账号状态监控
- 过期账号自动禁用

## 技术架构

### 后端架构

```
backend/app/
├── models/
│   ├── oauth_account.py          # OAuth账号模型
│   └── platform_config.py        # 平台配置模型
├── services/
│   └── oauth/
│       ├── oauth_service.py      # OAuth服务主类
│       ├── browser_automation.py # 浏览器自动化
│       ├── litellm_proxy.py      # LiteLLM代理
│       └── adapters/             # 平台适配器
│           ├── base.py           # 基础适配器
│           ├── qwen.py           # 通义千问适配器
│           ├── openai.py         # OpenAI适配器
│           ├── claude.py         # Claude适配器
│           ├── baidu.py          # 文心一言适配器
│           ├── zhipu.py          # 智谱AI适配器
│           ├── spark.py          # 讯飞星火适配器
│           ├── gemini.py         # Gemini适配器
│           └── doubao.py         # 豆包适配器
└── api/v1/
    └── oauth.py                  # OAuth API路由
```

### 数据库设计

#### oauth_accounts表
```sql
CREATE TABLE oauth_accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    platform_id VARCHAR(50) NOT NULL,
    account_name VARCHAR(100),
    cookies JSON,
    access_token VARCHAR(500),
    refresh_token VARCHAR(500),
    expires_at DATETIME,
    quota_used INT DEFAULT 0,
    quota_limit INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_expired BOOLEAN DEFAULT FALSE,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_platform (user_id, platform_id),
    INDEX idx_active (is_active, is_expired)
);
```

#### platform_configs表
```sql
CREATE TABLE platform_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    platform_id VARCHAR(50) UNIQUE NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    description TEXT,
    oauth_config JSON NOT NULL,
    litellm_config JSON NOT NULL,
    quota_config JSON,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## API接口

### 1. 获取支持的平台列表
```http
GET /api/v1/oauth/platforms
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "platform_id": "qwen",
      "platform_name": "通义千问",
      "description": "阿里云通义千问大模型",
      "is_enabled": true,
      "available_models": ["qwen-turbo", "qwen-plus", "qwen-max"]
    }
  ]
}
```

### 2. 发起OAuth授权
```http
POST /api/v1/oauth/initiate
Content-Type: application/json

{
  "platform": "qwen",
  "account_name": "我的通义千问账号"
}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "auth_url": "https://dashscope.aliyun.com/login",
    "state": "random_state_string"
  }
}
```

### 3. OAuth回调处理
```http
GET /api/v1/oauth/callback?state=xxx&code=xxx
```

### 4. 获取OAuth账号列表
```http
GET /api/v1/oauth/accounts
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "platform_id": "qwen",
      "platform_name": "通义千问",
      "account_name": "我的通义千问账号",
      "quota_used": 1000,
      "quota_limit": 1000000,
      "is_active": true,
      "is_expired": false,
      "last_used_at": "2024-01-01T12:00:00",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### 5. 刷新OAuth账号
```http
POST /api/v1/oauth/accounts/{account_id}/refresh
```

### 6. 启用/禁用OAuth账号
```http
PUT /api/v1/oauth/accounts/{account_id}/toggle
```

### 7. 删除OAuth账号
```http
DELETE /api/v1/oauth/accounts/{account_id}
```

### 8. 使用OAuth账号调用AI
```http
POST /api/v1/oauth/chat/completions
Content-Type: application/json

{
  "platform": "qwen",
  "model": "qwen-turbo",
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "stream": false
}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "qwen-turbo",
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
      "prompt_tokens": 10,
      "completion_tokens": 20,
      "total_tokens": 30
    }
  }
}
```

## 使用流程

### 1. 用户端流程

1. **添加OAuth账号**
   - 用户在设置页面点击"添加OAuth账号"
   - 选择要授权的平台（如通义千问）
   - 输入账号名称（用于识别）
   - 点击"开始授权"

2. **浏览器授权**
   - 系统打开新窗口，跳转到平台登录页
   - 用户在平台完成登录（账号密码/手机验证码等）
   - 系统自动捕获登录凭证（Cookie/Token）
   - 授权完成，窗口自动关闭

3. **使用OAuth账号**
   - 在写作工具中选择使用OAuth账号
   - 系统自动选择可用的账号
   - 调用AI模型生成内容
   - 自动扣除配额

4. **管理OAuth账号**
   - 查看账号列表和配额使用情况
   - 刷新过期的账号
   - 启用/禁用账号
   - 删除不需要的账号

### 2. 系统端流程

1. **OAuth授权流程**
   ```
   用户发起授权
   ↓
   生成授权状态码(state)
   ↓
   启动Playwright浏览器
   ↓
   导航到平台登录页
   ↓
   等待用户完成登录
   ↓
   捕获Cookie/Token
   ↓
   保存到数据库
   ↓
   关闭浏览器
   ↓
   返回授权成功
   ```

2. **AI调用流程**
   ```
   接收AI调用请求
   ↓
   查找可用的OAuth账号
   ↓
   检查配额是否充足
   ↓
   使用LiteLLM调用平台API
   ↓
   返回AI响应
   ↓
   更新配额使用量
   ```

3. **配额管理流程**
   ```
   每次调用前检查配额
   ↓
   配额充足：继续调用
   ↓
   配额不足：切换到下一个账号
   ↓
   所有账号配额用尽：返回错误
   ↓
   每日0点重置配额
   ```

## 平台适配器开发指南

### 创建新的平台适配器

1. **继承基础适配器**
```python
from .base import BasePlatformAdapter

class NewPlatformAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__()
        self.platform_id = "new_platform"
```

2. **实现登录方法**
```python
async def login(self, page, credentials: dict) -> dict:
    """
    实现平台特定的登录逻辑
    
    Args:
        page: Playwright页面对象
        credentials: 登录凭证
        
    Returns:
        包含cookies和tokens的字典
    """
    # 导航到登录页
    await page.goto("https://platform.com/login")
    
    # 填写登录表单
    await page.fill("input[name='username']", credentials["username"])
    await page.fill("input[name='password']", credentials["password"])
    
    # 点击登录按钮
    await page.click("button[type='submit']")
    
    # 等待登录完成
    await page.wait_for_url("**/dashboard")
    
    # 获取cookies
    cookies = await page.context.cookies()
    
    return {
        "cookies": cookies,
        "access_token": None,
        "refresh_token": None
    }
```

3. **实现Token刷新方法**
```python
async def refresh_token(self, account: OAuthAccount) -> dict:
    """
    刷新访问令牌
    
    Args:
        account: OAuth账号对象
        
    Returns:
        新的tokens
    """
    # 实现token刷新逻辑
    pass
```

4. **实现配额查询方法**
```python
async def get_quota(self, account: OAuthAccount) -> dict:
    """
    查询账号配额
    
    Args:
        account: OAuth账号对象
        
    Returns:
        配额信息
    """
    # 实现配额查询逻辑
    return {
        "used": 1000,
        "limit": 1000000,
        "reset_at": "2024-01-02T00:00:00"
    }
```

5. **注册适配器**
```python
# 在adapters/__init__.py中注册
from .new_platform import NewPlatformAdapter

PLATFORM_ADAPTERS = {
    "new_platform": NewPlatformAdapter,
    # ... 其他适配器
}
```

## 配置说明

### 环境变量

```bash
# Playwright配置
PLAYWRIGHT_HEADLESS=true          # 是否无头模式
PLAYWRIGHT_TIMEOUT=30000          # 超时时间(毫秒)

# OAuth配置
OAUTH_STATE_EXPIRE=600            # 授权状态过期时间(秒)
OAUTH_CALLBACK_URL=http://localhost:8000/api/v1/oauth/callback

# LiteLLM配置
LITELLM_LOG_LEVEL=INFO            # 日志级别
LITELLM_CACHE_ENABLED=true        # 是否启用缓存
```

### 平台配置示例

```json
{
  "platform_id": "qwen",
  "platform_name": "通义千问",
  "oauth_config": {
    "auth_url": "https://dashscope.aliyun.com",
    "login_selectors": {
      "username_input": "input[name='username']",
      "password_input": "input[name='password']",
      "submit_button": "button[type='submit']"
    },
    "cookie_names": ["session_id", "auth_token"]
  },
  "litellm_config": {
    "provider": "qwen",
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "default_model": "qwen-turbo",
    "available_models": ["qwen-turbo", "qwen-plus", "qwen-max"]
  },
  "quota_config": {
    "daily_limit": 1000000,
    "rate_limit": 60
  }
}
```

## 安全考虑

### 1. 凭证安全
- Cookie和Token加密存储在数据库
- 使用AES-256加密算法
- 密钥存储在环境变量中
- 定期轮换加密密钥

### 2. 访问控制
- 每个用户只能访问自己的OAuth账号
- API请求需要JWT认证
- 实施请求频率限制
- 记录所有敏感操作日志

### 3. 数据隔离
- 用户数据完全隔离
- 不同平台账号独立管理
- 配额独立计算
- 错误不会影响其他账号

### 4. 浏览器安全
- 使用无头浏览器模式
- 自动清理浏览器缓存
- 禁用不必要的浏览器功能
- 限制浏览器访问权限

## 故障处理

### 常见问题

1. **登录失败**
   - 检查平台登录页面是否变更
   - 验证选择器是否正确
   - 检查网络连接
   - 查看浏览器日志

2. **Token过期**
   - 自动尝试刷新Token
   - 刷新失败则标记账号为过期
   - 通知用户重新授权

3. **配额用尽**
   - 自动切换到其他可用账号
   - 所有账号配额用尽时返回错误
   - 每日自动重置配额

4. **API调用失败**
   - 自动重试（最多3次）
   - 记录错误日志
   - 切换到备用账号
   - 返回友好的错误信息

### 监控和告警

- 监控账号状态（正常/过期/禁用）
- 监控配额使用情况
- 监控API调用成功率
- 异常情况自动告警

## 性能优化

### 1. 缓存策略
- 缓存平台配置（1小时）
- 缓存账号列表（5分钟）
- 缓存配额信息（1分钟）

### 2. 连接池
- 复用HTTP连接
- 限制并发连接数
- 自动清理空闲连接

### 3. 异步处理
- 使用异步IO处理请求
- 浏览器操作异步化
- 批量更新配额信息

### 4. 负载均衡
- 多账号轮询使用
- 基于配额剩余量分配
- 避免单个账号过载

## 部署说明

### 1. 安装依赖

```bash
# 安装Python依赖
pip install playwright litellm aiohttp cryptography

# 安装Playwright浏览器
playwright install chromium
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
python backend/scripts/init_db.py

# 初始化平台配置
python backend/scripts/init_oauth_platforms.py
```

### 4. 启动服务

```bash
# 开发环境
uvicorn app.main:app --reload

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 测试

### 单元测试

```bash
# 运行所有测试
pytest

# 运行OAuth相关测试
pytest tests/test_oauth.py

# 运行适配器测试
pytest tests/test_adapters.py
```

### 集成测试

```bash
# 测试完整的OAuth流程
pytest tests/integration/test_oauth_flow.py

# 测试AI调用
pytest tests/integration/test_ai_call.py
```

## 未来计划

### 短期计划
- [ ] 支持更多AI平台（Cohere、Mistral等）
- [ ] 优化浏览器自动化性能
- [ ] 添加更详细的使用统计
- [ ] 支持账号自动续期

### 长期计划
- [ ] 支持企业级账号管理
- [ ] 添加成本分析功能
- [ ] 支持自定义平台适配器
- [ ] 提供API代理服务

## 贡献指南

欢迎贡献新的平台适配器或改进现有功能！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。
