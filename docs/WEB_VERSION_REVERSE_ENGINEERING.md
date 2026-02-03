# AI平台网页版逆向工程方案

## 概述

本文档说明如何通过逆向工程使用各大AI平台的网页版免费额度，而不是使用需要付费的API密钥。

## 核心理念

### 为什么使用网页版？

1. **免费额度**：网页版通常提供免费使用额度，无需付费
2. **无需API密钥**：不需要申请和管理API密钥
3. **降低成本**：对于个人用户和小型项目，可以大幅降低使用成本
4. **合法合规**：使用自己的账号登录，符合平台使用条款

### 技术方案

通过以下步骤实现网页版API调用：

1. **Cookie获取**：使用Playwright自动化浏览器，用户登录后提取Cookie
2. **API逆向**：分析网页版的API接口，模拟网页请求
3. **会话管理**：维护Cookie有效性，自动刷新过期凭证
4. **统一接口**：封装成统一的API接口，兼容LiteLLM

## 支持的平台

### 1. 通义千问（Qwen）

**网页版地址**：https://tongyi.aliyun.com/qianwen/

**登录方式**：
- 扫码登录（推荐）
- 账号密码登录

**关键Cookie**：
- `login_aliyunid_ticket`
- `login_aliyunid_pk`
- `t`

**API端点**：
```
POST https://qianwen.biz.aliyun.com/dialog/conversation
```

**免费额度**：每日大量免费对话次数

### 2. ChatGPT

**网页版地址**：https://chat.openai.com/

**登录方式**：
- 邮箱+密码
- Google/Microsoft账号

**关键Cookie**：
- `__Secure-next-auth.session-token`
- `_cfuvid`

**API端点**：
```
POST https://chatgpt.com/backend-api/conversation
```

**免费额度**：GPT-3.5无限制，GPT-4有限额度

### 3. Claude

**网页版地址**：https://claude.ai/

**登录方式**：
- 邮箱验证码登录
- Google账号

**关键Cookie**：
- `sessionKey`
- `__cf_bm`
- `_cfuvid`

**API端点**：
```
POST https://claude.ai/api/organizations/{org_id}/chat_conversations/{conversation_id}/completion
```

**免费额度**：每日有限次数的对话

### 4. 文心一言（Baidu）

**网页版地址**：https://yiyan.baidu.com/

**登录方式**：
- 百度账号扫码登录
- 百度账号密码登录

**关键Cookie**：
- `BAIDUID`
- `BDUSS`
- `BDUSS_BFESS`
- `STOKEN`
- `PTOKEN`

**API端点**：
```
POST https://yiyan.baidu.com/eb/chat/new
```

**免费额度**：每日大量免费对话次数

### 5. 智谱清言（ChatGLM）

**网页版地址**：https://chatglm.cn/

**登录方式**：
- 手机号+验证码

**关键Cookie**：
- `chatglm_token`
- `chatglm_refresh_token`
- `chatglm_user_id`

**API端点**：
```
POST https://chatglm.cn/chatglm/backend-api/assistant/stream
```

**免费额度**：每日大量免费对话次数

### 6. 讯飞星火（Spark）

**网页版地址**：https://xinghuo.xfyun.cn/

**登录方式**：
- 手机号+验证码

**关键Cookie**：
- `ssoSessionId`
- `refreshToken`
- `accessToken`

**API端点**：
```
POST https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat
```

**免费额度**：每日大量免费对话次数

### 7. Google Gemini

**网页版地址**：https://gemini.google.com/

**登录方式**：
- Google账号

**关键Cookie**：
- `SID`
- `HSID`
- `SSID`
- `APISID`
- `SAPISID`
- `__Secure-1PSID`
- `__Secure-3PSID`

**API端点**：
```
POST https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate
```

**免费额度**：每日大量免费对话次数

### 8. 豆包（Doubao）

**网页版地址**：https://www.doubao.com/

**登录方式**：
- 手机号+验证码

**关键Cookie**：
- `sessionid`
- `sessionid_ss`
- `s_v_web_id`
- `tt_webid`

**API端点**：
```
POST https://www.doubao.com/api/chat/stream
```

**免费额度**：每日大量免费对话次数

## 技术实现

### 1. Cookie获取流程

