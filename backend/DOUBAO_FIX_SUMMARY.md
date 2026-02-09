# 豆包 API 错误修复总结

## 修复的问题

### 1. KeyError: 'target_audience'
**文件**: `backend/app/services/writing_service.py`

**问题描述**:
写作服务在格式化提示词时要求所有参数必须存在，但用户可能只提供部分参数，导致 KeyError。

**解决方案**:
添加了 `TOOL_DEFAULTS` 字典，为每种写作工具类型定义默认参数值。修改参数处理逻辑：

```python
# 合并用户输入和默认值
defaults = cls.TOOL_DEFAULTS.get(tool_type, {})
merged_input = {**defaults, **user_input}  # 用户输入会覆盖默认值
```

**支持的工具类型默认参数**:
- `wechat_article`: topic, keywords, target_audience, style
- `xiaohongshu_note`: topic, keywords, note_type
- `official_document`: doc_type, topic, issuer, receiver, content
- `academic_paper`: title, field, method, main_points
- `marketing_copy`: product, target_customer, selling_points, goal
- `news_article`: topic, news_type, key_info
- `video_script`: topic, duration, platform, style
- `story_novel`: genre, theme, characters, setting
- `business_plan`: project_name, industry, business_model, target_market
- `work_report`: report_type, period, main_work, achievements
- `resume`: name, position, experience, education, skills
- `rewrite`: original_text, rewrite_type, target_style
- `translation`: source_text, source_lang, target_lang, style

---

### 2. HTTPStatusError: Client error '400 Bad Request'
**文件**: `backend/app/services/ai/doubao_service.py`

**问题描述**:
豆包 API 需要特定的请求格式，包括复杂的查询参数和消息负载结构，原代码使用了简化的格式导致 400 错误。

**解决方案**:

#### 2.1 添加必需的类属性和初始化
```python
DEFAULT_ASSISTANT_ID = "497858"
VERSION_CODE = "20800"

def __init__(self, cookies: Dict[str, str], user_agent: Optional[str] = None):
    super().__init__(cookies, user_agent)
    self.device_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
    self.web_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
```

#### 2.2 添加辅助方法
- `generate_fake_ms_token()`: 生成 128 字符的 msToken
- `generate_fake_a_bogus()`: 生成签名参数
- `generate_local_ids()`: 生成会话和消息 ID

#### 2.3 更新请求格式
**新的消息负载格式**:
```python
message_payload = {
    "content": prompt,
    "content_type": 2001,
    "role": "user",
    "create_time": int(time.time()),
    "sender_role": 0,
    "is_finish": True,
    "is_stop": False,
    "is_replace": False,
    "is_delete": False,
    "message_from": 0,
    "event_id": "0"
}

payload = {
    "message": message_payload,
    "conversation_id": conversation_id or "0",
    "local_conversation_id": local_conv_id,
    "local_message_id": local_msg_id
}
```

**查询参数**:
```python
params = {
    "aid": self.DEFAULT_ASSISTANT_ID,
    "device_id": self.device_id,
    "device_platform": "web",
    "language": "zh",
    "pkg_type": "release_version",
    "real_aid": self.DEFAULT_ASSISTANT_ID,
    "region": "CN",
    "samantha_web": 1,
    "sys_region": "CN",
    "tea_uuid": self.web_id,
    "use_olympus_account": 1,
    "version_code": self.VERSION_CODE,
    "web_id": self.web_id,
    "msToken": ms_token,
    "a_bogus": a_bogus,
}
```

#### 2.4 实现 SSE 流式响应解析
```python
# 解析 SSE 流响应
lines = response.text.strip().split("\n")
for line in lines:
    if line.startswith("data:"):
        data_str = line[5:].strip()
        if data_str and data_str != "[DONE]":
            raw_result = json.loads(data_str)
            
            # event_type == 2001 表示消息内容
            if raw_result.get("event_type") == 2001:
                event_data = json.loads(raw_result.get("event_data", "{}"))
                message_data = event_data.get("message", {})
                if message_data.get("content_type") in [2001, 2008]:
                    content_obj = json.loads(message_data.get("content", "{}"))
                    if "text" in content_obj:
                        result_text += content_obj["text"]
```

---

## 测试结果

### 基础功能测试
运行 `python3 backend/test_doubao_service.py` 的结果：

```
✅ 测试结果总结:
  1. DoubaoService 基础功能 - 正常
  2. 辅助方法（msToken, a_bogus, local_ids）- 正常
  3. 请求头构建 - 正常
  4. WritingService 默认参数 - 正常
  5. 参数合并逻辑 - 正常
```

### 真实 API 测试
使用 `python3 backend/test_doubao_api_real.py` 进行真实 Cookie 测试：

**步骤**:
1. 登录豆包网页版 (https://www.doubao.com)
2. 打开浏览器开发者工具 (F12)
3. 找到 Cookie 中的 `sessionid` 和 `sessionid_ss`
4. 在脚本中填入 Cookie 值
5. 运行测试

---

## API 使用示例

### 1. 使用默认参数
```bash
POST /v1/writing/generate
Content-Type: application/json

{
  "tool_type": "wechat_article",
  "parameters": {
    "topic": "人工智能的未来"
  },
  "platform": "doubao"
}
```

系统会自动应用默认值:
- `keywords`: "暂无关键词"
- `target_audience`: "广大读者"
- `style`: "轻松活泼"

### 2. 覆盖默认参数
```bash
POST /v1/writing/generate
Content-Type: application/json

{
  "tool_type": "wechat_article",
  "parameters": {
    "topic": "人工智能的未来",
    "keywords": "AI,机器学习,深度学习",
    "target_audience": "科技爱好者",
    "style": "专业严谨"
  },
  "platform": "doubao"
}
```

### 3. 其他写作工具
```bash
# 小红书笔记
POST /v1/writing/generate
{
  "tool_type": "xiaohongshu_note",
  "parameters": {
    "topic": "美食分享",
    "keywords": "好吃,推荐"
  },
  "platform": "doubao"
}

# 营销文案
POST /v1/writing/generate
{
  "tool_type": "marketing_copy",
  "parameters": {
    "product": "智能手表",
    "target_customer": "年轻白领"
  },
  "platform": "doubao"
}
```

---

## 注意事项

1. **Cookie 有效期**: 豆包的 Cookie 会过期，需要定期更新
2. **请求频率**: 避免频繁请求，建议添加请求间隔
3. **错误处理**: API 可能返回各种错误，需要妥善处理
4. **风控机制**: 频繁或异常请求可能触发风控

---

## 相关文件

修改的文件:
- `backend/app/services/writing_service.py`
- `backend/app/services/ai/doubao_service.py`

测试文件:
- `backend/test_doubao_service.py` - 基础功能测试
- `backend/test_doubao_api_real.py` - 真实 API 测试

---

## 下一步建议

1. ✅ 基础功能测试通过
2. 🔄 使用真实 Cookie 测试实际 API 调用
3. 🔄 前端集成测试
4. 🔄 监控 API 响应和成功率
5. 🔄 观察是否触发风控机制
6. 📝 考虑迁移到火山引擎官方 API（长期）

---

**修复完成时间**: 2026-02-09  
**测试状态**: 基础功能测试通过 ✅  
**待测试**: 真实 Cookie API 调用 🔄
