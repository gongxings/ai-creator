<template>
  <div class="traffic-stats">
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

    <el-card class="daily-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>每日统计</span>
          <el-radio-group v-model="days" @change="loadDailyStats" size="small">
            <el-radio-button :value="7">7天</el-radio-button>
            <el-radio-button :value="30">30天</el-radio-button>
            <el-radio-button :value="90">90天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <el-table :data="dailyStats" stripe v-loading="dailyLoading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="pv" label="PV" width="100" />
        <el-table-column prop="uv" label="UV" width="100" />
        <el-table-column prop="new_users" label="新用户" width="100" />
        <el-table-column prop="active_users" label="活跃用户" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTrafficOverview, getDailyStats } from '@/api/traffic'

const loading = ref(false)
const dailyLoading = ref(false)
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

const loadDailyStats = async () => {
  dailyLoading.value = true
  try {
    const res = await getDailyStats(days.value)
    if (res.code === 200) {
      dailyStats.value = res.data
    }
  } finally {
    dailyLoading.value = false
  }
}

onMounted(() => {
  loadOverview()
  loadDailyStats()
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
</style>
