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

const stats = ref({
  totalCreations: 0,
  todayCreations: 0,
  published: 0,
  platforms: 0,
})

const loadStats = async () => {
  // TODO: 从API加载统计数据
  stats.value = {
    totalCreations: 128,
    todayCreations: 5,
    published: 86,
    platforms: 4,
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