```python
# 使用Playwright启动浏览器
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    
    # 导航到登录页面
    await page.goto(platform_url)
    
    # 等待用户登录
    await page.wait_for_url(success_pattern, timeout=300000)
    
    # 提取Cookie
    cookies = await context.cookies()
    
    # 保存Cookie到数据库（加密存储）
    await save_cookies(cookies)
```

### 2. API调用流程

```python
# 构建请求头
headers = {
    "Cookie": cookie_string,
    "User-Agent": user_agent,
    "Referer": platform_url,
    "Origin": platform_url,
    "Content-Type": "application/json",
}

# 发送请求
async with httpx.AsyncClient() as client:
    response = await client.post(
        api_endpoint,
        headers=headers,
        json=payload,
        timeout=60.0,
    )
    
    # 解析响应
    return parse_response(response)
```

### 3. Cookie刷新机制

```python
# 定期检查Cookie有效性
async def check_cookie_validity(cookies):
    try:
        response = await client.get(
            check_url,
            headers={"Cookie": cookie_string}
        )
        return response.status_code == 200
    except:
        return False

# Cookie过期时自动刷新
if not await check_cookie_validity(cookies):
    await refresh_cookies()
```

## 安全考虑

### 1. Cookie加密存储

所有Cookie都使用AES-256加密存储在数据库中：

```python
from cryptography.fernet import Fernet

# 加密Cookie
def encrypt_cookies(cookies: dict, encryption_key: str) -> str:
    fernet = Fernet(encryption_key.encode())
    cookie_json = json.dumps(cookies)
    encrypted = fernet.encrypt(cookie_json.encode())
    return encrypted.decode()

# 解密Cookie
def decrypt_cookies(encrypted_data: str, encryption_key: str) -> dict:
    fernet = Fernet(encryption_key.encode())
    decrypted = fernet.decrypt(encrypted_data.encode())
    return json.loads(decrypted.decode())
```

### 2. 用户隔离

每个用户的Cookie独立存储和管理，互不干扰：

- 用户只能访问自己的OAuth账号
- Cookie与用户ID绑定
- 严格的权限验证

### 3. 凭证有效期管理

```python
# 定期检查Cookie有效性
@celery.task
def check_oauth_accounts():
    accounts = OAuthAccount.query.filter_by(is_active=True).all()
    for account in accounts:
        if not await check_validity(account):
            account.is_active = False
            # 通知用户重新登录
            notify_user(account.user_id)
```

### 4. 请求频率限制

防止滥用和被平台封禁：

```python
# 每个平台独立的速率限制
rate_limits = {
    "qwen": {"rpm": 60, "tpm": 100000},
    "openai": {"rpm": 60, "tpm": 90000},
    "claude": {"rpm": 50, "tpm": 80000},
    # ...
}
```

## 法律和道德考虑

### 使用条款

1. **个人账号使用**：用户必须使用自己的账号登录
2. **遵守平台规则**：不得违反各平台的使用条款
3. **合理使用**：不得滥用免费额度
4. **商业使用限制**：某些平台可能限制商业用途

### 风险提示

1. **账号风险**：频繁或异常使用可能导致账号被封
2. **服务稳定性**：网页版API可能随时变更
3. **功能限制**：网页版功能可能少于官方API
4. **法律风险**：某些地区可能有特殊法律限制

### 建议

1. **优先使用官方API**：对于商业项目，建议使用官方付费API
2. **备份方案**：准备多个平台作为备份
3. **监控使用量**：避免超出平台限制
4. **及时更新**：关注平台变更，及时更新适配器

## 逆向工程方法

### 1. 网络抓包

使用浏览器开发者工具分析网页版API：

```bash
# Chrome DevTools
1. 打开开发者工具 (F12)
2. 切换到 Network 标签
3. 在网页版发送消息
4. 查找 XHR/Fetch 请求
5. 分析请求头、请求体、响应格式
```

### 2. Cookie分析

识别关键Cookie：

```python
# 测试哪些Cookie是必需的
essential_cookies = []
for cookie in all_cookies:
    test_cookies = {cookie.name: cookie.value}
    if await test_request(test_cookies):
        essential_cookies.append(cookie.name)
```

### 3. API端点发现

常见的API端点模式：

- `/api/chat` - 聊天接口
- `/api/conversation` - 会话管理
- `/backend-api/` - 后端API
- `/stream` - 流式响应
- `/completion` - 补全接口

