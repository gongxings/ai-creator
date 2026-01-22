# 快速开始指南

本指南帮助您快速了解和使用AI创作者平台的新功能。

---

## 🎯 核心功能概览

### 1. 阿里通义千问模型 ✅
- 支持 qwen-max、qwen-plus、qwen-turbo 三种模型
- 提供文本生成和流式生成功能

### 2. 积分系统 ✅
- **充值规则：** 1元 = 10积分
- **消费规则：** 每次AI生成扣除10积分
- **会员优先：** 会员用户不扣积分

### 3. 会员系统 ✅
- **价格：** 9.9元/月
- **权益：** 不限次数使用，不扣积分

### 4. 运营系统 ✅
- 积分赠送活动
- 优惠券系统
- 推广返利
- 数据统计

---

## 📦 快速安装

### 1. 安装依赖
```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑配置文件，填入必要信息
# - 数据库配置
# - 阿里通义千问API密钥
# - 支付配置（可选）
```

### 3. 初始化数据库
```bash
# 运行数据库初始化脚本
python backend/scripts/init_db.py
```

### 4. 启动服务
```bash
# 启动后端（终端1）
cd backend
uvicorn app.main:app --reload

# 启动前端（终端2）
cd frontend
npm run dev
```

---

## 🚀 使用示例

### 1. 用户注册并获得积分
```python
# 用户注册时自动：
# - 生成唯一推荐码
# - 检查是否有推荐人
# - 参与注册赠送活动
# - 获得赠送积分
```

### 2. 充值积分
```bash
POST /api/v1/credit/recharge
{
    "amount": 100.00,
    "payment_method": "alipay"
}
# 返回：获得1000积分
```

### 3. 购买会员
```bash
POST /api/v1/credit/membership/purchase
{
    "membership_type": "monthly",
    "payment_method": "wechat"
}
# 返回：开通月度会员
```

### 4. AI生成（自动扣减积分）
```bash
POST /api/v1/writing/wechat/generate
{
    "title": "AI技术发展",
    "keywords": ["人工智能", "机器学习"],
    "style": "专业"
}
# 会员：不扣积分
# 非会员：扣除10积分
```

---

## 📊 核心API接口

### 积分管理
- `POST /api/v1/credit/recharge` - 创建充值订单
- `GET /api/v1/credit/balance` - 查询积分余额
- `GET /api/v1/credit/transactions` - 交易记录

### 会员管理
- `POST /api/v1/credit/membership/purchase` - 购买会员
- `GET /api/v1/credit/membership/status` - 会员状态
- `POST /api/v1/credit/membership/renew` - 续费会员

### 运营管理
- `GET /api/v1/operation/activities` - 活动列表
- `POST /api/v1/operation/activities/{id}/participate` - 参与活动
- `GET /api/v1/operation/coupons/my` - 我的优惠券
- `POST /api/v1/operation/referral/generate-code` - 生成推荐码

---

## 🔑 关键配置

### 环境变量 (.env)
```bash
# 阿里通义千问
QWEN_API_KEY=your_api_key

# 积分配置
CREDITS_PER_YUAN=10
CREDITS_PER_GENERATION=10

# 会员配置
MEMBERSHIP_MONTHLY_PRICE=9.9

# 推广返利
REFERRAL_REWARD_RATE=0.1
REFERRAL_MEMBERSHIP_REWARD=100
```

---

## 📝 业务规则

### 1. 积分规则
- 充值：1元 = 10积分
- 消费：每次生成扣10积分
- 退款：生成失败自动退款

### 2. 会员规则
- 价格：9.9元/月
- 权益：不限次数，不扣积分
- 优先级：会员 > 积分

### 3. 推广规则
- 充值返利：10%积分
- 会员返利：100积分
- 自动结算

---

## 🐛 常见问题

### Q1: 如何获取阿里通义千问API密钥？
访问 [阿里云DashScope](https://dashscope.aliyun.com/) 注册并获取API密钥。

### Q2: 会员和积分可以同时使用吗？
会员优先，会员用户不扣积分。会员到期后自动使用积分。

### Q3: 生成失败会扣积分吗？
不会。生成失败会自动退款积分。

### Q4: 如何查看推广收益？
访问 `GET /api/v1/operation/referral/statistics` 查看推广统计。

### Q5: 优惠券如何使用？
在充值或购买会员时，系统会自动匹配可用优惠券。

---

## 📚 更多文档

- [完整实现总结](./IMPLEMENTATION_SUMMARY.md) - 详细的功能实现文档
- [API接口文档](./API.md) - 完整的API接口说明
- [数据库设计](./DATABASE.md) - 数据库表结构设计
- [部署文档](./DEPLOYMENT.md) - 生产环境部署指南

---

## 💡 下一步

1. ✅ 配置阿里通义千问API密钥
2. ✅ 测试积分充值和消费
3. ✅ 测试会员购买和使用
4. ✅ 配置运营活动
5. ⚠️ 配置支付接口（生产环境）
6. ⚠️ 配置HTTPS证书（生产环境）

---

**文档版本：** v1.0  
**最后更新：** 2026-01-22
