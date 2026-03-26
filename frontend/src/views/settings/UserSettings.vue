<template>
  <div class="user-settings">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>用户设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="settings-tabs">
        <el-tab-pane label="个人信息" name="profile">
          <el-form :model="profileForm" label-width="100px" class="settings-form">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px" class="settings-form">
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input v-model="passwordForm.oldPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input v-model="passwordForm.newPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePasswordHandler">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="AI模型" name="models">
          <div class="models-section">
            <div class="section-header">
              <h3>AI模型管理</h3>
              <el-button type="primary" @click="showAddModelDialog">
                <el-icon><Plus /></el-icon>
                添加模型
              </el-button>
            </div>

            <el-table :data="models" style="width: 100%">
              <el-table-column prop="name" label="模型名称" />
              <el-table-column label="类型" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.is_system_builtin" type="warning" size="small">系统内置</el-tag>
                  <el-tag v-else type="info" size="small">自定义</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="提供商" min-width="120">
                <template #default="{ row }">
                  {{ getProviderLabel(row.provider) }}
                </template>
              </el-table-column>
              <el-table-column prop="model_name" label="模型标识" />
              <el-table-column label="能力" min-width="180">
                <template #default="{ row }">
                  <el-tag v-for="cap in (row.capabilities || [])" :key="cap" size="small" style="margin-right: 4px">
                    {{ capabilityLabels[cap] || cap }}
                  </el-tag>
                  <span v-if="!row.capabilities?.length" style="color: #909399">未设置</span>
                </template>
              </el-table-column>
              <el-table-column label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <template v-if="row.is_readonly">
                    <el-tag type="info" size="small">只读</el-tag>
                  </template>
                  <template v-else>
                    <el-button link type="primary" @click="editModel(row)">编辑</el-button>
                    <el-button link type="danger" @click="deleteModel(row.id)">删除</el-button>
                  </template>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加/编辑模型对话框 -->
    <el-dialog v-model="modelDialogVisible" :title="modelForm.id ? '编辑AI模型' : '添加AI模型'" width="650px">
      <el-form :model="modelForm" label-width="110px" class="model-form">
        <el-form-item label="模型名称" required>
          <el-input v-model="modelForm.name" placeholder="自定义名称，如：GPT-4 Turbo" />
        </el-form-item>

        <el-form-item label="提供商" required>
          <el-select v-model="modelForm.provider" placeholder="选择AI服务提供商" style="width: 100%" @change="handleProviderChange">
            <el-option-group label="开源模型平台">
              <el-option label="Hugging Face" value="huggingface" />
              <el-option label="ModelScope" value="modelscope" />
            </el-option-group>
            <el-option-group label="国外厂商">
              <el-option label="OpenAI" value="openai" />
              <el-option label="Anthropic" value="anthropic" />
              <el-option label="Google Gemini" value="google" />
              <el-option label="Stability AI" value="stability" />
              <el-option label="Replicate" value="replicate" />
            </el-option-group>
            <el-option-group label="国内厂商">
              <el-option label="智谱 AI" value="zhipu" />
              <el-option label="阿里通义" value="qwen" />
              <el-option label="百度文心" value="baidu" />
              <el-option label="火山引擎/豆包" value="doubao" />
              <el-option label="腾讯混元" value="hunyuan" />
              <el-option label="MiniMax" value="minimax" />
              <el-option label="讯飞星火" value="spark" />
              <el-option label="月之暗面" value="moonshot" />
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="百川" value="baichuan" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <!-- 动态认证字段 -->
        <template v-if="currentProviderConfig">
          <!-- API Key (所有厂商都有) -->
          <el-form-item label="API 密钥" required>
            <el-input v-model="modelForm.api_key" type="password" show-password placeholder="输入API密钥" />
          </el-form-item>

          <!-- Secret Key (百度、腾讯) -->
          <el-form-item v-if="currentProviderConfig.authType === 'dual_key'" label="Secret Key" required>
            <el-input v-model="modelForm.secret_key" type="password" show-password placeholder="输入Secret Key" />
            <div class="form-tip">{{ modelForm.provider === 'baidu' ? '百度文心需要 API Key 和 Secret Key' : '腾讯混元需要 SecretId 和 SecretKey' }}</div>
          </el-form-item>

          <!-- 讯飞星火三元组 -->
          <template v-if="currentProviderConfig.authType === 'triple_key'">
            <el-form-item label="App ID" required>
              <el-input v-model="modelForm.app_id" placeholder="输入讯飞 App ID" />
            </el-form-item>
            <el-form-item label="API Secret" required>
              <el-input v-model="modelForm.api_secret" type="password" show-password placeholder="输入 API Secret" />
            </el-form-item>
            <div class="form-tip" style="margin-bottom: 16px; margin-left: 110px;">讯飞星火需要 App ID、API Key 和 API Secret 三个凭证</div>
          </template>

          <!-- MiniMax Group ID -->
          <el-form-item v-if="currentProviderConfig.authType === 'api_key_group'" label="Group ID" required>
            <el-input v-model="modelForm.group_id" placeholder="输入 MiniMax Group ID" />
            <div class="form-tip">MiniMax 需要 API Key 和 Group ID</div>
          </el-form-item>
        </template>

        <el-form-item label="API 地址">
          <el-input 
            v-model="modelForm.base_url" 
            :placeholder="currentProviderConfig?.defaultBaseUrl || '默认使用官方地址'" 
            :disabled="currentProviderConfig && !currentProviderConfig.supportsCustomUrl"
          />
          <div v-if="currentProviderConfig && !currentProviderConfig.supportsCustomUrl" class="form-tip">
            该提供商不支持自定义 API 地址
          </div>
        </el-form-item>

        <el-form-item label="模型标识" required>
          <el-input v-model="modelForm.model_name" placeholder="例如：gpt-4-turbo-preview" />
          <div class="form-tip">请填写具体的模型名称/ID，如 gpt-4o、claude-3-opus-20240229、glm-4-plus 等</div>
        </el-form-item>

        <el-form-item label="模型能力">
          <el-checkbox-group v-model="modelForm.capabilities">
            <el-checkbox label="text">文本生成</el-checkbox>
            <el-checkbox label="image">图片生成</el-checkbox>
            <el-checkbox label="video">视频生成</el-checkbox>
            <el-checkbox label="audio">音频生成</el-checkbox>
          </el-checkbox-group>
          <div v-if="currentProviderConfig" class="form-tip">
            {{ currentProviderConfig.label }} 支持的能力：{{ currentProviderConfig.capabilities.map(c => capabilityLabels[c]).join('、') }}
          </div>
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="modelForm.is_active" />
        </el-form-item>

        <el-form-item v-if="isAdmin" label="系统内置">
          <el-switch v-model="modelForm.is_system_builtin" />
          <div class="form-tip">系统内置模型所有用户可见，但只有管理员可编辑</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModel">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Setting, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { updateUserInfo, changePassword } from '@/api/auth'
