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
              <el-table-column prop="provider" label="提供商" />
              <el-table-column prop="model_name" label="模型" />
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
                  <el-button link type="primary" @click="editModel(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteModel(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="modelDialogVisible" :title="modelForm.id ? '编辑AI模型' : '添加AI模型'" width="600px">
      <el-form :model="modelForm" label-width="100px">
        <el-form-item label="模型名称">
          <el-input v-model="modelForm.name" placeholder="例如：GPT-4" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="modelForm.provider" placeholder="选择提供商">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="智谱AI" value="zhipu" />
            <el-option label="百度文心" value="baidu" />
            <el-option label="阿里通义" value="qwen" />
          </el-select>
        </el-form-item>
        <el-form-item label="API密钥">
          <el-input v-model="modelForm.api_key" type="password" show-password placeholder="输入API密钥" />
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="modelForm.api_base" placeholder="可选，默认使用官方地址" />
        </el-form-item>
        <el-form-item label="模型标识">
          <el-input v-model="modelForm.model_name" placeholder="例如：gpt-4-turbo-preview" />
        </el-form-item>
        <el-form-item label="模型能力">
          <el-checkbox-group v-model="modelForm.capabilities">
            <el-checkbox label="text">文本生成</el-checkbox>
            <el-checkbox label="image">图片生成</el-checkbox>
            <el-checkbox label="video">视频生成</el-checkbox>
            <el-checkbox label="audio">音频生成</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="modelForm.is_active" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useUserStore } from '@/store/user'
import { updateUserInfo, changePassword } from '@/api/auth'
import { getAIModels, addAIModel, updateAIModel, deleteAIModel } from '@/api/models'
import type { AIModel, ModelCapability } from '@/types'

const userStore = useUserStore()
const activeTab = ref('profile')

// 能力标签映射
const capabilityLabels: Record<string, string> = {
  text: '文本',
  image: '图片',
  video: '视频',
  audio: '音频',
}

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
  api_base: '',
  model_name: '',
  is_active: true,
  capabilities: [] as ModelCapability[],
})

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
    // res 直接就是数组，响应拦截器已返回 response.data
    models.value = Array.isArray(res) ? res : (res.data || [])
  } catch {
    ElMessage.error('加载AI模型失败')
  }
}

const showAddModelDialog = () => {
  modelForm.id = undefined
  modelForm.name = ''
  modelForm.provider = ''
  modelForm.api_key = ''
  modelForm.api_base = ''
  modelForm.model_name = ''
  modelForm.is_active = true
  modelForm.capabilities = ['text']
  modelDialogVisible.value = true
}

const editModel = (model: AIModel) => {
  modelForm.id = model.id
  modelForm.name = model.name
  modelForm.provider = model.provider
  modelForm.api_key = ''
  modelForm.api_base = model.api_base || ''
  modelForm.model_name = model.model_name
  modelForm.is_active = model.is_active
  modelForm.capabilities = model.capabilities || ['text']
  modelDialogVisible.value = true
}

const saveModel = async () => {
  try {
    if (modelForm.id) {
      await updateAIModel(modelForm.id, modelForm)
      ElMessage.success('模型更新成功')
    } else {
      await addAIModel(modelForm)
      ElMessage.success('模型添加成功')
    }
    modelDialogVisible.value = false
    await loadModels()
  } catch {
    ElMessage.error('保存失败')
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
</style>
