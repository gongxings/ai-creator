# OAuth代理功能使用指南

## 功能概述

OAuth代理功能允许用户通过OAuth2.0授权方式绑定AI平台账号，使用平台的免费额度进行创作，无需消耗系统积分。

## 支持的平台

目前支持以下6个AI平台：

1. **通义千问（Qwen）**
   - 平台：阿里云百炼平台
   - 免费额度：每日100万tokens
   - 支持模型：qwen-turbo, qwen-plus, qwen-max等

2. **OpenAI ChatGPT**
   - 平台：OpenAI官网
   - 免费额度：根据账号类型
   - 支持模型：gpt-3.5-turbo, gpt-4等

3. **文心一言（ERNIE）**
   - 平台：百度智能云
   - 免费额度：每日10万tokens
   - 支持模型：ernie-bot-turbo, ernie-bot等

4. **智谱清言（GLM）**
   - 平台：智谱AI开放平台
   - 免费额度：每日100万tokens
   - 支持模型：glm-3-turbo, glm-4等

5. **讯飞星火（Spark）**
   - 平台：讯飞开放平台
   - 免费额度：每日50万tokens
   - 支持模型：spark-lite, spark-pro等

6. **Claude**
   - 平台：Anthropic官网
   - 免费额度：根据账号类型
   - 支持模型：claude-3-haiku, claude-3-sonnet等

## 使用流程

### 1. 添加OAuth账号

1. 登录系统后，进入"OAuth账号管理"页面
2. 点击"添加账号"按钮
3. 选择要绑定的平台
4. 输入账号名称（用于识别，如"我的通义千问账号"）
5. 点击"确定"，系统会自动打开浏览器窗口
6. 在浏览器中完成平台登录和授权
7. 授权成功后，系统会自动保存凭证并关闭浏览器

### 2. 使用OAuth账号创作

#### 方式一：在写作工具中使用

1. 进入任意写作工具（如公众号文章创作）
2. 在模型选择下拉框中，会看到"OAuth账号"分组
3. 选择已绑定的OAuth账号
4. 正常使用写作功能，不会消耗系统积分

#### 方式二：通过API调用

```python
import requests

# 使用OAuth账号进行聊天
response = requests.post(
    'http://your-domain/api/v1/oauth/chat/completions',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    json={
        'account_id': 1,  # OAuth账号ID
        'messages': [
            {'role': 'user', 'content': '你好'}
        ],
        'model': 'qwen-turbo',  # 可选，不指定则使用默认模型
        'stream': False
    }
)

print(response.json())
```

### 3. 管理OAuth账号

#### 查看账号状态

在"OAuth账号管理"页面可以看到：
- 账号名称和平台
- 当前状态（正常/已禁用）
- 配额使用情况（已用/总额）
- 最后使用时间
- 凭证过期时间

#### 检查账号有效性

点击"检查"按钮，系统会验证账号凭证是否有效：
- 如果凭证过期，会提示重新授权
- 如果账号被封禁，会显示相应提示
- 如果一切正常，会显示"账号有效"

#### 查看使用记录

点击"使用记录"按钮，可以查看该账号的所有API调用记录：
- 使用的模型
- 消耗的tokens（输入/输出/总计）
- 请求和响应数据
- 错误信息（如果有）
- 调用时间

#### 编辑账号

点击"编辑"按钮，可以：
- 修改账号名称
- 启用/禁用账号

#### 删除账号

点击"删除"按钮，确认后会删除该OAuth账号及其所有使用记录。

## 配额管理

### 配额计算

- 每个平台都有每日免费配额限制
- 系统会自动追踪每个账号的配额使用情况
- 当配额使用超过70%时，进度条会变为橙色
- 当配额使用超过90%时，进度条会变为红色

### 配额重置

- 大部分平台的配额每日0点重置
- 系统会自动重置配额计数器
- 如果配额用完，系统会自动切换到积分模式

### 多账号负载均衡

如果绑定了同一平台的多个账号：
- 系统会自动选择配额剩余最多的账号
- 实现负载均衡，充分利用免费额度
- 如果所有账号配额都用完，会提示用户

## 安全说明

### 凭证加密

- 所有OAuth凭证都使用AES-256加密存储
- 加密密钥存储在环境变量中，不会提交到代码库
- 即使数据库泄露，攻击者也无法获取原始凭证

### 权限隔离

- 每个用户只能访问自己的OAuth账号
- 管理员也无法查看用户的凭证明文
- API调用时会验证账号所有权

### 自动过期

- OAuth凭证都有过期时间
- 过期后需要重新授权
- 系统会在凭证过期前7天提醒用户

## 常见问题

### Q1: 为什么授权失败？

可能的原因：
1. 浏览器被拦截弹窗，请允许弹窗
2. 平台登录超时，请重试
3. 网络连接问题，请检查网络
4. 平台维护中，请稍后再试

### Q2: 配额用完了怎么办？

解决方案：
1. 等待配额重置（通常是每日0点）
2. 绑定同一平台的其他账号
3. 切换到其他平台的账号
4. 使用系统积分模式

### Q3: 账号显示"已禁用"是什么意思？

可能的原因：
1. 用户手动禁用了账号
2. 凭证已过期
3. 平台账号被封禁
4. 连续多次调用失败