import { getAIModels, addAIModel, updateAIModel, deleteAIModel } from '@/api/models'
import { providerOptions, getProviderConfig, capabilityLabels } from '@/config/providerOptions'
import type { AIModel, ModelCapability } from '@/types'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.isAdmin)
const activeTab = ref('profile')

const profileForm = reactive({ username: '', email: '', phone: '' })

const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== passwordForm.newPassword) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

const models = ref<AIModel[]>([])
const modelDialogVisible = ref(false)
const modelForm = reactive({
  id: undefined as number | undefined,
  name: '',
  provider: '',
  api_key: '',
  secret_key: '',
  app_id: '',
  api_secret: '',
  group_id: '',
  base_url: '',
  model_name: '',
  is_active: true,
  is_system_builtin: false,
  capabilities: [] as ModelCapability[],
})

// 当前选择的提供商配置
const currentProviderConfig = computed(() => {
  if (!modelForm.provider) return null
  return getProviderConfig(modelForm.provider)
})

// 获取提供商显示名称
const getProviderLabel = (provider: string): string => {
  const config = getProviderConfig(provider)
  return config?.label || provider
}

// 处理提供商变更
const handleProviderChange = (provider: string) => {
  const config = getProviderConfig(provider)
  if (config) {
    // 自动填充默认 API 地址
    modelForm.base_url = config.supportsCustomUrl ? '' : config.defaultBaseUrl
    // 自动勾选该厂商支持的能力
    modelForm.capabilities = [...config.capabilities] as ModelCapability[]
  }
  // 清空认证相关字段
  modelForm.api_key = ''
  modelForm.secret_key = ''
  modelForm.app_id = ''
  modelForm.api_secret = ''
  modelForm.group_id = ''
}

const loadUserInfo = () => {
  const user = userStore.user
  if (!user) return
  profileForm.username = user.username
  profileForm.email = user.email || ''
  profileForm.phone = user.phone || ''
}

