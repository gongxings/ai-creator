# API接口文档

## 基础信息

### 基础URL
```
开发环境: http://localhost:8000
生产环境: https://api.yourdomain.com
```

### 通用响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误码说明
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 429: 请求过于频繁
- 500: 服务器内部错误

### 认证方式
使用JWT Token认证，在请求头中添加：
```
Authorization: Bearer {access_token}
```

---

## 1. 认证接口

### 1.1 用户注册
```http
POST /api/v1/auth/register
```

**请求体：**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "credit_balance": 0,
    "is_member": false,
    "referral_code": "ABC123"
  }
}
```

### 1.2 用户登录
```http
POST /api/v1/auth/login
```

**请求体：**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "credit_balance": 100,
      "is_member": true,
      "membership_type": "monthly"
    }
  }
}
```

### 1.3 刷新Token
```http
POST /api/v1/auth/refresh
```

**请求头：**
```
Authorization: Bearer {refresh_token}
```

**响应：**
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
  }
}
```

### 1.4 获取当前用户信息
```http
GET /api/v1/auth/me
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "credit_balance": 100,
    "is_member": true,
    "membership_type": "monthly",
    "membership_end_date": "2026-02-22T10:00:00",
    "referral_code": "ABC123"
  }
}
```

---

## 2. 积分会员接口

### 2.1 创建充值订单
```http
POST /api/v1/credit/recharge
```

**请求体：**
```json
{
  "amount": 10.00,
  "payment_method": "alipay",
  "coupon_code": "DISCOUNT10"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "订单创建成功",
  "data": {
    "order_id": "R202601221000001",
    "amount": 10.00,
    "credits": 100,
    "payment_url": "https://payment.example.com/pay?order=..."
  }
}
```

### 2.2 创建会员订单
```http
POST /api/v1/credit/membership
```

**请求体：**
```json
{
  "membership_type": "monthly",
  "payment_method": "wechat"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "会员订单创建成功",
  "data": {
    "order_id": "M202601221000001",
    "membership_type": "monthly",
    "amount": 9.90,
    "payment_url": "https://payment.example.com/pay?order=..."
  }
}
```

### 2.3 支付回调
```http
POST /api/v1/credit/payment/callback
```

**请求体：**
```json
{
  "order_id": "R202601221000001",
  "payment_method": "alipay",
  "transaction_id": "2026012212345678",
  "status": "success"
}
```

### 2.4 获取积分余额
```http
GET /api/v1/credit/balance
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "credit_balance": 100,
    "is_member": true,
    "membership_type": "monthly",
    "membership_end_date": "2026-02-22T10:00:00"
  }
}
```

### 2.5 获取交易记录
```http
GET /api/v1/credit/transactions?page=1&page_size=20
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "type": "recharge",
        "amount": 100,
        "balance_after": 200,
        "description": "充值10元",
        "created_at": "2026-01-22T10:00:00"
      }
    ]
  }
}
```

### 2.6 获取充值订单列表
```http
GET /api/v1/credit/recharge/orders?page=1&page_size=20
```

### 2.7 获取会员订单列表
```http
GET /api/v1/credit/membership/orders?page=1&page_size=20
```

---

## 3. AI写作接口

### 3.1 生成内容
```http
POST /api/v1/writing/{tool_type}/generate
```

**路径参数：**
- tool_type: 工具类型（wechat_article, xiaohongshu_note等）

**请求体：**
```json
{
  "title": "如何提高工作效率",
  "keywords": ["时间管理", "效率工具"],
  "requirements": "字数2000字，包含实用技巧",
  "model_id": 1
}
```

**响应：**
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "creation_id": 123,
    "content": "生成的文章内容...",
    "credits_used": 10
  }
}
```

### 3.2 获取写作工具列表
```http
GET /api/v1/writing/tools
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "type": "wechat_article",
      "name": "公众号文章",
      "description": "生成适合微信公众号的文章",
      "credits_cost": 10
    }
  ]
}
```

---

## 4. 图片生成接口

### 4.1 文本生成图片
```http
POST /api/v1/image/generate
```

