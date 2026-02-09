# 豆包适配器修改总结

## 修改日期
2026-02-09

## 修改分支
`feature/proxycast-style-credential-provider`

## 修改内容

### 1. 借鉴 doubao-free-api 项目
参考了已归档的开源项目 [LLM-Red-Team/doubao-free-api](https://github.com/LLM-Red-Team/doubao-free-api)，该项目使用逆向工程实现了豆包网页版的 API 调用。

### 2. 主要改动

#### 2.1 更新 API 端点
- **旧端点**: `/api/chat/completions` ❌（不正确）
- **新端点**: `/samantha/chat/completion` ✅（正确的内部 API）

#### 2.2 添加伪装机制

##### msToken 生成
```python
def generate_fake_ms_token() -> str:
    """生成伪造的 msToken (128字符)"""
    random_bytes = secrets.token_bytes(96)
    ms_token = base64.b64encode(random_bytes).decode('utf-8')
    ms_token = ms_token.replace('+', '-').replace('/', '_').replace('=', '')
    return ms_token
```

##### a_bogus 签名生成
```python
def generate_fake_a_bogus() -> str:
    """生成伪造的 a_bogus 签名"""
    part1 = ''.join(secrets.choice(charset) for _ in range(34))
    part2 = ''.join(secrets.choice(charset) for _ in range(6))
    return f"mf-{part1}-{part2}"
```

#### 2.3 完整的 Cookie 构建

原来的简单 Cookie：
```python
Cookie: sessionid=xxx; sessionid_ss=yyy
```

修改后的完整 Cookie：
```python
Cookie: is_staff_user=false; store-region=cn-gd; sid_guard=xxx; 
        uid_tt=yyy; sessionid=xxx; sessionid_ss=yyy; msToken=zzz; ...
```

#### 2.4 完善请求头伪装

新增的关键请求头：
```python
{
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Agw-Js-Conv": "str",
    "X-Flow-Trace": "04-{uuid}-{uuid}-01",
}
```

#### 2.5 更新请求参数

新增的查询参数（参考 doubao-free-api）：
```python
params = {
    "aid": "497858",
    "device_id": "{random_id}",
    "device_platform": "web",
    "language": "zh",
    "pkg_type": "release_version",
    "real_aid": "497858",
    "region": "CN",
    "samantha_web": 1,
    "sys_region": "CN",
    "tea_uuid": "{web_id}",
    "use_olympus_account": 1,
    "version_code": "20800",
    "web_id": "{web_id}",
    "msToken": "{ms_token}",
    "a_bogus": "{a_bogus}",
}
```

#### 2.6 更新请求体格式

原来的请求体：
```python
{
    "conversation_id": "...",
    "bot_id": "...",
    "user_input": "...",
    "stream": True
}
```

修改后的请求体（符合内部 API 格式）：
```python
{
    "messages": [
        {
            "content": json.dumps({"text": message}),
            "content_type": 2001,
            "attachments": [],
            "references": [],
        }
    ],
    "completion_option": {
        "is_regen": False,
        "with_suggest": True,
        "need_create_conversation": True,
        "launch_stage": 1,
        "is_replace": False,
        "is_delete": False,
        "message_from": 0,
        "event_id": "0"
    },
    "conversation_id": "0",
    "local_conversation_id": "local_16...",
    "local_message_id": "{uuid}"
}
```

#### 2.7 添加会话清理功能

新增 `remove_conversation()` 方法，在对话完成后自动删除会话，避免污染用户的会话列表。

```python
async def remove_conversation(
    self, 
    conversation_id: str, 
    cookies: Dict[str, str]
) -> bool:
    """删除会话"""
    # 调用 /samantha/thread/delete 端点
    ...
```

### 3. 修改的文件

```
backend/app/services/oauth/adapters/doubao.py  (352 行 → 609 行)
backend/test_doubao_adapter.py                  (新增，测试脚本)
docs/DOUBAO_ADAPTER_CHANGES.md                  (本文档)
```

### 4. 测试方法

运行测试脚本：
```bash
cd backend
python test_doubao_adapter.py
```

测试内容：
- ✅ msToken 生成（128字符）
- ✅ a_bogus 生成（格式正确）
- ✅ Cookie 构建（包含所有必要字段）
- ✅ LiteLLM 配置（正确的端点）
- ✅ 请求头伪装（完整的浏览器指纹）

### 5. 风险提示

| 风险 | 级别 | 说明 |
|------|------|------|
| **API 随时失效** | 🔴 高 | doubao-free-api 已归档，说明可能已被封堵 |
| **违反服务条款** | 🔴 高 | 逆向工程违反豆包使用条款 |
| **账号封禁风险** | 🟡 中 | 频繁调用可能导致账号被封 |
| **不适合商用** | 🔴 高 | 仅供个人学习测试 |

### 6. 推荐方案

对于 SaaS 服务，**强烈推荐使用官方 API**：

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **火山引擎官方 API** | 稳定、合法、支持商用 | 需要付费 | ⭐⭐⭐⭐⭐ |
| **逆向 Cookie 方案** | 免费 | 不稳定、违反条款、随时失效 | ⭐⭐ |

官方 API 地址：https://www.volcengine.com/product/doubao

### 7. 对比：你的项目 vs ProxyCast

| 方面 | 你的项目 | ProxyCast |
|------|---------|-----------|
| **架构** | FastAPI + Vue (Web SaaS) | Tauri (桌面应用) |
| **凭证来源** | 用户手动提交 Cookie | 读取本地文件 |
| **适用场景** | 多用户 SaaS 服务 | 个人桌面工具 |
| **Cookie 方案** | ✅ 适合 | ❌ 不适合 |
| **API Key 方案** | ✅ 最适合 | ✅ 适合 |
| **本地凭证读取** | ❌ 无法实现（SaaS限制） | ✅ 核心功能 |

### 8. 下一步建议

#### 短期（测试验证）
1. 运行测试脚本验证逻辑正确性
2. 使用真实 sessionid 进行小规模测试
3. 监控 API 调用成功率

#### 中期（功能完善）
1. 同时支持 Cookie 方案（测试）+ API Key 方案（商用）
2. 添加请求频率限制，降低封号风险
3. 实现自动凭证健康检查

#### 长期（商业化）
1. **迁移到火山引擎官方 API**（强烈推荐）
2. 为用户提供 API Key 接入指南
3. Cookie 方案仅作为备选或测试功能

---

## 参考资料

- doubao-free-api 项目：https://github.com/LLM-Red-Team/doubao-free-api
- 火山引擎豆包官方文档：https://www.volcengine.com/docs/82379
- ProxyCast 项目：https://github.com/aiclientproxy/proxycast

---

## 修改人
AI Assistant (OpenCode)

## 审核状态
⏳ 待测试验证