const updateProfile = async () => {
  try {
    await updateUserInfo({ email: profileForm.email, phone: profileForm.phone })
    await userStore.fetchUserInfo()
    ElMessage.success('个人信息更新成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

const changePasswordHandler = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await changePassword({ old_password: passwordForm.oldPassword, new_password: passwordForm.newPassword })
      ElMessage.success('密码修改成功，请重新登录')
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      setTimeout(() => userStore.logout(), 2000)
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '密码修改失败')
    }
  })
}

const loadModels = async () => {
  try {
    const res = await getAIModels()
    models.value = Array.isArray(res) ? res : []
  } catch {
    ElMessage.error('加载AI模型失败')
  }
}

const showAddModelDialog = () => {
  modelForm.id = undefined
  modelForm.name = ''
  modelForm.provider = ''
  modelForm.api_key = ''
  modelForm.secret_key = ''
  modelForm.app_id = ''
  modelForm.api_secret = ''
  modelForm.group_id = ''
  modelForm.base_url = ''
  modelForm.model_name = ''
  modelForm.is_active = true
  modelForm.is_system_builtin = false
  modelForm.capabilities = ['text']
  modelDialogVisible.value = true
}

const editModel = (model: AIModel) => {
  modelForm.id = model.id
  modelForm.name = model.name
  modelForm.provider = model.provider
  modelForm.api_key = model.api_key || ''
  modelForm.secret_key = ''
  modelForm.app_id = ''
  modelForm.api_secret = ''
  modelForm.group_id = ''
  modelForm.base_url = model.base_url || ''
  modelForm.model_name = model.model_name
  modelForm.is_active = model.is_active
  modelForm.is_system_builtin = model.is_system_builtin || false
  modelForm.capabilities = model.capabilities || ['text']
  modelDialogVisible.value = true
}

const saveModel = async () => {
  // 基本验证
  if (!modelForm.name || !modelForm.provider || !modelForm.model_name) {
    ElMessage.warning('请填写必填字段')
    return
  }

  // 新增时必须填写密钥
  if (!modelForm.id && !modelForm.api_key) {
    ElMessage.warning('请输入 API 密钥')
    return
  }

  // 根据认证类型验证额外字段
  const config = currentProviderConfig.value
  if (config && !modelForm.id) {
    if (config.authType === 'dual_key' && !modelForm.secret_key) {
      ElMessage.warning('请输入 Secret Key')
      return
    }
    if (config.authType === 'triple_key' && (!modelForm.app_id || !modelForm.api_secret)) {
      ElMessage.warning('请输入 App ID 和 API Secret')
      return
    }
    if (config.authType === 'api_key_group' && !modelForm.group_id) {
      ElMessage.warning('请输入 Group ID')
      return
    }
  }

  try {
    // 构建提交数据，将多个密钥字段合并
    const submitData: any = {
      name: modelForm.name,
      provider: modelForm.provider,
      model_name: modelForm.model_name,
      base_url: modelForm.base_url || undefined,
      is_active: modelForm.is_active,
      capabilities: modelForm.capabilities,
    }

    if (isAdmin.value) {
      submitData.is_system_builtin = modelForm.is_system_builtin
    }

    // 处理 API 密钥（根据认证类型组合）
    if (modelForm.api_key) {
      if (config?.authType === 'dual_key') {
        // 百度/腾讯：用分隔符组合两个密钥
        submitData.api_key = `${modelForm.api_key}:${modelForm.secret_key}`
      } else if (config?.authType === 'triple_key') {
        // 讯飞：用分隔符组合三个密钥
        submitData.api_key = `${modelForm.app_id}:${modelForm.api_key}:${modelForm.api_secret}`
      } else if (config?.authType === 'api_key_group') {
        // MiniMax：用分隔符组合
        submitData.api_key = `${modelForm.api_key}:${modelForm.group_id}`
      } else {
        submitData.api_key = modelForm.api_key
      }
    }

    if (modelForm.id) {
      await updateAIModel(modelForm.id, submitData)
      ElMessage.success('模型更新成功')
    } else {
      await addAIModel(submitData)
      ElMessage.success('模型添加成功')
    }
    modelDialogVisible.value = false
    await loadModels()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}

const deleteModel = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个AI模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteAIModel(id)
    ElMessage.success('删除成功')
    await loadModels()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadUserInfo()
  loadModels()
})
</script>

<style scoped lang="scss">
.user-settings {
  padding: 20px;

  .settings-card {
    max-width: 1200px;
    margin: 0 auto;

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .settings-tabs {
    margin-top: 20px;
  }

  .settings-form {
    max-width: 600px;
    margin-top: 20px;
  }

  .models-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
    }
  }
}

.model-form {
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.4;
  }
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}
</style>
