# Cookie方式AI生成功能 - 实现指南

## 概述

本文档描述了AI创作者平台从API Key模式到Cookie模式的重大升级。该升级支持用户直接使用自己的平台账号（如豆包、通义千问等）的免费额度，无需购买API Key。

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────┐
│              用户前端(Vue 3)                     │
│  ┌────────────────────────────────────────────┐ │
│  │  OAuth授权流程 → 获取Cookie → 上传到后端   │ │
│  └────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────┘
                 │ HTTPS
                 ↓
┌─────────────────────────────────────────────────┐
│         FastAPI后端(Python)                      │
│  ┌────────────────────────────────────────────┐ │
│  │  API路由层 (writing/image/video/ppt)      │ │
│  └───────────────┬─────────────────────────────┘ │
│                  │                               │
│  ┌──────────────┴─────────────────────────┐    │
│  │                                        │    │
│  ↓                                        ↓    │
│  ┌─────────────────────────┐  ┌──────────────────────┐
│  │ WritingService          │  │ CookieAIServiceMgr   │
│  │ (支持双模式)            │  │ (Cookie调度器)        │
│  └──────────┬──────────────┘  └──────────┬───────────┘
│             │                           │
│  ┌──────────┴─────────────────────────┬─┘
│  │                                    │
│  ↓                                    ↓
│  ┌──────────────────────┐  ┌─────────────────────┐
│  │ APIServiceBase       │  │ CookieBasedService  │
│  │ (OpenAI/Anthropic)   │  │ (Doubao/Qwen等)    │
│  └──────────────────────┘  └─────────────────────┘
│                                    │
│                      ┌─────────────┼─────────────┐
│                      ↓             ↓             ↓
│                   DoubaoService VideoService PPTService
│
│  ┌─────────────────────────────────────────────┐
│  │       数据持久化层                          │
│  │  ┌──────────────────────────────────────┐  │
│  │  │ OAuthAccount (Cookie加密存储)         │  │
│  │  │ Creation (创作记录)                   │  │
│  │  │ CreditTransaction (积分记录)          │  │
│  │  └──────────────────────────────────────┘  │
│  └─────────────────────────────────────────────┘
└─────────────────────────────────────────────────┘
```

### 核心组件

#### 1. CookieBasedAIService (基类)

```python
class CookieBasedAIService(ABC):
    """Cookie-based AI服务基类"""
    
    def __init__(self, cookies: Dict[str, str], user_agent: Optional[str] = None):
        # Cookie字典：{cookie_name: cookie_value}
        # 自动构建请求头，模拟真实浏览器
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """生成文本"""
    
    @abstractmethod
    async def generate_image(self, prompt: str) -> Dict[str, Any]:
        """生成图片"""
    
    @abstractmethod
    async def generate_video(self, prompt: str) -> Dict[str, Any]:
        """生成视频"""
    
    async def validate_cookies(self) -> bool:
        """验证Cookie有效性"""
```

#### 2. DoubaoService (豆包实现)

```python
class DoubaoService(CookieBasedAIService):
    """豆包网页版AI服务"""
    
    # 关键方法
    async def generate_text(prompt: str) -> str:
        # POST https://www.doubao.com/api/chat/completions
        # 使用Cookie认证
    
    async def generate_image(prompt: str) -> Dict[str, Any]:
        # 支持两种方式：
        # 1. 通过Chat API (让AI画图)
        # 2. 直接图片生成API (如果豆包支持)
    
    async def generate_text_stream(prompt: str) -> AsyncGenerator[str, None]:
        # 流式生成文本
        # POST https://www.doubao.com/api/chat/stream
```

#### 3. CookieAIServiceManager (管理器)

```python
class CookieAIServiceManager:
    """Cookie AI服务管理器"""
    
    def get_service_for_platform(self, user_id: int, platform: str):
        # 从OAuthAccount获取用户的Cookie
        # 创建对应平台的Service实例
    
    async def generate_text_with_cookie(
        user_id: int,
        platform: str,
        prompt: str
    ) -> str:
        # 使用Cookie生成文本
        # 自动验证Cookie，处理过期情况
```

#### 4. WritingService (增强)

```python
class WritingService:
    # 原有方法（API Key模式）
    async def generate_content(
        db, tool_type, user_input, ai_model_id
    ) -> str:
        # 使用APIServiceBase调用官方API
    
    # 新增方法（Cookie模式）
    async def generate_content_with_cookie(
        db, user_id, tool_type, user_input, platform
    ) -> str:
        # 使用CookieAIServiceManager调用Cookie服务
