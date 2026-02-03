# OAuth代理功能实现完成

## 概述

本文档记录了OAuth代理功能的完整实现，该功能允许用户通过OAuth2.0授权登录各大AI平台，使用平台的免费额度调用AI模型。

## 实现日期

2026年2月3日

## 功能特性

### 1. 支持的平台（8个）

✅ **通义千问 (Qwen)** - 阿里云通义千问大模型
✅ **OpenAI** - GPT系列模型  
✅ **Claude** - Anthropic Claude系列模型
✅ **文心一言 (Baidu)** - 百度文心大模型
✅ **智谱AI (Zhipu)** - GLM系列模型
✅ **讯飞星火 (Spark)** - 讯飞星火认知大模型
✅ **Google Gemini** - Google Gemini系列模型
✅ **豆包 (Doubao)** - 字节跳动豆包大模型

### 2. 核心功能

✅ **浏览器自动化登录**
- 使用Playwright实现浏览器自动化
- 支持多种登录方式（账号密码、验证码等）
- 自动捕获Cookie和Token
- 支持无头模式和有头模式

✅ **统一的LiteLLM接口**
- 所有平台统一使用LiteLLM标准接口
- 自动转换不同平台的API格式
- 支持流式和非流式响应
- 自动处理错误和重试

✅ **配额管理**
- 自动追踪每个账号的使用量
- 支持每日配额限制
- 支持请求频率限制
- 配额用尽自动切换账号

✅ **多账号管理**
- 支持同一平台绑定多个账号
- 自动负载均衡
- 账号状态监控
- 过期账号自动禁用

## 技术实现

### 后端实现

#### 1. 数据库模型

**oauth_accounts表** - OAuth账号信息
```sql
CREATE TABLE oauth_accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    platform_id VARCHAR(50) NOT NULL,
    account_name VARCHAR(100),
    cookies JSON,
    access_token VARCHAR(500),
    refresh_token VARCHAR(500),
    expires_at DATETIME,
    quota_used INT DEFAULT 0,
    quota_limit INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_expired BOOLEAN DEFAULT FALSE,
    last_used_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

**platform_configs表** - 平台配置信息
```sql
CREATE TABLE platform_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    platform_id VARCHAR(50) UNIQUE NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    description TEXT,
    oauth_config JSON NOT NULL,
    litellm_config JSON NOT NULL,
    quota_config JSON,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### 2. 服务层架构

```
backend/app/services/oauth/
├── oauth_service.py          # OAuth服务主类
├── browser_automation.py     # 浏览器自动化服务
├── litellm_proxy.py          # LiteLLM代理服务
└── adapters/                 # 平台适配器
    ├── base.py               # 基础适配器类
    ├── qwen.py               # 通义千问适配器
    ├── openai.py             # OpenAI适配器
    ├── claude.py             # Claude适配器
    ├── baidu.py              # 文心一言适配器
    ├── zhipu.py              # 智谱AI适配器
    ├── spark.py              # 讯飞星火适配器
    ├── gemini.py             # Gemini适配器
    └── doubao.py             # 豆包适配器
```

#### 3. API路由

```python
# backend/app/api/v1/oauth.py
router = APIRouter(prefix="/oauth", tags=["OAuth"])

# 平台管理
GET    /platforms                    # 获取支持的平台列表

# OAuth授权
POST   /initiate                     # 发起OAuth授权
GET    /callback                     # OAuth回调处理

# 账号管理
GET    /accounts                     # 获取OAuth账号列表
POST   /accounts/{id}/refresh        # 刷新OAuth账号
PUT    /accounts/{id}/toggle         # 启用/禁用OAuth账号
DELETE /accounts/{id}                # 删除OAuth账号

# AI调用
POST   /chat/completions             # 使用OAuth账号调用AI
```

### 前端实现

#### 1. 用户设置页面

**文件**: `frontend/src/views/settings/UserSettings.vue`

