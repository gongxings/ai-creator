<template>
  <div class="system-default-keys">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>系统默认APIKey管理</span>
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-statistic title="系统默认 Key 数量" :value="totalKeys">
            <template #suffix>个</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="总分配用户数" :value="totalAssignedUsers">
            <template #suffix>人</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日请求数" :value="todayRequests">
            <template #suffix>次</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日 Token 消耗" :value="todayTokens">
            <template #suffix>万</template>
          </el-statistic>
        </el-col>
      </el-row>

      <!-- APIKey 列表 -->
      <el-table :data="keys" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="key_name" label="名称" min-width="150" />
        <el-table-column prop="key_display" label="Key" width="180">
          <template #default="{ row }">
            <el-tag size="small">{{ row.key_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="提供商" width="120" />
        <el-table-column prop="model_name" label="模型" width="150" />
        <el-table-column prop="system_default_order" label="排序" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="warning">{{ row.system_default_order }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_assigned_users" label="已分配用户" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_system_default"
              type="success"
              size="small"
              @click="handleSetDefault(row)"
            >
              设为默认
            </el-button>
            <el-button
              v-else
              type="warning"
              size="small"
              @click="handleUnsetDefault(row)"
            >
              取消默认
            </el-button>
            <el-button type="info" size="small" @click="handleViewStats(row)">
              统计
            </el-button>
            <el-button type="danger" size="small" @click="handleDecrypt(row)">
              解密
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 使用统计对话框 -->
    <el-dialog v-model="statsDialogVisible" title="使用统计" width="800px">
      <el-form :inline="true">
        <el-form-item label="统计天数">
          <el-select v-model="statsDays" size="small" @change="loadKeyStats">
            <el-option label="最近 7 天" :value="7" />
            <el-option label="最近 30 天" :value="30" />
            <el-option label="最近 90 天" :value="90" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="总请求数">
          {{ currentStats.total_requests || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="总 Token 数">
          {{ (currentStats.total_tokens || 0) / 10000 }} 万
        </el-descriptions-item>
      </el-descriptions>

      <el-table :data="userBreakdown" style="margin-top: 20px">
        <el-table-column prop="user_id" label="用户 ID" width="100" />
        <el-table-column prop="requests" label="请求数" width="120" />
        <el-table-column prop="tokens" label="Token 数" />
      </el-table>
    </el-dialog>

    <!-- 解密结果对话框 -->
    <el-dialog v-model="decryptDialogVisible" title="API Key 明文" width="600px">
      <el-alert
        title="警告：请妥善保管 API Key，切勿泄露给他人！"
        type="warning"
        :closable="false"
        show-icon
      />
      <el-input
        v-model="decryptedKey"
        readonly
        type="textarea"
        :rows="3"
        style="margin-top: 20px; font-family: monospace;"
      />
      <template #footer>
        <el-button @click="copyDecryptedKey">复制</el-button>
        <el-button type="primary" @click="decryptDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSystemDefaultKeys,
  setAsSystemDefault,
  unsetSystemDefault,
  getKeyUsageStats,
  decryptApiKey
} from '@/api/systemDefaultKeys'

// 数据
const loading = ref(false)
const keys = ref<any[]>([])
const statsDialogVisible = ref(false)
const decryptDialogVisible = ref(false)
const selectedKey = ref<any>(null)
const statsDays = ref(30)
const currentStats = ref<any>({ total_requests: 0, total_tokens: 0, user_breakdown: [] })
const decryptedKey = ref('')

// 统计数据
const totalKeys = computed(() => keys.value.length)
const totalAssignedUsers = computed(() => 
  keys.value.reduce((sum, key) => sum + (key.total_assigned_users || 0), 0)
)
const todayRequests = ref(0)
const todayTokens = ref(0)

// 加载数据
const loadKeys = async () => {
  loading.value = true
  try {
    const res = await getSystemDefaultKeys()
    keys.value = res.data || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 设为系统默认
const handleSetDefault = async (row: any) => {
  try {
    const order = prompt('请输入排序值（数字越小越优先）:', '99')
    if (!order) return
    
    await setAsSystemDefault(row.id, parseInt(order))
    ElMessage.success('设置成功')
    await loadKeys()
  } catch (error: any) {
    ElMessage.error(error.message || '设置失败')
  }
}

// 取消系统默认
const handleUnsetDefault = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要取消该系统默认 Key 吗？', '提示', {
      type: 'warning'
    })
    
    await unsetSystemDefault(row.id)
    ElMessage.success('取消成功')
    await loadKeys()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败')
    }
  }
}

// 查看统计
const handleViewStats = async (row: any) => {
  selectedKey.value = row
  statsDialogVisible.value = true
  await loadKeyStats()
}

// 加载使用统计
const loadKeyStats = async () => {
  if (!selectedKey.value) return
  
  try {
    const res = await getKeyUsageStats(selectedKey.value.id, statsDays.value)
    currentStats.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载统计失败')
  }
}

// 解密 API Key
const handleDecrypt = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要解密此 API Key 吗？此操作将被记录！', '警告', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    const res = await decryptApiKey(row.id)
    decryptedKey.value = res.data.api_key
    decryptDialogVisible.value = true
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '解密失败')
    }
  }
}

// 复制解密的 Key
const copyDecryptedKey = () => {
  navigator.clipboard.writeText(decryptedKey.value)
  ElMessage.success('复制成功')
  decryptDialogVisible.value = false
}

// 刷新
const handleRefresh = () => {
  loadKeys()
}

// 用户分布数据
const userBreakdown = computed(() => currentStats.value.user_breakdown || [])

onMounted(() => {
  loadKeys()
})
</script>

<style scoped>
.system-default-keys {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 20px;
}

.box-card {
  margin-bottom: 20px;
}
</style>
