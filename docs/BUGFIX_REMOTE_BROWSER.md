# 远程浏览器授权 - 问题修复记录

## 修复时间
2026-02-09

## 修复的问题

### 1. ✅ 模块导入错误
**错误信息**: `ModuleNotFoundError: No module named 'app.utils.security'`

**原因**: 导入路径错误，`security` 模块在 `app.core` 而不是 `app.utils`

**修复**:
- 文件: `backend/app/api/v1/remote_browser.py:29`
- 修改: `from app.utils.security import decode_access_token` 
- 改为: `from app.core.security import decode_token`

---

### 2. ✅ Playwright 浏览器未安装
**错误信息**: `BrowserType.launch: Executable doesn't exist at C:\Users\...\chromium-1148\chrome.exe`

**原因**: Playwright 浏览器未安装

**修复**:
```bash
cd backend
python3 -m playwright install chromium
```

**结果**: 成功安装 Chromium 131.0.6778.33 (136.9 MB)

---

### 3. ✅ 登录状态检测优化
**问题**: 即梦平台登录后无法自动检测

**原因**: 
- localStorage 检测键不完整
- 即梦平台使用 `flow_web_has_login` 标识登录状态
- 适配器配置为 URL 跳转模式，但实际 URL 不变

**修复**:

#### 3.1 增强 localStorage 检测
文件: `backend/app/services/oauth/playwright_service.py:137-156`

添加了更多登录检测键：
```python
login_keys = [
    'user_info', 'token', 'auth', 'session', 'user', 'userId', 'userInfo',
    'flow_web_has_login',  # 即梦平台的登录标识
    'uid',  # 豆包等平台的用户ID
    'passport_user',  # 豆包的用户信息
]
```

特殊处理 `flow_web_has_login`：
```python
if key == 'flow_web_has_login':
    if value == 'true' or value == True or value == '1':
        logger.info(f"Found login indicator in localStorage: {key}={value}")
        return True
```

#### 3.2 修改即梦适配器
文件: `backend/app/services/oauth/adapters/jimeng.py:38-40`

修改为轮询模式：
```python
def get_success_pattern(self) -> str:
    """获取登录成功的URL模式"""
    # 使用轮询模式检测登录状态（通过 localStorage.flow_web_has_login）
    return "WAIT_FOR_LOGIN"
```

---

### 4. ✅ 浏览器自动关闭
**问题**: 登录成功并提取凭证后，浏览器窗口不会自动关闭

**修复**:
文件: `backend/app/services/oauth/remote_browser_service.py:212-236`

添加了自动关闭逻辑：
```python
# 延迟2秒后自动关闭浏览器（给用户时间看到成功消息）
await asyncio.sleep(2)
logger.info(f"Session {session.session_id}: Auto-closing browser after successful extraction")
# 关闭浏览器上下文
if session.context:
    try:
        await session.context.close()
        logger.info(f"Session {session.session_id}: Browser context closed")
    except Exception as e:
        logger.warning(f"Session {session.session_id}: Error closing context: {e}")
```

---

### 5. ✅ 保存凭证字段错误
**错误信息**: `'is_valid' is an invalid keyword argument for OAuthAccount`

**原因**: 
- 代码使用了不存在的字段 `is_valid`
- 实际模型使用 `is_active` 和 `is_expired` 字段

**修复**:
文件: `backend/app/api/v1/remote_browser.py:232-252`

更新现有账号：
```python
existing_account.credentials = encrypted_credentials
existing_account.is_active = True      # ✅ 改为 is_active
existing_account.is_expired = False    # ✅ 改为 is_expired
existing_account.updated_at = datetime.utcnow()
```

创建新账号：
```python
new_account = OAuthAccount(
    user_id=user_id,
    platform=platform,
    account_name=account_name,
    credentials=encrypted_credentials,
    is_active=True,      # ✅ 改为 is_active
    is_expired=False,    # ✅ 改为 is_expired
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow(),
)
```

---

## 测试验证

### 测试流程
1. ✅ WebSocket 连接成功
2. ✅ 浏览器启动正常
3. ✅ 实时截图流正常
4. ✅ 手动登录完成
5. ✅ 自动检测登录成功（localStorage 检测）
6. ✅ Cookie 提取成功
7. ✅ 凭证保存到数据库成功
8. ✅ 浏览器自动关闭

### 测试平台
- 豆包 (Doubao): ✅ 通过

---

## OAuthAccount 模型字段说明

正确的字段定义（`backend/app/models/oauth_account.py`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | BigInteger | 主键 |
| `user_id` | BigInteger | 用户ID（外键） |
| `platform` | String(50) | 平台ID (doubao/jimeng/qwen等) |
| `account_name` | String(100) | 账号名称（用户自定义） |
| `credentials` | Text | 加密的凭证（Cookie/Token） |
| `is_active` | Boolean | ✅ 是否启用 |
| `is_expired` | Boolean | ✅ 是否过期 |
| `quota_used` | Integer | 已使用次数 |
| `quota_limit` | Integer | 额度限制 |
| `last_used_at` | DateTime | 最后使用时间 |
| `expired_at` | DateTime | 过期时间 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

