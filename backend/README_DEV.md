# 后端开发环境快速启动指南

## 问题说明

如果你遇到 `ModuleNotFoundError: No module named 'app'` 错误，这是因为 Python 无法找到 `app` 模块。

## 解决方案

我们提供了三种启动方式：

### 方式一：使用开发启动脚本（推荐）

#### Windows
```bash
cd backend
run_dev.bat
```

#### Linux/Mac
```bash
cd backend
chmod +x run_dev.sh
./run_dev.sh
```

这个脚本会自动：
- 检查 Python 环境
- 创建虚拟环境（如果不存在）
- 安装依赖
- 配置 Python 路径
- 启动应用

### 方式二：使用 run.py 启动

```bash
cd backend
python run.py
```

`run.py` 已经配置好了正确的 Python 路径，可以直接运行。

### 方式三：使用 Docker（生产环境推荐）

在项目根目录运行：

#### Windows
```bash
start.bat
```

#### Linux/Mac
```bash
./start.sh
```

## 开发环境配置

### 1. 创建虚拟环境（推荐）

```bash
cd backend
python -m venv venv
```

### 2. 激活虚拟环境

#### Windows
```bash
venv\Scripts\activate
```

#### Linux/Mac
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：
- 数据库连接信息
- Redis 连接信息
- AI 服务 API 密钥
- JWT 密钥等

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

### 6. 启动应用

```bash
python run.py
```

## 访问地址

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 常见问题

### Q: 为什么会出现 ModuleNotFoundError?

A: 这是因为直接运行 `python app/main.py` 时，Python 无法找到 `app` 模块。解决方法：
- 使用 `run.py` 启动（已配置好路径）
- 或使用开发启动脚本
- 或设置 PYTHONPATH 环境变量

### Q: 如何设置 PYTHONPATH?

A: 如果你想手动运行，可以设置 PYTHONPATH：

#### Windows
```bash
set PYTHONPATH=d:\workspace\openstudy\ai-creator\backend
python app/main.py
```

#### Linux/Mac
```bash
export PYTHONPATH=/path/to/ai-creator/backend
python app/main.py
```

### Q: 虚拟环境有什么好处?

A: 虚拟环境可以：
- 隔离项目依赖
- 避免版本冲突
- 便于依赖管理
- 保持系统 Python 环境干净

## 开发工具推荐

### VS Code 扩展
- Python
- Pylance
- Python Test Explorer
- REST Client

### 代码格式化
```bash
pip install black isort flake8
```

### 运行测试
```bash
pytest
```

### 代码检查
```bash
flake8 app/
```

## 项目结构

```
backend/
├── app/                    # 应用代码
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic 模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── scripts/               # 脚本文件
├── tests/                 # 测试文件
├── run.py                 # 启动脚本（推荐）
├── run_dev.bat           # Windows 开发启动脚本
├── run_dev.sh            # Linux/Mac 开发启动脚本
├── requirements.txt       # 依赖列表
└── .env                   # 环境变量配置
```

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL 8.0+ (SQLAlchemy ORM)
- **缓存**: Redis
- **任务队列**: Celery
- **认证**: JWT
- **API 文档**: Swagger/ReDoc

## 更多信息

查看项目根目录的文档：
- [快速开始](../docs/QUICK_START.md)
- [API 参考](../docs/API_REFERENCE.md)
- [部署指南](../docs/DEPLOYMENT.md)
