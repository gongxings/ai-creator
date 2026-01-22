# AI创作者平台

一个功能强大的AI创作平台，提供AI写作、图片生成、视频生成、PPT生成等创作工具，并支持一键发布到多个平台。

## 功能特性

### 核心功能
- **AI写作工具**：14个专业写作工具（公众号文章、小红书笔记、公文、论文、营销文案、新闻稿、短视频脚本、故事、商业计划书、工作报告、简历、教案、改写、翻译）
- **图片生成**：文本生成图片、图片变体、图片编辑等
- **视频生成**：文本转视频、图片转视频、AI配音等
- **PPT生成**：主题生成PPT、大纲生成PPT、文档转PPT等
- **自动发布**：一键发布到微信公众号、小红书、抖音、快手、今日头条、百家号、知乎、简书等平台

### 设计理念
- 场景化工具、一键生成、最少输入、智能优化、所见即所得

## 技术栈

**后端**：Python 3.10+ / FastAPI / SQLAlchemy / MySQL 8.0+ / Redis / Celery / JWT

**前端**：Vue 3 + TypeScript / Vite / Element Plus / Pinia / Axios / Quill

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis

### 后端安装

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库、Redis、AI API密钥等

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端安装

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

访问 http://localhost:3000

## Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 项目结构

```
ai-creator/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/v1/         # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   ├── store/         # 状态管理
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── scripts/               # 脚本文件
├── docker-compose.yml
└── README.md
```

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

详细的开发规范和指南请参考 `.clinerules` 文件。

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue。