新增"OAuth账号"标签页，包含：
- OAuth账号列表展示
- 添加OAuth账号对话框
- 账号状态和配额显示
- 刷新、启用/禁用、删除操作

#### 2. API接口封装

**文件**: `frontend/src/api/oauth.ts`（待创建）

```typescript
// OAuth相关API接口
export const getPlatforms = () => request.get('/oauth/platforms')
export const initiateOAuth = (data) => request.post('/oauth/initiate', data)
export const getOAuthAccounts = () => request.get('/oauth/accounts')
export const refreshOAuthAccount = (id) => request.post(`/oauth/accounts/${id}/refresh`)
export const toggleOAuthAccount = (id) => request.put(`/oauth/accounts/${id}/toggle`)
export const deleteOAuthAccount = (id) => request.delete(`/oauth/accounts/${id}`)
export const chatWithOAuth = (data) => request.post('/oauth/chat/completions', data)
```

## 文件清单

### 新增文件

#### 后端文件
1. `backend/app/models/oauth_account.py` - OAuth账号模型
2. `backend/app/models/platform_config.py` - 平台配置模型
3. `backend/app/services/oauth/oauth_service.py` - OAuth服务主类
4. `backend/app/services/oauth/browser_automation.py` - 浏览器自动化
5. `backend/app/services/oauth/litellm_proxy.py` - LiteLLM代理
6. `backend/app/services/oauth/adapters/base.py` - 基础适配器
7. `backend/app/services/oauth/adapters/qwen.py` - 通义千问适配器
8. `backend/app/services/oauth/adapters/openai.py` - OpenAI适配器
9. `backend/app/services/oauth/adapters/claude.py` - Claude适配器
10. `backend/app/services/oauth/adapters/baidu.py` - 文心一言适配器
11. `backend/app/services/oauth/adapters/zhipu.py` - 智谱AI适配器
12. `backend/app/services/oauth/adapters/spark.py` - 讯飞星火适配器
13. `backend/app/services/oauth/adapters/gemini.py` - Gemini适配器
14. `backend/app/services/oauth/adapters/doubao.py` - 豆包适配器
15. `backend/app/services/oauth/adapters/__init__.py` - 适配器导出
16. `backend/app/api/v1/oauth.py` - OAuth API路由
17. `backend/app/schemas/oauth.py` - OAuth数据模型（待创建）
18. `backend/scripts/init_oauth_platforms.py` - 平台配置初始化脚本

#### 前端文件
1. `frontend/src/api/oauth.ts` - OAuth API接口（待创建）
2. `frontend/src/views/settings/UserSettings.vue` - 用户设置页面（已更新）

#### 文档文件
1. `docs/OAUTH_PROXY.md` - OAuth代理功能完整文档
2. `docs/OAUTH_QUICK_START.md` - OAuth代理功能快速开始指南
3. `docs/OAUTH_IMPLEMENTATION_COMPLETE.md` - 本文档

### 修改的文件

1. `backend/app/models/__init__.py` - 添加新模型导出
2. `backend/app/api/v1/__init__.py` - 添加OAuth路由
3. `backend/app/main.py` - 注册OAuth路由
4. `backend/requirements.txt` - 添加新依赖
5. `frontend/src/views/settings/UserSettings.vue` - 添加OAuth账号管理

## 依赖项

### Python依赖

```txt
playwright>=1.40.0
litellm>=1.0.0
aiohttp>=3.9.0
cryptography>=41.0.0
```

### 安装命令

```bash
# 安装Python依赖
pip install playwright litellm aiohttp cryptography

# 安装Playwright浏览器
playwright install chromium
```

## 数据库迁移

### 创建新表

