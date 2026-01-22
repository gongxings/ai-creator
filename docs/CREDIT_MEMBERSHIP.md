# 积分和会员系统使用指南

## 概述

AI创作者平台提供了完善的积分和会员系统，用户可以通过充值积分或购买会员来使用AI创作功能。

## 功能特性

### 1. 积分系统

- **充值规则**：1元 = 10积分
- **消费规则**：每次AI生成消耗10积分（会员除外）
- **充值套餐**：
  - 10积分 = ¥1.00（无赠送）
  - 100积分 = ¥10.00（赠送10积分）
  - 500积分 = ¥50.00（赠送100积分）
  - 1000积分 = ¥100.00（赠送300积分）

### 2. 会员系统

- **会员特权**：不限次数使用所有AI创作功能
- **会员套餐**：
  - 月度会员：¥9.90/月（原价¥19.90）
  - 季度会员：¥25.00/季（原价¥59.70）
  - 年度会员：¥88.00/年（原价¥238.80）

### 3. 消费规则

- **会员用户**：使用AI创作功能不扣除积分
- **非会员用户**：每次AI生成扣除10积分
- **生成失败**：自动退还已扣除的积分

## API接口

### 积分相关

#### 获取用户余额
```http
GET /api/v1/credit/balance
Authorization: Bearer {token}
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "credits": 100,
    "is_member": false,
    "member_expired_at": null
  }
}
```

#### 获取交易记录
```http
GET /api/v1/credit/transactions?skip=0&limit=20&type=CONSUME
Authorization: Bearer {token}
```

#### 获取积分统计
```http
GET /api/v1/credit/statistics
Authorization: Bearer {token}
```

#### 获取积分价格列表
```http
GET /api/v1/credit/prices
```

#### 创建充值订单
```http
POST /api/v1/credit/recharge
Authorization: Bearer {token}
Content-Type: application/json

{
  "price_id": 1,
  "payment_method": "alipay"
}
```

#### 获取充值订单列表
```http
GET /api/v1/credit/recharge/orders?skip=0&limit=20
Authorization: Bearer {token}
```

### 会员相关

#### 获取会员价格列表
```http
GET /api/v1/credit/membership/prices
```

#### 创建会员订单
```http
POST /api/v1/credit/membership
Authorization: Bearer {token}
Content-Type: application/json

{
  "price_id": 1,
  "payment_method": "alipay"
}
```

#### 获取会员订单列表
```http
GET /api/v1/credit/membership/orders?skip=0&limit=20
Authorization: Bearer {token}
```

#### 获取会员统计
```http
GET /api/v1/credit/membership/statistics
Authorization: Bearer {token}
```

### 支付回调（模拟）

```http
POST /api/v1/credit/payment/callback
Content-Type: application/json

{
  "order_type": "recharge",
  "order_no": "R20260122001"
}
```

## 前端集成

### 1. 积分充值页面

路径：`/credit/recharge`

功能：
- 显示当前积分余额
- 展示充值套餐列表
- 选择支付方式
- 创建充值订单
- 模拟支付成功

### 2. 会员购买页面

路径：`/credit/membership`

功能：
- 显示会员状态和到期时间
- 展示会员套餐列表
- 选择支付方式
- 创建会员订单
- 模拟支付成功

### 3. 交易记录页面

路径：`/credit/transactions`

功能：
- 查看积分交易记录
- 筛选交易类型
- 分页显示
- 查看订单详情

### 4. 主布局集成

在主布局的头部显示：
- 会员标识（如果是会员）
- 当前积分余额
- 点击可快速跳转到充值/购买页面

## 使用流程

### 非会员用户

1. 注册/登录账号
2. 充值积分（可选择不同套餐）
3. 选择支付方式（支付宝/微信）
4. 完成支付（开发环境可模拟支付）
5. 积分到账后即可使用AI创作功能
6. 每次生成消耗10积分

### 会员用户

1. 注册/登录账号
2. 购买会员（可选择不同时长）
3. 选择支付方式（支付宝/微信）
4. 完成支付（开发环境可模拟支付）
5. 会员生效后不限次数使用AI创作功能
6. 会员到期后自动转为非会员

## 数据库模型

### CreditTransaction（积分交易记录）

```python
- id: 主键
- user_id: 用户ID
- type: 交易类型（RECHARGE/CONSUME/REFUND/REWARD/EXPIRE）
- amount: 交易金额
- balance_after: 交易后余额
- description: 交易描述
- related_order_id: 关联订单ID
- created_at: 创建时间
```

### RechargeOrder（充值订单）

```python
- id: 主键
- user_id: 用户ID
- order_no: 订单号
- amount: 充值积分数
- bonus: 赠送积分数
- total_amount: 总积分数
- price: 支付金额
- payment_method: 支付方式
- payment_status: 支付状态
- paid_at: 支付时间
- created_at: 创建时间
```

### MembershipOrder（会员订单）

```python
- id: 主键
- user_id: 用户ID
- order_no: 订单号
- membership_type: 会员类型
- duration_days: 时长（天）
- price: 支付金额
- payment_method: 支付方式
- payment_status: 支付状态
- start_date: 开始日期
- end_date: 结束日期
- paid_at: 支付时间
- created_at: 创建时间
```

### CreditPrice（积分价格配置）

```python
- id: 主键
- amount: 积分数量
- price: 价格
- bonus: 赠送积分
- is_active: 是否启用
- sort_order: 排序
