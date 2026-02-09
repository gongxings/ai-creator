# LLM-Red-Team 项目借鉴方案

## 项目概览

LLM-Red-Team 是一个专注于 AI 大模型逆向 API 的开源组织，提供了多个平台的免费 API 封装。

**重要提示**：这些项目均已归档（Archived），说明可能已被官方封堵，仅供学习参考。

---

## 已支持平台对比

### 你的项目现状

| 平台 | 适配器文件 | 状态 | 备注 |
|------|-----------|------|------|
| 通义千问 (Qwen) | `qwen.py` | ✅ 已支持 | 需参考 qwen-free-api 优化 |
| 智谱 AI (GLM) | `zhipu.py` | ✅ 已支持 | 需参考 glm-free-api 优化 |
| 豆包 (Doubao) | `doubao.py` | ✅ 刚修复 | 已参考 doubao-free-api |
| 百度文心 (Baidu) | `baidu.py` | ✅ 已支持 | 基础实现 |
| 讯飞星火 (Spark) | `spark.py` | ✅ 已支持 | 基础实现 |
| Claude | `claude.py` | ✅ 已支持 | 基础实现 |
| OpenAI | `openai.py` | ✅ 已支持 | 基础实现 |
| Gemini | `gemini.py` | ✅ 已支持 | 基础实现 |

### 可以新增的平台

| LLM-Red-Team 项目 | Stars | 状态 | 建议优先级 | 理由 |
|------------------|-------|------|-----------|------|
| **kimi-free-api** | 4.7k | 归档 | 🔴 高 | 长文本处理能力强，用户需求大 |
| **deepseek-free-api** | 2.8k | 归档 | 🟡 中 | DeepSeek 官方 API 很便宜，建议直接用官方 |
| **minimax-free-api** | 457 | 归档 | 🟢 低 | 海螺 AI，语音合成特色功能 |
| **step-free-api** | 247 | 归档 | 🟢 低 | 阶跃星辰，多模态能力 |
| **jimeng-free-api** | 1k | 归档 | 🟡 中 | 图像生成专用，如需图像功能可添加 |

---

## 推荐实施方案

### 方案 A：保守方案（推荐用于 SaaS）

**仅优化现有适配器，不新增平台**

| 任务 | 优先级 | 说明 |
|------|--------|------|
| 优化通义千问适配器 | 🔴 高 | 参考 qwen-free-api |
| 优化智谱适配器 | 🔴 高 | 参考 glm-free-api |
| 所有平台添加 API Key 支持 | 🔴 高 | 双轨制：Cookie + API Key |
| 完善错误处理 | 🟡 中 | 统一异常处理 |
| 添加速率限制 | 🟡 中 | 防止触发风控 |

**优点**：
- ✅ 稳定性高
- ✅ 维护成本低
- ✅ 适合商业化

**缺点**：
- ❌ 功能相对保守

---

### 方案 B：激进方案（仅供测试）

**新增 Kimi、DeepSeek 等热门平台**

| 任务 | 工作量 | 风险 |
|------|--------|------|
| 新增 Kimi 适配器 | 中 | 高（项目已归档） |
| 新增 DeepSeek 适配器 | 中 | 中（官方 API 便宜） |
| 新增 MiniMax 适配器 | 低 | 高（项目已归档） |
| 新增 Step 适配器 | 低 | 高（项目已归档） |

**优点**：
- ✅ 功能丰富
- ✅ 用户选择多

**缺点**：
- ❌ 维护成本极高
- ❌ 随时可能失效
- ❌ 不适合商用

---

## 详细实施指南

### 1. 优化通义千问适配器（推荐）

