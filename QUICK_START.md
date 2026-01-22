# 快速启动指南 - 阿里通义千问 + 积分会员系统

## 前置要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis

## 一、环境准备

### 1. 克隆项目

```bash
git clone https://github.com/gongxings/ai-creator.git
cd ai-creator
```

### 2. 配置后端环境

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

创建MySQL数据库：

```sql
CREATE DATABASE ai_creator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 配置环境变量

复制`.env.example`为`.env`并配置：

```bash
cp .env.example .env
```

编辑`.env`文件：

```bash
# 应用配置
APP_NAME=AI创作者平台
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_creator

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# 阿里云DashScope API密钥（通义千问）
QWEN_API_KEY=your-dashscope-api-key

# OpenAI API密钥（可选）
OPENAI_API_KEY=your-openai-api-key

# 其他AI服务API密钥（可选）
ANTHROPIC_API_KEY=
BAIDU_API_KEY=
BAIDU_SECRET_KEY=
ZHIPU_API_KEY=

# 支付配置（可选，用于真实支付）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
WECHAT_APP_ID=
WECHAT_MCH_ID=
WECHAT_API_KEY=
```

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

初始化成功后会创建：
- 测试用户：test_user / test123456（100积分）
- 管理员：admin / admin123456（1000积分，会员至2026-12-31）
- 积分价格配置
- 会员价格配置
- AI模型配置（包括通义千问）

### 6. 启动后端服务

```bash
python -m uvicorn app.main:app --reload
```

后端服务将在 http://localhost:8000 启动

API文档：http://localhost:8000/docs

## 二、前端配置

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建`.env.local`文件：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动前端服务

```bash
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 三、功能测试

### 1. 登录系统

访问 http://localhost:5173

使用测试账号登录：
- 用户名：test_user
- 密码：test123456

### 2. 测试AI写作（非会员）

1. 点击"AI写作"
2. 选择任意写作工具（如"公众号文章"）
3. 输入主题和要求
4. 点击"生成内容"
5. 查看积分扣减（从100变为90）

### 3. 充值积分

1. 点击右上角积分余额
2. 选择充值套餐
3. 选择支付方式（模拟支付）
4. 完成支付
5. 确认积分到账

### 4. 购买会员

1. 点击"购买会员"
2. 选择会员套餐（月/季/年）
3. 选择支付方式（模拟支付）
4. 完成支付
5. 确认会员状态激活

### 5. 测试AI写作（会员）

1. 使用会员账号生成内容
2. 确认不扣减积分
3. 可以无限次使用

### 6. 查看交易记录

1. 点击"交易记录"
2. 查看所有充值、消费、退款记录

## 四、配置通义千问API

### 1. 获取API密钥

1. 访问阿里云DashScope：https://dashscope.aliyun.com/
2. 注册/登录账号
3. 创建API密钥
4. 复制API密钥

### 2. 配置API密钥

方式一：在`.env`文件中配置

```bash
QWEN_API_KEY=your-dashscope-api-key
```

方式二：在管理后台配置

1. 登录管理员账号（admin / admin123456）
2. 进入"AI模型管理"
3. 找到"通义千问"模型
4. 编辑并填入API密钥
5. 保存配置

### 3. 测试通义千问

1. 在AI写作中选择使用"通义千问"模型
2. 生成内容测试

## 五、Docker部署（可选）

### 1. 使用Docker Compose

```bash
# 在项目根目录
docker-compose up -d
```

### 2. 访问服务

- 前端：http://localhost
- 后端API：http://localhost/api
- API文档：http://localhost/api/docs

## 六、常见问题

### 1. 数据库连接失败

检查MySQL服务是否启动，数据库配置是否正确。

### 2. Redis连接失败

检查Redis服务是否启动。

### 3. API密钥无效

确认API密钥是否正确，是否有足够的配额。

### 4. 积分扣减失败

检查用户余额是否充足，会员状态是否正常。

### 5. 支付回调失败

检查支付配置是否正确，回调URL是否可访问。

## 七、开发建议

### 1. 代码规范

- 后端遵循PEP 8
- 前端使用ESLint和Prettier
- 提交前运行代码检查

### 2. 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

### 3. 日志查看

```bash
# 后端日志
tail -f backend/logs/app.log

# 前端开发日志
# 在浏览器控制台查看
```

## 八、生产部署注意事项

1. **安全配