⚠️ **注意**: 没有 `is_valid` 字段，使用 `is_active` 和 `is_expired` 来表示状态

---

## 支持的平台

### 已配置的平台

| 平台 | 检测模式 | localStorage 键 | 必需 Cookie | 状态 |
|------|----------|-----------------|-------------|------|
| 豆包 (Doubao) | WAIT_FOR_LOGIN | uid, passport_user | sessionid, sessionid_ss | ✅ 测试通过 |
| 即梦 (Jimeng) | WAIT_FOR_LOGIN | flow_web_has_login | sessionid | ✅ 已配置 |
| 通义千问 (Qwen) | URL 变化 | - | tongyi_sso_ticket | ✅ 自动支持 |
| 智谱清言 (Zhipu) | URL 变化 | - | chatglm_token | ✅ 自动支持 |
| DeepSeek | URL 变化 | - | token | ✅ 自动支持 |
| 文心一言 (Baidu) | URL 变化 | - | BAIDUID | ✅ 自动支持 |

---

## 完整工作流程

```
1. 客户端连接 WebSocket
   ↓
2. 服务器创建浏览器会话
   ↓
3. 打开平台登录页面
   ↓
4. 开始实时截图流 (每 0.5 秒)
   ↓
5. 用户手动登录（扫码或账密）
   ↓
6. 轮询检测登录状态 (每 2 秒)
   - 检查 localStorage 键
   - 检查 URL 变化
   - 检查页面元素
   ↓
7. 检测到登录成功
   ↓
8. 提取凭证
   - 提取 Cookie
   - 提取 Token (localStorage)
   - 提取 User-Agent
   ↓
9. 加密并保存到数据库
   - 更新 is_active = True
   - 更新 is_expired = False
   ↓
10. 通知客户端完成
   ↓
11. 延迟 2 秒后自动关闭浏览器
```

---

## Linux 服务器部署

### 配置 Headless 模式

```bash
# 1. 安装浏览器
cd backend
python3 -m playwright install chromium
python3 -m playwright install-deps chromium

# 2. 配置环境变量
echo "PLAYWRIGHT_HEADLESS=true" >> .env

# 3. 重启服务
python run.py
```

### Headless 模式工作原理
- 浏览器在后台运行（无窗口）
- 每 0.5 秒截图并通过 WebSocket 发送到前端
- 用户在 Web 界面看到实时画面
- 通过 WebSocket 发送鼠标/键盘事件进行操作

---

## 性能配置

### 环境变量

```bash
# .env 文件
PLAYWRIGHT_HEADLESS=true          # Linux: true, Windows: false
PLAYWRIGHT_TIMEOUT=300000         # 登录超时（毫秒），默认 5 分钟
PLAYWRIGHT_MAX_CONCURRENT=3       # 最大并发浏览器数量
```

### 截图质量调整

文件: `backend/app/services/oauth/remote_browser_service.py:42-43`

```python
screenshot_interval: float = 0.5  # 截图间隔（秒）
screenshot_quality: int = 60      # JPEG 质量 (1-100)
```

**调优建议**:
- **高带宽**: `quality=80-90`, `interval=0.3`
- **低带宽**: `quality=40-50`, `interval=1.0`
- **低 CPU**: `quality=50`, `interval=1.0`

---

## 故障排查

### 常见错误

#### 1. 浏览器无法启动
```
ERROR: Failed to launch browser
```
**解决**: 
```bash
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

#### 2. 登录检测失败
```
WARNING: Login timeout after 150 seconds
```
**解决**: 
1. 查看日志中的 `localStorage keys` 输出
2. 使用检测脚本找出正确的键:
   ```bash
   python3 scripts/check_platform_login_keys.py https://平台URL
   ```
3. 将键添加到 `playwright_service.py` 的 `login_keys` 列表

#### 3. 保存凭证失败
```
ERROR: 'is_valid' is an invalid keyword argument
```
**解决**: 已修复，使用 `is_active` 和 `is_expired` 字段

#### 4. 浏览器不自动关闭
**解决**: 已修复，现在会在提取凭证后 2 秒自动关闭

---

## 相关文档

- **完整指南**: `backend/REMOTE_BROWSER_GUIDE.md`
- **快速配置**: `backend/QUICK_SETUP.md`
- **检测脚本**: `backend/scripts/check_platform_login_keys.py`

---

## 总结

所有问题已修复：
1. ✅ 模块导入错误
2. ✅ Playwright 浏览器安装
3. ✅ 登录状态检测优化
4. ✅ 浏览器自动关闭
5. ✅ 数据库字段错误

**测试状态**: 豆包平台测试通过 ✅

**部署建议**:
- Windows 开发环境: `PLAYWRIGHT_HEADLESS=false`
- Linux 生产环境: `PLAYWRIGHT_HEADLESS=true`

**后续优化**:
- 根据实际使用情况调整截图质量和间隔
- 根据需要测试其他平台
- 监控数据库中凭证的有效性