```

## 使用流程

### 1. 用户授权流程

```
用户 → 前端OAuth页面 → 选择平台 → 扫码/账号密码登录
  ↓
浏览器插件/前端自动化 → 提取Cookie
  ↓
上传Cookie到后端 → 加密存储到OAuthAccount表
  ↓
系统确认授权完成
```

### 2. 文本生成流程

**API Key模式（原有）：**
```
前端请求 → API路由 → WritingService.generate_content()
       → AIServiceBase (OpenAI/Anthropic) → 官方API
       → 返回结果
```

**Cookie模式（新增）：**
```
前端请求 (platform=doubao) → API路由 → WritingService.generate_content_with_cookie()
                          → CookieAIServiceManager → DoubaoService
                          → httpx请求豆包API (使用Cookie)
                          → 返回结果
```

### 3. 前端请求示例

**Cookie模式：**
```bash
POST /api/v1/writing/generate
Content-Type: application/json
Authorization: Bearer {access_token}

{
    "tool_type": "wechat_article",
    "prompt": "为一个AI公司写一篇科技文章",
    "parameters": {
        "topic": "AI创新",
        "keywords": "人工智能,深度学习",
        "target_audience": "技术从业者",
        "style": "专业"
    },
    "platform": "doubao"  // ← 指定使用豆包Cookie
}
```

**API Key模式：**
```bash
POST /api/v1/writing/generate
{
    ...
    "model_id": 1  // ← 使用模型ID（API Key模式）
}
```

## 文件结构

```
backend/app/
├── services/
│   ├── ai/
│   │   ├── cookie_based_service.py       ✨ 新增 - Cookie基类
│   │   ├── doubao_service.py            ✨ 新增 - 豆包实现
│   │   ├── video_service.py             ✨ 新增 - 视频生成
│   │   ├── ppt_service.py               ✨ 新增 - PPT生成
│   │   ├── openai_service.py            (原有)
│   │   ├── anthropic_service.py         (原有)
│   │   └── factory.py                   (原有)
│   ├── cookie_ai_manager.py             ✨ 新增 - Cookie管理器
│   ├── writing_service.py               📝 已更新 - 添加Cookie方法
│   ├── credit_service.py                (原有)
│   └── ...
├── api/
│   └── v1/
│       ├── writing.py                   📝 已更新 - 支持platform参数
│       ├── image.py                     (原有)
│       ├── video.py                     (原有)
│       ├── ppt.py                       (原有)
│       └── ...
├── schemas/
│   └── creation.py                      📝 已更新 - 添加platform字段
└── models/
    ├── oauth_account.py                 (原有 - 存储Cookie)
    ├── user.py                          (原有 - is_member, credits)
    └── creation.py                      (原有)
```

## 配置和部署

### 环境变量

```bash
# 加密密钥（用于Cookie加密存储）
OAUTH_ENCRYPTION_KEY=your-32-character-encryption-key

# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_creator

# Redis缓存
REDIS_URL=redis://localhost:6379/0

# 其他AI服务（API Key模式，可选）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 依赖安装

```bash
pip install -r requirements.txt

# 新增依赖
pip install httpx cryptography python-pptx
```

### 数据库准备

确保以下表存在：
- `users` - 用户表（需要is_member, credits字段）
- `oauth_accounts` - OAuth账号表（存储加密的Cookie）
- `creations` - 创作记录表
- `credit_transactions` - 积分交易表

### 启动服务

```bash
cd backend

# 开发环境
python -m uvicorn app.main:app --reload

# 生产环境
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## 性能优化

### 1. Cookie验证缓存

```python
# 验证结果缓存1小时
@lru_cache(maxsize=1000, ttl=3600)
async def validate_cookies(cookies_hash: str) -> bool:
    ...
```

### 2. 连接池

```python
# httpx自动使用连接池
async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
    ...
```

### 3. 超时设置

```python
# 根据操作类型设置不同超时
timeout = {
    "text": 120.0,      # 文本生成120秒
    "image": 180.0,     # 图片生成180秒
    "video": 300.0,     # 视频生成300秒
}
```

## 安全考虑

### 1. Cookie加密存储

```python
from cryptography.fernet import Fernet

# 使用Fernet对称加密
cipher = Fernet(encryption_key)
encrypted_cookies = cipher.encrypt(json.dumps(cookies).encode())

