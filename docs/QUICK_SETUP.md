# 快速配置指南

## Linux 服务器部署（3 步搞定）

### 步骤 1: 安装 Playwright 浏览器

```bash
cd backend
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 步骤 2: 配置环境变量

编辑 `backend/.env`，添加：

```bash
PLAYWRIGHT_HEADLESS=true
```

### 步骤 3: 重启服务

```bash
# 重启后端服务
python run.py
```

✅ 完成！现在可以使用远程浏览器授权了。

---

## 新平台支持（无需每个都测试）

### 平台分类

**类型 1: URL 会跳转的平台（不需要额外配置）**
- 通义千问 (tongyi.aliyun.com)
- 智谱清言 (chatglm.cn)
- DeepSeek (chat.deepseek.com)
- 文心一言 (yiyan.baidu.com)

这些平台登录后 URL 会变化，**已经自动支持**。

**类型 2: URL 不跳转的平台（需要配置 localStorage 检测）**
- ✅ 豆包 (doubao.com) - 已配置
- ✅ 即梦 (jimeng.jianying.com) - 已配置

如果新平台也属于这类，需要添加配置。

---

## 添加新平台的 localStorage 检测（仅类型 2 平台）

### 方法 1: 使用检测脚本（推荐）

```bash
cd backend
python3 scripts/check_platform_login_keys.py https://新平台URL

# 示例
python3 scripts/check_platform_login_keys.py https://www.doubao.com/
```

脚本会：
1. 打开浏览器
2. 等待你手动登录
3. 自动检测 localStorage 变化
4. 生成配置代码

### 方法 2: 手动检查

1. **打开浏览器开发者工具**
   - F12 -> Application -> Local Storage

2. **登录前后对比**
   - 登录前：记录所有键
   - 登录后：查看新增或变化的键

3. **查找登录标识键**
   - 名称包含：user, login, auth, token, session, uid, passport 等

4. **添加到配置**

编辑 `backend/app/services/oauth/playwright_service.py` 第 137-156 行：

```python
login_keys = [
    'user_info', 'token', 'auth', 'session', 'user', 'userId', 'userInfo',
    'flow_web_has_login',  # 即梦平台
    'uid', 'passport_user',  # 豆包平台
    '你找到的新键',  # 新平台名称
]
```

5. **修改适配器**

编辑对应平台的适配器文件 `backend/app/services/oauth/adapters/平台.py`：

```python
def get_success_pattern(self) -> str:
    """获取登录成功的URL模式"""
    return "WAIT_FOR_LOGIN"  # 改为轮询模式
```

---

## 测试建议

### 推荐测试策略

**只需测试 2-3 个代表性平台**：

1. **测试 1 个 URL 跳转型平台**（如通义千问）
   - 验证 URL 模式匹配是否正常

2. **测试 1-2 个轮询型平台**（豆包、即梦）
   - 验证 localStorage 检测是否正常

3. **其他平台无需逐个测试**
   - 同类型平台逻辑相同
   - 有问题时按需调试

### 快速测试流程

```bash
# 1. 启动后端
cd backend
python run.py

# 2. 使用 WebSocket 测试工具
# 方法 A: 使用 wscat (需要安装: npm install -g wscat)
wscat -c "ws://localhost:8000/api/v1/remote-browser/ws/doubao?token=YOUR_JWT"

# 方法 B: 使用前端测试页面（推荐）
# 打开浏览器访问前端的远程授权页面

# 3. 观察日志
tail -f backend/logs/app.log | grep "localStorage\|login"
```

---

## 常见问题速查

### Q1: Linux 服务器报错 "Failed to launch browser"

```bash
# 解决方法：安装系统依赖
python3 -m playwright install-deps chromium
```

### Q2: 登录后一直显示"等待登录"

**检查步骤**：

1. 查看日志中的 `localStorage keys` 输出
2. 对比是否包含配置的检测键
3. 如果没有，运行检测脚本找出正确的键

```bash
python3 scripts/check_platform_login_keys.py https://平台URL
```

### Q3: Docker 环境下浏览器无法启动

**Dockerfile 需要添加**：

```dockerfile
# 安装 Playwright 系统依赖
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 && rm -rf /var/lib/apt/lists/*

# 安装 Playwright 浏览器
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# 设置 headless 模式
ENV PLAYWRIGHT_HEADLESS=true
```

### Q4: Windows 和 Linux 切换

**Windows（开发环境）**：
```bash
# .env
PLAYWRIGHT_HEADLESS=false  # 可以看到浏览器窗口
```

**Linux（生产环境）**：
```bash
# .env
PLAYWRIGHT_HEADLESS=true   # 后台运行，通过截图显示
```

---

## 性能优化建议

### 对于资源有限的服务器

```bash
# .env
PLAYWRIGHT_MAX_CONCURRENT=1        # 限制并发数
PLAYWRIGHT_TIMEOUT=180000          # 减少超时时间（3分钟）
```

### 调整截图质量

编辑 `backend/app/services/oauth/remote_browser_service.py`:

```python
class RemoteBrowserSession:
    screenshot_interval: float = 1.0   # 1秒一次（降低CPU占用）
    screenshot_quality: int = 50       # 降低质量（减少带宽）
```

---

## 支持的平台列表

| 平台 | 类型 | 状态 | 需要配置 |
|------|------|------|----------|
| 豆包 | 轮询型 | ✅ 已配置 | ❌ |
| 即梦 | 轮询型 | ✅ 已配置 | ❌ |
| 通义千问 | URL跳转型 | ✅ 自动支持 | ❌ |
| 智谱清言 | URL跳转型 | ✅ 自动支持 | ❌ |
| DeepSeek | URL跳转型 | ✅ 自动支持 | ❌ |
| 文心一言 | URL跳转型 | ✅ 自动支持 | ❌ |

---

## 获取帮助

**查看完整文档**：
```
backend/REMOTE_BROWSER_GUIDE.md
```

**查看日志**：
```bash
tail -f backend/logs/app.log
```

**调试模式**：
```python
# 在代码中添加更多日志
logger.info(f"Debug info: {variable}")
```
