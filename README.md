# AI创作者平台

一个功能强大的AI创作平台，提供AI写作、图片生成、视频生成、PPT生成等创作工具，并支持一键发布到多个平台。

## ✨ 核心特性

### 🎯 场景化AI工具
- **14个专业写作工具**：公众号文章、小红书笔记、公文、论文、营销文案等
- **图片生成**：文本生成图片、图片变体、AI编辑、超分辨率
- **视频生成**：文本转视频、图片转视频、AI配音、自动字幕
- **PPT生成**：主题生成、大纲生成、文档转换、在线编辑

### 💎 积分会员系统
- **会员服务**：9.9元/月，不限制使用次数
- **积分充值**：非会员1元购买10积分，每次生成消耗10积分
- **智能扣费**：会员优先，生成失败自动退款

### 🎁 运营功能
- **活动管理**：积分赠送、会员折扣、首购优惠
- **优惠券系统**：折扣券、抵扣券、积分加赠
- **推广返利**：10%充值返利、100积分会员返利
- **数据统计**：用户增长、收入分析、转化率追踪

### 🚀 一键发布
支持发布到：微信公众号、小红书、抖音、快手、今日头条等平台

### 🤖 多模型支持
- OpenAI (GPT-3.5/GPT-4)
- Anthropic (Claude)
- 阿里通义千问 (Qwen)
- 百度文心一言
- 智谱AI (GLM)

## 📚 文档导航

- [功能说明](docs/FEATURES.md) - 详细的功能介绍
- [快速开始](docs/QUICK_START.md) - 5分钟快速上手
- [实现总结](docs/IMPLEMENTATION_SUMMARY.md) - 技术实现详解
- [API文档](docs/API_REFERENCE.md) - 完整的API接口文档
- [数据库设计](docs/DATABASE.md) - 数据库表结构
- [部署指南](docs/DEPLOYMENT.md) - 生产环境部署

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/ai-creator.git
cd ai-creator
```

2. **后端设置**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑.env文件，配置数据库和API密钥
python scripts/init_db.py
```

3. **前端设置**
```bash
cd frontend
npm install
```

4. **启动服务**

Windows:
```bash
start.bat
```

Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

5. **访问应用**
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 💡 使用示例

### 1. 生成公众号文章

```python
import requests

# 登录
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'testuser',
    'password': 'password123'
})
token = response.json()['data']['access_token']

# 生成文章
response = requests.post(
    'http://localhost:8000/api/v1/writing/wechat_article/generate',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'title': '如何提高工作效率',
        'keywords': ['时间管理', '效率工具'],
        'requirements': '字数2000字，包含实用技巧',
        'model_id': 1
    }
)
print(response.json())
```

### 2. 充值积分

```python
# 创建充值订单
response = requests.post(
    'http://localhost:8000/api/v1/credit/recharge',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'amount': 10.00,
        'payment_method': 'alipay'
    }
)
print(response.json())
```

### 3. 购买会员

```python
# 创建会员订单
response = requests.post(
    'http://localhost:8000/api/v1/credit/membership',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'membership_type': 'monthly',
        'payment_method': 'wechat'
    }
)
print(response.json())
```

## 🏗️ 技术架构

### 后端技术栈
- **框架**：FastAPI (Python 3.10+)
- **数据库**：MySQL 8.0+ (SQLAlchemy ORM)
- **缓存**：Redis
- **任务队列**：Celery
- **认证**：JWT
- **AI集成**：OpenAI、Anthropic、阿里云、百度、智谱

### 前端技术栈
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **UI框架**：Element Plus
- **状态管理**：Pinia
- **HTTP客户端**：Axios
- **富文本编辑器**：Quill/TipTap

### 部署方案
- **容器化**：Docker + Docker Compose
- **反向代理**：Nginx
- **进程管理**：Supervisor
- **SSL证书**：Let's Encrypt

## 📊 项目结构

```
ai-creator/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/v1/         # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── scripts/            # 脚本文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # 公共组件
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── store/         # 状态管理
│   └── package.json       # Node依赖
├── docs/                  # 文档
│   ├── FEATURES.md        # 功能说明
│   ├── QUICK_START.md     # 快速开始
