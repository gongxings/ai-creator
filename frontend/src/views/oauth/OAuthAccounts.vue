<template>
  <div class="oauth-accounts">
    <section class="page-hero">
      <div>
        <p class="eyebrow">OAuth Hub</p>
        <h1>OAuth 账号管理</h1>
        <p class="description">绑定第三方 AI 平台账号，优先使用平台免费额度，统一查看可用状态、配额和调用记录。</p>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加账号
        </el-button>
      </div>
    </section>

    <section class="summary-grid">
      <el-card class="glass-card summary-card">
        <div class="summary-label">账号总数</div>
        <div class="summary-value">{{ accounts.length }}</div>
        <div class="summary-meta">当前筛选条件下的 OAuth 账号数量</div>
      </el-card>
      <el-card class="glass-card summary-card">
        <div class="summary-label">正常可用</div>
        <div class="summary-value">{{ activeAccounts.length }}</div>
        <div class="summary-meta">仍可用于模型调用的有效账号</div>
      </el-card>
      <el-card class="glass-card summary-card">
        <div class="summary-label">支持平台</div>
        <div class="summary-value">{{ platforms.length }}</div>
        <div class="summary-meta">已开放接入的 OAuth 平台数量</div>
      </el-card>
    </section>

    <el-card v-if="accounts.length === 0 && !loading" class="glass-card guide-card">
      <div class="guide-content">
        <el-icon class="guide-icon"><Key /></el-icon>
        <h3>首次使用 OAuth 账号管理</h3>
        <p>绑定你的 AI 平台账号后，创作时可以直接走平台授权能力，减少积分消耗。</p>
        <div class="guide-steps">
          <div class="step"><div class="step-num">1</div><div class="step-content"><h4>选择平台</h4><p>选择要绑定的 AI 服务平台。</p></div></div>
          <div class="step"><div class="step-num">2</div><div class="step-content"><h4>完成授权</h4><p>在弹出窗口中登录并完成授权。</p></div></div>
          <div class="step"><div class="step-num">3</div><div class="step-content"><h4>开始使用</h4><p>授权成功后即可在创作时选择该账号。</p></div></div>
        </div>
        <el-button type="primary" size="large" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          立即添加账号
        </el-button>
      </div>
    </el-card>

    <el-card class="glass-card accounts-card">
      <template #header>
        <div class="panel-head panel-head-row">
          <div>
            <h3>账号列表</h3>
            <p>按平台筛选账号，查看配额使用、有效状态和最近调用情况。</p>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="platform-tabs">
        <el-tab-pane label="全部账号" name="all" />
        <el-tab-pane v-for="platform in platforms" :key="platform.platform_id" :label="platform.platform_name" :name="platform.platform_id" />
      </el-tabs>

      <div class="table-view">
        <el-table v-loading="loading" :data="accounts" style="width: 100%" :empty-text="'暂无账号'">
          <el-table-column prop="platform_name" label="平台" width="140">
            <template #default="{ row }"><el-tag effect="plain">{{ row.platform_name }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="account_name" label="账号名称" width="160" />
          <el-table-column label="状态" width="110">
            <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'danger'" effect="plain">{{ row.is_active ? '正常' : '已禁用' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="配额使用" min-width="240">
            <template #default="{ row }">
              <div class="quota-info">
                <el-progress :percentage="getQuotaPercentage(row)" :color="getQuotaColor(row)" />
                <span class="quota-text">{{ formatNumber(row.quota_used) }} / {{ formatNumber(row.quota_limit) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="最近使用" width="180">
            <template #default="{ row }">{{ row.last_used_at ? formatDate(row.last_used_at) : '未使用' }}</template>
          </el-table-column>
          <el-table-column label="到期时间" width="180">
            <template #default="{ row }"><span :class="{ 'text-danger': isExpiringSoon(row.expires_at) }">{{ formatDate(row.expires_at) }}</span></template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleCheck(row)" :loading="checkingId === row.id">检测</el-button>
              <el-button size="small" @click="handleViewUsage(row)">记录</el-button>
              <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="card-view">
        <div v-for="account in accounts" :key="account.id" class="account-card">
          <div class="account-top">
            <div>
              <div class="account-platform">{{ account.platform_name }}</div>
              <div class="account-name">{{ account.account_name }}</div>
            </div>
            <el-tag :type="account.is_active ? 'success' : 'danger'" effect="plain">{{ account.is_active ? '正常' : '已禁用' }}</el-tag>
          </div>
          <div class="quota-section">
            <div class="label">配额使用情况</div>
            <el-progress :percentage="getQuotaPercentage(account)" :color="getQuotaColor(account)" />
            <div class="quota-text">{{ formatNumber(account.quota_used) }} / {{ formatNumber(account.quota_limit) }}</div>
          </div>
          <div class="info-row"><span>最近使用</span><span>{{ account.last_used_at ? formatDate(account.last_used_at) : '未使用' }}</span></div>
          <div class="info-row" :class="{ 'text-danger': isExpiringSoon(account.expires_at) }"><span>到期时间</span><span>{{ formatDate(account.expires_at) }}</span></div>
          <div class="card-actions">
            <el-button size="small" @click="handleCheck(account)" :loading="checkingId === account.id">检测</el-button>
            <el-button size="small" @click="handleViewUsage(account)">记录</el-button>
            <el-button size="small" type="primary" @click="handleEdit(account)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(account)">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!loading && accounts.length === 0" description="暂无账号" />
      </div>
    </el-card>

    <el-dialog v-model="showAddDialog" title="添加 OAuth 账号" width="min(720px, 94vw)" :close-on-click-modal="false">
      <el-steps :active="authStep" align-center finish-status="success" class="auth-steps">
        <el-step title="选择平台" />
        <el-step title="登录授权" />
        <el-step title="完成绑定" />
      </el-steps>

      <el-form ref="addFormRef" :model="addForm" :rules="addFormRules" label-position="top">
        <el-form-item label="选择平台" prop="platform">
          <el-select v-model="addForm.platform" placeholder="请选择要绑定的 AI 平台" style="width: 100%" size="large">
            <el-option v-for="platform in platforms" :key="platform.platform_id" :label="platform.platform_name" :value="platform.platform_id">
              <div class="platform-option"><span class="platform-name">{{ platform.platform_name }}</span><span class="platform-desc">{{ platform.description }}</span></div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="账号名称" prop="account_name">
          <el-input v-model="addForm.account_name" placeholder="给这个账号起一个便于识别的名称" size="large" />
        </el-form-item>

        <div class="auth-method-section">
          <div class="method-label">选择授权方式</div>
          <el-radio-group v-model="authMethod" size="large" class="auth-methods">
            <el-radio-button label="frontend"><el-icon><Link /></el-icon>前端授权</el-radio-button>
            <el-radio-button label="backend"><el-icon><Monitor /></el-icon>后端授权</el-radio-button>
          </el-radio-group>
          <el-alert v-if="authMethod === 'frontend'" type="success" :closable="false" class="method-tip">前端授权会打开独立窗口，完成登录后自动回填授权结果。</el-alert>
          <el-alert v-else type="info" :closable="false" class="method-tip">后端授权会由系统发起授权流程，适合受控环境下使用。</el-alert>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="authMethod === 'frontend' ? handleFrontendAuth() : handleAdd()" :loading="adding" :disabled="!addForm.platform || !addForm.account_name">
          {{ authMethod === 'frontend' ? '打开授权窗口' : '开始授权' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑账号" width="500px">
      <el-form ref="editFormRef" :model="editForm" label-position="top">
        <el-form-item label="账号名称"><el-input v-model="editForm.account_name" /></el-form-item>
        <el-form-item label="账号状态"><el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updating">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showUsageDialog" title="使用记录" width="min(980px, 96vw)">
      <el-table v-loading="loadingUsage" :data="usageLogs" style="width: 100%" max-height="520">
        <el-table-column prop="model" label="模型" width="200" />
        <el-table-column label="Tokens" width="220">
          <template #default="{ row }"><div class="tokens-info"><div>输入：{{ row.prompt_tokens }}</div><div>输出：{{ row.completion_tokens }}</div><div>总计：{{ row.total_tokens }}</div></div></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><el-tag :type="row.error_message ? 'danger' : 'success'" effect="plain">{{ row.error_message ? '失败' : '成功' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }"><el-button size="small" @click="handleViewDetail(row)">详情</el-button></template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="请求详情" width="min(760px, 96vw)">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="模型">{{ currentLog?.model }}</el-descriptions-item>
        <el-descriptions-item label="Tokens">输入：{{ currentLog?.prompt_tokens }} | 输出：{{ currentLog?.completion_tokens }} | 总计：{{ currentLog?.total_tokens }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ formatDate(currentLog?.created_at || '') }}</el-descriptions-item>
        <el-descriptions-item label="请求数据"><pre class="json-content">{{ formatJSON(currentLog?.request_data) }}</pre></el-descriptions-item>
        <el-descriptions-item v-if="!currentLog?.error_message" label="响应数据"><pre class="json-content">{{ formatJSON(currentLog?.response_data) }}</pre></el-descriptions-item>
        <el-descriptions-item v-if="currentLog?.error_message" label="错误信息"><el-alert :title="currentLog.error_message" type="error" :closable="false" /></el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Key, Link, Monitor, Plus } from '@element-plus/icons-vue'
import { authorizeAccount, checkAccountValidity, deleteAccount, getAccounts, getPlatforms, getUsageLogs, updateAccount, type OAuthAccount, type OAuthPlatform, type OAuthUsageLog } from '@/api/oauth'

const platforms = ref<OAuthPlatform[]>([])
const accounts = ref<OAuthAccount[]>([])
const usageLogs = ref<OAuthUsageLog[]>([])
const currentLog = ref<OAuthUsageLog | null>(null)

const loading = ref(false)
const loadingUsage = ref(false)
const adding = ref(false)
const updating = ref(false)
const checkingId = ref<number | null>(null)
const activeTab = ref('all')
const authMethod = ref('frontend')
const authStep = ref(0)
const authWindow = ref<Window | null>(null)

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showUsageDialog = ref(false)
const showDetailDialog = ref(false)

const addFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const addForm = reactive({ platform: '', account_name: '' })
const editForm = reactive({ id: 0, account_name: '', is_active: true })

const addFormRules: FormRules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  account_name: [{ required: true, message: '请输入账号名称', trigger: 'blur' }],
}

const activeAccounts = computed(() => accounts.value.filter((item) => item.is_active))

let removeAuthListener: (() => void) | null = null

const loadPlatforms = async () => {
  try {
    const res = await getPlatforms()
    platforms.value = res.data || res || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载平台列表失败')
  }
}

const loadAccounts = async () => {
  loading.value = true
  try {
    const params = activeTab.value === 'all' ? {} : { platform: activeTab.value }
    const res = await getAccounts(params)
    accounts.value = res.data || res || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载账号列表失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => { loadAccounts() }

const resetAddForm = () => {
  addForm.platform = ''
  addForm.account_name = ''
  authMethod.value = 'frontend'
  authStep.value = 0
}

const handleAdd = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (!valid) return
    adding.value = true
    try {
      authStep.value = 1
      await authorizeAccount({ platform: addForm.platform, account_name: addForm.account_name })
      authStep.value = 2
      ElMessage.success('账号添加成功')
      showAddDialog.value = false
      resetAddForm()
      loadAccounts()
    } catch (error: any) {
      ElMessage.error(error.message || '添加账号失败')
    } finally {
      adding.value = false
    }
  })
}

