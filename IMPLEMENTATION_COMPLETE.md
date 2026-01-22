# 阿里通义千问模型 + 积分会员系统实施完成报告

## 实施日期
2026年1月22日

## 实施内容概述

本次实施完成了以下三个核心功能：

1. **阿里通义千问(Qwen)模型集成**
2. **积分系统**：非会员1元购买10积分，每次生成扣10积分
3. **会员系统**：会员9.9元/月，不限制使用次数

---

## 一、阿里通义千问模型集成

### 1.1 实施文件

#### backend/app/services/ai/qwen_service.py
- 实现了`QwenService`类，继承自`AIServiceBase`
- 支持文本生成和图片生成
- 支持流式输出
- API端点：https://dashscope.aliyuncs.com/api/v1
- 支持模型：qwen-turbo, qwen-plus, qwen-max, qwen-vl-plus

#### backend/app/services/ai/factory.py
- 在`SERVICE_MAP`中添加了"qwen": QwenService
- 在`create_service`方法中添加了Qwen服务创建逻辑

#### backend/scripts/init_db.py
- 添加了通义千问模型的初始配置

### 1.2 使用方法

```python
# 在AI模型管理中添加通义千问配置
{
    "name": "通义千问",
    "provider": "qwen",
    "model_id": "qwen-max",
    "api_key": "your-dashscope-api-key",
    "is_active": true
}
```

---

## 二、积分系统

### 2.1 数据库模型

#### backend/app/models/credit.py

**CreditTransaction（积分交易记录）**
- id: 主键
- user_id: 用户ID
- transaction_type: 交易类型（充值/消费/退款/奖励/过期）
- credits: 积分数量
- balance_after: 交易后余额
- description: 交易描述
- order_id: 关联订单ID
- created_at: 创建时间

**RechargeOrder（充值订单）**
- id: 主键
- user_id: 用户ID
- order_no: 订单号
- credits: 购买积分数
- bonus_credits: 赠送积分数
- amount: 支付金额
- payment_method: 支付方式
- payment_status: 支付状态
- paid_at: 支付时间
- created_at/updated_at: 时间戳

**CreditPrice（积分价格配置）**
- id: 主键
- amount: 积分数量
- price: 价格
- bonus: 赠送积分
- is_active: 是否启用
- sort_order: 排序

### 2.2 业务逻辑

#### backend/app/services/credit_service.py

**CreditService类**
- `get_user_balance()`: 获取用户余额和会员状态
- `check_and_consume_credits()`: 核心方法，会员不扣积分，非会员扣10积分
- `add_credits()`: 增加积分（充值、退款）
- `get_transactions()`: 获取交易记录
- `get_credit_statistics()`: 获取积分统计

**RechargeService类**
- `create_recharge_order()`: 创建充值订单
- `process_payment_callback()`: 处理支付回调
- `get_recharge_orders()`: 获取充值订单列表
- `get_credit_prices()`: 获取积分价格配置

### 2.3 API接口

#### backend/app/api/v1/credit.py

```
GET  /api/v1/credit/balance          # 获取余额
POST /api/v1/credit/recharge         # 创建充值订单
POST /api/v1/credit/payment/callback # 支付回调
GET  /api/v1/credit/transactions     # 交易记录
GET  /api/v1/credit/prices           # 积分价格
GET  /api/v1/credit/statistics       # 积分统计
```

### 2.4 前端页面

#### frontend/src/views/credit/CreditRecharge.vue
- 积分充值页面
- 显示当前余额
- 选择充值套餐
- 支付方式选择
- 支付二维码展示

#### frontend/src/views/credit/TransactionHistory.vue
- 交易历史记录
- 筛选和搜索
- 分页显示

---

## 三、会员系统

### 3.1 数据库模型

#### backend/app/models/credit.py

**MembershipOrder（会员订单）**
- id: 主键
- user_id: 用户ID
- order_no: 订单号
- membership_type: 会员类型（月/季/年）
- duration_days: 时长（天）
- amount: 支付金额
- payment_method: 支付方式
- payment_status: 支付状态
- start_date: 开始日期
- end_date: 结束日期
- paid_at: 支付时间
- created_at/updated_at: 时间戳

**MembershipPrice（会员价格配置）**
- id: 主键
- membership_type: 会员类型
- duration_days: 时长
- price: 价格
- original_price: 原价
- is_active: 是否启用
- sort_order: 排序

#### backend/app/models/user.py（更新）
- credits: 积分余额（默认0）
- is_member: 是否会员
- member_expired_at: 会员到期时间

### 3.2 业务逻辑

#### backend/app/services/credit_service.py

**MembershipService类**
- `purchase_membership()`: 购买会员
- `process_payment_callback()`: 处理支付回调
- `check_membership_status()`: 检查会员状态
- `get_membership_orders()`: 获取会员订单列表
- `get_membership_prices()`: 获取会员价格配置
- `get_membership_statistics()`: 获取会员统计

### 3.3 API接口

#### backend/app/api/v1/credit.py

