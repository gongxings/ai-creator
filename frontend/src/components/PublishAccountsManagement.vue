<template>
  <div class="publish-accounts-management">
    <div class="section-header">
      <div class="header-content">
        <h3>发布平台账号管理</h3>
        <p class="section-subtitle">绑定微信公众号、小红书、抖音等平台账号，一键发布创作内容</p>
      </div>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>
        添加账号
      </el-button>
    </div>

    <!-- 首次使用引导 -->
    <el-card v-if="accounts.length === 0 && !loading" class="guide-card">
      <div class="guide-content">
        <el-icon class="guide-icon"><Upload /></el-icon>
        <h3>欢迎使用发布平台账号管理</h3>
        <p>绑定您的发布平台账号，即可将创作内容一键发布到多个平台！</p>
        
        <div class="guide-steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-content">
              <h4>选择平台</h4>
              <p>选择要绑定的发布平台</p>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div class="step-content">
              <h4>登录授权</h4>
              <p>在弹出窗口中登录平台账号</p>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div class="step-content">
              <h4>开始发布</h4>
              <p>授权成功后即可发布内容</p>
            </div>
          </div>
        </div>
        
        <el-button type="primary" size="large" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          立即添加账号
        </el-button>
      </div>
    </el-card>

    <!-- 账号列表 -->
    <el-table
      v-else
      v-loading="loading"
      :data="accounts"
      style="width: 100%"
    >
      <el-table-column label="平台" width="160">
        <template #default="{ row }">
          <el-tag>{{ getPlatformName(row.platform) }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="account_name" label="账号名称" min-width="180" />
      
      <el-table-column label="Cookie状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getCookieStatusType(row.cookies_valid)">
            {{ getCookieStatusText(row.cookies_valid) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="Cookie更新时间" width="180">
        <template #default="{ row }">
          {{ row.cookies_updated_at ? formatDate(row.cookies_updated_at) : '-' }}
        </template>
      </el-table-column>
      
      <el-table-column label="账号状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_active === 'active' ? 'success' : 'info'">
            {{ row.is_active === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleAutoAuthorize(row)">
            自动获取
          </el-button>
          <el-button size="small" @click="handleValidateCookies(row)">
            校验
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加发布平台账号"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="授权方式说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p><strong>方式1：远程浏览器（推荐）</strong></p>
        <ul>
          <li>实时显示浏览器画面</li>
          <li>支持鼠标点击操作</li>
          <li>登录成功后自动获取Cookie</li>
        </ul>
        
        <p><strong>方式2：前端授权</strong></p>
        <ul>
          <li>在弹出窗口中手动登录</li>
          <li>需要手动复制Cookie</li>
        </ul>
        
        <p><strong>方式3：后端授权</strong></p>
        <ul>
          <li>系统自动打开浏览器</li>
          <li>在浏览器中扫码登录</li>
        </ul>
      </el-alert>
      
      <el-tabs v-model="authMethod">
        <el-tab-pane label="远程浏览器" name="remote">
          <div class="auth-remote">
            <el-form-item label="选择平台" prop="platformCode">
              <el-select
                v-model="addForm.platformCode"
                placeholder="请选择平台"
                style="width: 100%"
                @change="handlePlatformChange"
              >
                <el-option
                  v-for="platform in platforms"
                  :key="platform.platform"
                  :label="platform.name"
                  :value="platform.platform"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="账号名称" prop="accountName">
              <el-input v-model="addForm.accountName" placeholder="请输入账号名称（用于识别）" />
            </el-form-item>
            
            <el-alert
              title="点击按钮后将打开远程浏览器，您可以直接在画面中操作完成登录"
              type="success"
              :closable="false"
              show-icon
            />
          </div>
          
          <el-button
            type="primary"
            @click="handleRemoteAuth"
            :loading="binding"
            style="width: 100%; margin-top: 20px"
            size="large"
          >
            <el-icon><VideoCamera /></el-icon>
            打开远程浏览器
          </el-button>
        </el-tab-pane>
        
        <el-tab-pane label="前端授权" name="frontend">
          <div class="auth-frontend">
            <el-form-item label="选择平台" prop="platformCode">
              <el-select
                v-model="addForm.platformCode"
                placeholder="请选择平台"
                style="width: 100%"
                @change="handlePlatformChange"
              >
                <el-option
                  v-for="platform in platforms"
                  :key="platform.platform"
                  :label="platform.name"
                  :value="platform.platform"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="账号名称" prop="accountName">
              <el-input v-model="addForm.accountName" placeholder="请输入账号名称（用于识别）" />
            </el-form-item>
          </div>
          
          <el-button
            type="primary"
            @click="handleFrontendAuth"
            :loading="binding"
            style="width: 100%; margin-top: 20px"
            size="large"
          >
            前端授权
          </el-button>
        </el-tab-pane>
        
        <el-tab-pane label="后端授权" name="backend">
          <el-form-item label="选择平台" prop="platformCode">
            <el-select
              v-model="addForm.platformCode"
              placeholder="选择要绑定的平台"
              style="width: 100%"
              @change="handlePlatformChange"
            >
              <el-option
                v-for="platform in platforms"
                :key="platform.platform"
                :label="platform.name"
                :value="platform.platform"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="账号名称" prop="accountName">
            <el-input v-model="addForm.accountName" placeholder="输入账号名称" />
          </el-form-item>
          
          <el-alert
            title="点击绑定后将自动打开浏览器登录并抓取Cookie"
            type="info"
            :closable="false"
            show-icon
          />
          
          <el-button
            type="primary"
            @click="handleBackendAuth"
            :loading="binding"
            style="width: 100%; margin-top: 20px"
            size="large"
          >
            后端授权
          </el-button>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 远程浏览器授权对话框 -->
    <RemoteBrowser
      v-model="showRemoteBrowser"
      :platform="addForm.platformCode"
      :platform-name="getPlatformName(addForm.platformCode)"
      platform-type="publish"
      :account-name="addForm.accountName"
      @success="handleRemoteBrowserSuccess"
      @cancel="handleRemoteBrowserCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, VideoCamera } from '@element-plus/icons-vue'
import RemoteBrowser from '@/components/RemoteBrowser.vue'
import {
  getPlatforms,
  getPlatformAccounts,
  authorizePlatformAccount,
  validatePlatformCookies,
  deletePlatformAccount,
} from '@/api/publish'

// 事件
const emit = defineEmits(['accounts-updated'])

// 数据
const platforms = ref<any[]>([])
const accounts = ref<any[]>([])

// 状态
const loading = ref(false)
const binding = ref(false)
const authMethod = ref('remote')

// 对话框
const showAddDialog = ref(false)
const showRemoteBrowser = ref(false)

// 授权窗口引用
const authWindow = ref<Window | null>(null)

// 表单
const addForm = ref({
  platformCode: '',
  accountName: '',
})

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await getPlatforms()
    platforms.value = response || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载平台列表失败')
  }
}

// 加载账号列表
const loadAccounts = async () => {
  loading.value = true
  try {
    const response = await getPlatformAccounts()
    accounts.value = response || []
    emit('accounts-updated')
  } catch (error: any) {
    ElMessage.error(error.message || '加载账号列表失败')
  } finally {
    loading.value = false
  }
}

// 打开添加对话框
const openAddDialog = () => {
  addForm.value = {
    platformCode: '',
    accountName: '',
  }
  authMethod.value = 'remote'
  showAddDialog.value = true
}

// 平台变化
const handlePlatformChange = async (platformCode: string) => {
  // 可以在这里加载平台特定的配置
}

// 远程浏览器授权
const handleRemoteAuth = () => {
  if (!addForm.value.platformCode) {
    ElMessage.warning('请选择平台')
    return
  }
  
  if (!addForm.value.accountName) {
    ElMessage.warning('请输入账号名称')
    return
  }
  
  showRemoteBrowser.value = true
  showAddDialog.value = false
}

// 前端授权
const handleFrontendAuth = async () => {
  if (!addForm.value.platformCode) {
    ElMessage.warning('请选择平台')
    return
  }
  
  if (!addForm.value.accountName) {
    ElMessage.warning('请输入账号名称')
    return
  }
  
  binding.value = true
  try {
    const width = 800
    const height = 600
    const left = (window.innerWidth - width) / 2 + window.screenX
    const top = (window.innerHeight - height) / 2 + window.screenY
    
    const authUrl = `${window.location.origin}/api/v1/publish/platforms/accounts/cookie-validate/${addForm.value.platformCode}`
    
    authWindow.value = window.open(
      authUrl,
      `publish-${Date.now()}`,
      `width=${width},height=${height},left=${left},top=${top}`
    )
    
    const handleAuthMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return
      
      const { type } = event.data
      
      if (type === 'publish_cookies_success') {
        ElMessage.success('授权成功！')
        
        if (authWindow.value && !authWindow.value.closed) {
          authWindow.value.close()
        }
        
        loadAccounts()
        showAddDialog.value = false
        addForm.value = { platformCode: '', accountName: '' }
      }
    }
    
    window.addEventListener('message', handleAuthMessage)
    
    setTimeout(() => {
      window.removeEventListener('message', handleAuthMessage)
      if (authWindow.value && !authWindow.value.closed) {
        authWindow.value.close()
      }
      binding.value = false
    }, 5 * 60 * 1000)
    
  } catch (error: any) {
    ElMessage.error('打开授权窗口失败')
    binding.value = false
  }
}

// 后端授权
const handleBackendAuth = async () => {
  if (!addForm.value.platformCode) {
    ElMessage.warning('请选择平台')
    return
  }
  
  if (!addForm.value.accountName) {
    ElMessage.warning('请输入账号名称')
    return
  }
  
  binding.value = true
  try {
    await authorizePlatformAccount({
      platform: addForm.value.platformCode,
      account_name: addForm.value.accountName,
    })
    ElMessage.success('授权成功，已自动获取Cookie')
    showAddDialog.value = false
    addForm.value = { platformCode: '', accountName: '' }
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '授权失败')
  } finally {
    binding.value = false
  }
}

// 远程浏览器授权成功
const handleRemoteBrowserSuccess = () => {
  ElMessage.success('授权成功！Cookie已自动保存')
  loadAccounts()
  addForm.value = { platformCode: '', accountName: '' }
}

// 远程浏览器授权取消
const handleRemoteBrowserCancel = () => {
  showAddDialog.value = true
}

// 自动获取Cookie
const handleAutoAuthorize = async (row: any) => {
  try {
    binding.value = true
    await authorizePlatformAccount({
      platform: row.platform,
      account_name: row.account_name,
    })
    ElMessage.success('授权成功，已自动获取Cookie')
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '自动授权失败')
  } finally {
    binding.value = false
  }
}