**请求体：**
```json
{
  "prompt": "一只可爱的猫咪在花园里玩耍",
  "size": "1024x1024",
  "model_id": 2
}
```

**响应：**
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "image_url": "https://cdn.example.com/images/xxx.png",
    "credits_used": 20
  }
}
```

---

## 5. 视频生成接口

### 5.1 生成视频
```http
POST /api/v1/video/generate
```

**请求体：**
```json
{
  "script": "视频脚本内容",
  "duration": 30,
  "model_id": 3
}
```

**响应：**
```json
{
  "code": 200,
  "message": "任务已创建",
  "data": {
    "task_id": "video_task_123",
    "status": "processing"
  }
}
```

### 5.2 获取视频生成状态
```http
GET /api/v1/video/{task_id}/status
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "video_task_123",
    "status": "completed",
    "video_url": "https://cdn.example.com/videos/xxx.mp4",
    "credits_used": 50
  }
}
```

---

## 6. PPT生成接口

### 6.1 生成PPT
```http
POST /api/v1/ppt/generate
```

**请求体：**
```json
{
  "topic": "产品发布会",
  "outline": ["产品介绍", "核心功能", "市场分析"],
  "model_id": 4
}
```

**响应：**
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "ppt_id": 456,
    "download_url": "https://cdn.example.com/ppt/xxx.pptx",
    "credits_used": 30
  }
}
```

---

## 7. 创作记录接口

### 7.1 获取创作列表
```http
GET /api/v1/creations?page=1&page_size=20&type=writing
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 123,
        "type": "writing",
        "tool_type": "wechat_article",
        "title": "如何提高工作效率",
        "content": "文章内容...",
        "created_at": "2026-01-22T10:00:00"
      }
    ]
  }
}
```

### 7.2 获取创作详情
```http
GET /api/v1/creations/{id}
```

### 7.3 更新创作内容
```http
PUT /api/v1/creations/{id}
```

**请求体：**
```json
{
  "title": "新标题",
  "content": "更新后的内容"
}
```

### 7.4 删除创作
```http
DELETE /api/v1/creations/{id}
```

---

## 8. 发布管理接口

### 8.1 发布内容
```http
POST /api/v1/publish
```

**请求体：**
```json
{
  "creation_id": 123,
  "platforms": ["wechat", "xiaohongshu"],
  "schedule_time": "2026-01-23T10:00:00"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "发布任务已创建",
  "data": {
    "publish_id": 789,
    "status": "pending"
  }
}
```

### 8.2 获取支持的平台列表
```http
GET /api/v1/publish/platforms
```

### 8.3 绑定平台账号
```http
POST /api/v1/publish/platforms/bind
```

**请求体：**
```json
{
  "platform": "wechat",
  "credentials": {
    "app_id": "xxx",
    "app_secret": "xxx"
  }
}
```

### 8.4 获取发布历史
```http
GET /api/v1/publish/history?page=1&page_size=20
```

---

## 9. 运营管理接口

### 9.1 创建活动
```http
POST /api/v1/operation/activities
```

**请求体：**
```json
{
  "name": "新用户注册送积分",
  "type": "credit_gift",
  "description": "新用户注册即送100积分",
  "config": {
    "credits": 100
  },
  "start_time": "2026-01-22T00:00:00",
  "end_time": "2026-02-22T23:59:59"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "活动创建成功",
  "data": {
    "id": 1,
    "name": "新用户注册送积分",
    "status": "active"
  }
}
```

### 9.2 获取活动列表
```http
GET /api/v1/operation/activities?status=active&page=1&page_size=20
```

### 9.3 参与活动
```http
POST /api/v1/operation/activities/{activity_id}/participate
```

### 9.4 创建优惠券
```http
POST /api/v1/operation/coupons
```

**请求体：**
```json
{
  "code": "DISCOUNT10",
  "name": "充值优惠券",
  "type": "discount",
  "value": 10.0,
  "min_amount": 100.0,
  "max_usage": 1000,
  "valid_from": "2026-01-22T00:00:00",
  "valid_until": "2026-02-22T23:59:59"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "优惠券创建成功",
  "data": {
    "id": 1,
    "code": "DISCOUNT10",
    "status": "active"
  }
}
```

