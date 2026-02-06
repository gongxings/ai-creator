<template>
  <div class="oauth-accounts">
    <el-card class="header-card">
      <div class="header">
        <div class="header-left">
          <h2>OAuth账号管理</h2>
          <p class="description">
            绑定AI平台账号，使用平台免费额度进行创作，无需消耗积分
          </p>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加账号
        </el-button>
      </div>
    </el-card>

    <!-- 首次使用引导 -->
    <el-card v-if="accounts.length === 0 && !loading" class="guide-card">
      <div class="guide-content">
        <el-icon class="guide-icon"><Key /></el-icon>
        <h3>欢迎使用OAuth账号管理</h3>
        <p>绑定您的AI平台账号（如豆包、通义千问），即可使用平台免费额度进行创作！</p>
        
        <div class="guide-steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-content">
              <h4>选择平台</h4>
              <p>选择要绑定的AI平台</p>
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
              <h4>开始使用</h4>
              <p>授权成功后即可免费使用</p>
            </div>
          </div>
        </div>
        
        <el-button type="primary" size="large" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          立即添加账号
        </el-button>
      </div>
    </el-card>

    <!-- 账号列表 - 桌面版表格 -->
    <el-card class="accounts-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部账号" name="all"></el-tab-pane>
        <el-tab-pane
          v-for="platform in platforms"
          :key="platform.platform_id"
          :label="platform.platform_name"
          :name="platform.platform_id"
        ></el-tab-pane>
      </el-tabs>

      <!-- 桌面版表格 -->
      <div class="table-view">
        <el-table
          v-loading="loading"
          :data="accounts"
          style="width: 100%"
          :empty-text="'暂无账号'"
        >
          <el-table-column prop="platform_name" label="平台" width="120">
            <template #default="{ row }">
              <el-tag>{{ row.platform_name }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="account_name" label="账号名称" width="150" />
          
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="配额使用" width="200">
            <template #default="{ row }">
              <div class="quota-info">
                <el-progress
                  :percentage="getQuotaPercentage(row)"
                  :color="getQuotaColor(row)"
                />
                <span class="quota-text">
                  {{ formatNumber(row.quota_used) }} / {{ formatNumber(row.quota_limit) }}
                </span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="last_used_at" label="最后使用" width="180">
            <template #default="{ row }">
              {{ row.last_used_at ? formatDate(row.last_used_at) : '未使用' }}
            </template>
          </el-table-column>
          
          <el-table-column prop="expires_at" label="过期时间" width="180">
            <template #default="{ row }">
              <span :class="{ 'text-danger': isExpiringSoon(row.expires_at) }">
                {{ formatDate(row.expires_at) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                @click="handleCheck(row)"
                :loading="checkingId === row.id"
              >
                检查
              </el-button>
              <el-button
                size="small"
                @click="handleViewUsage(row)"
              >
                使用记录
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 手机版卡片视图 -->
      <div v-if="accounts.length > 0" class="card-view">
        <div v-for="account in accounts" :key="account.id" class="account-card">
          <div class="card-header">
            <div class="header-info">
              <el-tag>{{ account.platform_name }}</el-tag>
              <span class="account-name">{{ account.account_name }}</span>
            </div>
            <el-tag :type="account.is_active ? 'success' : 'danger'">
              {{ account.is_active ? '正常' : '已禁用' }}
            </el-tag>
          </div>

          <div class="card-body">
            <div class="quota-section">
              <div class="label">配额使用情况</div>
              <el-progress
                :percentage="getQuotaPercentage(account)"
                :color="getQuotaColor(account)"
              />
              <div class="quota-text">
                {{ formatNumber(account.quota_used) }} / {{ formatNumber(account.quota_limit) }}
              </div>
            </div>

            <div class="info-row">
              <span class="label">最后使用：</span>
              <span>{{ account.last_used_at ? formatDate(account.last_used_at) : '未使用' }}</span>
            </div>

            <div class="info-row" :class="{ 'text-danger': isExpiringSoon(account.expires_at) }">
              <span class="label">过期时间：</span>
              <span>{{ formatDate(account.expires_at) }}</span>
            </div>
          </div>

          <div class="card-footer">
            <el-button
              type="text"
              size="small"
              @click="handleCheck(account)"
              :loading="checkingId === account.id"
            >
              检查
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="handleViewUsage(account)"
            >
              记录
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="handleEdit(account)"
            >
              编辑
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="handleDelete(account)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无账号" />
    </el-card>

     <!-- 添加账号对话框 -->
     <el-dialog
       v-model="showAddDialog"
       title="添加OAuth账号"
       width="600px"
       :close-on-click-modal="false"
     >
       <el-steps :active="authStep" align-center finish-status="success" class="auth-steps">
         <el-step title="选择平台" />
         <el-step title="登录授权" />
         <el-step title="完成" />
       </el-steps>

       <div class="auth-content">
         <el-form-item label="选择平台" prop="platform">
           <el-select
             v-model="addForm.platform"
             placeholder="请选择要绑定的AI平台"
             style="width: 100%"
             size="large"
           >
             <el-option
               v-for="platform in platforms"
               :key="platform.platform_id"
               :label="platform.platform_name"
               :value="platform.platform_id"
             >
               <div class="platform-option">
                 <span class="platform-name">{{ platform.platform_name }}</span>
                 <span class="platform-desc">{{ platform.description }}</span>
               </div>
             </el-option>
           </el-select>
         </el-form-item>
         
         <el-form-item label="账号名称" prop="account_name">
           <el-input
             v-model="addForm.account_name"
             placeholder="为该账号起个名字（用于识别）"
             size="large"
           />
         </el-form-item>

         <div class="auth-method-section">
           <div class="method-label">选择授权方式</div>
           <el-radio-group v-model="authMethod" size="large" class="auth-methods">
             <el-radio-button label="frontend">
               <el-icon><Chrome /></el-icon>
               前端授权（推荐）
             </el-radio-button>
             <el-radio-button label="backend">
               <el-icon><Monitor /></el-icon>
               后端授权
             </el-radio-button>
           </el-radio-group>

           <div class="method-tip">
             <el-alert
               v-if="authMethod === 'frontend'"
               type="success"
               :closable="false"
             >
               <template #title>
                 <span>前端授权：在弹出窗口中登录，自动获取Cookie</span>
               </template>
             </el-alert>
             <el-alert
               v-else
               type="info"
               :closable="false"
             >
               <template #title>
                 <span>后端授权：系统打开浏览器，在浏览器中扫码登录</span>
               </template>
             </el-alert>
           </div>
         </div>
       </div>

       <template #footer>
         <el-button @click="showAddDialog = false">取消</el-button>
         <el-button
           type="primary"
           @click="authMethod === 'frontend' ? handleFrontendAuth() : handleAdd()"
           :loading="adding"
           :disabled="!addForm.platform || !addForm.account_name"
         >
           {{ authMethod === 'frontend' ? '打开授权窗口' : '后端授权' }}
         </el-button>
       </template>
     </el-dialog>

    <!-- 编辑账号对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑账号"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="100px"
      >
        <el-form-item label="账号名称">
          <el-input v-model="editForm.account_name" />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleUpdate"
          :loading="updating"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 使用记录对话框 -->
    <el-dialog
      v-model="showUsageDialog"
      title="使用记录"
      width="900px"
    >
      <el-table
        v-loading="loadingUsage"
        :data="usageLogs"
        style="width: 100%"
        max-height="500"
      >
        <el-table-column prop="model" label="模型" width="180" />
        <el-table-column label="Tokens" width="200">
          <template #default="{ row }">
            <div class="tokens-info">
              <div>输入: {{ row.prompt_tokens }}</div>
              <div>输出: {{ row.completion_tokens }}</div>
              <div>总计: {{ row.total_tokens }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.error_message ? 'danger' : 'success'">
              {{ row.error_message ? '失败' : '成功' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              size="small"
              @click="handleViewDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="请求详情"
      width="700px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="模型">
          {{ currentLog?.model }}
        </el-descriptions-item>
        <el-descriptions-item label="Tokens">
          输入: {{ currentLog?.prompt_tokens }} | 
          输出: {{ currentLog?.completion_tokens }} | 
          总计: {{ currentLog?.total_tokens }}
        </el-descriptions-item>
        <el-descriptions-item label="时间">
          {{ formatDate(currentLog?.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="请求数据">
          <pre class="json-content">{{ formatJSON(currentLog?.request_data) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应数据" v-if="!currentLog?.error_message">
          <pre class="json-content">{{ formatJSON(currentLog?.response_data) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" v-if="currentLog?.error_message">
          <el-alert
            :title="currentLog.error_message"
            type="error"
            :closable="false"
          />
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus, Key, Chrome, Monitor } from '@element-plus/icons-vue'
import {
  getPlatforms,
  getAccounts,
  authorizeAccount,
  updateAccount,
  deleteAccount,
  checkAccountValidity,
  getUsageLogs,
  type OAuthPlatform,
  type OAuthAccount,
  type OAuthUsageLog,
} from '@/api/oauth'

// 数据
const platforms = ref<OAuthPlatform[]>([])
const accounts = ref<OAuthAccount[]>([])
const usageLogs = ref<OAuthUsageLog[]>([])
const currentLog = ref<OAuthUsageLog | null>(null)

 // 状态
const loading = ref(false)
const loadingUsage = ref(false)
const adding = ref(false)
const updating = ref(false)
const checkingId = ref<number | null>(null)
const activeTab = ref('all')
const authMethod = ref('frontend')
const authStep = ref(0)  // 授权步骤

// 授权窗口引用
const authWindow = ref<Window | null>(null)

// 对话框
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showUsageDialog = ref(false)
const showDetailDialog = ref(false)

// 表单
const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const addForm = ref({
  platform: '',
  account_name: '',
})
const editForm = ref({
  id: 0,
  account_name: '',
  is_active: true,
})

// 表单验证规则
const addFormRules: FormRules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  account_name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }],
}

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const res = await getPlatforms()
    platforms.value = res.data || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载平台列表失败')
  }
}

// 加载账号列表
const loadAccounts = async () => {
  loading.value = true
  try {
    const params = activeTab.value === 'all' ? {} : { platform: activeTab.value }
    const res = await getAccounts(params)
    accounts.value = res.data || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载账号列表失败')
  } finally {
    loading.value = false
  }
}

// 切换标签
const handleTabChange = () => {
  loadAccounts()
}

// 添加账号
const handleAdd = async () => {
  if (!addFormRef.value) return
  
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    adding.value = true
    try {
      await authorizeAccount(addForm.value)
      ElMessage.success('账号添加成功')
      showAddDialog.value = false
      addForm.value = { platform: '', account_name: '' }
      loadAccounts()
    } catch (error: any) {
      ElMessage.error(error.message || '添加账号失败')
    } finally {
      adding.value = false
    }
  })
}

// 前端授权
const handleFrontendAuth = async () => {
  if (!addForm.platform) {
    ElMessage.warning('请选择平台')
    return
  }
  
  if (!addForm.account_name) {
    ElMessage.warning('请输入账号名称')
    return
  }
  
  adding.value = true
  try {
    // 打开授权窗口
    const width = 800
    const height = 600
    const left = (window.innerWidth - width) / 2 + window.screenX
    const top = (window.innerHeight - height) / 2 + window.screenY
    
    const authUrl = `${window.location.origin}/api/v1/oauth/accounts/cookie-validate/${addForm.platform}`
    
    authWindow.value = window.open(
      authUrl,
      `oauth-${Date.now()}`,
      `width=${width},height=${height},left=${left},top=${top}`
    )
    
    // 监听来自授权窗口的消息
    const handleAuthMessage = (event: MessageEvent) => {
      // 验证消息来源
      if (event.origin !== window.location.origin) {
        return
      }
      
      const { type, platform, data } = event.data
      
      if (type === 'oauth_success') {
        ElMessage.success('授权成功！')
        
        // 关闭授权窗口
        if (authWindow.value && !authWindow.value.closed) {
          authWindow.value.close()
        }
        
        // 刷新账号列表
        loadAccounts()
        
        // 关闭对话框
        showAddDialog.value = false
        addForm.value = { platform: '', account_name: '' }
      }
    }
    
    window.addEventListener('message', handleAuthMessage)
    
    // 设置超时，5分钟后自动清理
    setTimeout(() => {
      window.removeEventListener('message', handleAuthMessage)
      if (authWindow.value && !authWindow.value.closed) {
        authWindow.value.close()
      }
      adding.value = false
    }, 5 * 60 * 1000)
    
  } catch (error: any) {
    console.error('打开授权窗口失败:', error)
    ElMessage.error('打开授权窗口失败')
    adding.value = false
  }
}

// 编辑账号
const handleEdit = (row: OAuthAccount) => {
  editForm.value = {
    id: row.id,
    account_name: row.account_name,
    is_active: row.is_active,
  }
  showEditDialog.value = true
}

// 更新账号
const handleUpdate = async () => {
  updating.value = true
  try {
    await updateAccount(editForm.value.id, {
      account_name: editForm.value.account_name,
      is_active: editForm.value.is_active,
    })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updating.value = false
  }
}

// 删除账号
const handleDelete = async (row: OAuthAccount) => {
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
    
    await deleteAccount(row.id)
    ElMessage.success('删除成功')
    loadAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 检查账号
const handleCheck = async (row: OAuthAccount) => {
  checkingId.value = row.id
  try {
    const res = await checkAccountValidity(row.id)
    if (res.data.is_valid) {
      ElMessage.success('账号有效')
    } else {
      ElMessage.warning(res.data.message || '账号无效')
    }
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '检查失败')
  } finally {
    checkingId.value = null
  }
}

// 查看使用记录
const handleViewUsage = async (row: OAuthAccount) => {
  loadingUsage.value = true
  showUsageDialog.value = true
  try {
    const res = await getUsageLogs(row.id)
    usageLogs.value = res.data || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载使用记录失败')
  } finally {
    loadingUsage.value = false
  }
}

// 查看详情
const handleViewDetail = (row: OAuthUsageLog) => {
  currentLog.value = row
  showDetailDialog.value = true
}

// 工具函数
const getQuotaPercentage = (row: OAuthAccount) => {
  if (!row.quota_limit) return 0
  return Math.round((row.quota_used / row.quota_limit) * 100)
}

const getQuotaColor = (row: OAuthAccount) => {
  const percentage = getQuotaPercentage(row)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

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

const isExpiringSoon = (dateStr: string) => {
  if (!dateStr) return false
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = diff / (1000 * 60 * 60 * 24)
  return days < 7 && days > 0
}

const formatJSON = (data: any) => {
  if (!data) return ''
  return JSON.stringify(data, null, 2)
}

// 生命周期
onMounted(() => {
  loadPlatforms()
  loadAccounts()
})

onUnmounted(() => {
  // 清理授权窗口引用
  if (authWindow.value && !authWindow.value.closed) {
    authWindow.value.close()
  }
  authWindow.value = null
})
</script>

<style scoped lang="scss">
.oauth-accounts {
  padding: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);

  :deep(.el-card) {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  }

  .header-card {
    margin-bottom: 20px;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);

    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .header-left {
        h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: #1f2937;
        }

        .description {
          margin: 0;
          color: #64748b;
          font-size: 14px;
        }
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
        color: #409eff;
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
            background: linear-gradient(135deg, #409eff, #79bbff);
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

  .accounts-card {
    // 桌面版表格
    .table-view {
      display: block;
    }

    // 手机版卡片
    .card-view {
      display: none;
    }

    .quota-info {
      .quota-text {
        display: block;
        margin-top: 5px;
        font-size: 12px;
        color: #666;
      }
    }

    .text-danger {
      color: #f56c6c;
    }
  }

  // 手机版卡片样式
  .account-card {
    background: #fff;
    border: 1px solid #edf2f7;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .header-info {
        display: flex;
        align-items: center;
        gap: 10px;

        .account-name {
          font-weight: 600;
          color: #1f2937;
        }
      }
    }

    .card-body {
      .quota-section {
        margin-bottom: 16px;
        
        .label {
          font-size: 12px;
          color: #64748b;
          margin-bottom: 8px;
        }

        .quota-text {
          font-size: 12px;
          color: #64748b;
          margin-top: 6px;
        }
      }

      .info-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        margin-bottom: 8px;
        color: #64748b;

        .label {
          color: #94a3b8;
        }
      }
    }

    .card-footer {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #f1f5f9;
      margin-top: 12px;
    }
  }

  // 添加账号对话框
  .auth-steps {
    margin-bottom: 24px;
  }

  .auth-content {
    .auth-method-section {
      margin-top: 20px;

      .method-label {
        font-size: 14px;
        color: #606266;
        margin-bottom: 12px;
      }

      .auth-methods {
        width: 100%;
        display: flex;

        :deep(.el-radio-button) {
          flex: 1;

          .el-radio-button__inner {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
          }
        }
      }

      .method-tip {
        margin-top: 12px;
      }
    }
  }

  .platform-option {
    display: flex;
    flex-direction: column;
    padding: 4px 0;

    .platform-name {
      font-weight: 500;
    }

    .platform-desc {
      font-size: 12px;
      color: #999;
      margin-top: 2px;
    }
  }

  .tokens-info {
    font-size: 12px;
    line-height: 1.5;

    div {
      color: #666;
    }
  }

  .json-content {
    max-height: 300px;
    overflow: auto;
    background: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    font-size: 12px;
    line-height: 1.5;
  }
}

// 响应式适配
@media (max-width: 992px) {
  .oauth-accounts {
    padding: 12px;

    .header-card {
      .header {
        flex-direction: column;
        gap: 12px;

        .header-left {
          h2 {
            font-size: 20px;
          }
        }
      }
    }

    .guide-card {
      .guide-content {
        padding: 24px 12px;

        .guide-steps {
          flex-direction: column;
          gap: 20px;
        }
      }
    }

    .accounts-card {
      .table-view {
        display: none;
      }

      .card-view {
        display: block;
      }
    }
  }
}
</style>
