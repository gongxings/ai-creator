# OAuth功能单元测试

## 测试概述

本目录包含OAuth功能的完整单元测试，覆盖以下模块：

- **OAuth服务测试** (`test_oauth_service.py`)
  - 平台管理
  - 账号管理
  - Cookie加密解密
  - Playwright浏览器自动化

- **OAuth API测试** (`test_oauth_api.py`)
  - 平台API端点
  - 账号API端点
  - OAuth流程API
  - LiteLLM代理API

## 安装测试依赖

```bash
cd backend
pip install -r requirements-test.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_oauth_service.py
pytest tests/test_oauth_api.py
```

### 运行特定测试类
```bash
pytest tests/test_oauth_service.py::TestOAuthService
pytest tests/test_oauth_api.py::TestOAuthAPI
```

### 运行特定测试方法
```bash
pytest tests/test_oauth_service.py::TestOAuthService::test_get_platforms
```

### 查看测试覆盖率
```bash
pytest --cov=app --cov-report=html
```

覆盖率报告将生成在 `htmlcov/index.html`

### 详细输出
```bash
pytest -v -s
```

### 只运行失败的测试
```bash
pytest --lf
```

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # Pytest配置和fixtures
├── test_oauth_service.py    # OAuth服务测试
├── test_oauth_api.py        # OAuth API测试
└── README.md                # 本文件
```

## Fixtures说明

### 数据库Fixtures
- `engine`: 测试数据库引擎（session级别）
- `db_session`: 测试数据库会话（function级别）
- `client`: FastAPI测试客户端

### 测试数据Fixtures
- `test_user`: 测试用户
- `test_platform`: 测试平台配置
- `test_oauth_account`: 测试OAuth账号
- `auth_headers`: 认证请求头

### Mock Fixtures
- `mock_playwright`: Mock的Playwright对象

## 测试覆盖范围

### OAuth服务测试
- ✅ 获取平台列表
- ✅ 根据ID获取平台
- ✅ 获取用户账号列表
- ✅ 根据ID获取账号
- ✅ 创建OAuth账号
- ✅ 更新账号Cookie
- ✅ 删除账号
- ✅ 检查账号有效性
- ✅ 获取账号Cookie
- ✅ 数据加密解密

### OAuth API测试
- ✅ 获取平台列表API
- ✅ 获取平台详情API
- ✅ 获取用户账号列表API
- ✅ 获取账号详情API
- ✅ 启动OAuth流程API
- ✅ 执行OAuth操作API
- ✅ 完成OAuth流程API
- ✅ 删除账号API
- ✅ 检查账号有效性API
- ✅ 聊天完成API
- ✅ 错误处理测试

## 注意事项

1. **测试数据库**
   - 使用SQLite内存数据库进行测试
   - 每个测试函数都会回滚数据库事务
   - 测试结束后自动清理数据库文件

2. **Mock对象**
   - Playwright相关操作使用Mock对象
   - LiteLLM API调用使用Mock对象
   - 避免实际的网络请求和浏览器操作

3. **异步测试**
   - 使用`@pytest.mark.asyncio`标记异步测试
   - 配置文件中已启用`asyncio_mode = auto`

4. **测试隔离**
   - 每个测试函数独立运行
   - 使用fixtures确保测试数据隔离
   - 避免测试之间的相互影响

## 持续集成

可以在CI/CD流程中集成测试：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 故障排查

### 测试失败
1. 检查数据库连接配置
2. 确认所有依赖已安装
3. 查看详细错误信息：`pytest -v -s`

### 导入错误
1. 确认项目根目录在Python路径中
2. 检查`conftest.py`中的路径配置

### 异步测试问题
1. 确认已安装`pytest-asyncio`
2. 检查`pytest.ini`中的`asyncio_mode`配置

## 扩展测试

添加新测试时：

1. 在相应的测试文件中添加测试类或方法
2. 使用现有的fixtures或创建新的fixtures
3. 遵循命名规范：`test_*`
4. 添加清晰的文档字符串
5. 确保测试独立且可重复运行

## 参考资料

- [Pytest文档](https://docs.pytest.org/)
- [FastAPI测试](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy测试](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