# 存储到数据库
oauth_account.credentials = encrypted_cookies
```

### 2. 用户隔离

```python
# 确保用户只能访问自己的Cookie
oauth_accounts = db.query(OAuthAccount).filter(
    OAuthAccount.user_id == current_user.id,  # ← 关键
    OAuthAccount.platform == platform
).all()
```

### 3. 请求头安全

```python
# 模拟真实浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "Referer": "https://www.doubao.com/",
    "Origin": "https://www.doubao.com",
}
```

## 错误处理

### 常见问题

#### 1. Cookie已过期

```python
# 自动检测和提示
if response.status_code == 401:
    raise ValueError("Cookie已过期，请重新登录授权")
```

#### 2. 网络错误

```python
try:
    response = await client.post(url, headers=headers, json=payload, timeout=120.0)
except asyncio.TimeoutError:
    raise ValueError("请求超时，请稍后重试")
except httpx.ConnectionError:
    raise ValueError("网络连接失败")
```

#### 3. 积分不足

```python
# WritingService已处理
# 非会员检查积分
if not user.is_member and user.credits < 10:
    raise HTTPException(status_code=402, detail="积分不足")
```

## 扩展支持新平台

### 步骤1：创建平台Service

```python
# app/services/ai/qwen_service.py
class QwenService(CookieBasedAIService):
    """通义千问服务"""
    
    BASE_URL = "https://qwen.aliyun.com"
    
    def get_platform_name(self) -> str:
        return "qwen"
    
    def get_check_url(self) -> str:
        return self.BASE_URL
    
    async def generate_text(self, prompt: str) -> str:
        headers = self.get_headers()
        # 实现通义千问的API调用
        ...
```

### 步骤2：注册到管理器

```python
# app/services/cookie_ai_manager.py
def get_service_for_platform(self, user_id: int, platform: str):
    ...
    if platform == "qwen":
        service = QwenService(cookies=cookies, user_agent=user_agent)
        return service
    ...
```

### 步骤3：更新数据库

```sql
-- 允许新平台
UPDATE oauth_account_config
SET allowed_platforms = CONCAT(allowed_platforms, ',qwen');
```

## 测试

### 单元测试

```python
# backend/tests/test_doubao_cookie.py
@pytest.mark.asyncio
async def test_doubao_text_generation():
    service = DoubaoService(cookies=test_cookies)
    result = await service.generate_text("Hello world")
    assert len(result) > 0

@pytest.mark.asyncio
async def test_cookie_validation():
    service = DoubaoService(cookies=test_cookies)
    is_valid = await service.validate_cookies()
    assert is_valid in [True, False]
```

### 集成测试

```python
# 测试完整的生成流程
@pytest.mark.asyncio
async def test_writing_with_cookie():
    # 1. 创建测试用户和Cookie
    # 2. 调用API生成文本
    # 3. 验证结果和积分扣费
    ...
```

## 监控和日志

### 日志级别

```python
logger.info(f"Generating text with {platform}")
logger.warning(f"Cookie validation failed for {platform}")
logger.error(f"Generation failed: {e}", exc_info=True)
```

### 监控指标

```python
# 追踪的关键指标
metrics = {
    "request_count": ...,
    "success_rate": ...,
    "average_latency": ...,
    "cookie_expired_count": ...,
    "error_count": ...,
}
```

## 参考文档

- [OAUTH_CONFIG.md](./OAUTH_CONFIG.md) - OAuth配置说明
- [COOKIE_BASED_PUBLISH.md](./COOKIE_BASED_PUBLISH.md) - Cookie发布框架
- [CREDIT_MEMBERSHIP.md](./CREDIT_MEMBERSHIP.md) - 积分会员系统

## 后续优化

1. **多平台支持**
   - 通义千问 (Qwen) Cookie版本
   - Claude Cookie版本（如果支持）
   - 讯飞星火、Google Gemini等

2. **功能完善**
   - 完善发布框架的Cookie模式
   - 视频/PPT实际生成API集成
   - 异步任务队列

3. **用户体验**
   - Cookie自动续期提醒
   - 使用统计和分析
   - 性能优化和加速

## 问题排查

### 问题1：Cookie过期

**症状**：生成内容时返回401错误

**解决**：
1. 在OAuth账号管理中重新授权
2. 检查Cookie有效期
3. 使用浏览器插件重新获取Cookie

### 问题2：网络超时

**症状**：请求在120秒后超时

**解决**：
1. 检查网络连接
2. 尝试简化提示词
3. 查看服务器日志

### 问题3：积分不足

**症状**：返回402 Payment Required

**解决**：
1. 非会员需要充值积分
2. 购买会员获得无限使用
3. 等待每日积分赠送

---

**文档版本**：1.0  
**最后更新**：2026年2月6日  
**作者**：AI Creator开发团队
