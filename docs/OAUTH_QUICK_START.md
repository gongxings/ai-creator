# OAuth代理功能快速开始指南

## 简介

本指南将帮助你快速开始使用OAuth代理功能，通过授权登录AI平台账号，使用平台的免费额度调用AI模型。

## 5分钟快速开始

### 步骤1：安装依赖

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install playwright litellm aiohttp cryptography

# 安装Playwright浏览器
playwright install chromium
```

### 步骤2：初始化数据库

```bash
# 运行数据库初始化脚本
python scripts/init_db.py

# 初始化OAuth平台配置
python scripts/init_oauth_platforms.py
```

### 步骤3：启动服务

```bash
# 启动后端服务
uvicorn app.main:app --reload

# 在另一个终端启动前端服务
cd frontend
npm run dev
```

### 步骤4：添加OAuth账号

1. 打开浏览器访问 `http://localhost:5173`
2. 登录你的账号
3. 进入"设置" -> "OAuth账号"标签
4. 点击"添加账号"按钮
5. 选择要授权的平台（如"通义千问"）
6. 输入账号名称（如"我的通义千问账号"）
7. 点击"开始授权"

### 步骤5：完成授权

1. 系统会打开新窗口跳转到平台登录页
2. 在平台完成登录（使用你的账号密码或手机验证码）
3. 登录成功后，系统自动捕获登录凭证
4. 窗口自动关闭，授权完成

### 步骤6：使用OAuth账号

1. 进入任意写作工具（如"公众号文章创作"）
2. 在AI模型选择中，会看到你授权的OAuth账号
3. 选择OAuth账号，输入创作需求
4. 点击生成，系统会使用OAuth账号调用AI模型
5. 查看生成的内容

## 支持的平台

目前支持以下8个AI平台：

| 平台 | 说明 | 免费额度 |
|------|------|----------|
| 通义千问 | 阿里云通义千问大模型 | 每日100万tokens |
| OpenAI | GPT系列模型 | 新用户$5免费额度 |
| Claude | Anthropic Claude系列 | 新用户免费试用 |
| 文心一言 | 百度文心大模型 | 每日免费调用 |
| 智谱AI | GLM系列模型 | 新用户免费tokens |
| 讯飞星火 | 讯飞星火认知大模型 | 每日免费调用 |
| Google Gemini | Google Gemini系列 | 免费层级 |
| 豆包 | 字节跳动豆包大模型 | 每日免费调用 |

## 常见问题

### Q1: 授权失败怎么办？

**A:** 可能的原因和解决方法：
- 网络连接问题：检查网络是否正常
- 平台登录页面变更：等待系统更新适配器
- 浏览器被阻止：检查浏览器设置，允许弹出窗口
- 验证码问题：手动完成验证码验证

### Q2: 配额用完了怎么办？

**A:** 有以下几种方法：
- 等待每日配额重置（通常在每天0点）
- 添加同一平台的其他账号
- 添加其他平台的账号
- 购买平台的付费套餐

### Q3: 账号过期了怎么办？

**A:** 
- 在OAuth账号列表中点击"刷新"按钮
- 如果刷新失败，需要重新授权
- 删除旧账号，重新添加

### Q4: 可以同时使用多个平台吗？

**A:** 
- 可以！你可以添加多个平台的账号
- 系统会自动选择可用的账号
- 配额用尽会自动切换到其他账号

### Q5: OAuth账号安全吗？

**A:** 
- 所有凭证都加密存储在数据库中
- 使用AES-256加密算法
- 每个用户只能访问自己的账号
- 支持随时删除账号

## 使用技巧

### 技巧1：多账号策略

为了确保服务稳定，建议：
- 同一平台添加2-3个账号
- 添加多个不同平台的账号
- 定期检查账号状态和配额

### 技巧2：配额管理

合理使用配额：
- 查看每日配额使用情况
- 避免在配额即将用尽时进行大量调用
- 优先使用配额充足的账号

### 技巧3：账号命名

