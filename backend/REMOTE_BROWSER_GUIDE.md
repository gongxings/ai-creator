# 远程浏览器授权指南

## 概述

本系统支持通过远程浏览器进行 OAuth 授权，用户可以在 Web 界面上看到实时截图并通过鼠标/键盘操作完成登录。

## 工作模式

### 1. Windows/有界面服务器 (默认模式)

- **特点**: 浏览器窗口会实际显示，用户可以在服务器上直接看到
- **配置**: 默认配置，无需修改
- **适用场景**: 本地开发、Windows 服务器

### 2. Linux/无界面服务器 (Headless 模式)

- **特点**: 浏览器在后台运行，通过 WebSocket 发送截图到前端
- **配置**: 设置环境变量 `PLAYWRIGHT_HEADLESS=true`
- **适用场景**: Linux 服务器、Docker 容器、无 X11 显示的环境

## 环境变量配置

在 `backend/.env` 文件中添加：

```bash
# Playwright 配置
PLAYWRIGHT_HEADLESS=true          # Linux 服务器设为 true，Windows 可设为 false
PLAYWRIGHT_TIMEOUT=300000         # 登录超时时间（毫秒），默认 5 分钟
PLAYWRIGHT_MAX_CONCURRENT=3       # 最大并发浏览器数量
```

## Linux 服务器部署指南

### 1. 安装依赖

```bash
# 安装 Playwright 浏览器和系统依赖
cd backend
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 2. 配置环境变量

编辑 `backend/.env`：

```bash
PLAYWRIGHT_HEADLESS=true
```

### 3. 验证安装

```bash
# 测试 Playwright 是否正常工作
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); print('OK'); b.close(); p.stop()"
```

## 平台登录检测配置

不同平台使用不同的方式检测登录成功：

### 方式 1: URL 变化检测

**适用平台**: 通义千问、智谱清言、DeepSeek、文心一言等

登录后 URL 会跳转到控制台页面，通过 URL 模式匹配检测。

```python
def get_success_pattern(self) -> str:
    return "**/tongyi.aliyun.com/**"  # 示例：通义千问
```

### 方式 2: localStorage 轮询检测 (WAIT_FOR_LOGIN)

**适用平台**: 豆包、即梦等

登录后 URL 不变，通过轮询检查 localStorage 或页面元素判断登录状态。

```python
def get_success_pattern(self) -> str:
    return "WAIT_FOR_LOGIN"  # 启用轮询模式
```

**检测的 localStorage 键**:
- `flow_web_has_login` (即梦)
- `uid` (豆包)
- `passport_user` (豆包)
- `user_info`, `token`, `auth`, `session`, `userId` (通用)

## 各平台配置状态

| 平台 | 检测模式 | localStorage 键 | 必需 Cookie | 状态 |
|------|----------|-----------------|-------------|------|
| 豆包 (Doubao) | WAIT_FOR_LOGIN | uid, passport_user | sessionid, sessionid_ss | ✅ |
| 即梦 (Jimeng) | WAIT_FOR_LOGIN | flow_web_has_login | sessionid | ✅ |
| 通义千问 (Qwen) | URL 变化 | - | tongyi_sso_ticket | ✅ |
| 智谱清言 (Zhipu) | URL 变化 | - | chatglm_token | ✅ |
| DeepSeek | URL 变化 | - | token | ✅ |
| 文心一言 (Baidu) | URL 变化 | - | BAIDUID | ✅ |

## WebSocket API 使用

### 连接

```javascript
const ws = new WebSocket(`ws://your-host/api/v1/remote-browser/ws/{platform}?token={jwt_token}&account_name={name}`);
```

**参数**:
- `platform`: 平台 ID (doubao, jimeng, qwen, zhipu 等)
- `token`: JWT 认证令牌
- `account_name`: 账号名称（可选，默认为 "default"）

### 接收消息

```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'screenshot':
            // 显示截图: data:image/jpeg;base64,{data.data}
            break;
        
        case 'status':
            // 状态更新: starting, navigating, waiting_login, logged_in, extracting, completed
            console.log(data.status, data.data.message);
            break;
        
        case 'credentials':
            // 凭证提取完成
            console.log('授权成功！', data.data);
            break;
        
        case 'error':
            // 错误
            console.error(data.data.message);
            break;
    }
};
```

### 发送操作

```javascript
// 鼠标点击 (坐标为 0-1 之间的百分比)
ws.send(JSON.stringify({
    type: 'mouse',
    event: 'click',
    x: 0.5,      // 50% 宽度位置
    y: 0.3,      // 30% 高度位置
    button: 'left'
}));

// 键盘输入
ws.send(JSON.stringify({
    type: 'keyboard',
    event: 'type',
    text: 'hello'
}));

// 滚动
ws.send(JSON.stringify({
    type: 'scroll',
    deltaX: 0,
    deltaY: 100
}));