### 9.5 获取优惠券列表
```http
GET /api/v1/operation/coupons?status=active&page=1&page_size=20
```

### 9.6 领取优惠券
```http
POST /api/v1/operation/coupons/{coupon_id}/claim
```

### 9.7 获取我的优惠券
```http
GET /api/v1/operation/my-coupons?status=unused
```

### 9.8 生成推荐码
```http
POST /api/v1/operation/referral/generate
```

**响应：**
```json
{
  "code": 200,
  "message": "推荐码已生成",
  "data": {
    "referral_code": "ABC123",
    "referral_url": "https://example.com/register?ref=ABC123"
  }
}
```

### 9.9 获取推荐记录
```http
GET /api/v1/operation/referral/records?page=1&page_size=20
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "total_rewards": 500,
    "items": [
      {
        "id": 1,
        "referred_user": "user123",
        "reward_amount": 50,
        "status": "completed",
        "created_at": "2026-01-22T10:00:00"
      }
    ]
  }
}
```

### 9.10 获取运营统计
```http
GET /api/v1/operation/statistics?start_date=2026-01-01&end_date=2026-01-31
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 10000,
    "new_users": 500,
    "total_revenue": 50000.00,
    "total_credits_sold": 500000,
    "active_members": 1000,
    "conversion_rate": 0.15
  }
}
```

---

## 10. AI模型管理接口

### 10.1 获取AI模型列表
```http
GET /api/v1/models?provider=qwen&is_active=true
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "通义千问Max",
      "provider": "qwen",
      "model_name": "qwen-max",
      "is_active": true,
      "credits_cost": 10
    }
  ]
}
```

### 10.2 添加AI模型配置
```http
POST /api/v1/models
```

**请求体：**
```json
{
  "name": "通义千问Plus",
  "provider": "qwen",
  "model_name": "qwen-plus",
  "api_key": "sk-xxx",
  "api_base": "https://dashscope.aliyuncs.com/api/v1",
  "config": {
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "credits_cost": 8
}
```

### 10.3 更新AI模型配置
```http
PUT /api/v1/models/{id}
```

### 10.4 删除AI模型配置
```http
DELETE /api/v1/models/{id}
```

---

## 附录

### A. 写作工具类型
- `wechat_article`: 公众号文章
- `xiaohongshu_note`: 小红书笔记
- `official_document`: 公文写作
- `academic_paper`: 论文写作
- `marketing_copy`: 营销文案
- `news_article`: 新闻稿/软文
- `video_script`: 短视频脚本
- `story_novel`: 故事/小说
- `business_plan`: 商业计划书
- `work_report`: 工作报告
- `resume`: 简历/求职信
- `lesson_plan`: 教案/课件
- `content_rewrite`: 内容改写
- `translation`: 多语言翻译

### B. 活动类型
- `credit_gift`: 积分赠送
- `membership_discount`: 会员折扣
- `referral_bonus`: 推荐奖励
- `first_purchase`: 首次购买优惠

### C. 优惠券类型
- `discount`: 折扣券（百分比）
- `deduction`: 抵扣券（固定金额）
- `credit_bonus`: 积分加赠

### D. 会员类型
- `monthly`: 月度会员（9.9元/月）
- `quarterly`: 季度会员（25元/季）
- `yearly`: 年度会员（99元/年）

### E. 支付方式
- `alipay`: 支付宝
- `wechat`: 微信支付
- `balance`: 余额支付

### F. 发布平台
- `wechat`: 微信公众号
- `xiaohongshu`: 小红书
- `douyin`: 抖音
- `kuaishou`: 快手
- `toutiao`: 今日头条

