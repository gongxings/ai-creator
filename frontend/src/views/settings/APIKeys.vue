<template>
  <div class="api-keys-page flagship-page page-shell">
    <section class="page-hero api-keys-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">API Hub</span>
          <h1 class="hero-title">API Key 管理</h1>
          <p class="hero-subtitle">管理你的 API Key 与使用统计，支持多模型调用。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建 API Key
            </el-button>
            <el-button @click="loadAPIKeys">刷新列表</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">当前概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ apiKeys.length }}</div>
              <div class="hero-stat-label">API Key 数量</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ availableModels.length }}</div>
              <div class="hero-stat-label">可用模型</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ loading ? '加载中' : '就绪' }}</div>
              <div class="hero-stat-label">列表状态</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ stats ? stats.total_requests : 0 }}</div>
              <div class="hero-stat-label">累计请求</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">OpenAI 兼容</span>
            <span class="hero-tag">速率限制</span>
            <span class="hero-tag">使用统计</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">API Key 数量</div>
          <div class="value">{{ apiKeys.length }}</div>
          <div class="delta">支持多项目调用</div>
        </div>
        <div class="dashboard-card">
          <div class="label">可用模型</div>
          <div class="value">{{ availableModels.length }}</div>
          <div class="delta">覆盖多种场景</div>
        </div>
        <div class="dashboard-card">
          <div class="label">请求总量</div>
          <div class="value">{{ stats ? formatNumber(stats.total_requests) : 0 }}</div>
          <div class="delta">可查看详细统计</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-card>
      <template #header>
        <div class="card-header">
          <span>API Key 管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建 API Key
          </el-button>
        </div>
      </template>

      <el-alert
        title="什么是 API Key？"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>API Key 允许你将平台的 AI 能力通过标准的 OpenAI 兼容接口对外提供，可用于：</p>
        <ul>
          <li>集成到第三方应用（如 Cursor、Continue 等 IDE 插件）</li>
          <li>开发自己的应用程序</li>
          <li>与团队成员共享 AI 能力</li>
        </ul>
      </el-alert>

      <el-table :data="apiKeys" v-loading="loading">
        <el-table-column prop="key_name" label="名称" min-width="150" />
        <el-table-column prop="masked_key" label="API Key" min-width="200">
          <template #default="{ row }">
            <el-text class="masked-key">{{ row.masked_key }}</el-text>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rate_limit" label="速率限制" width="120">
          <template #default="{ row }">
            {{ row.rate_limit }}/分钟
          </template>
        </el-table-column>
        <el-table-column label="使用统计" width="150">
          <template #default="{ row }">
            <div>请求: {{ row.total_requests }}</div>
            <div>Token: {{ formatNumber(row.total_tokens) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="last_used_at" label="最后使用" width="180">
          <template #default="{ row }">
            {{ row.last_used_at ? formatDate(row.last_used_at) : '未使用' }}
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" width="180">
          <template #default="{ row }">
            {{ row.expires_at ? formatDate(row.expires_at) : '永不过期' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewStats(row)">
              统计
            </el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
        </el-card>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">使用建议</h3>
          <p class="panel-subtitle">合理规划 Key 提升调用效率</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Plus /></el-icon></div>
              <div>
                <div class="info-title">分场景管理</div>
                <div class="info-desc">按项目或团队创建独立 Key。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><CopyDocument /></el-icon></div>
              <div>
                <div class="info-title">及时保存</div>
                <div class="info-desc">Key 仅显示一次，请妥善保存。</div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3 class="panel-title">调用状态</h3>
          <div class="info-list">
            <div class="info-item">
              <div>
                <div class="info-title">总请求</div>
                <div class="info-desc">{{ stats ? formatNumber(stats.total_requests) : 0 }}</div>
              </div>
            </div>
            <div class="info-item">
              <div>
                <div class="info-title">总 Token</div>
                <div class="info-desc">{{ stats ? formatNumber(stats.total_tokens) : 0 }}</div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <!-- 创建 API Key 对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建 API Key" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="名称" prop="key_name">
          <el-input v-model="form.key_name" placeholder="为这个 API Key 起个名字" />
        </el-form-item>
        <el-form-item label="过期时间" prop="expires_days">
          <el-select v-model="form.expires_days" placeholder="选择过期时间">
            <el-option label="永不过期" :value="undefined" />
            <el-option label="7天" :value="7" />
            <el-option label="30天" :value="30" />
            <el-option label="90天" :value="90" />
            <el-option label="180天" :value="180" />
            <el-option label="365天" :value="365" />
          </el-select>
        </el-form-item>
        <el-form-item label="速率限制" prop="rate_limit">
          <el-input-number v-model="form.rate_limit" :min="1" :max="1000" placeholder="每分钟请求次数" />
          <span style="margin-left: 10px">次/分钟</span>
        </el-form-item>
        <el-form-item label="允许的模型">
          <el-select v-model="form.allowed_models" multiple placeholder="留空表示允许所有模型" style="width: 100%">
            <el-option v-for="model in availableModels" :key="model.model_id" :label="model.display_name" :value="model.model_id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 显示新创建的 API Key -->
    <el-dialog v-model="showKeyDialog" title="API Key 创建成功" width="600px" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-alert title="请妥善保管你的 API Key" type="warning" :closable="false" style="margin-bottom: 20px">
        这是唯一一次显示完整的 API Key，请立即复制保存。关闭后将无法再次查看。
      </el-alert>
      <el-input v-model="newApiKey" readonly type="textarea" :rows="3" style="margin-bottom: 10px" />
      <el-button type="primary" @click="copyApiKey" style="width: 100%">
        <el-icon><CopyDocument /></el-icon>
        复制 API Key
      </el-button>
      <template #footer>
        <el-button type="primary" @click="showKeyDialog = false">我已保存</el-button>
      </template>
    </el-dialog>

    <!-- 统计对话框 -->
    <el-dialog v-model="showStatsDialog" title="使用统计" width="800px">
      <div v-loading="loadingStats">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="总请求数">{{ stats?.total_requests || 0 }}</el-descriptions-item>
          <el-descriptions-item label="总Token数">{{ formatNumber(stats?.total_tokens || 0) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>按模型统计</el-divider>
        <el-table :data="modelStatsData" style="margin-bottom: 20px">
          <el-table-column prop="model" label="模型" />
          <el-table-column prop="requests" label="请求数" />
          <el-table-column prop="tokens" label="Token数" />
        </el-table>

        <el-divider>最近使用记录</el-divider>
        <el-table :data="stats?.recent_logs || []" max-height="300">
          <el-table-column prop="model_name" label="模型" width="150" />
          <el-table-column prop="endpoint" label="接口" width="200" />
          <el-table-column label="Token" width="120">
            <template #default="{ row }">
              {{ row.total_tokens }}
            </template>
          </el-table-column>
          <el-table-column prop="ip_address" label="IP地址" width="150" />
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, CopyDocument } from '@element-plus/icons-vue'
import { getAPIKeys, createAPIKey, deleteAPIKey, getAPIKeyStats } from '@/api/apiKeys'
import { getAvailableModels } from '@/api/models'
import type { APIKey, APIKeyForm, APIKeyStats, AvailableModel } from '@/types'

const loading = ref(false)
const creating = ref(false)
const loadingStats = ref(false)
const apiKeys = ref<APIKey[]>([])
const availableModels = ref<AvailableModel[]>([])
const showCreateDialog = ref(false)
const showKeyDialog = ref(false)
const showStatsDialog = ref(false)
const newApiKey = ref('')
const stats = ref<APIKeyStats | null>(null)
const formRef = ref<FormInstance>()

const form = ref<APIKeyForm>({
  key_name: '',
  expires_days: undefined,
  rate_limit: 60,
  allowed_models: []
})

const rules = {
  key_name: [
    { required: true, message: '请输入名称', trigger: 'blur' }
  ],
  rate_limit: [
    { required: true, message: '请设置速率限制', trigger: 'blur' }
  ]
}

// 模型统计数据
const modelStatsData = computed(() => {
  if (!stats.value) return []
  return Object.entries(stats.value.requests_by_model).map(([model, requests]) => ({
    model,
    requests,
    tokens: stats.value!.tokens_by_model[model] || 0
  }))
})

// 加载API Keys
const loadAPIKeys = async () => {
  loading.value = true
  try {
    const response = await getAPIKeys()
    apiKeys.value = response.api_keys
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 加载可用模型
const loadAvailableModels = async () => {
  try {
    const response = await getAvailableModels()
    availableModels.value = response.models
  } catch (error: any) {
    console.error('加载模型失败:', error)
  }
}

// 创建API Key
const handleCreate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    creating.value = true
    try {
      const response = await createAPIKey(form.value)
      newApiKey.value = response.api_key || ''
      showCreateDialog.value = false
      showKeyDialog.value = true
      await loadAPIKeys()
      ElMessage.success('创建成功')
    } catch (error: any) {
      ElMessage.error(error.message || '创建失败')
    } finally {
      creating.value = false
    }
  })
}

// 复制API Key
const copyApiKey = async () => {
  try {
    await navigator.clipboard.writeText(newApiKey.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 查看统计
const viewStats = async (row: APIKey) => {
  showStatsDialog.value = true
  loadingStats.value = true
  try {
    stats.value = await getAPIKeyStats(row.id)
  } catch (error: any) {
    ElMessage.error(error.message || '加载统计失败')
  } finally {
    loadingStats.value = false
  }
}

// 删除API Key
const handleDelete = async (row: APIKey) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 "${row.key_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAPIKey(row.id)
    await loadAPIKeys()
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 重置表单
const resetForm = () => {
  form.value = {
    key_name: '',
    expires_days: undefined,
    rate_limit: 60,
    allowed_models: []
  }
  formRef.value?.resetFields()
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadAPIKeys()
  loadAvailableModels()
})
</script>

<style scoped lang="scss">
.api-keys-page {
  padding: 20px;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .masked-key {
    font-family: monospace;
    font-size: 13px;
  }
}
</style>

