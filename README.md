# AI Creator Platform

[English](README_EN.md) | 简体中文

## 📸 界面展示

![登录页面](https://biyebang.com.cn/upload/image-DHza.png)

**🌐 线上地址：http://ai-creator.biyebang.com.cn**

一个功能强大的AI创作平台，提供AI写作、图片生成、视频生成、PPT生成等创作工具，并支持一键发布到多个平台。

## ✨ 核心特性

- **14个专业写作工具**：公众号文章、小红书笔记、公文、论文、营销文案等
- **图片生成**：文本生成图片、图片变体、AI编辑
- **视频生成**：文本转视频、图片转视频、AI配音
- **PPT生成**：主题生成、大纲生成、在线编辑
- **一键发布**：微信公众号、小红书、抖音、快手、今日头条
- **多模型支持**：OpenAI、Claude、通义千问、文心一言、智谱AI
- **积分会员系统**：灵活的计费方式

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Node.js 22+
- MySQL 8.0+
- Redis 6.0+

### 本地开发

```bash
# 克隆项目
git clone https://github.com/gongxings/ai-creator.git
cd ai-creator

# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑配置
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

访问：前端 http://localhost:5173 | 后端 http://localhost:8000/docs

### Docker 部署

**方式一：使用外部数据库（推荐生产环境）**

```bash
cp .env.example .env
# 编辑 .env，配置 DATABASE_URL 和 REDIS_URL
docker-compose up -d --build
```

**方式二：完整部署（含 MySQL + Redis）**

```bash
cp .env.example .env
docker-compose -f docker-compose.full.yml up -d --build
```

启动后自动创建 22 张数据库表并初始化基础数据。

## 🏗️ 技术栈

| 后端 | 前端 |
|------|------|
| FastAPI | Vue 3 + TypeScript |
| SQLAlchemy + MySQL | Element Plus |
| Redis | Pinia |
| JWT 认证 | Vite |

## 📁 项目结构

```
ai-creator/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/      # API 路由
│   │   ├── models/   # 数据库模型
│   │   ├── schemas/  # Pydantic 模型
│   │   └── services/ # 业务逻辑
│   └── requirements.txt
├── frontend/         # Vue 前端
│   ├── src/
│   │   ├── api/      # API 接口
│   │   ├── views/    # 页面组件
│   │   └── store/    # 状态管理
│   └── package.json
├── docker-compose.yml
└── docker-compose.full.yml
```

## ⚙️ 配置说明

核心环境变量（`.env`）：

```bash
# 数据库
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/ai_creator

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key

# AI API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## 📚 文档

- [功能说明](docs/FEATURES.md)
- [API文档](docs/API_REFERENCE.md)
- [部署指南](docs/DEPLOYMENT.md)
- [数据库设计](docs/DATABASE.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

[MIT License](LICENSE)

---

## 关注一下

| 公众号 | 解答群 |
|--------|--------|
| ![公众号](https://biyebang.com.cn/upload/wechat_Official-Account.png) | ![解答群](https://biyebang.com.cn/upload/wechat_group.jpg) |

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！