```sql
-- OAuth账号表
CREATE TABLE oauth_accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    platform_id VARCHAR(50) NOT NULL,
    account_name VARCHAR(100),
    cookies JSON,
    access_token VARCHAR(500),
    refresh_token VARCHAR(500),
    expires_at DATETIME,
    quota_used INT DEFAULT 0,
    quota_limit INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_expired BOOLEAN DEFAULT FALSE,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_platform (user_id, platform_id),
    INDEX idx_active (is_active, is_expired),
    INDEX idx_platform (platform_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 平台配置表
CREATE TABLE platform_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    platform_id VARCHAR(50) UNIQUE NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    description TEXT,
    oauth_config JSON NOT NULL,
    litellm_config JSON NOT NULL,
    quota_config JSON,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_platform_id (platform_id),
    INDEX idx_enabled (is_enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 初始化平台配置

```bash
python backend/scripts/init_oauth_platforms.py
```

## 配置说明

### 环境变量

在 `.env` 文件中添加以下配置：

```bash
# Playwright配置
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000

# OAuth配置
OAUTH_STATE_EXPIRE=600
OAUTH_CALLBACK_URL=http://localhost:8000/api/v1/oauth/callback

# LiteLLM配置
LITELLM_LOG_LEVEL=INFO
LITELLM_CACHE_ENABLED=true

# 加密密钥（用于加密存储Cookie和Token）
OAUTH_ENCRYPTION_KEY=your-32-character-encryption-key
```

## 使用流程

### 1. 用户添加OAuth账号

```
用户 -> 点击"添加OAuth账号"
     -> 选择平台（如通义千问）
     -> 输入账号名称
     -> 点击"开始授权"
     -> 系统打开浏览器窗口
     -> 用户在平台完成登录
     -> 系统捕获登录凭证
     -> 保存到数据库
     -> 授权完成
```

### 2. 系统使用OAuth账号调用AI

```
用户 -> 发起AI调用请求
     -> 系统查找可用的OAuth账号
     -> 检查配额是否充足
     -> 使用LiteLLM调用平台API
     -> 返回AI响应
     -> 更新配额使用量
```

### 3. 配额管理

```
系统 -> 每次调用前检查配额
     -> 配额充足：继续调用
     -> 配额不足：切换到下一个账号
     -> 所有账号配额用尽：返回错误
     -> 每日0点自动重置配额
```

## 安全措施

### 1. 数据加密
- Cookie和Token使用AES-256加密存储
- 加密密钥存储在环境变量中
- 定期轮换加密密钥

### 2. 访问控制
- 每个用户只能访问自己的OAuth账号
- API请求需要JWT认证
- 实施请求频率限制

### 3. 日志审计
- 记录所有OAuth操作
- 记录所有AI调用
- 记录配额使用情况

## 测试计划

### 单元测试

- [ ] OAuth服务测试
- [ ] 浏览器自动化测试
- [ ] LiteLLM代理测试
- [ ] 各平台适配器测试
- [ ] 配额管理测试

### 集成测试

- [ ] 完整OAuth授权流程测试
- [ ] AI调用流程测试
- [ ] 多账号切换测试
- [ ] 配额用尽处理测试
- [ ] 错误处理测试

### 性能测试

- [ ] 并发调用测试
- [ ] 大量账号管理测试
- [ ] 浏览器自动化性能测试
- [ ] API响应时间测试

## 已知限制

1. **浏览器自动化**
   - 依赖平台登录页面结构稳定
   - 平台更新可能导致适配器失效
   - 需要定期维护和更新

2. **配额限制**
   - 受各平台免费额度限制
   - 无法突破平台的速率限制
   - 需要用户自行管理多个账号

3. **平台支持**
   - 目前仅支持8个主流平台
   - 新平台需要开发适配器
   - 部分平台可能不支持自动化登录

4. **安全性**
   - 需要用户提供平台登录凭证
   - 凭证存储在本地数据库
   - 建议使用独立的AI平台账号

## 后续优化计划

### 短期计划（1-2周）

- [ ] 完善错误处理和重试机制
- [ ] 添加更详细的日志记录
- [ ] 优化浏览器自动化性能
- [ ] 添加配额预警功能
- [ ] 完善API文档

### 中期计划（1-2个月）

- [ ] 支持更多AI平台（Cohere、Mistral等）
- [ ] 添加账号健康度监控
- [ ] 实现智能账号调度算法
- [ ] 添加使用统计和分析
- [ ] 支持账号自动续期

### 长期计划（3-6个月）

- [ ] 支持企业级账号管理
- [ ] 添加成本分析和优化建议
- [ ] 支持自定义平台适配器插件
- [ ] 提供独立的API代理服务
- [ ] 支持分布式部署

## 部署步骤

### 1. 准备环境

```bash
# 安装Python 3.10+
python --version