const cleanupAuthListener = () => {
  if (removeAuthListener) {
    removeAuthListener()
    removeAuthListener = null
  }
}

const handleFrontendAuth = async () => {
  if (!addForm.platform) return ElMessage.warning('请选择平台')
  if (!addForm.account_name) return ElMessage.warning('请输入账号名称')

  adding.value = true
  authStep.value = 1
  try {
    const width = 860
    const height = 680
    const left = (window.innerWidth - width) / 2 + window.screenX
    const top = (window.innerHeight - height) / 2 + window.screenY
    const authUrl = `${window.location.origin}/api/v1/oauth/accounts/cookie-validate/${addForm.platform}`
    authWindow.value = window.open(authUrl, `oauth-${Date.now()}`, `width=${width},height=${height},left=${left},top=${top}`)

    const handleAuthMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return
      const { type } = event.data || {}
      if (type === 'oauth_success') {
        authStep.value = 2
        ElMessage.success('授权成功')
        if (authWindow.value && !authWindow.value.closed) authWindow.value.close()
        showAddDialog.value = false
        resetAddForm()
        loadAccounts()
        cleanupAuthListener()
        adding.value = false
      }
    }

    window.addEventListener('message', handleAuthMessage)
    removeAuthListener = () => window.removeEventListener('message', handleAuthMessage)

    setTimeout(() => {
      cleanupAuthListener()
      if (authWindow.value && !authWindow.value.closed) authWindow.value.close()
      adding.value = false
    }, 5 * 60 * 1000)
  } catch (error: any) {
    console.error('打开授权窗口失败:', error)
    ElMessage.error('打开授权窗口失败')
    adding.value = false
  }
}

