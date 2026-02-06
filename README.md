# AI创作者平台

一个功能强大的AI创作平台，提供AI写作、图片生成、视频生成、PPT生成等创作工具，并支持一键发布到多个平台。

![登录页面](assert/login.png)

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
├── backend/                      # 后端代码
│   ├── app/
│   │   ├── api/v1/              # API路由
│   │   │   ├── auth.py          # 认证相关API
│   │   │   ├── writing.py       # 写作工具API
│   │   │   ├── image.py         # 图片生成API
│   │   │   ├── video.py         # 视频生成API
│   │   │   ├── ppt.py           # PPT生成API
│   │   │   ├── creations.py     # 创作记录API
│   │   │   ├── publish.py       # 发布管理API
│   │   │   ├── credit.py        # 积分会员API
│   │   │   ├── operation.py     # 运营管理API
│   │   │   └── models.py        # AI模型管理API
│   │   ├── core/                # 核心配置
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── security.py      # 安全认证
│   │   │   └── exceptions.py    # 异常处理
│   │   ├── models/              # 数据库模型
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── creation.py      # 创作记录模型
│   │   │   ├── credit.py        # 积分会员模型
│   │   │   ├── operation.py     # 运营活动模型
│   │   │   ├── publish.py       # 发布记录模型
│   │   │   └── ai_model.py      # AI模型配置
│   │   ├── schemas/             # Pydantic模型
│   │   │   ├── user.py          # 用户Schema
│   │   │   ├── creation.py      # 创作Schema
│   │   │   ├── credit.py        # 积分Schema
│   │   │   ├── operation.py     # 运营Schema
│   │   │   ├── publish.py       # 发布Schema
│   │   │   ├── platform.py      # 平台Schema
│   │   │   ├── ai_model.py      # AI模型Schema
│   │   │   └── common.py        # 通用Schema
│   │   ├── services/            # 业务逻辑
│   │   │   ├── ai/              # AI服务集成
│   │   │   │   ├── base.py      # 基础服务类
│   │   │   │   ├── factory.py   # 服务工厂
│   │   │   │   ├── openai_service.py      # OpenAI服务
│   │   │   │   ├── anthropic_service.py   # Anthropic服务
│   │   │   │   ├── qwen_service.py        # 通义千问服务
│   │   │   │   ├── baidu_service.py       # 文心一言服务
│   │   │   │   └── zhipu_service.py       # 智谱AI服务
│   │   │   ├── writing/         # 写作服务
│   │   │   │   ├── service.py   # 写作服务主类
│   │   │   │   ├── prompts.py   # 提示词模板
│   │   │   │   └── writing_service.py
│   │   │   ├── publish/         # 发布服务
│   │   │   │   ├── service.py   # 发布服务主类
│   │   │   │   ├── publish_service.py
│   │   │   │   └── platforms/   # 平台集成
│   │   │   │       ├── base.py          # 平台基类
│   │   │   │       ├── wechat.py        # 微信公众号
│   │   │   │       ├── xiaohongshu.py   # 小红书
│   │   │   │       ├── douyin.py        # 抖音
│   │   │   │       ├── kuaishou.py      # 快手
│   │   │   │       └── toutiao.py       # 今日头条
│   │   │   ├── credit_service.py        # 积分会员服务
│   │   │   └── operation_service.py     # 运营服务
│   │   └── utils/               # 工具函数
│   │       ├── deps.py          # 依赖注入
│   │       ├── cache.py         # 缓存工具
│   │       └── helpers.py       # 辅助函数
│   ├── scripts/                 # 脚本文件
│   │   └── init_db.py          # 数据库初始化
│   ├── Dockerfile              # Docker配置
│   ├── requirements.txt        # Python依赖
│   └── .env.example           # 环境变量示例
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── api/                # API接口
│   │   │   ├── request.ts      # 请求封装
│   │   │   ├── auth.ts         # 认证接口
│   │   │   ├── writing.ts      # 写作接口
│   │   │   ├── image.ts        # 图片接口
│   │   │   ├── video.ts        # 视频接口
│   │   │   ├── ppt.ts          # PPT接口
│   │   │   ├── creations.ts    # 创作记录接口
│   │   │   ├── publish.ts      # 发布接口
│   │   │   ├── credit.ts       # 积分接口
│   │   │   ├── operation.ts    # 运营接口
│   │   │   └── models.ts       # 模型接口
│   │   ├── components/         # 公共组件
│   │   │   └── home/           # 首页组件
│   │   │       ├── LoginGuide.vue         # 登录引导
│   │   │       ├── MembershipBenefits.vue # 会员权益
│   │   │       ├── StatsSection.vue       # 统计展示
│   │   │       ├── ToolsSection.vue       # 工具展示
│   │   │       └── UserStatusCards.vue    # 用户状态卡片
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页
│   │   │   ├── auth/           # 认证页面
│   │   │   │   ├── Login.vue   # 登录
│   │   │   │   └── Register.vue # 注册
│   │   │   ├── writing/        # 写作工具页面
│   │   │   │   ├── WritingTools.vue  # 工具列表
│   │   │   │   └── WritingEditor.vue # 编辑器
│   │   │   ├── image/          # 图片生成页面
│   │   │   │   └── ImageGeneration.vue
│   │   │   ├── video/          # 视频生成页面
│   │   │   │   └── VideoGeneration.vue
│   │   │   ├── ppt/            # PPT生成页面
│   │   │   │   └── PPTGeneration.vue
│   │   │   ├── history/        # 历史记录页面
│   │   │   │   └── CreationHistory.vue
│   │   │   ├── publish/        # 发布管理页面
│   │   │   │   └── PublishManagement.vue
│   │   │   ├── credit/         # 积分会员页面
│   │   │   │   ├── CreditRecharge.vue      # 积分充值
│   │   │   │   ├── MembershipPurchase.vue  # 会员购买
│   │   │   │   └── TransactionHistory.vue  # 交易记录
│   │   │   ├── operation/      # 运营管理页面
│   │   │   │   ├── ActivityManagement.vue  # 活动管理
│   │   │   │   ├── CouponManagement.vue    # 优惠券管理
│   │   │   │   ├── ReferralManagement.vue  # 推广管理
│   │   │   │   └── OperationStatistics.vue # 运营统计
│   │   │   └── settings/       # 设置页面
│   │   │       └── UserSettings.vue
│   │   ├── layouts/            # 布局组件
│   │   │   └── MainLayout.vue  # 主布局
│   │   ├── router/             # 路由配置
│   │   │   └── index.ts        # 路由定义
│   │   ├── store/              # 状态管理
│   │   │   └── user.ts         # 用户状态
│   │   ├── types/              # 类型定义
│   │   │   └── index.ts        # 通用类型
│   │   ├── utils/              # 工具函数
│   │   │   └── request.ts      # 请求工具
│   │   ├── App.vue             # 根组件
│   │   └── main.ts             # 入口文件
│   ├── public/                 # 静态资源
│   │   └── logo.svg           # Logo
│   ├── Dockerfile             # Docker配置
│   ├── nginx.conf             # Nginx配置
│   ├── package.json           # Node依赖
│   ├── tsconfig.json          # TypeScript配置
│   ├── vite.config.ts         # Vite配置
│   └── index.html             # HTML模板
├── docs/                       # 文档
│   ├── FEATURES.md            # 功能说明
│   ├── QUICK_START.md         # 快速开始
│   ├── IMPLEMENTATION_SUMMARY.md  # 实现总结
│   ├── API_REFERENCE.md       # API文档
│   ├── DATABASE.md            # 数据库设计
│   ├── DEPLOYMENT.md          # 部署指南
│   ├── CREDIT_MEMBERSHIP.md   # 积分会员文档
│   └── COOKIE_BASED_PUBLISH.md # Cookie发布文档
├── scripts/                    # 脚本文件
│   ├── init_db.py             # 数据库初始化
│   └── create_frontend.sh     # 前端创建脚本
├── docker-compose.yml         # Docker Compose配置
├── start.bat                  # Windows启动脚本
├── start.sh                   # Linux/Mac启动脚本
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
├── LICENSE                   # 开源协议
└── README.md                 # 项目说明
```

## 🔧 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_creator

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# AI模型API密钥
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
QWEN_API_KEY=your-qwen-api-key
BAIDU_API_KEY=your-baidu-api-key
ZHIPU_API_KEY=your-zhipu-api-key

# 支付配置
ALIPAY_APP_ID=your-alipay-app-id
ALIPAY_PRIVATE_KEY=your-alipay-private-key
WECHAT_APP_ID=your-wechat-app-id
WECHAT_MCH_ID=your-wechat-mch-id
```

