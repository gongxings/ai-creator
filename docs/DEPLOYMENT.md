# AI创作者平台部署指南

## 目录
- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [Docker部署](#docker部署)
- [生产环境部署](#生产环境部署)
- [常见问题](#常见问题)

## 环境要求

### 基础环境
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 7+
- Docker & Docker Compose (可选)

### 系统要求
- 操作系统：Linux/macOS/Windows
- 内存：最低4GB，推荐8GB+
- 磁盘：最低20GB可用空间
- 网络：需要访问外部AI服务API

## 本地开发部署

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/ai-creator.git
cd ai-creator
```

### 2. 配置环境变量
```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，填写实际配置
vim .env
```

### 3. 后端部署

#### 3.1 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 3.2 初始化数据库
```bash
# 确保MySQL已启动
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ai_creator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行初始化脚本
python scripts/init_db.py
```

#### 3.3 启动后端服务
```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用脚本
python -m app.main
```

#### 3.4 启动Celery Worker（可选）
```bash
# 新开一个终端
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

### 4. 前端部署

#### 4.1 安装依赖
```bash
cd frontend
npm install
```

#### 4.2 配置API地址
编辑 `frontend/src/api/request.ts`，确保baseURL指向后端地址：
```typescript
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

#### 4.3 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:5173 查看应用

### 5. 验证部署
- 后端API文档：http://localhost:8000/docs
- 前端应用：http://localhost:5173
- 测试注册登录功能
- 测试AI写作功能

## Docker部署

### 1. 准备工作
```bash
# 确保已安装Docker和Docker Compose
docker --version
docker-compose --version

# 配置环境变量
cp .env.example .env
vim .env
```

### 2. 构建并启动服务
```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 初始化数据库
```bash
# 进入后端容器
docker-compose exec backend bash

# 运行初始化脚本
python scripts/init_db.py

# 退出容器
exit
```

### 4. 访问应用
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 5. 常用Docker命令
```bash
# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec [service_name] bash
```

## 生产环境部署

### 1. 服务器准备

#### 1.1 系统配置
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y git curl wget vim

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 1.2 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. 部署应用

#### 2.1 克隆代码
```bash
cd /opt
sudo git clone https://github.com/your-repo/ai-creator.git
cd ai-creator
```

#### 2.2 配置环境
```bash
# 复制并编辑环境变量
sudo cp .env.example .env
sudo vim .env

# 重要：修改以下配置
# - SECRET_KEY: 生成强密码
# - JWT_SECRET_KEY: 生成强密码
# - 数据库密码
# - Redis密码
# - AI服务API密钥
# - 平台发布配置
```

#### 2.3 配置SSL证书（推荐）
```bash
# 使用Let's Encrypt
sudo apt install -y certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 证书路径
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

#### 2.4 配置Nginx（如果使用SSL）
编辑 `nginx/nginx.conf`：
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... 其他配置
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 2.5 启动服务
```bash
# 构建并启动
sudo docker-compose -f docker-compose.yml up -d --build

# 初始化数据库
sudo docker-compose exec backend python scripts/init_db.py

# 查看日志
sudo docker-compose logs -f
```

### 3. 配置自动备份

#### 3.1 数据库备份脚本
创建 `scripts/backup.sh`：
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_CONTAINER="ai-creator-mysql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker exec $MYSQL_CONTAINER mysqldump -u root -p$
