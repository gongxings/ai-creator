<template>
  <div class="api-monitor">
    <!-- 概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总请求数（{{ overviewData.period_days }}天）" :value="overviewData.total_requests">
            <template #suffix>次</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总 Token 消耗" :value="(overviewData.total_tokens / 10000).toFixed(2)">
            <template #suffix>万</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="活跃用户数" :value="overviewData.active_users">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="系统默认 Key 数量" :value="overviewData.total_keys">
            <template #suffix>个</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>每日请求趋势</span>
            <el-select v-model="trendDays" size="small" @change="loadDailyStats" style="float: right;">
              <el-option label="最近 7 天" :value="7" />
              <el-option label="最近 30 天" :value="30" />
            </el-select>
          </template>
          <div ref="trendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Top 模型排行</span>
          </template>
          <el-table :data="topModels" height="300">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="model_name" label="模型名称" min-width="150" />
            <el-table-column prop="request_count" label="请求数" width="120" />
            <el-table-column prop="token_count" label="Token 数" width="120">
              <template #default="{ row }">
                {{ (row.token_count / 1000).toFixed(1) }}k
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 错误分析 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>错误分析</span>
          <el-select v-model="errorDays" size="small" @change="loadErrorAnalysis">
            <el-option label="最近 7 天" :value="7" />
            <el-option label="最近 14 天" :value="14" />
          </el-select>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总错误数">{{ errorData.total_errors }}</el-descriptions-item>
            <el-descriptions-item label="错误率">
              <el-tag :type="getErrorType(errorData.error_rate)">
                {{ errorData.error_rate }}%
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <h4 style="margin-top: 20px;">错误类型分布</h4>
          <el-table :data="errorData.error_types" size="small">
            <el-table-column prop="status_code" label="状态码" width="100" />
            <el-table-column prop="count" label="次数" width="100" />
            <el-table-column prop="percentage" label="占比">
              <template #default="{ row }">
                <el-progress :percentage="row.percentage" :stroke-width="10" />
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="12">
          <h4>Top 错误信息</h4>
          <el-table :data="errorData.top_errors" size="small" max-height="300">
            <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
            <el-table-column prop="count" label="次数" width="80" />
            <el-table-column prop="percentage" label="占比" width="100" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <!-- 使用日志 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>使用日志</span>
          <el-button size="small" @click="loadUsageLogs">刷新</el-button>
        </div>
      </template>

      <el-table :data="usageLogs" v-loading="logsLoading" max-height="400">
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="key_name" label="API Key" width="150" />
        <el-table-column prop="model_name" label="模型" width="120" />
        <el-table-column prop="endpoint" label="端点" min-width="150" />
        <el-table-column prop="total_tokens" label="Token 数" width="100" />
        <el-table-column prop="status_code" label="状态码" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status_code)">
              {{ row.status_code || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_time" label="响应时间" width="100">
          <template #default="{ row }">
            {{ row.response_time }}ms
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  getMonitorOverview,
  getDailyStats,
  getErrorAnalysis,
  getUserUsage
} from '@/api/apiMonitor'

// 数据
const overviewData = reactive({
  total_requests: 0,
  total_tokens: 0,
  active_users: 0,
  total_keys: 0,
  avg_daily_requests: 0,
  period_days: 7,
  top_models: []
})

const trendDays = ref(7)
const trendChart = ref<ECharts | null>(null)
const dailyStats = ref<any[]>([])
const topModels = ref<any[]>([])

const errorDays = ref(7)
const errorData = reactive({
  total_errors: 0,
  error_rate: 0,
  period_days: 7,
  error_types: [],
  top_errors: []
})

const usageLogs = ref<any[]>([])
const logsLoading = ref(false)

// 加载概览数据
const loadOverview = async () => {
  try {
    const res = await getMonitorOverview(7)
    Object.assign(overviewData, res.data)
    topModels.value = res.data.top_models || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载概览失败')
  }
}

// 加载每日趋势
const loadDailyStats = async () => {
  try {
    const res = await getDailyStats(trendDays.value)
    dailyStats.value = res.data
    
    nextTick(() => {
      renderTrendChart()
    })
  } catch (error: any) {
    ElMessage.error(error.message || '加载趋势失败')
  }
}

// 渲染趋势图表
const renderTrendChart = () => {
  if (!trendChart.value) return
  
  const dates = dailyStats.value.map((item: any) => item.date)
  const requests = dailyStats.value.map((item: any) => item.requests)
  const users = dailyStats.value.map((item: any) => item.active_users)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['请求数', '活跃用户']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '请求数'
      },
      {
        type: 'value',
        name: '活跃用户'
      }
    ],
    series: [
      {
        name: '请求数',
        type: 'line',
        data: requests,
        smooth: true
      },
      {
        name: '活跃用户',
        type: 'line',
        yAxisIndex: 1,
        data: users,
        smooth: true
      }
    ]
  }
  
  trendChart.value.setOption(option)
}

// 加载错误分析
const loadErrorAnalysis = async () => {
  try {
    const res = await getErrorAnalysis(errorDays.value)
    Object.assign(errorData, res.data)
  } catch (error: any) {
    ElMessage.error(error.message || '加载错误分析失败')
  }
}

// 加载使用日志
const loadUsageLogs = async () => {
  logsLoading.value = true
  try {
    const res = await getUserUsage({
      days: 7,
      page: 1,
      page_size: 50
    })
    usageLogs.value = res.data.logs
  } catch (error: any) {
    ElMessage.error(error.message || '加载日志失败')
  } finally {
    logsLoading.value = false
  }
}

// 辅助函数
const getErrorType = (rate: number) => {
  if (rate < 1) return 'success'
  if (rate < 5) return 'warning'
  return 'danger'
}

const getStatusType = (code: number | null) => {
  if (!code) return 'info'
  if (code >= 200 && code < 300) return 'success'
  if (code >= 400 && code < 500) return 'warning'
  return 'danger'
}

// 初始化图表
onMounted(() => {
  loadOverview()
  loadDailyStats()
  loadErrorAnalysis()
  loadUsageLogs()
  
  // 初始化 ECharts
  nextTick(() => {
    if (trendChart.value) {
      trendChart.value = echarts.init(trendChart.value)
      
      window.addEventListener('resize', () => {
        trendChart.value?.resize()
      })
    }
  })
})
</script>

<style scoped>
.api-monitor {
  padding: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h4 {
  margin: 15px 0 10px 0;
  font-size: 14px;
  color: #606266;
}
</style>
