# OAuth 授权配置说明

## 两种授权方式

### 方式一：一次性授权（适合开发测试）

浏览器模式：**非 headless 模式（可见浏览器窗口）**

当调用 `/api/v1/oauth/accounts/authorize` 接口时，系统会：
1. 打开一个可见的浏览器窗口
2. 自动点击登录按钮
3. 轮询检测登录状态（每2秒检查一次）
4. 检测到登录成功后，提取 Cookie 并保存

**注意**：此方式需要在服务器上看到浏览器窗口，适合开发测试。

### 方式二：分步授权（推荐用于生产环境）

使用新的分步授权流程，支持在前端显示二维码：

1. **开始授权** - `POST /api/v1/oauth/authorize/start?platform=doubao`
   - 在服务器上打开浏览器
   - 点击登录按钮
   - 返回会话ID

2. **获取二维码** - `GET /api/v1/oauth/authorize/qr?platform=doubao`
   - 返回 base64 编码的二维码图片
   - 前端显示二维码，用户用手机扫码

3. **检查登录状态** - `GET /api/v1/oauth/authorize/status?platform=doubao`
   - 轮询此接口检查是否已登录
   - 返回 `logged_in: true/false`

4. **完成授权** - `POST /api/v1/oauth/authorize/complete?platform=doubao`
   - 提取 Cookie 并保存到数据库
   - 关闭浏览器会话

## 前端实现示例

```javascript
// 1. 开始授权
const startResponse = await fetch('/api/v1/oauth/authorize/start?platform=doubao', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
const { session_id } = await startResponse.json();

// 2. 获取二维码并显示
const qrResponse = await fetch('/api/v1/oauth/authorize/qr?platform=doubao', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { qr_code } = await qrResponse.json();

if (qr_code) {
  document.getElementById('qrcode').src = `data:image/png;base64,${qr_code}`;
} else {
  alert('未找到二维码，请使用账号密码登录');
}

// 3. 轮询检查登录状态
const checkInterval = setInterval(async () => {
  const statusResponse = await fetch('/api/v1/oauth/authorize/status?platform=doubao', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const { logged_in } = await statusResponse.json();
  
  if (logged_in) {
    clearInterval(checkInterval);
    alert('登录成功！');
    
    // 4. 完成授权
    const completeResponse = await fetch('/api/v1/oauth/authorize/complete?platform=doubao', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const account = await completeResponse.json();
    console.log('授权成功', account);
  }
}, 2000); // 每2秒检查一次
```

## 配置参数

### .env 文件配置

```bash
# 浏览器模式（true=后台运行，false=可见窗口）
PLAYWRIGHT_HEADLESS=false

# 授权超时时间（毫秒）
PLAYWRIGHT_TIMEOUT=300000

# 最大并发授权数
PLAYWRIGHT_MAX_CONCURRENT=3
```

### 服务器部署配置

在生产环境中部署到服务器时，有两种方案：

#### 方案1：使用 VNC 远程桌面（适合开发测试）

```bash
# 安装 Xvfb 和 VNC
sudo apt-get install xvfb x11vnc

# 创建虚拟显示
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# 启动 VNC 服务器
x11vnc -display :99 -rfbport 5900 &

# 设置 PLAYWRIGHT_HEADLESS=false
PLAYWRIGHT_HEADLESS=false
```

用户可以通过 VNC 客户端连接到服务器的 5900 端口查看浏览器窗口。

#### 方案2：使用分步授权 + 二维码（推荐用于生产）

使用分步授权流程，前端显示二维码，用户用手机扫码登录。

这种方式不需要用户访问服务器，更适合生产环境。

## 注意事项

1. **Cookie 过期**：如果 Cookie 过期，需要重新授权
2. **多账户支持**：可以为一个平台添加多个账户
3. **安全提示**：不要在公共环境或日志中暴露账号密码
4. **会话超时**：授权会话会在完成后自动清理，长时间未完成会超时

## 获取 Cookie（手动方式）

如果自动提取失败，可以手动获取 Cookie：

1. 在浏览器中登录豆包
2. 打开开发者工具（F12）→ Application → Cookies
3. 复制以下 Cookie：
   - `sessionid`
   - `sessionid_ss`
   - `s_v_web_id`
   - `tt_webid`
4. 使用 `/api/v1/oauth/accounts/manual` 接口手动添加

## 常见问题

### Q: 二维码获取失败？
A: 豆包可能使用动态二维码，需要使用账号密码登录

### Q: 登录状态一直未更新？
A: 检查浏览器是否正常打开，登录后检查 localStorage 是否有用户信息

### Q: 如何验证 Cookie 是否有效？
A: 调用 `/api/v1/oauth/accounts/{account_id}/check` 接口验证

### Q: 服务器部署如何使用？
A: 推荐使用分步授权流程，前端显示二维码，用户扫码登录