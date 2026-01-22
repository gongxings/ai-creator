# 阿里Qwen模型、积分和会员功能实现总结

## 实现概述

本次更新为AI创作者平台添加了三个核心功能：
1. **阿里通义千问(Qwen)模型支持**
2. **积分充值系统**
3. **会员订阅系统**

## 一、阿里Qwen模型集成

### 1. 实现文件

#### backend/app/services/ai/qwen_service.py
- 实现了`QwenService`类，继承自`AIServiceBase`
- 支持文本生成和图片生成
- 使用DashScope SDK进行API调用
- 支持流式输出
- 支持的模型：qwen-turbo, qwen-plus, qwen-max, qwen-vl-plus

#### backend/app/services/ai/factory.py
- 在`SERVICE_MAP`中注册Qwen服务
- 在`create_service`方法中添加Qwen服务创建逻辑

### 2. 配置说明

在`.env`文件中添加：
```env
QWEN_API_KEY=your_qwen_api_key
```

### 3. 使用示例

```python
from app.services.ai.factory import AIServiceFactory

# 创建Qwen服务
service = AIServiceFactory.create_service(
    provider="qwen",
    api_key="your_api_key"
)

# 生成文本
result = await service.generate_text(
    prompt="写一篇关于AI的文章",
    model="qwen-max"
)
```

## 二、积分系统

### 1. 核心功能

- **充值规则**：1元 = 10积分
- **消费规则**：每次AI生成消耗10积分（会员除外）
- **充值套餐**：
  - 10积分 = ¥1.00
  - 100积分 = ¥10.00（赠送10积分）
  - 500积分 = ¥50.00（赠送100积分）
  - 1000积分 = ¥100.00（赠送300积分）

### 2. 实现文件

#### 后端

- `backend/app/models/credit.py` - 数据库模型
  - CreditTransaction：积分交易记录
  - RechargeOrder：充值订单
  - CreditPrice：积分价格配置

- `backend/app/schemas/credit.py` - 请求/响应Schema
  - 定义所有积分相关的数据结构

- `backend/app/services/credit_service.py` - 业务逻辑
  - CreditService：积分管理服务
  - RechargeService：充值服务

- `backend/app/api/v1/credit.py` - API路由
  - GET /api/v1/credit/balance - 获取余额
  - GET /api/v1/credit/transactions - 获取交易记录
  - POST /api/v1/credit/recharge - 创建充值订单
  - GET /api/v1/credit/recharge/orders - 获取充值订单列表

#### 前端

- `frontend/src/api/credit.ts` - API接口定义
- `frontend/src/views/credit/CreditRecharge.vue` - 积分充值页面
- `frontend/src/views/credit/TransactionHistory.vue` - 交易记录页面

### 3. 使用流程

1. 用户选择充值套餐
2. 选择支付方式（支付宝/微信）
3. 创建充值订单
4. 完成支付（开发环境可模拟支付）
5. 积分自动到账

## 三、会员系统

### 1. 核心功能

- **会员特权**：不限次数使用所有AI创作功能
- **会员套餐**：
  - 月度会员：¥9.90/月
  - 季度会员：¥25.00/季
  - 年度会员：¥88.00/年

### 2. 实现文件

#### 后端

- `backend/app/models/credit.py` - 数据库模型
  - MembershipOrder：会员订单
  - MembershipPrice：会员价格配置

- `backend/app/models/user.py` - 用户模型扩展
  - is_member：是否会员
  - member_expired_at：会员到期时间

- `backend/app/services/credit_service.py` - 业务逻辑
  - MembershipService：会员管理服务

- `backend/app/api/v1/credit.py` - API路由
  - GET /api/v1/credit/membership/prices - 获取会员价格
  - POST /api/v1/credit/membership - 创建会员订单
  - GET /api/v1/credit/membership/orders - 获取会员订单列表

#### 前端

- `frontend/src/views/credit/MembershipPurchase.vue` - 会员购买页面
- `frontend/src/layouts/MainLayout.vue` - 主布局（显示会员状态）

### 3. 使用流程

1. 用户选择会员套餐
2. 选择支付方式（支付宝/微信）
3. 创建会员订单
4. 完成支付（开发环境可模拟支付）
5. 会员立即生效

## 四、积分扣减集成

### 1. 实现位置

`backend/app/api/v1/writing.py` - AI写作API

### 2. 扣减逻辑

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

# 生成内容...

# 如果生成失败，退还积分
if not current_user.is_member:
    await credit_service.add_credits(
        user_id=current_user.id,
        credits=credits_required,
        transaction_type="REFUND",
        description=f"AI写作失败退款 - {request.tool_type}"
    )
```

### 3. 扣减规则

- **会员用户**：不扣除积分，直接生成
- **非会员用户**：先扣除10积分，再生成
- **积分不足**：返回402错误，提示充值
- **生成失败**：自动退还已扣除的积分

## 五、数据库变更

### 1. 新增表

```sql
-- 积分交易记录表
CREATE TABLE credit_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL,
    amount INT NOT NULL,
    balance_after INT NOT NULL,
    description VARCHAR(500),
    related_order_id BIGINT,