### G. 错误码详细说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | 积分不足 | 请充值积分或购买会员 |
| 40002 | 会员已过期 | 请续费会员 |
| 40003 | 优惠券无效 | 检查优惠券状态和有效期 |
| 40004 | 订单不存在 | 检查订单ID是否正确 |
| 40005 | 支付失败 | 重试支付或联系客服 |
| 40006 | AI服务调用失败 | 稍后重试或更换模型 |
| 40007 | 内容生成失败 | 检查输入参数或重试 |
| 40008 | 平台账号未绑定 | 先绑定平台账号 |
| 40009 | 发布失败 | 检查平台规则或重试 |
| 40010 | 活动已结束 | 查看其他活动 |

### H. 请求频率限制

| 接口类型 | 限制 |
|---------|------|
| 认证接口 | 10次/分钟 |
| AI生成接口 | 会员：无限制<br>非会员：20次/小时 |
| 查询接口 | 100次/分钟 |
| 其他接口 | 60次/分钟 |

### I. 最佳实践

1. **Token管理**
   - 访问令牌有效期2小时，刷新令牌有效期7天
   - 在访问令牌过期前使用刷新令牌获取新的访问令牌
   - 安全存储Token，不要在客户端明文存储

2. **错误处理**
   - 始终检查响应的code字段
   - 根据错误码进行相应的错误处理
   - 对于5xx错误，实施重试机制（指数退避）

3. **积分消费**
   - 生成前检查用户积分余额或会员状态
   - 会员用户优先使用会员权益（不扣积分）
   - 生成失败会自动退还积分

4. **异步任务**
   - 视频生成等耗时任务采用异步处理
   - 定期轮询任务状态或使用WebSocket接收通知
   - 任务完成后及时获取结果

5. **分页查询**
   - 使用page和page_size参数进行分页
   - 默认page_size为20，最大100
   - 响应中包含total字段表示总记录数

6. **日期时间**
   - 所有时间使用ISO 8601格式
   - 时区为UTC+8（北京时间）
   - 示例：2026-01-22T10:00:00

---

## 示例代码

### Python示例

```python
import requests

# 基础配置
BASE_URL = "http://localhost:8000"
headers = {}

# 1. 用户登录
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    data = response.json()
    if data["code"] == 200:
        token = data["data"]["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        return token
    return None

# 2. 生成文章
def generate_article(title, keywords):
    response = requests.post(
        f"{BASE_URL}/api/v1/writing/wechat_article/generate",
        headers=headers,
        json={
            "title": title,
            "keywords": keywords,
            "requirements": "字数2000字",
            "model_id": 1
        }
    )
    return response.json()

# 3. 充值积分
def recharge(amount):
    response = requests.post(
        f"{BASE_URL}/api/v1/credit/recharge",
        headers=headers,
        json={
            "amount": amount,
            "payment_method": "alipay"
        }
    )
    return response.json()

# 使用示例
token = login("testuser", "password123")
if token:
    result = generate_article("如何提高工作效率", ["时间管理", "效率工具"])
    print(result)
```

### JavaScript示例

```javascript
const BASE_URL = 'http://localhost:8000';
let token = '';

// 1. 用户登录
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  if (data.code === 200) {
    token = data.data.access_token;
    return token;
  }
  return null;
}

// 2. 生成文章
async function generateArticle(title, keywords) {
  const response = await fetch(
    `${BASE_URL}/api/v1/writing/wechat_article/generate`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        title,
        keywords,
        requirements: '字数2000字',
        model_id: 1
      })
    }
  );
  return await response.json();
}

// 3. 获取积分余额
async function getBalance() {
  const response = await fetch(`${BASE_URL}/api/v1/credit/balance`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 使用示例
(async () => {
  await login('testuser', 'password123');
  const result = await generateArticle('如何提高工作效率', ['时间管理', '效率工具']);
  console.log(result);
})();
```

---

## 更新日志

### v1.0.0 (2026-01-22)
- 初始版本发布
- 支持阿里通义千问模型
- 实现积分和会员系统
- 实现运营管理功能
- 14个AI写作工具
- 图片、视频、PPT生成功能
- 多平台发布功能

---

## 技术支持

如有问题，请联系：
- 邮箱：support@example.com
- 文档：https://docs.example.com
- GitHub：https://github.com/yourusername/ai-creator