const handleEdit = (row: OAuthAccount) => {
  editForm.id = row.id
  editForm.account_name = row.account_name
  editForm.is_active = row.is_active
  showEditDialog.value = true
}

const handleUpdate = async () => {
  updating.value = true
  try {
    await updateAccount(editForm.id, { account_name: editForm.account_name, is_active: editForm.is_active })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updating.value = false
  }
}

const handleDelete = async (row: OAuthAccount) => {
  try {
    await ElMessageBox.confirm(`确认删除账号“${row.account_name}”吗？`, '确认删除', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
    await deleteAccount(row.id)
    ElMessage.success('删除成功')
    loadAccounts()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
  }
}

const handleCheck = async (row: OAuthAccount) => {
  checkingId.value = row.id
  try {
    const res = await checkAccountValidity(row.id)
    const result = res.data || res
    if (result.is_valid) ElMessage.success('账号有效')
    else ElMessage.warning(result.message || '账号无效')
    loadAccounts()
  } catch (error: any) {
    ElMessage.error(error.message || '检测失败')
  } finally {
    checkingId.value = null
  }
}

const handleViewUsage = async (row: OAuthAccount) => {
  loadingUsage.value = true
  showUsageDialog.value = true
  try {
    const res = await getUsageLogs(row.id)
    usageLogs.value = res.data || res || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载使用记录失败')
  } finally {
    loadingUsage.value = false
  }
}

const handleViewDetail = (row: OAuthUsageLog) => {
  currentLog.value = row
  showDetailDialog.value = true
}

const getQuotaPercentage = (row: OAuthAccount) => row.quota_limit ? Math.round((row.quota_used / row.quota_limit) * 100) : 0
const getQuotaColor = (row: OAuthAccount) => { const p = getQuotaPercentage(row); if (p >= 90) return '#ef4444'; if (p >= 70) return '#f59e0b'; return '#10b981' }
const formatNumber = (num: number) => num >= 1000000 ? `${(num / 1000000).toFixed(1)}M` : num >= 1000 ? `${(num / 1000).toFixed(1)}K` : `${num || 0}`
const formatDate = (dateStr: string) => { if (!dateStr) return '-'; const date = new Date(dateStr); return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }
const isExpiringSoon = (dateStr: string) => { if (!dateStr) return false; const days = (new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24); return days < 7 && days > 0 }
const formatJSON = (data: any) => data ? JSON.stringify(data, null, 2) : ''

onMounted(() => { loadPlatforms(); loadAccounts() })
onUnmounted(() => { cleanupAuthListener(); if (authWindow.value && !authWindow.value.closed) authWindow.value.close(); authWindow.value = null })
</script>

<style scoped lang="scss">
.oauth-accounts{display:flex;flex-direction:column;gap:24px;padding:28px}.page-hero{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;padding:30px;border:1px solid rgba(148,163,184,.2);border-radius:30px;background:radial-gradient(circle at top right,rgba(125,211,252,.38),transparent 28%),linear-gradient(135deg,rgba(239,246,255,.94),rgba(255,255,255,.92));box-shadow:0 24px 60px rgba(15,23,42,.08)}.eyebrow{margin:0 0 10px;font-size:13px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#2563eb}.page-hero h1{margin:0;font-size:clamp(30px,4vw,42px);color:#12304a}.description{margin:14px 0 0;max-width:760px;font-size:15px;line-height:1.75;color:#60758e}.summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.glass-card{border:1px solid rgba(148,163,184,.2);border-radius:26px;background:rgba(255,255,255,.9);box-shadow:0 20px 44px rgba(15,23,42,.07)}.summary-label{font-size:13px;color:#6b7280}.summary-value{margin-top:12px;font-size:34px;font-weight:700;color:#12304a}.summary-meta{margin-top:10px;font-size:13px;line-height:1.6;color:#7c8da0}.guide-content{text-align:center;padding:40px 20px}.guide-icon{font-size:64px;color:#2563eb}.guide-content h3{margin:18px 0 10px;color:#12304a}.guide-content p{margin:0 auto;max-width:680px;color:#60758e;line-height:1.7}.guide-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:28px 0}.step{padding:18px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(180deg,rgba(248,250,252,.96),rgba(239,246,255,.82))}.step-num{width:40px;height:40px;margin:0 auto 12px;border-radius:999px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff;background:linear-gradient(135deg,#2563eb,#38bdf8)}.step-content h4{margin:0 0 4px;color:#12304a}.step-content p{font-size:13px}.panel-head{display:flex;justify-content:space-between;gap:16px}.panel-head h3{margin:0;font-size:20px;color:#12304a}.panel-head p{margin:8px 0 0;font-size:14px;color:#62748a}.platform-tabs{margin-bottom:12px}.quota-info .quota-text,.quota-section .quota-text{display:block;margin-top:8px;font-size:12px;color:#64748b}.table-view{display:block}.card-view{display:none}.account-card{padding:18px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(180deg,rgba(248,250,252,.96),rgba(239,246,255,.82));margin-bottom:14px}.account-top,.info-row,.card-actions{display:flex;justify-content:space-between;align-items:center;gap:12px}.account-platform{font-size:18px;font-weight:700;color:#12304a}.account-name{margin-top:6px;font-size:14px;color:#64748b}.quota-section{margin:16px 0}.label{font-size:12px;color:#64748b;margin-bottom:8px}.info-row{font-size:13px;color:#64748b;margin-bottom:8px}.card-actions{flex-wrap:wrap;margin-top:14px;padding-top:12px;border-top:1px solid rgba(148,163,184,.18)}.auth-steps{margin-bottom:24px}.auth-method-section{margin-top:20px}.method-label{margin-bottom:12px;font-size:14px;color:#606266}.auth-methods{display:flex;width:100%}.auth-methods :deep(.el-radio-button){flex:1}.auth-methods :deep(.el-radio-button__inner){width:100%;display:flex;align-items:center;justify-content:center;gap:8px}.method-tip{margin-top:12px}.platform-option{display:flex;flex-direction:column;padding:4px 0}.platform-name{font-weight:500}.platform-desc{margin-top:2px;font-size:12px;color:#999}.tokens-info{font-size:12px;line-height:1.6}.json-content{max-height:320px;overflow:auto;padding:12px;border-radius:14px;background:#f8fafc;font-size:12px;line-height:1.6}.text-danger{color:#ef4444}@media (max-width:1080px){.summary-grid,.guide-steps{grid-template-columns:1fr}}@media (max-width:768px){.oauth-accounts{padding:16px}.page-hero,.panel-head,.hero-actions{flex-direction:column;align-items:flex-start}.table-view{display:none}.card-view{display:block}.summary-grid{grid-template-columns:1fr}}
</style>
