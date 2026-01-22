<template>
  <div class="operation-statistics">
    <el-card class="header-card">
      <h2>数据统计</h2>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="loadStatistics"
      />
    </el-card>

    <!-- 核心指标 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">总收入</div>
            <div class="metric-value">¥{{ statistics.totalRevenue.toFixed(2) }}</div>
            <div class="metric-trend" :class="{ positive: statistics.revenueTrend > 0 }">
              <el-icon v-if="statistics.revenueTrend > 0"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ Math.abs(statistics.revenueTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon users">
            <el-icon><User /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">新增用户</div>
            <div class="metric-value">{{ statistics.newUsers }}</div>
            <div class="metric-trend" :class="{ positive: statistics.usersTrend > 0 }">
              <el-icon v-if="statistics.usersTrend > 0"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ Math.abs(statistics.usersTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon members">
            <el-icon><Stamp /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">会员数</div>
            <div class="metric-value">{{ statistics.totalMembers }}</div>
            <div class="metric-trend" :class="{ positive: statistics.membersTrend > 0 }">
              <el-icon v-if="statistics.membersTrend > 0"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ Math.abs(statistics.membersTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-icon creations">
            <el-icon><Document /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">创作数</div>
            <div class="metric-value">{{ statistics.totalCreations }}</div>
            <div class="metric-trend" :class="{ positive: statistics.creationsTrend > 0 }">
              <el-icon v-if="statistics.creationsTrend > 0"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ Math.abs(statistics.creationsTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>收入趋势</span>
          </template>
          <div ref="revenueChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>用户增长</span>
          </template>
          <div ref="usersChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>创作类型分布</span>
          </template>
          <div ref="creationTypeChart" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>充值方式分布</span>
          </template>
          <div ref="paymentMethodChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>详细数据</span>
          <el-button type="primary" @click="exportData">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="收入明细" name="revenue">
          <el-table :data="revenueDetails" stripe>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="recharge_amount" label="充值金额" width="120">
              <template #default="{ row }">¥{{ row.recharge_amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="membership_amount" label="会员收入" width="120">
              <template #default="{ row }">¥{{ row.membership_amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="total_amount" label="总收入" width="120">
              <template #default="{ row }">¥{{ row.total_amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="order_count" label="订单数" width="100" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="用户数据" name="users">
          <el-table :data="userDetails" stripe>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="new_users" label="新增用户" width="100" />
            <el-table-column prop="active_users" label="活跃用户" width="100" />
            <el-table-column prop="new_members" label="新增会员" width="100" />
            <el-table-column prop="total_members" label="累计会员" width="100" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="创作数据" name="creations">
          <el-table :data="creationDetails" stripe>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="writing_count" label="写作" width="80" />
            <el-table-column prop="image_count" label="图片" width="80" />
            <el-table-column prop="video_count" label="视频" width="80" />
            <el-table-column prop="ppt_count" label="PPT" width="80" />
            <el-table-column prop="total_count" label="总计" width="80" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Money, User, Stamp, Document, CaretTop, CaretBottom, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getOperationStatistics } from '@/api/operation'

const dateRange = ref<[Date, Date]>([
  new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  new Date()
])

const statistics = ref({
  totalRevenue: 0,
  revenueTrend: 0,
  newUsers: 0,
  usersTrend: 0,
  totalMembers: 0,
  membersTrend: 0,
  totalCreations: 0,
  creationsTrend: 0
})

const activeTab = ref('revenue')
const revenueDetails = ref([])
const userDetails = ref([])
const creationDetails = ref([])

const revenueChart = ref<HTMLElement>()
const usersChart = ref<HTMLElement>()
const creationTypeChart = ref<HTMLElement>()
const paymentMethodChart = ref<HTMLElement>()

const loadStatistics = async () => {
  try {
    const [startDate, endDate] = dateRange.value
    const params = {
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    }
    
    const data = await getOperationStatistics(params)
    
    statistics.value = {
      totalRevenue: data.overview.total_revenue || 0,
      revenueTrend: data.overview.revenue_trend || 0,
      newUsers: data.overview.new_users || 0,
      usersTrend: data.overview.users_trend || 0,
      totalMembers: data.overview.total_members || 0,
      membersTrend: data.overview.members_trend || 0,
      totalCreations: data.overview.total_creations || 0,
      creationsTrend: data.overview.creations_trend || 0
    }
    
    revenueDetails.value = data.revenue_details || []
    userDetails.value = data.user_details || []
    creationDetails.value = data.creation_details || []
    
    initCharts(data)
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const initCharts = (data: any) => {
  if (revenueChart.value) {
    const chart = echarts.init(revenueChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: data.revenue_trend?.dates || []
      },
      yAxis: { type: 'value' },
      series: [{
        name: '收入',
        type: 'line',
        data: data.revenue_trend?.amounts || [],
        smooth: true,
        areaStyle: {}
      }]
    })
  }
  
  if (usersChart.value) {
    const chart = echarts.init(usersChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['新增用户', '活跃用户'] },
      xAxis: {
        type: 'category',
        data: data.user_trend?.dates || []
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '新增用户',
          type: 'bar',
          data: data.user_trend?.new_users || []
        },
        {
          name: '活跃用户',
          type: 'line',
          data: data.user_trend?.active_users || []
        }
      ]
    })
  }
  
  if (creationTypeChart.value) {
    const chart = echarts.init(creationTypeChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: '创作类型',
        type: 'pie',
        radius: '50%',
        data: data.creation_distribution || []
      }]
    })
  }
  
  if (paymentMethodChart.value) {
    const chart = echarts.init(paymentMethodChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: '充值方式',
        type: 'pie',
        radius: '50%',
        data: data.payment_distribution || []
      }]
    })
  }
}

const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped lang="scss">
.operation-statistics {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
    
    h2 {
      margin: 0 0 20px 0;
    }
  }

  .metrics-row {
    margin-bottom: 20px;
  }

  .metric-card {
    display: flex;
    align-items: center;
    padding: 20px;

    .metric-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;

      .el-icon {
        font-size: 30px;
        color: white;
      }

      &.revenue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.users {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.members {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.creations {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }

    .metric-content {
      flex: 1;

      .metric-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }

      .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 8px;
      }

      .metric-trend {
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;

        &.positive {
          color: #67c23a;
        }

        &:not(.positive) {
          color: #f56c6c;
        }
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;

    .chart {
      height: 300px;
    }
  }

  .table-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}
</style>