# 安装Node.js 18+
node --version

# 安装MySQL 8.0+
mysql --version

# 安装Redis
redis-server --version
```

### 2. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt
playwright install chromium

# 前端依赖
cd frontend
npm install
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑环境变量
vim backend/.env
```

### 4. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ai_creator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行初始化脚本
cd backend
python scripts/init_db.py
python scripts/init_oauth_platforms.py
```

### 5. 启动服务

```bash
# 启动后端（开发模式）
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（开发模式）
cd frontend
npm run dev

# 生产模式部署请参考 docs/DEPLOYMENT.md
```

## 验证测试

### 1. 验证后端服务

```bash
# 检查API文档
curl http://localhost:8000/docs

# 测试OAuth平台列表
curl http://localhost:8000/api/v1/oauth/platforms
```

### 2. 验证前端服务

```bash
# 访问前端页面
open http://localhost:5173

# 登录并进入设置页面
# 检查OAuth账号标签页是否正常显示
```

### 3. 测试OAuth授权流程

1. 在设置页面点击"添加OAuth账号"
2. 选择一个平台（建议先测试通义千问）
3. 输入账号名称
4. 点击"开始授权"
5. 在弹出的浏览器窗口完成登录
6. 验证账号是否成功添加到列表

### 4. 测试AI调用

1. 进入任意写作工具
2. 选择刚添加的OAuth账号
3. 输入测试内容
4. 点击生成
5. 验证是否成功生成内容

## 故障排查

### 常见问题

1. **Playwright安装失败**
   - 使用国内镜像：`export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/`
   - 手动安装：`playwright install --with-deps chromium`

2. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库配置是否正确
   - 检查防火墙设置

3. **浏览器无法打开**
   - 检查Playwright是否正确安装
   - 验证浏览器路径配置
   - 尝试使用有头模式调试

4. **OAuth授权失败**
   - 检查网络连接
   - 验证平台登录页面是否变更
   - 查看浏览器控制台日志

## 监控和维护

### 日常监控

- 监控OAuth账号状态
- 监控配额使用情况
- 监控API调用成功率
- 监控系统资源使用

### 定期维护

- 每周检查账号健康度
- 每月更新平台适配器
- 定期备份数据库
- 定期清理过期数据

## 贡献指南

欢迎贡献代码和建议！

### 如何贡献

1. Fork项目
2. 创建特性分支：`git checkout -b feature/new-platform`
3. 提交更改：`git commit -am 'Add new platform adapter'`
4. 推送到分支：`git push origin feature/new-platform`
5. 创建Pull Request

### 贡献内容

- 新平台适配器
- Bug修复
- 性能优化
- 文档改进
- 测试用例

## 相关文档

- [OAuth代理功能文档](./OAUTH_PROXY.md) - 完整的功能文档
- [OAuth快速开始指南](./OAUTH_QUICK_START.md) - 快速上手指南
- [API参考文档](./API_REFERENCE.md) - API接口文档
- [部署指南](./DEPLOYMENT.md) - 生产环境部署
- [开发指南](./DESIGN.md) - 开发和贡献指南

## 许可证

MIT License

## 联系方式

如有问题或建议，请：
- 提交GitHub Issue
- 发送邮件至开发团队
- 加入开发者社区讨论

---

**实现状态**: ✅ 核心功能已完成，待测试和优化

**最后更新**: 2026年2月3日
