# 管理员账号登录问题修复说明

## 问题描述
管理员账号登录时出现 500 Internal Server Error，错误发生在密码验证环节。

## 错误原因
`passlib 1.7.4` 与 `bcrypt 5.0.0` 存在兼容性问题，导致密码验证时抛出异常：
```
ValueError: password cannot be longer than 72 bytes
```

## 解决方案
修改 `backend/app/core/security.py`，将密码加密和验证改为直接使用 `bcrypt` 库，而不是通过 `passlib`。

### 修改内容

**修改前：**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

**修改后：**
```python
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
```

## 测试结果

### 1. 密码验证测试
```bash
cd backend
python test_login.py
```

输出：
```
用户找到: admin
存储的密码哈希: $2b$12$GeSP7DrBzGF9JqkdNS6Iqu6GViKpd2qafYLuT732omjDrRjzj38Uu
状态: UserStatus.ACTIVE
状态类型: <enum 'UserStatus'>

测试密码验证...
密码验证结果: True

状态检查:
user.status != 'active': False
user.status == 'active': True
```

✅ 密码验证成功

### 2. 管理员账号信息
```
用户名: admin
密码: admin123456
邮箱: admin@example.com
角色: ADMIN
积分: 1000
会员状态: 已开通
会员到期时间: 2027-02-06
```

## 使用说明

### 启动服务器
```bash
cd backend
uvicorn app.main:app --reload
```

### 登录测试
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}'
```

预期响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "expires_in": 7200,
    "user": {
      "id": 8,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      ...
    }
  }
}
```

## 注意事项

1. ⚠️ **安全警告：** 在生产环境中，请立即修改默认密码！

2. 如果之前使用 `passlib` 创建的密码哈希，现在也能正常验证（因为都是 bcrypt 格式）

3. 该修复对所有用户账号都适用，不仅限于管理员账号

## 相关文件
- `backend/app/core/security.py` - 密码加密和验证函数
- `backend/scripts/create_admin.py` - 创建管理员账号脚本
- `backend/app/api/v1/auth.py` - 登录接口

## 后续建议
建议在 `requirements.txt` 中明确指定 bcrypt 版本以避免未来的兼容性问题：
```txt
bcrypt==5.0.0
```

或者降级使用更稳定的版本：
```txt
bcrypt==4.0.1
passlib==1.7.4
```