### 4. 请求格式分析

```python
# 典型的请求格式
{
    "model": "model-name",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "stream": true,
    "conversation_id": "uuid",
    "parent_message_id": "uuid"
}
```

### 5. 响应解析

不同平台的响应格式：

**SSE流式响应**（ChatGPT、Claude）：
```
data: {"type": "content", "text": "Hello"}
data: {"type": "content", "text": " World"}
data: [DONE]
```

**JSON流式响应**（通义千问、文心一言）：
```json
{"event": "add", "text": "Hello"}
{"event": "add", "text": " World"}
{"event": "finish"}
```

**普通JSON响应**（某些平台）：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "content": "Hello World",
        "conversation_id": "uuid"
    }
}
```

## 维护和更新

### 1. 监控平台变更

```python
# 定期测试适配器
@celery.task
def test_adapters():
    for platform in platforms:
        try:
            result = await platform.test_connection()
            if not result.success:
                alert_admin(f"{platform.name} adapter failed")
        except Exception as e:
            alert_admin(f"{platform.name} error: {e}")
```

### 2. 版本控制

为每个适配器维护版本号：

```python
class QwenAdapter(PlatformAdapter):
    VERSION = "1.0.0"
    LAST_UPDATED = "2024-01-15"
    API_VERSION = "v1"
```

### 3. 降级策略

当某个平台不可用时自动切换：

```python
async def call_ai(message: str, preferred_platform: str):
    platforms = [preferred_platform] + backup_platforms
    
    for platform in platforms:
        try:
            return await platform.send_message(message)
        except Exception as e:
            logger.warning(f"{platform} failed: {e}")
            continue
    
    raise Exception("All platforms failed")
```

## 最佳实践

### 1. 用户体验

- 提供清晰的登录指引
- 显示Cookie有效期
- 及时通知用户重新登录
- 提供多平台选择

### 2. 性能优化

- Cookie缓存
- 请求池管理
- 异步并发处理
- 响应流式传输

### 3. 错误处理

```python
# 统一的错误处理
try:
    response = await send_request()
except httpx.TimeoutException:
    raise APITimeoutError("Request timeout")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise AuthenticationError("Cookie expired")
    elif e.response.status_code == 429:
        raise RateLimitError("Rate limit exceeded")
    else:
        raise APIError(f"HTTP {e.response.status_code}")
```

### 4. 日志记录

```python
# 记录所有API调用
logger.info(
    "API call",
    extra={
        "platform": platform_id,
        "user_id": user_id,
        "model": model,
        "tokens": token_count,
        "duration": duration_ms,
    }
)

# 记录错误
logger.error(
    "API error",
    extra={
        "platform": platform_id,
        "error": str(e),
        "traceback": traceback.format_exc(),
    }
)
```

## 总结

通过逆向工程使用AI平台网页版是一个技术上可行的方案，可以为个人用户和小型项目节省大量成本。但需要注意：

### 优点

1. ✅ **零成本**：使用免费额度，无需付费
2. ✅ **快速接入**：无需申请API密钥
3. ✅ **多平台支持**：可以同时使用多个平台
4. ✅ **灵活切换**：平台间自由切换

### 缺点

1. ❌ **稳定性较差**：API可能随时变更
2. ❌ **功能受限**：某些高级功能不可用
3. ❌ **维护成本**：需要持续维护适配器
4. ❌ **法律风险**：可能违反某些平台条款

### 适用场景

**适合**：
- 个人学习和研究
- 小型项目和原型开发
- 成本敏感的应用
- 多平台对比测试

**不适合**：
- 商业生产环境
- 高可用性要求
- 大规模并发调用
- 需要官方技术支持

### 未来展望

随着AI技术的发展，预计：

1. 更多平台提供免费API
2. 网页版功能逐步完善
3. 官方API价格下降
4. 更好的开发者生态

## 参考资源

- [Playwright文档](https://playwright.dev/)
- [LiteLLM文档](https://docs.litellm.ai/)
- [各平台官方文档](#)
- [逆向工程最佳实践](#)

## 免责声明

本文档仅供技术学习和研究使用。使用本方案时，请：

1. 遵守各平台的使用条款
2. 尊重知识产权
3. 合理使用资源
4. 承担相应风险

作者不对使用本方案造成的任何后果负责。
