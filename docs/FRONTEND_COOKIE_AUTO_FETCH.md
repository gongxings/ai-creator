# 前端Cookie自动获取方案

## 方案概述

通过前端授权窗口 + postMessage通信实现无感Cookie获取和提交

## 核心流程

```
前端主页面
    ↓
打开授权窗口
    ↓
用户扫码登录（豆包页面）
    ↓
登录完成，返回授权窗口
    ↓
点击"获取Cookie并提交"
    ↓
自动读取/提示粘贴Cookie
    ↓
提交到后端
    ↓
自动关闭窗口
    ↓
通知主页面刷新
```

## 后端API（已实现）

### 1. Cookie提交接口
```http
POST /api/v1/oauth/accounts/cookie-submit
Content-Type: application/json

{
  "platform": "doubao",
  "cookies": {
    "s_v_web_id": "xxx",
    "sessionid": "xxx",
    "sessionid_ss": "xxx"
  },
  "account_name": "我的豆包账号",
  "user_agent": "Mozilla/5.0 ..."
}
```

### 2. 授权页面接口
```http
GET /api/v1/oauth/accounts/cookie-validate/{platform}
```

返回HTML页面，包含获取Cookie的UI和逻辑

## 前端实现

### 主页面组件

```vue
<template>
  <div>
    <el-button @click="openAuthWindow" type="primary">
      授权豆包账号
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const authWindow = ref(null)

// 打开授权窗口
const openAuthWindow = () => {
  const platform = 'doubao'
  const width = 800
  const height = 600
  const left = (window.innerWidth - width) / 2 + window.screenX
  const top = (window.innerHeight - height) / 2 + window.screenY
  
  const authUrl = `${window.location.origin}/api/v1/oauth/accounts/cookie-validate/${platform}`
  
  authWindow.value = window.open(
    authUrl,
    `oauth-${Date.now()}`,
    `width=${width},height=${height},left=${left},top=${top}`
  )
  
  // 监听来自授权窗口的消息
  window.addEventListener('message', handleAuthMessage)
}

// 处理来自授权窗口的消息
const handleAuthMessage = (event) => {
  // 验证消息来源
  if (event.origin !== window.location.origin) {
    return
  }
  
  const { type, platform, data } = event.data
  
  if (type === 'oauth_success') {
    ElMessage.success('授权成功！')
    
    // 刷新账号列表
    refreshAccounts()
    
    // 关闭授权窗口
    if (authWindow.value) {
      authWindow.value.close()
    }
  }
}

// 刷新账号列表
const refreshAccounts = () => {
  // 调用刷新账号列表的API
  // 例如：emit('accounts:refresh')
}

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('message', handleAuthMessage)
})
</script>
```

### 授权页面（由后端返回）

授权页面已通过后端实现，包含：
1. 登录页面按钮
2. Cookie获取和提交逻辑
3. 成功/失败提示
4. 自动关闭窗口

## 使用方法

### 前端调用

```javascript
// 1. 用户点击"授权豆包账号"按钮
// 2. 打开授权窗口
const openAuth = () => {
  const url = '/api/v1/oauth/accounts/cookie-validate/doubao'
  const authWindow = window.open(url, 'oauth-doubao', 'width=800,height=600')
  
  // 监听授权完成消息
  window.addEventListener('message', (event) => {
    if (event.data.type === 'oauth_success') {
      console.log('授权成功:', event.data.data)
      // 刷新账号列表
      location.reload()
      authWindow.close()
    }
  })
}
```

### 用户操作流程

1. **打开授权窗口**
   - 前端打开新的浏览器窗口
   - 显示豆包授权页面

2. **完成登录**
   - 点击"打开登录页面"按钮
   - 在新标签页中打开豆包
   - 扫码或输入账号密码登录

3. **获取Cookie**
   - 返回授权窗口
   - 点击"获取Cookie并提交"按钮
   - 如果能自动读取Cookie，会自动提交
   - 如果不能自动读取，会提示用户手动复制粘贴

4. **完成授权**
   - Cookie提交到后端
   - 验证并保存
   - 授权窗口自动关闭
   - 主页面刷新账号列表

## 优势

### 无感刷新
- 用户只需操作一次（扫码登录）
- Cookie自动获取和提交
- 窗口自动关闭
- 主页面自动刷新

### 无需后端浏览器
- 完全前端获取Cookie
- 不占用后端资源
- 适合生产环境

### 灵活可靠
- 支持手动粘贴（防止自动获取失败）
- 清晰的操作指引
- 完善的错误处理

## 注意事项

### 浏览器同源策略
由于浏览器的同源策略（CORS）限制，直接获取Cookie有以下限制：

1. **跨域Cookie无法直接读取**
   - 豆包网站（www.doubao.com）和你的网站不同域
   - JavaScript无法直接读取跨域Cookie
   - 需要用户手动复制粘贴

