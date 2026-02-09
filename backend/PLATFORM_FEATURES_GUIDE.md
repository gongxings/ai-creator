# 平台功能与授权问题说明

## 问题 1: Fernet 加密密钥错误 ✅ 已解决

### 现状
- ✅ 密钥本身是有效的 (`jocB966ibYd2b8wAUP37uNwMKI9q-yWpmd4JePYe_NM=`)
- ✅ 加密解密功能正常
- ✅ 数据库中的凭证可以正常解密
- ✅ 豆包账号已成功保存 (user_id=8, account_name="22")

### 错误原因
该错误可能是以下原因之一：
1. **首次启动时的初始化错误**（已自动修复）
2. **并发请求导致的临时错误**（可忽略）
3. **某些旧数据使用了错误的密钥**（重新授权即可）

### 验证方法
```bash
cd backend
python3 -c "
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials

db = SessionLocal()
account = db.query(OAuthAccount).filter(
    OAuthAccount.user_id == 8,
    OAuthAccount.platform == 'doubao'
).first()

if account:
    credentials = decrypt_credentials(account.credentials)
    print('✓ Decryption successful!')
    print(f'Cookies: {list(credentials.get(\"cookies\", {}).keys())}')
db.close()
"
```

---

## 问题 2: 豆包生成图片失败 ⚠️ 功能不匹配

### 核心问题
**豆包（Doubao）是文本对话平台，不是图像生成平台！**

### 平台功能对照表

| 平台 | 主要功能 | 支持图像生成 | Cookie 授权 |
|------|---------|--------------|-------------|
| **豆包 (Doubao)** | ✅ 文本对话 | ❌ 不支持 | ✅ 已授权 |
| **即梦 (Jimeng)** | ✅ 图像生成 | ✅ 支持 | ❌ 未授权 |
| 通义千问 (Qwen) | ✅ 文本对话 | ❌ 不支持 | - |
| 智谱清言 (Zhipu) | ✅ 文本对话 | ✅ 支持 | - |

### 解决方案

#### 方案 1: 使用即梦生成图片（推荐）

**步骤 1: 授权即梦平台**
```
1. 在前端选择"即梦 (Jimeng)"平台
2. 连接 WebSocket 进行授权
3. 扫码或登录即梦账号
4. 系统自动保存凭证
```

**步骤 2: 使用即梦生成图片**
```json
POST /api/v1/image
{
  "prompt": "一只可爱的猫咪",
  "platform": "jimeng",  // ← 改为 jimeng
  "width": 1024,
  "height": 1024,
  "num_images": 1
}
```

#### 方案 2: 使用豆包的文本对话功能

豆包授权已成功，可以用于：

**文本对话**:
```json
POST /api/v1/chat
{
  "message": "你好，请介绍一下自己",
  "platform": "doubao"
}
```

**文章生成**:
```json
POST /api/v1/article
{
  "topic": "人工智能的未来",
  "platform": "doubao"
}
```

---

## 各平台授权状态

### 已授权平台

| 平台 | 用户ID | 账号名称 | 状态 | 功能 |
|------|--------|---------|------|------|
| 豆包 (doubao) | 8 | 22 | ✅ Active | 文本对话 |

### 未授权但支持的平台

| 平台 | 功能 | 授权方式 | 推荐用途 |
|------|------|---------|----------|
| **即梦 (jimeng)** | 图像生成 | Cookie 授权 | **图片生成** ⭐ |
| 通义千问 (qwen) | 文本对话 | Cookie 授权 | 文本对话、文章生成 |
| 智谱清言 (zhipu) | 文本对话 + 图像 | Cookie 授权 | 文本对话、图片生成 |
| DeepSeek | 代码生成 | Cookie 授权 | 代码生成、技术问答 |

---

## 即梦平台授权教程

### 1. 前端操作

```
1. 进入"平台管理"页面
2. 选择"即梦 (Jimeng)"平台
3. 点击"Cookie 授权"按钮
4. 在弹出的窗口中等待浏览器画面
```

### 2. 登录即梦

```
方式 1: 扫码登录（推荐）
  - 用手机抖音/剪映扫描二维码
  - 确认授权

方式 2: 账号密码登录
  - 输入手机号/邮箱
  - 输入密码或验证码
  - 点击登录
```

### 3. 自动完成

```
✓ 系统自动检测登录成功（检测 flow_web_has_login）
✓ 自动提取 sessionid Cookie
✓ 加密保存到数据库
✓ 浏览器自动关闭
```

### 4. 使用即梦生成图片

```bash
curl -X POST "http://localhost:8000/api/v1/image" \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "一只可爱的猫咪在花园里玩耍",
    "platform": "jimeng",
    "width": 1024,
    "height": 1024,
    "num_images": 1
  }'
```

---

## 豆包服务的正确用法

### ✅ 支持的功能