```
POST /api/v1/credit/membership/purchase        # 购买会员
POST /api/v1/credit/membership/payment/callback # 支付回调
GET  /api/v1/credit/membership/orders          # 会员订单
GET  /api/v1/credit/membership/prices          # 会员价格
GET  /api/v1/credit/membership/status          # 会员状态
GET  /api/v1/credit/membership/statistics      # 会员统计
```

### 3.4 前端页面

#### frontend/src/views/credit/MembershipPurchase.vue
- 会员购买页面
- 显示会员状态和到期时间
- 选择会员套餐（月/季/年）
- 支付方式选择
- 会员权益说明

---

## 四、积分扣减逻辑集成

### 4.1 AI写作功能集成

#### backend/app/api/v1/writing.py

在`generate_content`和`regenerate_content`接口中集成了积分扣减逻辑：

```python
# 检查并扣减积分（会员不扣积分）
credit_service = CreditService(db)
credits_required = 10  # 每次生成需要10积分

try:
    await credit_service.check_and_consume_credits(
        user_id=current_user.id,
        credits=credits_required,
        description=f"AI写作 - {request.tool_type}"
    )
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=str(e),
    )

# 生成失败时自动退款
except Exception as e:
    if not current_user.is_member:
        await credit_service.add_credits(
            user_id=current_user.id,
            credits=credits_required,
            transaction_type="REFUND",
            description=f"AI写作失败退款 - {request.tool_type}"
        )
```

### 4.2 其他功能集成

同样的积分扣减逻辑需要集成到：
- 图片生成（backend/app/api/v1/image.py）
- 视频生成（backend/app/api/v1/video.py）
- PPT生成（backend/app/api/v1/ppt.py）

---

## 五、前端状态管理

### 5.1 用户状态更新

#### frontend/src/store/user.ts

更新了用户状态管理，添加了：
- credits: 积分余额
- isMember: 是否会员
- memberExpiredAt: 会员到期时间

### 5.2 类型定义

#### frontend/src/types/index.ts

添加了积分和会员相关的类型定义：
- CreditBalance
- CreditTransaction
- RechargeOrder
- MembershipOrder
- CreditPrice
- MembershipPrice

---

## 六、路由配置

### 6.1 新增路由

#### frontend/src/router/index.ts

```javascript
{
  path: '/credit',
  name: 'Credit',
  children: [
    {
      path: 'recharge',
      name: 'CreditRecharge',
      component: () => import('@/views/credit/CreditRecharge.vue')
    },
    {
      path: 'membership',
      name: 'MembershipPurchase',
      component: () => import('@/views/credit/MembershipPurchase.vue')
    },
    {
      path: 'transactions',
      name: 'TransactionHistory',
      component: () => import('@/views/credit/TransactionHistory.vue')
    }
  ]
}
```

### 6.2 导航菜单更新

#### frontend/src/layouts/MainLayout.vue

在主布局中添加了积分和会员入口：
- 显示当前积分余额
- 显示会员状态
- 充值入口
- 购买会员入口

---

## 七、数据库初始化

### 7.1 初始数据

#### backend/scripts/init_db.py

初始化脚本包含：

**测试用户**
- 普通用户：test_user / test123456（100积分）
- 管理员：admin / admin123456（1000积分，会员至2026-12-31）

**积分价格配置**
- 10积分 = 1元（无赠送）
- 100积分 = 10元（赠送10积分）
- 500积分 = 50元（赠送100积分）
- 1000积分 = 100元（赠送300积分）

**会员价格配置**
- 月会员：9.9元/30天（原价19.9元）
- 季会员：25元/90天（原价59.7元）
- 年会员：88元/365天（原价238.8元）

**AI模型配置**
- 添加了通义千问模型配置

---

## 八、部署和测试

### 8.1 环境配置

需要在`.env`文件中添加：

```bash
# 阿里云DashScope API密钥
QWEN_API_KEY=your-dashscope-api-key

# 支付配置（可选，用于真实支付）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
WECHAT_APP_ID=
WECHAT_MCH_ID=
WECHAT_API_KEY=
```

### 8.2 数据库初始化

```bash
# 进入后端目录
cd backend

# 运行初始化脚本
python scripts/init_db.py
```

### 8.3 启动服务

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 8.4 测试流程

1. **注册/登录**
   - 使用测试账号登录：test_user / test123456

2. **查看余额**
   - 访问个人中心，查看当前积分余额（100积分）

3. **测试AI写作（非会员）**
   - 选择任意写作工具
   - 输入内容生成
   - 确认扣减10积分
   - 余额变为90积分

4. **充值积分**
   - 访问充值页面
   - 选择充值套餐
   - 使用模拟支付完成充值
   - 确认积分到账

5. **购买会员**
   - 访问会员购买页面
   - 选择会员套餐（月/季/年）
   - 使用模拟支付完成购买
   - 确认会员状态激活

6. **测试AI写作（会员）**
   - 使用会员账号生成内容
   - 确认不扣减积分
   - 可以无限次使用

7. **查看交易记录**
   - 访问交易历史页面
   - 查看所有充值、消费、退款记录

---

## 九、核心业务逻辑

### 9.1 积分消费逻辑

```python
async def check_and_consume_credits(
    self,
    user_id: int,
    credits: int,
    description: str
) -> bool:
    """检查并消费积分（会员不扣积分）"""
    user = self.db.query(