#### 参考项目
[qwen-free-api](https://github.com/LLM-Red-Team/qwen-free-api)

#### 需要借鉴的技术点

```python
# backend/app/services/oauth/adapters/qwen.py

class QwenAdapter(PlatformAdapter):
    """通义千问适配器 - 优化版"""
    
    # 1. 完整的 Cookie 构建
    def build_complete_cookie(self, credentials):
        cookies = credentials.get("cookies", {})
        return "; ".join([
            f"tongyi_sso_ticket={cookies.get('tongyi_sso_ticket')}",
            f"cna={cookies.get('cna', '')}",
            f"isg={cookies.get('isg', '')}",
            # ... 其他可选 Cookie
        ])
    
    # 2. 正确的 API 端点
    API_ENDPOINT = "https://www.qianwen.com/api/chat/completions"
    
    # 3. 请求签名（如有）
    def generate_signature(self, timestamp, nonce):
        # 参考 qwen-free-api 的签名算法
        pass
    
    # 4. 会话管理
    async def remove_conversation(self, conv_id, cookies):
        # 自动清理会话
        pass
```

#### 优化重点
- [ ] 更新 API 端点
- [ ] 完善 Cookie 字段
- [ ] 添加请求签名（如需要）
- [ ] 实现会话清理
- [ ] 增加错误重试机制

---

### 2. 优化智谱 AI 适配器（推荐）

#### 参考项目
[glm-free-api](https://github.com/LLM-Red-Team/glm-free-api)

#### 需要借鉴的技术点

```python
# backend/app/services/oauth/adapters/zhipu.py

class ZhipuAdapter(PlatformAdapter):
    """智谱 AI 适配器 - 优化版"""
    
    # 1. 支持多种模型
    SUPPORTED_MODELS = [
        "glm-4-plus",
        "glm-4-air",
        "glm-4-flashx",
        "glm-zero",  # 思考模型
    ]
    
    # 2. 完整的请求格式
    def build_request_body(self, message, model="glm-4-plus"):
        return {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": True,
            "tools": [],  # 支持工具调用
        }
    
    # 3. SSE 流解析
    async def parse_sse_stream(self, response):
        # 解析 Server-Sent Events
        pass
```

#### 优化重点
- [ ] 支持更多模型
- [ ] 添加工具调用支持
- [ ] 优化流式响应解析
- [ ] 添加图像生成支持（如需要）

---

### 3. 新增 Kimi 适配器（可选）

#### 参考项目
[kimi-free-api](https://github.com/LLM-Red-Team/kimi-free-api)

#### 实施步骤

**步骤 1：创建适配器文件**
```bash
backend/app/services/oauth/adapters/kimi.py
```

**步骤 2：实现核心功能**
```python
class KimiAdapter(PlatformAdapter):
    """Kimi AI 适配器"""
    
    API_ENDPOINT = "https://kimi.moonshot.cn/api/chat/completion"
    
    def get_oauth_url(self) -> str:
        return "https://kimi.moonshot.cn/"
    
    def get_cookie_names(self) -> list:
        return [
            "refresh_token",
            "access_token",
        ]
    
    async def send_message(self, message, cookies):
        # 参考 kimi-free-api 实现
        pass
```

**步骤 3：注册适配器**
```python
# backend/app/services/oauth/oauth_service.py

PLATFORM_ADAPTERS = {
    # ... 现有适配器
    'kimi': KimiAdapter,  # 新增
}
```

**步骤 4：更新数据库配置**
```sql
INSERT INTO platform_configs (platform_id, platform_name, is_enabled)
VALUES ('kimi', 'Kimi AI', TRUE);
```

#### 风险评估
| 风险 | 级别 | 说明 |
|------|------|------|
| API 失效 | 🔴 高 | 项目已归档 |
| 账号封禁 | 🟡 中 | 频繁调用可能触发风控 |
| 法律风险 | 🔴 高 | 违反服务条款 |

---

### 4. 新增 DeepSeek 适配器（可选）

#### 参考项目
[deepseek-free-api](https://github.com/LLM-Red-Team/deepseek-free-api)

#### 特别说明
**DeepSeek 官方 API 非常便宜，强烈建议直接使用官方 API！**

| 模型 | 官方价格 | 性价比 |
|------|---------|--------|
| DeepSeek-V3 | ¥0.0007/千tokens | 极高 |
| DeepSeek-R1 | ¥0.55/百万tokens | 极高 |

**建议**：不要逆向 DeepSeek，直接引导用户使用官方 API Key。

---

## 双轨制实施方案

### Cookie 方案 + API Key 方案并存

```python
# backend/app/services/oauth/adapters/base.py

class PlatformAdapter(ABC):
    """平台适配器基类 - 支持双轨制"""
    
    def __init__(self, platform_id: str, config: Dict[str, Any]):
        self.platform_id = platform_id
        self.config = config
        self.auth_type = config.get("auth_type", "cookie")  # "cookie" | "api_key"
    
    async def send_message(self, message, credentials):
        """发送消息 - 根据凭证类型选择方法"""
        if self.auth_type == "api_key":
            return await self._send_with_api_key(message, credentials)
        else:
            return await self._send_with_cookie(message, credentials)
    
    @abstractmethod
    async def _send_with_cookie(self, message, cookies):
        """Cookie 方式发送消息"""
        pass
    
    @abstractmethod
    async def _send_with_api_key(self, message, api_key):
        """API Key 方式发送消息"""
        pass
```

### 前端选择界面

```vue
<!-- frontend/src/views/oauth/OAuthAccounts.vue -->

<template>
  <div>
    <el-radio-group v-model="authType">
      <el-radio label="cookie">Cookie 方式（免费，不稳定）</el-radio>
      <el-radio label="api_key">API Key 方式（付费，稳定）⭐推荐</el-radio>
    </el-radio-group>
    
    <div v-if="authType === 'cookie'">
      <el-alert type="warning">
        Cookie 方式基于逆向工程，可能随时失效，仅供测试使用
      </el-alert>
      <!-- Cookie 输入表单 -->
    </div>
    
    <div v-else>
      <el-alert type="success">
        API Key 方式稳定可靠，适合商业使用
      </el-alert>
      <!-- API Key 输入表单 -->
      <el-link href="https://官方API申请地址" target="_blank">
        去申请 API Key →
      </el-link>
    </div>
  </div>
</template>
```

---

## 实施时间表

### 第一阶段（1-2天） - 优化现有平台
- [x] 豆包适配器修复（已完成）
- [ ] 通义千问适配器优化
- [ ] 智谱 AI 适配器优化
- [ ] 测试所有现有适配器

### 第二阶段（3-5天） - 双轨制改造
- [ ] 修改适配器基类，支持双轨制
- [ ] 为所有平台添加 API Key 支持
- [ ] 前端界面改造
- [ ] 文档更新

### 第三阶段（可选，5-7天） - 新增平台
- [ ] 新增 Kimi 适配器（如需要）
- [ ] 新增 MiniMax 适配器（如需要）
- [ ] 全面测试
- [ ] 上线灰度测试

---

## 风险提示汇总

### Cookie 逆向方案风险

| 风险类别 | 风险级别 | 应对措施 |
|---------|---------|---------|
| API 随时失效 | 🔴 极高 | 定期监控，快速响应 |
| 账号封禁 | 🟡 中 | 添加速率限制，单账号单IP |
| 法律风险 | 🔴 高 | 免责声明，禁止商用 |
| 用户投诉 | 🟡 中 | 明确告知风险，推荐官方 API |

### 建议

1. **短期测试**：Cookie 方案用于演示和个人测试
2. **长期商用**：全部切换到官方 API Key
3. **用户引导**：前端明确提示风险，推荐官方 API
4. **法律保护**：添加完整的免责声明

---

## 官方 API 资源

| 平台 | 官方 API 文档 | 价格 |
|------|--------------|------|
| 豆包 | https://www.volcengine.com/docs/82379 | 按量付费 |
| 通义千问 | https://help.aliyun.com/zh/dashscope/ | 按量付费 |
| 智谱 AI | https://open.bigmodel.cn/ | 按量付费 |
| DeepSeek | https://platform.deepseek.com/ | 极低价 |
| Kimi | https://platform.moonshot.cn/ | 按量付费 |
| 百度文心 | https://cloud.baidu.com/doc/WENXINWORKSHOP/ | 按量付费 |

---

## 总结

### 推荐路线

```
短期（测试阶段）
   ↓
优化现有 Cookie 适配器
   ↓
添加官方 API Key 支持（双轨制）
   ↓
引导用户使用 API Key
   ↓
长期（商业化）
   ↓
全面切换到官方 API
```

### 核心原则

1. **稳定性优先**：Cookie 方案不稳定，仅供测试
2. **合法合规**：避免法律风险，推荐官方 API
3. **用户体验**：明确告知风险，提供多种选择
4. **可持续发展**：长期依赖官方 API，保证服务质量

---

需要我帮你实施哪个方案？或者开始优化某个具体的适配器？
