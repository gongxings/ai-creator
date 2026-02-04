<template>
  <div class="stats-section">
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="总创作数" :value="stats.totalCreations">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="今日创作" :value="stats.todayCreations">
            <template #prefix>
              <el-icon><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="已发布" :value="stats.published">
            <template #prefix>
              <el-icon><Upload /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
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
import { ref, onMounted } from 'vue'
import { Document, Calendar, Upload, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getDashboardStatistics } from '@/api/operation'
import { getCreations } from '@/api/creations'
import { getPublishHistory } from '@/api/publish'
import { getPlatformAccounts } from '@/api/publish'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const stats = ref({
  totalCreations: 0,
  todayCreations: 0,
  published: 0,
  platforms: 0,
})

const loadStats = async () => {
  // 只有登录用户才加载统计数据
  if (!userStore.isLoggedIn) {
    return
  }
  
  try {
    // 加载创作统计
    const creationsResponse = await getCreations({ page: 1, page_size: 1 })
    stats.value.totalCreations = creationsResponse.total || 0
    
    // 加载今日创作数（从dashboard统计获取）
    try {
      const dashboardResponse = await getDashboardStatistics()
      stats.value.todayCreations = dashboardResponse.today?.generation_count || 0
    } catch (error) {
      // 如果dashboard API不可用，使用默认值
      stats.value.todayCreations = 0
    }
    
    // 加载发布统计
    const publishResponse = await getPublishHistory({ page: 1, page_size: 1 })
    stats.value.published = publishResponse.total || 0
    
    // 加载绑定平台数
    const platformsResponse = await getPlatformAccounts()
    stats.value.platforms = platformsResponse.length || 0
  } catch (error: any) {
    console.error('加载统计数据失败:', error)
    // 不显示错误消息，避免干扰用户体验
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.stats-section {
  margin-bottom: 32px;

  .stat-card {
    text-align: center;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }

    :deep(.el-card__body) {
      padding: 24px;
    }

    :deep(.el-statistic) {
      .el-statistic__head {
        font-size: 14px;
        color: #666;
        margin-bottom: 12px;
        font-weight: 500;
      }

      .el-statistic__content {
        font-size: 32px;
        font-weight: 700;
        color: #333;

        .el-icon {
          color: #409eff;
          margin-right: 8px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .stats-section {
    :deep(.el-col) {
      margin-bottom: 16px;
    }

    .stat-card {
      :deep(.el-statistic) {
        .el-statistic__content {
          font-size: 24px;
        }
      }
    }
  }
}
</style>
