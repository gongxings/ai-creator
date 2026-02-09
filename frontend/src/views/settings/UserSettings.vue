<template>
  <div class="user-settings flagship-page page-shell">
    <section class="page-hero settings-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Settings</span>
          <h1 class="hero-title">用户设置</h1>
          <p class="hero-subtitle">管理个人信息、账号授权与模型配置。</p>
          <div class="hero-actions">
            <el-button v-if="activeTab === 'profile'" type="primary" @click="updateProfile">保存资料</el-button>
            <el-button v-if="activeTab === 'password'" type="primary" @click="changePasswordHandler">修改密码</el-button>
            <el-button v-if="activeTab === 'models'" type="primary" @click="showAddModelDialog">添加模型</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">配置概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ models.length }}</div>
              <div class="hero-stat-label">AI模型</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ activeTab }}</div>
              <div class="hero-stat-label">当前标签</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ profileForm.username || '-' }}</div>
              <div class="hero-stat-label">账号昵称</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">账号安全</span>
            <span class="hero-tag">模型管理</span>
            <span class="hero-tag">授权同步</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">当前标签</div>
          <div class="value">{{ activeTab }}</div>
          <div class="delta">支持多维度配置</div>
        </div>
        <div class="dashboard-card">
          <div class="label">模型配置</div>
          <div class="value">{{ models.length }}</div>
          <div class="delta">自定义模型可用</div>
        </div>
        <div class="dashboard-card">
          <div class="label">账号授权</div>
          <div class="value">
            <el-button size="small" @click="$router.push('/authorization')">管理授权</el-button>
          </div>
          <div class="delta">统一授权入口</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>用户设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 个人信息 -->
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

        <!-- 修改密码 -->
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

        <!-- AI模型配置 -->
        <el-tab-pane label="AI模型" name="models">
          <div class="models-section">
            <div class="section-header">
              <h3>AI模型配置</h3>
              <el-button type="primary" @click="showAddModelDialog">
                <el-icon><Plus /></el-icon>
                添加模型
              </el-button>
            </div>

            <el-table :data="models" style="width: 100%">
              <el-table-column prop="name" label="模型名称" />
              <el-table-column prop="provider" label="提供商" />
              <el-table-column prop="model_name" label="模型" />
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
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">设置指南</h3>
          <p class="panel-subtitle">维护资料与账号安全</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Setting /></el-icon></div>
              <div>
                <div class="info-title">保持更新</div>
                <div class="info-desc">及时更新邮箱与手机号。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Plus /></el-icon></div>
              <div>
                <div class="info-title">授权管理</div>
                <div class="info-desc">为多平台账号设置独立授权。</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="panel">
          <h3 class="panel-title">快捷操作</h3>
          <div class="info-list">
            <div class="info-item">
              <div>
                <div class="info-title">账号授权</div>
                <div class="info-desc">
                  <el-button size="small" @click="$router.push('/authorization')">
                    前往授权中心
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <!-- 添加/编辑AI模型对话框 -->
    <el-dialog
      v-model="modelDialogVisible"
      :title="modelForm.id ? '编辑AI模型' : '添加AI模型'"
      width="600px"
    >
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
          </el-select>
        </el-form-item>
        <el-form-item label="API密钥">
          <el-input v-model="modelForm.api_key" type="password" show-password placeholder="输入API密钥" />
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="modelForm.api_base" placeholder="可选，默认使用官方地址" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="modelForm.model_name" placeholder="例如：gpt-4-turbo-preview" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { updateUserInfo, changePassword } from '@/api/auth'
import { getAIModels, addAIModel, updateAIModel, deleteAIModel } from '@/api/models'
import type { AIModel } from '@/types'

const userStore = useUserStore()
const activeTab = ref('profile')

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
})

// 密码表单
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// OAuth账号（已移至账号授权页面）
// const oauthAccounts = ref<any[]>([])

// AI模型
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
})

// 加载用户信息
const loadUserInfo = () => {
  const user = userStore.user
  if (user) {
    profileForm.username = user.username
    profileForm.email = user.email || ''
    profileForm.phone = user.phone || ''
  }
}

// 更新个人信息
const updateProfile = async () => {
  try {
    await updateUserInfo({
      email: profileForm.email,
      phone: profileForm.phone,
    })
    await userStore.fetchUserInfo()
    ElMessage.success('个人信息更新成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

// 修改密码
const changePasswordHandler = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await changePassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword,
        })
        ElMessage.success('密码修改成功，请重新登录')
        // 清空表单
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
        // 可选：自动登出用户
        setTimeout(() => {
          userStore.logout()
        }, 2000)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '密码修改失败')
      }
    }
  })
}

// 加载AI模型列表
const loadModels = async () => {
  try {
    const data = await getAIModels()
    models.value = data
  } catch (error) {
    ElMessage.error('加载AI模型失败')
  }
}

// 显示添加模型对话框
const showAddModelDialog = () => {
  modelForm.id = undefined
  modelForm.name = ''
  modelForm.provider = ''
  modelForm.api_key = ''
  modelForm.api_base = ''
  modelForm.model_name = ''
  modelForm.is_active = true
  modelDialogVisible.value = true
}

// 编辑模型
const editModel = (model: AIModel) => {
  modelForm.id = model.id
  modelForm.name = model.name
  modelForm.provider = model.provider
  modelForm.api_key = model.api_key
  modelForm.api_base = model.api_base || ''
  modelForm.model_name = model.model_name
  modelForm.is_active = model.is_active
  modelDialogVisible.value = true
}

// 保存模型
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
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 删除模型
const deleteModel = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个AI模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteAIModel(id)
    ElMessage.success('删除成功')
    loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// OAuth账号管理方法（已移至账号授权页面）
// const loadOAuthAccounts = async () => { ... }

onMounted(() => {
  loadUserInfo()
  loadModels()
})
</script>

<style scoped lang="scss">
.user-settings {
  padding: 20px;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;

  .page-body {
    align-items: stretch;
  }

  .main-panel,
  .side-panel {
    height: 100%;
  }

  .settings-card {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.settings-card .el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .settings-tabs {
    margin-top: 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  :deep(.settings-tabs .el-tabs__content) {
    flex: 1;
    min-height: 0;
  }

  :deep(.settings-tabs .el-tab-pane) {
    height: 100%;
  }

  .settings-form {
    max-width: 600px;
    margin-top: 20px;
  }

  .oauth-section,
  .models-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 0;

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

    .quota-text {
      display: block;
      margin-top: 5px;
      font-size: 12px;
      color: #666;
    }
  }
}
</style>

