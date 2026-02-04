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

        <!-- OAuth账号管理 -->
        <el-tab-pane label="OAuth账号" name="oauth">
          <div class="oauth-section">
            <div class="section-header">
              <h3>OAuth账号管理</h3>
              <el-button type="primary" @click="showAddOAuthDialog">
                <el-icon><Plus /></el-icon>
                添加账号
              </el-button>
            </div>

            <el-table :data="oauthAccounts" style="width: 100%">
              <el-table-column prop="platform_name" label="平台" />
              <el-table-column prop="account_name" label="账号名称" />
              <el-table-column label="配额使用">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.quota_limit ? (row.quota_used / row.quota_limit * 100) : 0"
                    :status="row.is_expired ? 'exception' : 'success'"
                  />
                  <span class="quota-text">
                    {{ row.quota_used }} / {{ row.quota_limit || '无限制' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="状态">
                <template #default="{ row }">
                  <el-tag v-if="row.is_expired" type="danger">已过期</el-tag>
                  <el-tag v-else-if="row.is_active" type="success">正常</el-tag>
                  <el-tag v-else type="info">已禁用</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="180" />
              <el-table-column label="操作" width="250">
                <template #default="{ row }">
                  <el-button link type="primary" @click="refreshOAuthAccount(row.id)">刷新</el-button>
                  <el-button link type="warning" @click="toggleOAuthAccount(row)">
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                  <el-button link type="danger" @click="deleteOAuthAccount(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
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

    <!-- 添加OAuth账号对话框 -->
    <el-dialog
      v-model="oauthDialogVisible"
      title="添加OAuth账号"
      width="600px"
    >
      <el-form :model="oauthForm" label-width="100px">
        <el-form-item label="选择平台">
          <el-select v-model="oauthForm.platform" placeholder="选择要授权的平台" style="width: 100%">
            <el-option
              v-for="platform in oauthPlatforms"
              :key="platform.id"
              :label="`${platform.icon} ${platform.name}`"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账号名称">
          <el-input
            v-model="oauthForm.account_name"
            placeholder="为这个账号起个名字，方便识别"
          />
        </el-form-item>
        <el-alert
          title="授权说明"
          type="info"
          :closable="false"
          style="margin-top: 10px"
        >
          <p>点击"开始授权"后，将打开新窗口进行平台登录授权。</p>
          <p>授权完成后，系统会自动获取您的免费额度。</p>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="oauthDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addOAuthAccount">开始授权</el-button>
      </template>
    </el-dialog>

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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useUserStore } from '@/store/user'
import { updateUserInfo, changePassword } from '@/api/auth'
import { getAIModels, addAIModel, updateAIModel, deleteAIModel } from '@/api/models'
import { 
  getPlatforms,
  authorizeAccount, 
  getAccounts, 
  updateAccount, 
  deleteAccount, 
  checkAccountValidity 
} from '@/api/oauth'
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

// OAuth账号
const oauthAccounts = ref<any[]>([])
const oauthDialogVisible = ref(false)
const oauthForm = reactive({
  platform: '',
  account_name: '',
})

// OAuth平台列表（从后端获取）
const oauthPlatforms = ref<any[]>([])

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

// OAuth账号管理方法
const showAddOAuthDialog = () => {
  oauthForm.platform = ''
  oauthForm.account_name = ''
  oauthDialogVisible.value = true
}

const loadOAuthPlatforms = async () => {
  try {
    const data = await getPlatforms()
    oauthPlatforms.value = data.map((platform: any) => ({
      id: platform.platform_id,
      name: platform.platform_name,
      icon: platform.platform_icon || '🤖',
    }))
  } catch (error) {
    ElMessage.error('加载OAuth平台失败')
  }
}

const loadOAuthAccounts = async () => {
  try {
    const data = await getAccounts()
    oauthAccounts.value = data
  } catch (error) {
    ElMessage.error('加载OAuth账号失败')
  }
}

const addOAuthAccount = async () => {
  if (!oauthForm.platform || !oauthForm.account_name) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  try {
    // 显示加载提示
    const loadingMessage = ElMessage({
      message: '正在启动授权流程，后端将打开浏览器窗口，请在浏览器中完成登录...',
      type: 'info',
      duration: 0, // 不自动关闭
      showClose: true,
    })
    
    // 关闭对话框
    oauthDialogVisible.value = false
    
    // 调用授权API（这会在后端使用Playwright打开浏览器窗口）
    await authorizeAccount({
      platform: oauthForm.platform,
      account_name: oauthForm.account_name,
    })
    
    // 关闭加载提示
    loadingMessage.close()
    
    // 显示成功消息
    ElMessage.success('OAuth账号授权成功！')
    
    // 重新加载账号列表
    await loadOAuthAccounts()
    
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '授权失败，请重试')
  }
}

const refreshOAuthAccount = async (id: number) => {
  try {
    const loadingMessage = ElMessage({
      message: '正在刷新账号，请稍候...',
      type: 'info',
      duration: 0,
      showClose: true,
    })
    
    await checkAccountValidity(id)
    loadingMessage.close()
    
    ElMessage.success('刷新成功')
    await loadOAuthAccounts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '刷新失败')
  }
}

const toggleOAuthAccount = async (account: any) => {
  try {
    await updateAccount(account.id, {
      is_active: !account.is_active
    })
    ElMessage.success(account.is_active ? '已禁用' : '已启用')
    await loadOAuthAccounts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const deleteOAuthAccount = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个OAuth账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await deleteAccount(id)
    ElMessage.success('删除成功')
    await loadOAuthAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  loadUserInfo()
  loadModels()
  loadOAuthPlatforms()
  loadOAuthAccounts()
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

  .oauth-section,
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

    .quota-text {
      display: block;
      margin-top: 5px;
      font-size: 12px;
      color: #666;
    }
  }
}
</style>