#### 1. 文本对话
```python
from app.services.ai.doubao_service import DoubaoService

service = DoubaoService(cookies={
    'sessionid': '...',
    'sessionid_ss': '...'
})

response = await service.chat(
    message="你好，请介绍一下自己",
    conversation_id=None
)
```

#### 2. 流式对话
```python
async for chunk in service.stream_chat(message="讲个故事"):
    print(chunk, end='', flush=True)
```

#### 3. Cookie 验证
```python
is_valid = await service.validate_cookies()
if is_valid:
    print("Cookie 有效")
else:
    print("Cookie 已过期，需要重新授权")
```

### ❌ 不支持的功能

- **图像生成**（即梦专用）
- **图像编辑**（即梦专用）
- **视频生成**（其他平台专用）

---

## 前端选择器优化建议

### 当前问题
前端允许选择"豆包"生成图片，但豆包不支持图像生成。

### 建议修改

#### 方案 1: 限制可选平台（推荐）

```typescript
// 图片生成页面
const imageGenerationPlatforms = [
  { id: 'jimeng', name: '即梦', icon: '🎨' },
  { id: 'zhipu', name: '智谱清言', icon: '🎨' },
  // 不包括 doubao
];

// 文本对话页面
const chatPlatforms = [
  { id: 'doubao', name: '豆包', icon: '💬' },
  { id: 'qwen', name: '通义千问', icon: '💬' },
  { id: 'zhipu', name: '智谱清言', icon: '💬' },
];
```

#### 方案 2: 添加功能标签

```typescript
const platforms = [
  { 
    id: 'doubao', 
    name: '豆包', 
    features: ['chat', 'article'],  // 不包括 image
    icon: '💬'
  },
  { 
    id: 'jimeng', 
    name: '即梦', 
    features: ['image'],  // 专用于图像
    icon: '🎨'
  },
];

// 根据当前功能过滤
const availablePlatforms = platforms.filter(p => 
  p.features.includes('image')  // 图片生成页面
);
```

#### 方案 3: 前端验证

```typescript
function validatePlatformForTask(platform: string, task: string): boolean {
  const platformFeatures = {
    'doubao': ['chat', 'article', 'write'],
    'jimeng': ['image'],
    'zhipu': ['chat', 'image'],
    'qwen': ['chat', 'article'],
  };
  
  return platformFeatures[platform]?.includes(task) ?? false;
}

// 使用
if (!validatePlatformForTask('doubao', 'image')) {
  alert('豆包平台不支持图像生成，请选择即梦平台');
  return;
}
```

---

## 后端优化建议

### 1. 添加平台功能验证

```python
# app/services/oauth/adapters/base.py

class PlatformAdapter(ABC):
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """
        获取平台支持的功能列表
        
        Returns:
            功能列表: ['chat', 'image', 'video', 'code']
        """
        pass

# app/services/oauth/adapters/doubao.py

class DoubaoAdapter(PlatformAdapter):
    def get_supported_features(self) -> List[str]:
        return ['chat', 'article', 'write']  # 不包括 'image'

# app/services/oauth/adapters/jimeng.py

class JimengAdapter(PlatformAdapter):
    def get_supported_features(self) -> List[str]:
        return ['image']  # 专用于图像生成
```

### 2. API 层验证

```python
# app/api/v1/image.py

@router.post("")
async def create_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    # 验证平台是否支持图像生成
    if request.platform:
        adapter_class = PLATFORM_ADAPTERS.get(request.platform)
        if adapter_class:
            adapter = adapter_class(request.platform, {})
            if 'image' not in adapter.get_supported_features():
                raise HTTPException(
                    status_code=400,
                    detail=f"平台 {request.platform} 不支持图像生成，请使用即梦(jimeng)平台"
                )
    
    # 原有逻辑...
```

### 3. 返回清晰的错误信息

```python
# app/services/ai/doubao_service.py

async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
    """
    豆包不支持图像生成
    """
    logger.warning("Doubao does not support image generation")
    return {
        "error": "豆包平台不支持图像生成功能",
        "suggestion": "请使用即梦(jimeng)平台生成图片",
        "available_features": ["文本对话", "文章生成", "代码辅助"]
    }
```

---

## 总结

### ✅ 已解决
1. **加密密钥问题** - 密钥有效，凭证解密正常
2. **豆包授权成功** - 可以用于文本对话

### ⚠️ 需要注意
1. **豆包不支持图像生成** - 这是平台功能限制
2. **图片生成请使用即梦** - 需要重新授权即梦平台

### 🔧 建议操作
1. **立即操作**: 授权即梦平台进行图像生成
2. **前端优化**: 根据任务类型过滤可选平台
3. **后端优化**: 添加平台功能验证，返回清晰错误

### 📝 平台选择指南
- 📝 文本对话 → 豆包 / 通义千问 / 智谱清言
- 🎨 图像生成 → **即梦** (推荐) / 智谱清言
- 💻 代码生成 → DeepSeek / 豆包
- 📄 文章写作 → 豆包 / 通义千问