// 关闭
ws.send(JSON.stringify({
    type: 'close'
}));
```

## 工作流程

1. **客户端连接 WebSocket**
   - 提供平台 ID 和认证令牌
   
2. **服务器创建浏览器会话**
   - 启动 Chromium 浏览器（headless 或非 headless）
   - 打开平台登录页面
   
3. **实时截图流**
   - 每 0.5 秒发送一次 JPEG 截图（质量 60%）
   - 前端显示实时画面
   
4. **用户操作登录**
   - 通过鼠标/键盘事件远程操作
   - 或在服务器上直接操作（非 headless 模式）
   
5. **登录检测**
   - 每 2 秒检查一次登录状态
   - URL 变化或 localStorage 键值变化
   
6. **提取凭证**
   - 自动提取 Cookie 和 Token
   - 加密保存到数据库
   
7. **自动关闭**
   - 延迟 2 秒后自动关闭浏览器
   - 清理会话资源

## 故障排查

### 1. 浏览器无法启动

**错误**: `Executable doesn't exist`

**解决**:
```bash
cd backend
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 2. Linux 无法启动浏览器

**错误**: `Failed to launch browser`

**检查**:
1. 是否设置了 `PLAYWRIGHT_HEADLESS=true`
2. 是否安装了系统依赖：`playwright install-deps chromium`
3. 是否有足够的内存（建议 2GB+）

### 3. 登录检测失败

**症状**: 登录后一直显示"等待登录"

**调试**:
1. 查看日志中的 `localStorage keys` 输出
2. 检查平台适配器的 `get_success_pattern()` 配置
3. 如果需要，添加平台特定的 localStorage 键到检测列表

**修改方法**:
编辑 `backend/app/services/oauth/playwright_service.py:137-156`，添加平台特定的 localStorage 键。

### 4. Cookie 提取失败

**错误**: `No cookies extracted`

**检查**:
1. 确认平台适配器的 `get_cookie_names()` 配置正确
2. 查看日志中的 `Total cookies found` 数量
3. 验证登录是否真正成功（手动访问平台控制台）

## 性能优化

### 截图质量调整

```python
# 在 RemoteBrowserSession 中调整
screenshot_quality: int = 60  # 降低可减少带宽，提高到 80-90 可提升清晰度
screenshot_interval: float = 0.5  # 增大可减少 CPU 占用
```

### 并发控制

```bash
# 在 .env 中设置
PLAYWRIGHT_MAX_CONCURRENT=3  # 同时最多 3 个浏览器会话
```

### 超时设置

```bash
# 在 .env 中设置
PLAYWRIGHT_TIMEOUT=300000  # 5 分钟，根据实际情况调整
```

## Docker 部署示例

```dockerfile
FROM python:3.11-slim

# 安装 Playwright 依赖
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 安装应用
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装 Playwright 浏览器
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# 设置环境变量
ENV PLAYWRIGHT_HEADLESS=true

# 启动应用
CMD ["python", "run.py"]
```

## 安全建议

1. **使用 HTTPS/WSS**: 生产环境必须使用加密连接
2. **JWT 认证**: 确保 token 有效期合理（建议 1-2 小时）
3. **会话限制**: 限制每个用户的并发会话数
4. **凭证加密**: 数据库中的 Cookie 已加密存储
5. **日志脱敏**: 避免在日志中输出完整的 Cookie 值

## 开发建议

### 添加新平台支持

1. 创建适配器类继承 `PlatformAdapter`
2. 实现 `get_success_pattern()` 方法
3. 如果使用 `WAIT_FOR_LOGIN` 模式，确保在 `playwright_service.py` 中添加平台特定的 localStorage 检测键
4. 测试登录流程和凭证提取

### 测试流程

```bash
# 1. 启动后端
cd backend
python run.py

# 2. 连接 WebSocket (使用工具如 wscat)
wscat -c "ws://localhost:8000/api/v1/remote-browser/ws/doubao?token=YOUR_JWT"

# 3. 观察日志输出
tail -f backend/logs/app.log
```

## 常见问题

**Q: 为什么 Linux 服务器上必须用 headless 模式？**
A: Linux 服务器通常没有 X11 显示服务，无法显示图形界面。Headless 模式在后台运行浏览器，通过截图展示界面。

**Q: headless 模式下用户怎么看到登录界面？**
A: 系统会每 0.5 秒发送截图到前端，用户在 Web 界面上看到实时画面，并通过 WebSocket 发送鼠标/键盘事件进行操作。

**Q: 可以支持扫码登录吗？**
A: 可以。截图会包含二维码，用户可以在前端看到并用手机扫码。

**Q: 所有平台都需要逐个测试吗？**
A: 主要测试两类：
- URL 变化型：测试一个即可，其他平台类似
- WAIT_FOR_LOGIN 型：每个平台的 localStorage 键可能不同，需要分别测试和配置

**Q: 如何查看某个平台需要什么 localStorage 键？**
A: 
1. 手动在浏览器中登录该平台
2. 打开开发者工具 -> Application -> Local Storage
3. 查看登录前后的变化，找到登录后新增或变化的键
4. 将该键添加到 `playwright_service.py` 的检测列表中
