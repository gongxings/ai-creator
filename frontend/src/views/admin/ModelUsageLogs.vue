<template>
  <div class="model-usage">
    <!-- 统计概览 -->
    <el-card style="margin-bottom: 16px">
      <template #header>
        <div class="card-header">
          <span>调用概览</span>
          <el-button size="small" @click="loadStats" :loading="loadingStats">刷新</el-button>
        </div>
      </template>
      <el-row :gutter="16" v-if="stats">
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ stats.overview.total_calls }}</div>
            <div class="stat-label">总调用次数</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ stats.overview.today_calls }}</div>
            <div class="stat-label">今日调用</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(stats.overview.total_tokens) }}</div>
            <div class="stat-label">总 Token</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ formatNumber(stats.overview.today_tokens) }}</div>
            <div class="stat-label">今日 Token</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ stats.overview.failed_calls }}</div>
            <div class="stat-label">失败次数</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-value">{{ stats.overview.success_rate }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 筛选条件 -->
    <el-card style="margin-bottom: 16px">
      <el-row :gutter="12">
        <el-col :span="4">
          <el-select v-model="filters.provider" placeholder="厂商" clearable style="width: 100%">
            <el-option label="全部" value="" />
            <el-option v-for="p in stats?.by_provider || []" :key="p.provider" :label="p.provider" :value="p.provider" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.tool" placeholder="工具步骤" clearable style="width: 100%">
            <el-option label="全部" value="" />
            <el-option v-for="t in stats?.by_tool || []" :key="t.tool" :label="t.tool" :value="t.tool" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 100%">
            <el-option label="全部" value="" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="loadLogs">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志列表 -->
    <el-card>
      <template #header>
        <span>调用日志（共 {{ total }} 条）</span>
      </template>
      <el-table :data="logs" v-loading="loadingLogs" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="provider" label="厂商" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.provider }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型" width="160" :show-overflow-tooltip="true" />
        <el-table-column prop="tool" label="工具步骤" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.tool" size="small" type="info">{{ row.tool }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="prompt_tokens" label="输入Token" width="100" />
        <el-table-column prop="completion_tokens" label="输出Token" width="100" />
        <el-table-column prop="total_tokens" label="总Token" width="100" />
        <el-table-column prop="response_time_ms" label="响应时间" width="100">
          <template #default="{ row }">
            {{ row.response_time_ms ? `${row.response_time_ms}ms` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="loadLogs"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="调用详情" width="70%" top="5vh">
      <template v-if="detailLog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ detailLog.id }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ detailLog.user_id }}</el-descriptions-item>
          <el-descriptions-item label="AI模型ID">{{ detailLog.ai_model_id }}</el-descriptions-item>
          <el-descriptions-item label="创作ID">{{ detailLog.creation_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="厂商">{{ detailLog.provider }}</el-descriptions-item>
          <el-descriptions-item label="模型">{{ detailLog.model_name }}</el-descriptions-item>
          <el-descriptions-item label="工具步骤">{{ detailLog.tool || '-' }}</el-descriptions-item>
          <el-descriptions-item label="请求类型">{{ detailLog.request_type }}</el-descriptions-item>
          <el-descriptions-item label="输入Token">{{ detailLog.prompt_tokens }}</el-descriptions-item>
          <el-descriptions-item label="输出Token">{{ detailLog.completion_tokens }}</el-descriptions-item>
          <el-descriptions-item label="总Token">{{ detailLog.total_tokens }}</el-descriptions-item>
          <el-descriptions-item label="响应时间">{{ detailLog.response_time_ms ? `${detailLog.response_time_ms}ms` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailLog.status === 'success' ? 'success' : 'danger'" size="small">
              {{ detailLog.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时间">{{ detailLog.created_at }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>输入内容（Prompt）</el-divider>
        <el-input type="textarea" :model-value="detailLog.input_content || '无'" :rows="6" readonly />

        <el-divider>输出内容</el-divider>
        <el-input type="textarea" :model-value="detailLog.output_content || '无'" :rows="6" readonly />

        <template v-if="detailLog.error_message">
          <el-divider>错误信息</el-divider>
          <el-input type="textarea" :model-value="detailLog.error_message" :rows="3" readonly />
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsageLogs, getUsageLogDetail, getUsageStats, type UsageLogItem, type UsageStats } from '@/api/modelUsage'

const loadingStats = ref(false)
const loadingLogs = ref(false)
const stats = ref<UsageStats | null>(null)
const logs = ref<UsageLogItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = reactive({
  provider: '',
  tool: '',
  status: '',
})

const detailVisible = ref(false)
const detailLog = ref<UsageLogItem | null>(null)

const formatNumber = (num: number) => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return String(num)
}

const loadStats = async () => {
  loadingStats.value = true
  try {
    const res = await getUsageStats()
    stats.value = res.data
  } catch {
    ElMessage.error('加载统计失败')
  } finally {
    loadingStats.value = false
  }
}

const loadLogs = async () => {
  loadingLogs.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.provider) params.provider = filters.provider
    if (filters.tool) params.tool = filters.tool
    if (filters.status) params.status = filters.status
    
    const res = await getUsageLogs(params)
    logs.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch {
    ElMessage.error('加载日志失败')
  } finally {
    loadingLogs.value = false
  }
}

const resetFilters = () => {
  filters.provider = ''
  filters.tool = ''
  filters.status = ''
  currentPage.value = 1
  loadLogs()
}

const showDetail = async (log: UsageLogItem) => {
  detailLog.value = log
  detailVisible.value = true
}

onMounted(() => {
  loadStats()
  loadLogs()
})
</script>

<style scoped lang="scss">
.model-usage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 12px;
  
  .stat-value {
    font-size: 24px;
    font-weight: 600;
    color: var(--el-color-primary);
  }
  
  .stat-label {
    font-size: 13px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
