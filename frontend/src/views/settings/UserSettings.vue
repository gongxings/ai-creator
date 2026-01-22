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
              <el-button type="primary" @click="changePassword">修改密码</el-button>
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

        <!-- 平台账号 -->
        <el-tab-pane label="平台账号" name="platforms">
          <div class="platforms-section">
            <div class="section-header">
              <h3>发布平台账号</h3>
              <el-button type="primary" @click="showBindPlatformDialog">
                <el-icon><Link /></el-icon>
                绑定账号
              </el-button>
            </div>

            <el-table :data="platformAccounts" style="width: 100%">
              <el-table-column prop="platform_name" label="平台" />
              <el-table-column prop="account_name" label="账号名称" />
              <el-table-column label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'">
                    {{ row.is_active ? '已绑定' : '未激活' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editPlatformAccount(row)">编辑</el-button>
                  <el-button link type="danger" @click="unbindPlatform(row.id)">解绑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

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

    <!-- 绑定/编辑平台账号对话框 -->
    <el-dialog
      v-model="platformDialogVisible"
      :title="platformForm.id ? '编辑平台账号' : '绑定平台账号'"
      width="600px"
    >
      <el-form :model="platformForm" label-width="100px">
        <el-form-item label="平台">
          <el-select v-model="platformForm.platform_name" placeholder="选择平台">
            <el-option label="微信公众号" value="wechat" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="今日头条" value="toutiao" />
            <el-option label="百家号" value="baijiahao" />
            <el-option label="知乎" value="zhihu" />
            <el-option label="简书" value="jianshu" />
          </el-select>
        </el-form-item>
        <el-form-item label="账号名称">
          <el-input v-model="platformForm.account_name" placeholder="输入账号名称" />
        </el-form-item>
        <el-form-item label="配置信息">
          <el-input
            v-model="platformForm.config"
            type="textarea"
            :rows="6"
            placeholder="输入JSON格式的配置信息，例如：&#10;{&#10;  &quot;app_id&quot;: &quot;xxx&quot;,&#10;  &quot;app_secret&quot;: &quot;xxx&quot;&#10;}"
          />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="platformForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="platformDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlatformAccount">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getModels, createModel, updateModel, deleteModel as deleteModelApi } from '@/api/models'
import { getPlatforms, bindPlatform, updatePlatformAccount as updatePlatformApi, unbindPlatform as unbindPlatformApi } from '@/api/publish'
import type { AIModel, PlatformAccount } from '@/types'

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

// 平台账号
const platformAccounts = ref<PlatformAccount[]>([])
const platformDialogVisible = ref(false)
const platformForm = reactive({
  id: undefined as number | undefined,
  platform_name: '',
  account_name: '',
  config: '',
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
    // TODO: 调用更新用户信息API
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: 调用修改密码API
        ElMessage.success('密码修改成功，请重新登录')
        // 清空表单
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } catch (error) {
        ElMessage.error('密码修改失败')
      }
    }
  })
}

// 加载AI模型列表
const loadModels = async () => {
  try {
    const response = await getModels()
    models.value = response.data
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
      await updateModel(modelForm.id, modelForm)
      ElMessage.success('模型更新成功')
    } else {
      await createModel(modelForm)
      ElMessage.success('模型添加成功')
    }
    modelDialogVisible.value = false
    loadModels()
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
    await deleteModelApi(id)
    ElMessage.success('删除成功')
    loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载平台账号列表
const loadPlatformAccounts = async () => {
  try {
    const response = await getPlatforms()
    platformAccounts.value = response.data
  } catch (error) {
    ElMessage.error('加载平台账号失败')
  }
}

// 显示绑定平台对话框
const showBindPlatformDialog = () => {
  platformForm.id = undefined
  platformForm.platform_name = ''
  platformForm.account_name = ''
  platformForm.config = ''
  platformForm.is_active = true
  platformDialogVisible.value = true
}

// 编辑平台账号
const editPlatformAccount = (account: PlatformAccount) => {
  platformForm.id = account.id
  platformForm.platform_name = account.platform_name
  platformForm.account_name = account.account_name
  platformForm.config = JSON.stringify(account.config, null, 2)
  platformForm.is_active = account.is_active
  platformDialogVisible.value = true
}

// 保存平台账号
const savePlatformAccount = async () => {
  try {
    // 验证JSON格式
    let config = {}
    if (platformForm.config) {
      try {
        config = JSON.parse(platformForm.config)
      } catch (e) {
        ElMessage.error('配置信息格式错误，请输入有效的JSON')
        return
      }
    }

    const data = {
      platform_name: platformForm.platform_name,
      account_name: platformForm.account_name,
      config,
      is_active: platformForm.is_active,
    }

    if (platformForm.id) {
      await updatePlatformApi(platformForm.id, data)
      ElMessage.success('平台账号更新成功')
    } else {
      await bindPlatform(data)
      ElMessage.success('平台账号绑定成功')
    }
    platformDialogVisible.value = false
    loadPlatformAccounts()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 解绑平台
const unbindPlatform = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要解绑这个平台账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await unbindPlatformApi(id)
    ElMessage.success('解绑成功')
    loadPlatformAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('解绑失败')
    }
  }
}

onMounted(() => {
  loadUserInfo()
  loadModels()
  loadPlatformAccounts()
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

  .models-section,
  .platforms-section {
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
