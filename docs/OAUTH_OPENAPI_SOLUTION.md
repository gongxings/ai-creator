# OAuth账号对外提供OpenAPI服务 - 完整方案

## 一、项目背景与目标

### 1.1 当前状况
- 已实现OAuth授权管理系统，支持通义千问、OpenAI、Claude等多个AI平台
- 已集成LiteLLM代理，可以调用OAuth授权的账号
- 凭证加密存储，支持配额管理和使用日志

### 1.2 核心需求
1. **统一模型管理**：在写作/图片/视频等场景中，用户可以选择使用哪个来源的模型（OAuth账号或API Key）
2. **OpenAPI代理服务**：将授权的账号通过标准OpenAI兼容接口对外提供，供其他应用调用
3. **智能默认选择**：从用户历史创作记录中读取上次使用的模型，作为默认选项
4. **状态管理**：过期/配额用尽的账号自动过滤或标记为不可用

### 1.3 使用场景
- **场景A**：用户在平台内创作时，可以灵活选择使用免费的OAuth账号或自己的API Key
- **场景B**：用户通过API Key将自己的OAuth账号授权给第三方应用使用
- **场景C**：统一管理所有AI账号的使用情况和配额

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端应用                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  写作工具    │  │  图片生成    │  │  视频生成    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  内部API接口    │
                    │  /api/v1/*      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  模型服务层    │  │  API Key管理    │  │  OpenAPI代理   │
│ ModelService   │  │ APIKeyService   │  │  /v1/*         │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  LiteLLM代理    │
                    │  OAuth服务      │
                    │  AI服务工厂     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  OAuth账号     │  │  API Key模型    │  │  外部AI服务    │
│  (免费额度)    │  │  (用户付费)     │  │  (直接调用)    │
└────────────────┘  └─────────────────┘  └────────────────┘
```

### 2.2 核心组件

#### 模型服务层（ModelService）
- 统一管理OAuth账号和API Key配置的模型
- 提供模型列表查询接口
- 实现模型调用路由逻辑
- 处理模型状态过滤和排序

#### API Key管理（APIKeyService）
- 生成和管理用户的API Key
- 实现API Key认证和验证
- 速率限制和配额控制
- 使用日志记录和统计

#### OpenAPI代理（OpenAPIProxy）
- 提供OpenAI兼容的API接口
- 支持流式和非流式响应
- 统一的错误处理
- 请求日志和监控

---

## 三、数据模型设计

### 3.1 现有表（无需修改）
- **oauth_accounts**：OAuth账号信息
- **oauth_usage_logs**：OAuth使用日志
- **ai_models**：API Key配置的模型
- **creations**：用户创作记录
- **platform_config**：平台配置

### 3.2 新增表

#### api_keys（API Key管理表）
**用途**：管理用户生成的API Key，用于对外提供服务

**核心字段**：
- 基本信息：id, user_id, key_name, api_key, key_hash
- 权限控制：is_active, allowed_models, rate_limit
- 使用统计：total_requests, total_tokens, last_used_at
- 时间管理：expires_at, created_at, updated_at

**关键特性**：
- API Key格式：`sk-{32位随机字符}`
- 使用SHA256哈希存储，不保存明文
- 支持设置过期时间和速率限制
- 可限制允许使用的模型列表

#### api_key_usage_logs（API Key使用日志表）
**用途**：记录通过API Key调用的详细日志

**核心字段**：
- 关联信息：id, api_key_id
- 请求信息：model_id, model_name, endpoint
- Token统计：prompt_tokens, completion_tokens, total_tokens
- 详细数据：request_data, response_data, error_message
- 追踪信息：ip_address, user_agent, created_at

---

## 四、API接口设计

### 4.1 内部API（给前端使用）

#### 获取可用模型列表
- **接口**：`GET /api/v1/models/available`
- **参数**：scene_type（可选，如writing/image/video）
- **功能**：
  - 返回用户所有可用的模型（OAuth + API Key）
  - 自动过滤过期和配额用尽的账号
  - 标记用户上次使用的模型（is_preferred）
  - 按优先级排序：preferred > oauth(免费) > api_key

#### 统一模型调用
- **接口**：`POST /api/v1/ai/chat`
- **参数**：model_id, messages, scene_type, stream
- **功能**：
  - 根据model_id自动路由到对应的服务
  - 支持流式和非流式响应
  - 自动记录使用日志
  - 更新creations表的model_id字段

### 4.2 API Key管理接口

#### 生成API Key
- **接口**：`POST /api/v1/api-keys`
- **参数**：key_name, expires_days, rate_limit, allowed_models
- **功能**：
  - 生成新的API Key（sk-开头）
  - 只在创建时返回完整Key
  - 存储SHA256哈希值
  - 设置过期时间和权限

#### 获取API Key列表
- **接口**：`GET /api/v1/api-keys`
- **功能**：
  - 返回用户的所有API Key
  - 只显示Key的前后几位（如sk-****...****1234）
  - 显示使用统计和状态

#### 删除/禁用API Key
- **接口**：`DELETE /api/v1/api-keys/{key_id}`
- **功能**：立即撤销API Key

#### 获取API Key使用统计
- **接口**：`GET /api/v1/api-keys/{key_id}/stats`
- **功能**：查看详细的使用日志和统计

### 4.3 OpenAPI代理接口（兼容OpenAI）

#### 聊天完成
- **接口**：`POST /v1/chat/completions`
- **认证**：Bearer Token（API Key）
- **参数**：model, messages, stream, temperature等
- **功能**：
  - 完全兼容OpenAI API格式
  - 自动路由到对应的OAuth账号或AI模型
  - 支持流式响应（SSE）
  - 返回标准的OpenAI响应格式

#### 获取模型列表
- **接口**：`GET /v1/models`
- **认证**：Bearer Token（API Key）
- **功能**：
  - 返回该API Key可用的所有模型
  - 兼容OpenAI的models接口格式

---

## 五、核心功能实现

### 5.1 模型ID设计

为了统一管理不同来源的模型，设计统一的model_id格式：

- **OAuth账号模型**：`oauth_{account_id}_{model_name}`
  - 示例：`oauth_123_qwen-max`
  - 解析：账号ID=123，模型=qwen-max

- **API Key模型**：`ai_model_{model_id}`
  - 示例：`ai_model_456`
  - 解析：ai_models表的ID=456

### 5.2 模型列表返回格式

返回给前端的模型信息结构：

**字段说明**：
- model_id：统一的模型标识符
- model_name：实际的模型名称（如gpt-4, qwen-max）
- display_name：显示名称（如"qwen-max (我的通义千问)"）
- provider：提供商（qwen/openai/claude等）
- source_type：来源类型（oauth/api_key）
- source_id：来源ID（账号ID或模型ID）
- is_free：是否免费（OAuth账号为true）
- is_preferred：是否为用户偏好（上次使用）
- status：状态（active/expired/quota_exceeded）
- quota_info：配额信息（已用/总量/百分比）

### 5.3 模型调用路由逻辑

**流程**：
1. 接收model_id和请求参数
2. 解析model_id，判断来源类型
3. 如果是oauth_*：
   - 提取account_id和model_name
   - 调用litellm_proxy.chat_completion()
   - 记录到oauth_usage_logs
4. 如果是ai_model_*：
   - 查询ai_models表获取配置
   - 使用AI服务工厂调用对应服务
   - 记录使用日志
5. 返回统一格式的响应

### 5.4 智能默认选择

**实现方式**：
1. 查询creations表，按created_at倒序
2. 筛选条件：user_id + scene_type（如writing）
3. 获取最近一条记录的model_id
4. 在模型列表中标记该模型的is_preferred=true
5. 前端优先显示/选中该模型

### 5.5 状态过滤规则

**过滤逻辑**：
- OAuth账号：
  - is_active=false：不显示
  - is_expired=true：标记为expired，可显示但不可用
  - quota_used >= quota_limit：标记为quota_exceeded
  
- API Key模型：
  - is_enabled=false：不显示
  - 其他情况：正常显示

### 5.6 API Key认证流程

**认证步骤**：
1. 从请求头提取：`Authorization: Bearer sk-xxx`
2. 计算API Key的SHA256哈希
3. 查询api_keys表匹配key_hash
4. 验证：
   - is_active必须为true
   - expires_at未过期（如果设置）
   - 检查速率限制（Redis）
5. 认证成功后，将user_id注入到请求上下文

---

## 六、安全设计

### 6.1 API Key安全

**生成规则**：
- 格式：`sk-{32位随机字符}`
- 使用secrets.token_urlsafe()生成
- 只在创建时返回完整Key
- 后续只显示：`sk-****...****1234`

**存储安全**：
- 使用SHA256哈希存储
- 不保存明文Key
- 验证时对比哈希值

**使用安全**：
- 支持设置过期时间
- 支持随时撤销（删除或禁用）
- 记录所有使用日志

### 6.2 速率限制

**实现方案**：
- 使用Redis的滑动窗口算法
- 每个API Key独立限制
- 默认：60次/分钟
- 可在创建时自定义

**限制响应**：
- 超限返回429状态码
- 响应头包含限制信息：
  - X-RateLimit-Limit：限制数
  - X-RateLimit-Remaining：剩余次数
  - X-RateLimit-Reset：重置时间戳

### 6.3 权限控制

**模型访问控制**：
- API Key可限制allowed_models列表
- 为空表示可访问所有模型
- 请求时验证model是否在允许列表中

**用户隔离**：
- 用户只能访问自己的OAuth账号
- 用户只能访问自己的API Key配置
- API Key只能调用所属用户的模型

### 6.4 日志审计

**记录内容**：
- 所有API调用（成功和失败）
- IP地址和User-Agent
- 请求和响应数据（可选）
- Token使用量
- 错误信息

**日志用途**：
- 安全审计和异常检测
- 使用统计和成本分析
- 问题排查和调试

---

## 七、前端集成

### 7.1 模型选择组件

**组件功能**：
- 下拉选择框展示所有可用模型
- 分组显示：OAuth账号（免费）/ API Key（付费）
- 显示模型状态图标（正常/过期/配额不足）
- 显示配额使用情况进度条
- 自动选中用户上次使用的模型
- 支持搜索和过滤

**集成位置**：
- 写作工具页面
- 图片生成页面
- 视频生成页面
- 其他需要调用AI的场景

### 7.2 API Key管理页面

**页面功能**：
- 创建新的API Key
- 查看已有的API Key列表
- 查看使用统计和图表
- 删除/禁用API Key
- 复制API Key（仅创建时）
- 查看使用文档和示例

---

## 八、使用示例

### 8.1 内部使用（前端调用）

**获取模型列表**：
```
GET /api/v1/models/available?scene_type=writing
Authorization: Bearer {jwt_token}
```

**调用模型**：
```
POST /api/v1/ai/chat
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "model_id": "oauth_123_qwen-max",
  "messages": [...],
  "scene_type": "writing",
  "stream": false
}
```

### 8.2 外部使用（OpenAPI代理）

**获取模型列表**：
```
GET /v1/models
Authorization: Bearer sk-xxxxx
```

**聊天完成（非流式）**：
```
POST /v1/chat/completions
Authorization: Bearer sk-xxxxx
Content-Type: application/json

{
  "model": "oauth_123_qwen-max",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
```

**聊天完成（流式）**：
```
POST /v1/chat/completions
Authorization: Bearer sk-xxxxx
Content-Type: application/json

{
  "model": "oauth_123_qwen-max",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "stream": true
}
```

### 8.3 第三方应用集成

**Python示例**：
使用OpenAI SDK，只需修改base_url和api_key即可无缝集成

**Node.js示例**：
使用OpenAI官方库，配置自定义endpoint

**Cursor/Continue等IDE插件**：
在配置中添加自定义模型提供商

---

## 九、技术优势

### 9.1 统一管理
- 一个平台管理所有AI账号
- 统一的使用日志和统计
- 集中的配额监控
- 简化的账号维护

### 9.2 灵活选择
- 自由切换免费和付费模型
- 智能记忆用户偏好
- 实时显示账号状态
- 支持多账号负载均衡

### 9.3 安全可靠
- 凭证加密存储
- API Key哈希验证
- 完善的权限控制
- 详细的审计日志

### 9.4 易于集成
- 完全兼容OpenAI API
- 支持主流开发语言
- 可集成到各类应用
- 丰富的使用文档

---

## 十、注意事项

### 10.1 配额管理
- 定期检查OAuth账号配额
- 设置配额预警阈值
- 配额用尽自动切换备用账号
- 提供配额充值提醒

### 10.2 账号维护
- 定期验证OAuth凭证有效性
- 自动刷新即将过期的凭证
- 及时处理失效账号
- 保持平台配置更新

### 10.3 性能优化
- 使用Redis缓存模型列表
- 异步处理使用日志
- 连接池管理数据库连接
- 合理设置超时时间

### 10.4 监控告警
- 监控API调用成功率
- 监控响应时间
- 监控错误率和类型
- 设置异常告警通知

---

## 十一、扩展规划

### 11.1 功能扩展
- 支持图片生成模型
- 支持视频生成模型
- 支持语音合成模型
- 支持更多AI平台

### 11.2 管理增强
- 多用户协作管理
- 团队配额分配
- 成本统计和分析
- 使用报表导出

### 11.3 性能提升
- 模型调用负载均衡
- 智能路由选择
- 请求队列管理
- 缓存策略优化

---

## 十二、总结

本方案通过统一的模型服务层，将OAuth授权的免费账号和用户自己的API Key整合在一起，提供了：

1. **统一的模型管理界面**：用户可以在一个地方管理所有AI模型来源
2. **智能的模型选择**：自动记忆用户偏好，优先推荐免费可用的模型
3. **标准的OpenAPI接口**：完全兼容OpenAI API，方便第三方应用集成
4. **完善的安全机制**：API Key哈希存储、速率限制、权限控制、审计日志
5. **灵活的扩展能力**：易于添加新的AI平台和模型类型

通过这套方案，用户不仅可以在平台内灵活使用各种AI模型，还可以通过API Key将自己的账号授权给其他应用使用，实现了AI能力的统一管理和对外服务。
