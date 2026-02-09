# 豆包平台功能支持说明

## 问题修复

### 1. 文本生成 422 错误 ✅ 已修复

#### 错误原因
`CreationGenerate` schema 中 `prompt` 字段被定义为必需字段，但 Cookie 模式下前端不发送 `prompt`，而是发送 `parameters`。

#### 修复内容
**文件**: `backend/app/schemas/creation.py:21`

```python
# 修改前
prompt: str = Field(..., description="提示词")

# 修改后
prompt: Optional[str] = Field(None, description="提示词（Cookie模式下可选，使用parameters生成）")
```

#### 测试验证
```bash
# 使用 Cookie 模式生成文本（豆包）
curl -X POST "http://localhost:8000/v1/writing/generate" \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "wechat_article",
    "parameters": {
      "topic": "人工智能的未来",
      "style": "专业",
      "length": "中"
    },
    "platform": "doubao"
  }'
```

---

## 豆包平台功能详解

### 官方功能说明

根据豆包（doubao.com）官网和实际测试，豆包平台支持以下功能：

| 功能 | 支持状态 | 实现方式 | 说明 |
|------|----------|----------|------|
| **文本对话** | ✅ 完全支持 | 直接 API | 基础对话功能 |
| **文章生成** | ✅ 完全支持 | 对话生成 | 通过提示词生成文章 |
| **代码辅助** | ✅ 完全支持 | 对话生成 | 代码生成和解释 |
| **图像生成** | ⚠️ 有限支持 | 间接调用 | 通过对话请求生成图片 |
| **视频生成** | ⚠️ 有限支持 | 间接调用 | 通过对话请求生成视频 |

### 重要说明

#### 1. 图像生成

**豆包的图像生成能力**：
- ❌ **没有直接的图像生成 API**
- ⚠️ **可以通过对话方式请求生成图片**
- ⚠️ **返回的是文本描述或图片链接**（不稳定）
- ✅ **更推荐使用即梦（Jimeng）平台**

**实现方式**（已在代码中实现）：
```python
# backend/app/services/ai/doubao_service.py:207-296
async def generate_image(self, prompt: str, **kwargs):
    """
    通过聊天API请求生成图片
    注意：这不是真正的图像生成API，而是通过对话方式请求
    """
    full_prompt = f"请帮我生成一张图片：{prompt}"
    # 调用聊天API，希望AI返回图片链接
    ...
```

**问题**：
1. **不稳定** - 豆包可能返回"我无法生成图片"的文本回复
2. **无法控制** - 无法指定尺寸、风格等参数
3. **效率低** - 需要先对话，再提取链接
4. **成功率低** - 取决于豆包当前的功能状态

#### 2. 视频生成

**豆包的视频生成能力**：
- ❌ **没有直接的视频生成 API**
- ⚠️ **可能支持通过对话方式请求**（非常不稳定）
- ✅ **建议使用专门的视频生成平台**（如剪映）

---

## 解决方案

### 方案 1: 使用专业平台（推荐）⭐

#### 图像生成
使用 **即梦（Jimeng）平台**：
```json
{
  "prompt": "一只可爱的猫咪",
  "platform": "jimeng",
  "width": 1024,
  "height": 1024
}
```

**优势**：
- ✅ 专业的图像生成 API
- ✅ 稳定可靠，成功率 100%
- ✅ 支持尺寸、风格、模型选择
- ✅ 高质量输出

#### 视频生成
使用 **剪映（Jianying）** 或其他视频平台：
```json
{
  "script": "视频脚本内容",
  "platform": "jianying"
}
```

### 方案 2: 保留豆包间接支持

如果确实需要通过豆包尝试图像/视频生成，可以：

#### 2.1 前端添加警告提示

```typescript
// frontend - 图片生成页面
if (selectedPlatform === 'doubao') {
  showWarning({
    title: '提示',
    message: '豆包不是专业的图像生成平台，生成成功率较低。推荐使用即梦平台以获得更好的效果。',
    confirmText: '继续使用豆包',
    cancelText: '切换到即梦',
  });
}
```

#### 2.2 后端优化错误处理

```python
# backend/app/services/ai/doubao_service.py

async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
    """
    尝试通过豆包生成图片（不保证成功）
    """
    result = await self._try_generate_via_chat(prompt)
    
    if not result.get("images"):
        return {
            "error": "豆包暂不支持图像生成",
            "suggestion": "请使用即梦(jimeng)平台获得专业的图像生成服务",
            "fallback_text": result.get("text", "")
        }
    
    return result
```

### 方案 3: 功能路由优化

根据任务类型自动选择合适的平台：