// 校验Cookie
const handleValidateCookies = async (row: any) => {
  try {
    const response = await validatePlatformCookies(row.id)
    if (response.valid) {
      ElMessage.success('Cookie有效')
    } else {
      ElMessage.warning(response.message || 'Cookie已失效')
    }
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '校验Cookie失败')
  }
}

// 删除账号
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除账号"${row.account_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deletePlatformAccount(row.id)
    ElMessage.success('删除成功')
    loadAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 获取平台名称
const getPlatformName = (code: string) => {
  const platform = platforms.value.find((p: any) => p.platform === code)
  return platform?.name || code
}

// Cookie状态
const getCookieStatusType = (status?: string | null) => {
  if (status === 'valid') return 'success'
  if (status === 'invalid') return 'danger'
  return 'info'
}

const getCookieStatusText = (status?: string | null) => {
  if (status === 'valid') return '有效'
  if (status === 'invalid') return '失效'
  return '未知'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 生命周期
onMounted(() => {
  loadPlatforms()
  loadAccounts()
})

onUnmounted(() => {
  if (authWindow.value && !authWindow.value.closed) {
    authWindow.value.close()
  }
  authWindow.value = null
})

// 暴露方法给父组件
defineExpose({
  openAddDialog,
})
</script>

<style scoped lang="scss">
.publish-accounts-management {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;

    .header-content {
      h3 {
        margin: 0 0 4px 0;
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
      }

      .section-subtitle {
        margin: 0;
        color: #64748b;
        font-size: 13px;
      }
    }
  }

  // 首次使用引导卡片
  .guide-card {
    margin-bottom: 20px;

    .guide-content {
      text-align: center;
      padding: 40px 20px;

      .guide-icon {
        font-size: 64px;
        color: #2563eb;
        margin-bottom: 20px;
      }

      h3 {
        font-size: 20px;
        color: #1f2937;
        margin: 0 0 12px 0;
      }

      > p {
        color: #64748b;
        margin-bottom: 32px;
      }

      .guide-steps {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-bottom: 32px;

        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;

          .step-num {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white;
            font-size: 18px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 12px;
          }

          .step-content {
            h4 {
              margin: 0 0 4px 0;
              font-size: 14px;
              color: #1f2937;
            }

            p {
              margin: 0;
              font-size: 12px;
              color: #64748b;
            }
          }
        }
      }
    }
  }
}
</style>
