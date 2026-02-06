<template>
  <div class="oauth-accounts">
    <el-card class="header-card">
      <div class="header">
        <h2>OAuth账号管理</h2>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加账号
        </el-button>
      </div>
      <p class="description">
        绑定AI平台账号，使用平台免费额度进行创作，无需消耗积分
      </p>
    </el-card>

    <!-- 账号列表 -->
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
    </el-card>

     <!-- 添加账号对话框 -->
     <el-dialog
       v-model="showAddDialog"
       title="添加OAuth账号"
       width="600px"
     >
       <el-alert
         title="授权方式说明"
         type="info"
         :closable="false"
         style="margin-bottom: 20px"
       >
         <p><strong>方式1：前端授权（推荐）</strong></p>
         <ul>
           <li>点击"前端授权"按钮打开授权窗口</li>
           <li>在授权窗口中完成登录</li>
           <li>Cookie会自动获取和提交</li>
           <li>无需手动操作</li>
         </ul>
         
         <p><strong>方式2：后端浏览器授权</strong></p>
         <ul>
           <li>点击"后端授权"按钮</li>
           <li>系统自动打开浏览器</li>
           <li>在浏览器中扫码登录</li>
           <li>系统自动提取Cookie</li>
         </ul>
       </el-alert>
       
       <el-tabs v-model="authMethod">
         <el-tab-pane label="前端授权" name="frontend">
           <div class="auth-frontend">
             <el-form-item label="选择平台" prop="platform">
               <el-select
                 v-model="addForm.platform"
                 placeholder="请选择平台"
                 style="width: 100%"
               >
                 <el-option
                   v-for="platform in platforms"
                   :key="platform.platform_id"
                   :label="platform.platform_name"
                   :value="platform.platform_id"
                 >
                   <div class="platform-option">
                     <span>{{ platform.platform_name }}</span>
                     <span class="platform-desc">{{ platform.description }}</span>
                   </div>
                 </el-option>
               </el-select>
             </el-form-item>
             
             <el-form-item label="账号名称" prop="account_name">
               <el-input
                 v-model="addForm.account_name"
                 placeholder="请输入账号名称（用于识别）"
               />
             </el-form-item>
           </div>
           
           <el-button
             type="primary"
             @click="handleFrontendAuth"
             :loading="adding"
             style="width: 100%; margin-top: 20px"
             size="large"
           >
             前端授权
           </el-button>
         </el-tab-pane>
         
          <el-tab-pane label="后端授权" name="backend">
            <el-form-item label="选择平台" prop="platform">
              <el-select
                v-model="addForm.platform"
                placeholder="请选择平台"
                style="width: 100%"
              >
                <el-option
                  v-for="platform in platforms"
                  :key="platform.platform_id"
                  :label="platform.platform_name"
                  :value="platform.platform_id"
                >
                  <div class="platform-option">
                    <span>{{ platform.platform_name }}</span>
                    <span class="platform-desc">{{ platform.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="账号名称" prop="account_name">
              <el-input
                v-model="addForm.account_name"
                placeholder="请输入账号名称（用于识别）"
              />
            </el-form-item>
            
            <el-button
              type="primary"
              @click="handleAdd"
              :loading="adding"
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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

  .header-card {
    margin-bottom: 20px;

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
      }
    }

    .description {
      margin: 0;
      color: #666;
      font-size: 14px;
    }
  }

  .accounts-card {
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

  .platform-option {
    display: flex;
    flex-direction: column;

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
</style>