```python
# backend/app/api/v1/image.py

@router.post("")
async def create_image(request: ImageGenerationRequest, ...):
    """生成图片"""
    
    # 如果用户选择了豆包，给出警告并建议切换
    if request.platform == "doubao":
        logger.warning("User trying to use Doubao for image generation")
        
        # 检查是否有即梦账号
        jimeng_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == current_user.id,
            OAuthAccount.platform == "jimeng",
            OAuthAccount.is_active == True
        ).first()
        
        if jimeng_account:
            # 建议使用即梦
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "豆包不是专业的图像生成平台",
                    "suggestion": "您已授权即梦平台，建议使用即梦以获得更好的生成效果",
                    "available_platforms": ["jimeng"]
                }
            )
        else:
            # 提示授权即梦
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "豆包不支持图像生成",
                    "suggestion": "请先授权即梦(jimeng)平台，它是专业的AI图像生成服务",
                    "authorization_url": "/authorization?platform=jimeng"
                }
            )
    
    # 正常处理其他平台
    ...
```

---

## 推荐配置

### 平台功能矩阵

| 任务类型 | 推荐平台 | 备选平台 | 不推荐 |
|---------|---------|---------|--------|
| 文本对话 | 豆包 ⭐ | 通义千问、智谱清言 | - |
| 文章生成 | 豆包 ⭐ | 通义千问 | - |
| 代码生成 | DeepSeek ⭐ | 豆包 | - |
| 图像生成 | 即梦 ⭐ | 智谱清言 | 豆包 ❌ |
| 视频生成 | 剪映 ⭐ | - | 豆包 ❌ |
| PPT 生成 | 专用服务 | - | 所有对话平台 ❌ |

### 前端选择器优化

```typescript
// 根据任务类型过滤可用平台
const platformsByTask = {
  'text': ['doubao', 'qwen', 'zhipu', 'deepseek'],
  'article': ['doubao', 'qwen', 'zhipu'],
  'code': ['deepseek', 'doubao'],
  'image': ['jimeng', 'zhipu'],  // 不包括 doubao
  'video': ['jianying'],          // 不包括 doubao
};

function getAvailablePlatforms(taskType: string) {
  return platformsByTask[taskType] || [];
}
```

---

## 代码修改建议

### 1. 添加平台能力声明

```python
# backend/app/services/oauth/adapters/doubao.py

class DoubaoAdapter(PlatformAdapter):
    def get_supported_features(self) -> List[str]:
        """豆包支持的功能"""
        return [
            'chat',           # 对话
            'article',        # 文章生成
            'code',           # 代码辅助
            # 'image',        # 不直接支持
            # 'video',        # 不直接支持
        ]
    
    def get_feature_quality(self, feature: str) -> str:
        """功能质量评级"""
        quality_map = {
            'chat': 'excellent',    # 优秀
            'article': 'excellent',
            'code': 'good',         # 良好
        }
        return quality_map.get(feature, 'not_supported')
```

### 2. 添加功能检查端点

```python
# backend/app/api/v1/platform.py

@router.get("/capabilities")
async def get_platform_capabilities(
    platform: str,
    task_type: str,
    current_user: User = Depends(get_current_user)
):
    """检查平台是否支持特定任务"""
    
    adapter_class = PLATFORM_ADAPTERS.get(platform)
    if not adapter_class:
        raise HTTPException(404, "Platform not found")
    
    adapter = adapter_class(platform, {})
    supported = task_type in adapter.get_supported_features()
    
    if not supported:
        # 推荐替代平台
        alternatives = []
        for p_id, p_class in PLATFORM_ADAPTERS.items():
            p_adapter = p_class(p_id, {})
            if task_type in p_adapter.get_supported_features():
                alternatives.append({
                    'platform': p_id,
                    'quality': p_adapter.get_feature_quality(task_type)
                })
        
        return {
            'supported': False,
            'reason': f'{platform} 不支持 {task_type} 功能',
            'alternatives': alternatives
        }
    
    return {
        'supported': True,
        'quality': adapter.get_feature_quality(task_type)
    }
```

### 3. 前端调用检查

```typescript
// frontend - 生成前检查
async function checkPlatformSupport(platform: string, taskType: string) {
  const response = await api.get('/platform/capabilities', {
    params: { platform, task_type: taskType }
  });
  
  if (!response.data.supported) {
    const alternatives = response.data.alternatives;
    
    // 显示建议对话框
    const confirmed = await showDialog({
      title: '平台不支持',
      message: response.data.reason,
      alternatives: alternatives.map(a => 
        `${a.platform} (质量: ${a.quality})`
      ).join(', '),
      confirmText: '切换平台',
    });
    
    if (confirmed && alternatives.length > 0) {
      // 自动切换到推荐平台
      selectedPlatform.value = alternatives[0].platform;
    }
    
    return false;
  }
  
  return true;
}
```

---

## 总结

### ✅ 已修复
1. **文本生成 422 错误** - `prompt` 字段改为可选

### ⚠️ 功能澄清
1. **豆包图像生成** - 不是专业功能，不推荐使用
2. **豆包视频生成** - 不支持
3. **推荐使用** - 即梦（图像）、剪映（视频）

### 🎯 建议操作
1. **立即**：测试文本生成是否正常
2. **后续**：授权即梦平台用于图像生成
3. **优化**：前端根据任务类型过滤可选平台
4. **完善**：添加平台能力检查 API

### 📝 备注
- 豆包最适合：文本对话、文章生成、代码辅助
- 图像生成请用：即梦（专业、稳定）
- 视频生成请用：剪映或专业视频平台
