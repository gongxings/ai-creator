<template>
  <div class="traffic-stats">
    <!-- 概览卡片 -->
    <el-card class="overview-card">
      <template #header>
        <div class="card-header">
          <span>流量概览</span>
          <el-button @click="loadOverview" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ overview.today_pv }}</div>
            <div class="stat-label">今日 PV</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ overview.today_uv }}</div>
            <div class="stat-label">今日 UV</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ overview.today_new_users }}</div>
            <div class="stat-label">今日新用户</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ overview.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item secondary">
            <div class="stat-value">{{ overview.week_pv }}</div>
            <div class="stat-label">本周 PV</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item secondary">
            <div class="stat-value">{{ overview.week_uv }}</div>
            <div class="stat-label">本周 UV</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item secondary">
            <div class="stat-value">{{ overview.month_pv }}</div>
            <div class="stat-label">本月 PV</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 趋势图表 -->
    <el-card class="chart-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>访问趋势</span>
          <el-radio-group v-model="days" @change="loadDailyStats" size="small">
            <el-radio-button :value="7">7天</el-radio-button>
            <el-radio-button :value="30">30天</el-radio-button>
            <el-radio-button :value="90">90天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div ref="trendChartRef" style="height: 300px; width: 100%"></div>
    </el-card>

    <!-- 热门页面 -->
    <el-card class="hot-pages-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>热门页面 (Top 10)</span>
          <el-button @click="loadHotPages" :loading="hotLoading" size="small">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="hotPages" stripe v-loading="hotLoading" :max-height="400">
        <el-table-column prop="path" label="页面路径" min-width="200" />
        <el-table-column prop="pv" label="PV" width="100" />
        <el-table-column prop="uv" label="UV" width="100" />
        <el-table-column prop="avg_duration" label="平均停留(秒)" width="120" />
      </el-table>
    </el-card>

    <!-- 点击事件统计 -->
    <el-card class="click-events-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>点击事件统计 (Top 20)</span>
          <el-button @click="loadClickEvents" :loading="clickLoading" size="small">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="clickEvents" stripe v-loading="clickLoading" :max-height="400">
        <el-table-column prop="event_name" label="事件名称" width="180" />
        <el-table-column prop="event_target" label="目标元素" width="200" />
        <el-table-column prop="page_path" label="页面路径" min-width="200" />
        <el-table-column prop="click_count" label="点击次数" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getTrafficOverview, getDailyStats, getHotPages, getClickEvents } from '@/api/traffic'

const loading = ref(false)
const dailyLoading = ref(false)
const hotLoading = ref(false)
const clickLoading = ref(false)
const days = ref(30)

const overview = ref({
  today_pv: 0,
  today_uv: 0,
  today_new_users: 0,
  total_users: 0,
  total_creations: 0,
  week_pv: 0,
  week_uv: 0,
  month_pv: 0,
  month_uv: 0
})

const dailyStats = ref<Array<{
  date: string
  pv: number
  uv: number
  new_users: number
  active_users: number
}>>([])

const hotPages = ref<Array<{
  path: string
  pv: number
  uv: number
  avg_duration: number
}>>([])

const clickEvents = ref<Array<{
  event_name: string
  event_target: string
  page_path: string
  click_count: number
}>>([])

const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

// 加载概览数据
const loadOverview = async () => {
  loading.value = true
  try {
    const res = await getTrafficOverview()
    if (res.code === 200) {
      overview.value = res.data
    }
  } finally {
    loading.value = false
  }
}

// 加载每日统计
const loadDailyStats = async () => {
  dailyLoading.value = true
  try {
    const res = await getDailyStats(days.value)
    if (res.code === 200) {
      dailyStats.value = res.data
      renderTrendChart()
    }
  } finally {
    dailyLoading.value = false
  }
}

// 加载热门页面
const loadHotPages = async () => {
  hotLoading.value = true
  try {
    const res = await getHotPages(7, 10)
    if (res.code === 200) {
      hotPages.value = res.data
    }
  } finally {
    hotLoading.value = false
  }
}

// 加载点击事件
const loadClickEvents = async () => {
  clickLoading.value = true
  try {
    const res = await getClickEvents(7, 20)
    if (res.code === 200) {
      clickEvents.value = res.data
    }
  } finally {
    clickLoading.value = false
  }
}

// 渲染趋势图
const renderTrendChart = () => {
  if (!trendChartRef.value) return

  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }

  const dates = dailyStats.value.map(item => item.date)
  const pvData = dailyStats.value.map(item => item.pv)
  const uvData = dailyStats.value.map(item => item.uv)

  const option: echarts.EChartOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['PV', 'UV']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'PV',
        type: 'line',
        smooth: true,
        data: pvData,
        itemStyle: { color: '#409eff' }
      },
      {
        name: 'UV',
        type: 'line',
        smooth: true,
        data: uvData,
        itemStyle: { color: '#67c23a' }
      }
    ]
  }

  trendChart.setOption(option)
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  loadOverview()
  loadDailyStats()
  loadHotPages()
  loadClickEvents()
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.traffic-stats {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-item .stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-item.secondary .stat-value {
  font-size: 24px;
  color: #67c23a;
}

.stat-item .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.chart-card {
  overflow: hidden;
}
</style>