2. **解决方案**
   - **手动复制粘贴**：提示用户从开发者工具复制Cookie
   - **浏览器扩展**：开发浏览器扩展，可以读取跨域Cookie
   - **同源代理**：后端提供代理接口（仍需后端浏览器）

### 生产环境建议

对于生产环境，建议：
1. **推荐使用浏览器扩展**
   - 开发Chrome扩展
   - 可以读取任意网站的Cookie
   - 前端可以调用扩展API获取Cookie
2. **提供清晰的指引**
   - 详细说明如何手动获取Cookie
   - 在授权页面提供截图示例
   - 提供常见问题解答

## 开发Chrome扩展方案

如果需要完全自动化的Cookie获取，需要开发浏览器扩展：

### 扩展manifest.json

```json
{
  "manifest_version": 3,
  "name": "Cookie Helper",
  "version": "1.0",
  "permissions": [
    "cookies",
    "activeTab"
  ],
  "host_permissions": [
    "https://www.doubao.com/*",
    "http://localhost:*/api/v1/oauth/accounts/cookie-validate/*"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "Cookie Helper"
  },
  "content_scripts": [
    {
      "matches": ["https://www.doubao.com/*"],
      "js": ["content.js"]
    }
  ]
}
```

### popup.html

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 300px; padding: 10px; }
    button { width: 100%; padding: 10px; margin: 5px 0; }
  </style>
</head>
<body>
  <h2>Cookie Helper</h2>
  <button id="getCookies">获取当前页面Cookie</button>
  <button id="extractDoubao">提取豆包Cookie</button>
  <pre id="result"></pre>
  
  <script>
    document.getElementById('getCookies').addEventListener('click', async () => {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      
      chrome.cookies.getAll({url: tab.url}, (cookies) => {
        const cookieObj = {};
        cookies.forEach(cookie => {
          cookieObj[cookie.name] = cookie.value;
        });
        
        document.getElementById('result').textContent = JSON.stringify(cookieObj, null, 2);
        
        // 发送消息到内容脚本
        chrome.tabs.sendMessage(tab.id, {type: 'extract_cookies', cookies: cookieObj});
      });
    });
    
    document.getElementById('extractDoubao').addEventListener('click', async () => {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      
      if (tab.url.includes('doubao.com')) {
        chrome.cookies.getAll({url: tab.url}, (cookies) => {
          const requiredCookies = ['s_v_web_id', 'sessionid', 'sessionid_ss'];
          const cookieObj = {};
          
          cookies.forEach(cookie => {
            if (requiredCookies.includes(cookie.name)) {
              cookieObj[cookie.name] = cookie.value;
            }
          });
          
          document.getElementById('result').textContent = JSON.stringify(cookieObj, null, 2);
        });
      } else {
        alert('请在豆包网站上使用此扩展');
      }
    });
  </script>
</body>
</html>
```

### content.js

```javascript
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'extract_cookies') {
    // 将Cookie发送到授权窗口
    chrome.tabs.query({active: true, currentWindow: true}, ([tab]) => {
      chrome.tabs.sendMessage(tab.id, {
        type: 'from_extension',
        cookies: request.cookies
      });
    });
  }
});
```

### 前端与扩展交互

```javascript
// 检查是否有扩展可用
const isExtensionAvailable = () => {
  return new Promise((resolve) => {
    // 发送消息到扩展
    window.postMessage({type: 'check_extension'}, '*');
    
    // 监听扩展响应
    const handler = (event) => {
      if (event.data.type === 'extension_ready') {
        window.removeEventListener('message', handler);
        resolve(true);
      }
    };
    
    window.addEventListener('message', handler);
    
    // 3秒超时
    setTimeout(() => {
      window.removeEventListener('message', handler);
      resolve(false);
    }, 3000);
  });
}

// 获取扩展中的Cookie
const getCookiesFromExtension = () => {
  return new Promise((resolve) => {
    const handler = (event) => {
      if (event.data.type === 'extension_cookies') {
        window.removeEventListener('message', handler);
        resolve(event.data.cookies);
      }
    };
    
    window.addEventListener('message', handler);
    window.postMessage({type: 'get_cookies'}, '*');
  });
}

// 在授权页面中调用
if (await isExtensionAvailable()) {
  const cookies = await getCookiesFromExtension();
  await submitCookies(cookies);
} else {
  // 回退到手动粘贴方式
  await submitManually();
}
```

## 总结

本方案提供了：
1. ✅ **后端API**：Cookie提交和验证接口
2. ✅ **前端授权页面**：自动获取和手动粘贴两种方式
3. ✅ **浏览器扩展方案**：完全自动化Cookie获取（需要开发）
4. ✅ **灵活性强**：支持多种场景和备选方案

推荐优先级：
1. **手动复制粘贴**（已实现，立即可用）
2. **浏览器扩展**（需要开发，但体验最好）
3. **同源代理**（需要后端支持，复杂度高）