给账号起个好名字：
- 使用描述性名称，如"工作账号"、"个人账号"
- 包含平台信息，如"通义千问-主账号"
- 方便识别和管理

### 技巧4：定期维护

保持账号健康：
- 定期刷新过期的账号
- 删除不再使用的账号
- 关注平台政策变化

## 进阶使用

### 自定义平台适配器

如果你想添加新的AI平台支持，可以：

1. 创建新的适配器文件
```python
# backend/app/services/oauth/adapters/new_platform.py
from .base import BasePlatformAdapter

class NewPlatformAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__()
        self.platform_id = "new_platform"
    
    async def login(self, page, credentials):
        # 实现登录逻辑
        pass
```

2. 注册适配器
```python
# backend/app/services/oauth/adapters/__init__.py
from .new_platform import NewPlatformAdapter

PLATFORM_ADAPTERS = {
    "new_platform": NewPlatformAdapter,
    # ...
}
```

3. 添加平台配置
```python
# backend/scripts/init_oauth_platforms.py
platforms.append({
    "platform_id": "new_platform",
    "platform_name": "新平台",
    # ...
})
```

### API直接调用

你也可以通过API直接调用OAuth账号：

```python
import requests

# 调用AI模型
response = requests.post(
    "http://localhost:8000/api/v1/oauth/chat/completions",
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"},
    json={
        "platform": "qwen",
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)

print(response.json())
```

## 故障排除

### 问题1：Playwright安装失败

```bash
# 如果playwright install失败，尝试：
playwright install --with-deps chromium

# 或者使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 问题2：数据库连接失败

检查MySQL是否正常运行：
```bash
# 检查MySQL状态
systemctl status mysql

# 启动MySQL
systemctl start mysql
```

检查数据库配置：
```bash
# 编辑.env文件
vim backend/.env

# 确认数据库配置正确
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_creator
```

### 问题3：浏览器无法打开

可能是防火墙或安全软件阻止，尝试：
- 临时关闭防火墙
- 将应用添加到白名单
- 检查浏览器弹出窗口设置

### 问题4：OAuth回调失败

确保回调URL配置正确：
```bash
# 在.env文件中设置
OAUTH_CALLBACK_URL=http://localhost:8000/api/v1/oauth/callback
```

## 最佳实践

### 1. 账号管理

- **多账号备份**：为每个平台准备2-3个账号
- **定期检查**：每周检查一次账号状态
- **及时更新**：平台政策变化时及时更新配置

### 2. 配额优化

- **监控使用**：实时监控配额使用情况
- **合理分配**：根据任务重要性分配配额
- **错峰使用**：避开高峰期使用

### 3. 安全建议

- **定期更换**：定期更换OAuth账号
- **权限最小化**：只授权必要的权限
- **日志审计**：定期检查使用日志

### 4. 性能优化

- **缓存策略**：合理使用缓存减少API调用
- **批量处理**：批量处理相似任务
- **异步调用**：使用异步方式提高效率

## 下一步

现在你已经成功设置了OAuth代理功能，可以：

1. **探索更多平台**：尝试添加其他AI平台的账号
2. **阅读完整文档**：查看 [OAuth代理功能文档](./OAUTH_PROXY.md)
3. **自定义适配器**：为新平台创建适配器
4. **参与贡献**：提交你的改进和建议

## 获取帮助

如果遇到问题：

1. 查看 [常见问题](#常见问题)
2. 查看 [故障排除](#故障排除)
3. 查看完整的 [OAuth代理功能文档](./OAUTH_PROXY.md)
4. 在GitHub提交Issue
5. 联系开发团队

## 相关文档

- [OAuth代理功能文档](./OAUTH_PROXY.md) - 完整的功能文档
- [API参考](./API_REFERENCE.md) - API接口文档
- [部署指南](./DEPLOYMENT.md) - 生产环境部署
- [开发指南](./DESIGN.md) - 开发和贡献指南

---

祝你使用愉快！🎉