## 🐳 Docker部署

### 使用Docker Compose部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Docker Compose配置说明

项目包含完整的 `docker-compose.yml` 配置，包括：
- **backend**: FastAPI后端服务
- **frontend**: Vue前端服务
- **mysql**: MySQL数据库
- **redis**: Redis缓存
- **nginx**: 反向代理服务器

## 📦 生产环境部署

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **硬盘**: 20GB以上
- **网络**: 公网IP，开放80/443端口

### 2. 部署步骤

```bash
# 1. 安装Docker和Docker Compose
curl -fsSL https://get.docker.com | sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 2. 克隆项目
git clone https://github.com/yourusername/ai-creator.git
cd ai-creator

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入实际配置

# 4. 启动服务
docker-compose up -d

# 5. 初始化数据库
docker-compose exec backend python scripts/init_db.py

# 6. 配置SSL证书（可选）
# 使用Let's Encrypt自动获取SSL证书
```

### 3. Nginx配置

生产环境建议使用Nginx作为反向代理：

```bash
# 安装Nginx
sudo apt install nginx

# 配置站点
sudo nano /etc/nginx/sites-available/ai-creator

# 启用站点
sudo ln -s /etc/nginx/sites-available/ai-creator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 安全建议

1. **修改默认密码**: 部署后立即修改数据库和管理员密码
2. **启用HTTPS**: 使用SSL证书加密传输
3. **配置防火墙**: 只开放必要的端口
4. **定期备份**: 设置自动备份数据库和用户数据
5. **更新依赖**: 定期更新系统和依赖包
6. **监控日志**: 配置日志监控和告警

## 📈 性能优化

1. **数据库优化**
   - 添加适当的索引
   - 使用连接池
   - 定期清理过期数据

2. **缓存策略**
   - Redis缓存热点数据
   - API响应缓存
   - 静态资源CDN

3. **异步处理**
   - 使用Celery处理耗时任务
   - 消息队列解耦服务

4. **负载均衡**
   - 多实例部署
   - Nginx负载均衡
   - 数据库读写分离

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **项目主页**: https://github.com/yourusername/ai-creator
- **问题反馈**: https://github.com/yourusername/ai-creator/issues
- **邮箱**: your-email@example.com

## 🙏 致谢

感谢以下开源项目：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [OpenAI](https://openai.com/)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
