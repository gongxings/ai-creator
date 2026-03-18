<template>
  <div class="stats-section">
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-primary">
          <el-statistic title="总创作数" :value="stats.totalCreations">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-success">
          <el-statistic title="今日创作" :value="stats.todayCreations">
            <template #prefix>
              <el-icon><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-warning">
          <el-statistic title="已发布" :value="stats.published">
            <template #prefix>
              <el-icon><Upload /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-purple">
          <el-statistic title="绑定平台" :value="stats.platforms">
            <template #prefix>
              <el-icon><Link /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Calendar, Document, Link, Upload } from '@element-plus/icons-vue'
import { getCreations } from '@/api/creations'
import { getDashboardStatistics } from '@/api/operation'
import { getPlatformAccounts, getPublishHistory } from '@/api/publish'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const stats = ref({
  totalCreations: 0,
  todayCreations: 0,
  published: 0,
  platforms: 0,
})

const loadStats = async () => {
  if (!userStore.isLoggedIn) {
    return
  }

  try {
    const creationsResponse = await getCreations({ page: 1, page_size: 1 })
    stats.value.totalCreations = creationsResponse.total || 0

    try {
      const dashboardResponse = await getDashboardStatistics()
      stats.value.todayCreations = dashboardResponse.today?.generation_count || 0
    } catch {
      stats.value.todayCreations = 0
    }

    const publishResponse = await getPublishHistory({ skip: 0, limit: 1 })
    stats.value.published = publishResponse.total || 0

    const platformsResponse = await getPlatformAccounts()
    stats.value.platforms = platformsResponse.length || 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.stats-section {
  :deep(.el-row) {
    row-gap: 18px;
  }

  .stat-card {
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(37, 99, 235, 0.12);
    background: rgba(255, 255, 255, 0.82);
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(14px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;

    &::before {
      content: '';
      display: block;
      height: 4px;
      background: linear-gradient(90deg, #2563eb, #38bdf8);
    }

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 22px 40px rgba(37, 99, 235, 0.12);
      border-color: rgba(37, 99, 235, 0.2);
    }

    :deep(.el-card__body) {
      padding: 22px 20px;
    }

    :deep(.el-statistic__head) {
      margin-bottom: 12px;
      color: #64748b;
      font-size: 14px;
      font-weight: 600;
    }

    :deep(.el-statistic__content) {
      color: #0f172a;
      font-size: 32px;
      font-weight: 700;

      .el-icon {
        margin-right: 8px;
        color: #2563eb;
      }
    }
  }

  .stat-card-success::before {
    background: linear-gradient(90deg, #0f9f6e, #34d399);
  }

  .stat-card-warning::before {
    background: linear-gradient(90deg, #f59e0b, #fcd34d);
  }

  .stat-card-purple::before {
    background: linear-gradient(90deg, #2563eb, #7dd3fc);
  }
}

@media (max-width: 768px) {
  .stats-section :deep(.el-statistic__content) {
    font-size: 24px;
  }
}
</style>