解决方案：
1. 点击"检查"按钮查看具体原因
2. 如果凭证过期，重新授权即可
3. 如果账号被封禁，联系平台客服
4. 如果是手动禁用，在编辑页面重新启用

### Q4: 如何知道哪个平台的免费额度最多？

参考上面"支持的平台"部分的免费额度说明：
- 通义千问和智谱清言：每日100万tokens（最多）
- 讯飞星火：每日50万tokens
- 文心一言：每日10万tokens
- OpenAI和Claude：根据账号类型而定

### Q5: 可以同时绑定多个平台吗？

可以！建议：
1. 绑定多个不同平台的账号
2. 每个平台可以绑定多个账号
3. 系统会自动选择最优账号
4. 充分利用各平台的免费额度

### Q6: OAuth账号和API密钥有什么区别？

| 特性 | OAuth账号 | API密钥 |
|------|----------|---------|
| 获取方式 | 浏览器登录授权 | 平台后台申请 |
| 免费额度 | 使用平台免费额度 | 需要充值 |
| 消耗积分 | 不消耗 | 消耗系统积分 |
| 安全性 | 更高（加密存储） | 较高 |
| 使用限制 | 受平台配额限制 | 受积分余额限制 |

### Q7: 凭证会泄露吗？

不会，因为：
1. 凭证使用AES-256加密存储
2. 加密密钥不在代码库中
3. 传输过程使用HTTPS
4. 只有账号所有者可以使用
5. 管理员也无法查看明文

## 最佳实践

### 1. 多平台策略

建议绑定多个平台的账号：
```
通义千问（主力） → 智谱清言（备用） → 讯飞星火（备用）
```

### 2. 多账号策略

对于高频使用场景，建议同一平台绑定多个账号：
```
通义千问账号1（工作） + 通义千问账号2（个人）
```

### 3. 配额监控

定期检查配额使用情况：
- 每天查看一次配额使用
- 配额超过80%时考虑切换账号
- 提前准备备用账号

### 4. 定期检查

建议每周检查一次账号状态：
- 验证凭证是否有效
- 查看是否有异常调用
- 更新即将过期的凭证

### 5. 合理使用

避免滥用免费额度：
- 不要频繁调用API
- 不要用于商业用途
- 遵守平台使用条款
- 避免被平台封禁

## 技术细节

### 凭证存储格式

```json
{
  "cookies": {
    "session_id": "encrypted_value",
    "token": "encrypted_value"
  },
  "headers": {
    "Authorization": "encrypted_value"
  },
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### API调用流程

```
用户请求 → 验证账号所有权 → 检查配额 → 解密凭证 
→ 调用平台API → 记录使用量 → 返回结果
```

### 配额计算方式

```python
# 输入tokens
prompt_tokens = len(prompt) / 4  # 粗略估算

# 输出tokens
completion_tokens = len(completion) / 4

# 总tokens
total_tokens = prompt_tokens + completion_tokens

# 更新配额
quota_used += total_tokens
```

## 开发者接口

### REST API

```bash
# 获取平台列表
GET /api/v1/oauth/platforms

# 授权账号
POST /api/v1/oauth/accounts/authorize
{
  "platform": "qwen",
  "account_name": "我的账号"
}

# 获取账号列表
GET /api/v1/oauth/accounts?platform=qwen

# 聊天完成
POST /api/v1/oauth/chat/completions
{
  "account_id": 1,
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "model": "qwen-turbo",
  "stream": false
}
```

### Python SDK示例

```python
from ai_creator import OAuthClient

# 初始化客户端
client = OAuthClient(api_key='your_api_key')

# 获取账号列表
accounts = client.oauth.list_accounts()

# 使用OAuth账号聊天
response = client.oauth.chat_completion(
    account_id=1,
    messages=[
        {'role': 'user', 'content': '你好'}
    ],
    model='qwen-turbo'
)

print(response.choices[0].message.content)
```

### JavaScript SDK示例

```javascript
import { OAuthClient } from 'ai-creator-sdk'

// 初始化客户端
const client = new OAuthClient({ apiKey: 'your_api_key' })

// 获取账号列表
const accounts = await client.oauth.listAccounts()

// 使用OAuth账号聊天
const response = await client.oauth.chatCompletion({
  accountId: 1,
  messages: [
    { role: 'user', content: '你好' }
  ],
  model: 'qwen-turbo'
})

console.log(response.choices[0].message.content)
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持6个AI平台
- 实现OAuth2.0授权
- 实现凭证加密存储
- 实现配额管理
- 实现使用记录追踪

### 未来计划

- [ ] 支持更多AI平台
- [ ] 实现自动凭证刷新
- [ ] 添加配额预警通知
- [ ] 支持团队共享账号
- [ ] 添加使用统计报表
- [ ] 支持自定义配额限制

## 联系支持

如有问题，请通过以下方式联系我们：

- 邮箱：support@ai-creator.com
- 微信：AI_Creator_Support
- QQ群：123456789
- GitHub：https://github.com/your-org/ai-creator

## 许可证

本功能遵循 MIT 许可证。
</content>
<task_progress>
- [x] 确认技术实现方案（方案B：纯后端代理）
- [x] 确认代理平台范围（6个平台）
