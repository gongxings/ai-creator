<template>
  <div class="user-status-section">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="status-card credit-card">
          <div class="card-header">
            <el-icon class="card-icon"><Coin /></el-icon>
            <span class="card-title">我的积分</span>
          </div>
          <div class="card-content">
            <div class="main-value">{{ userStore.user?.credits || 0 }}</div>
            <el-button type="primary" size="small" @click="goToRecharge">
              立即充值
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="status-card member-card">
          <div class="card-header">
            <el-icon class="card-icon"><Trophy /></el-icon>
            <span class="card-title">会员状态</span>
          </div>
          <div class="card-content">
            <div class="member-status">
              <span v-if="userStore.user?.membership_type === 'free'" class="member-badge free">
                免费用户
              </span>
              <span v-else-if="userStore.user?.membership_type === 'basic'" class="member-badge basic">
                基础会员
              </span>
              <span v-else-if="userStore.user?.membership_type === 'pro'" class="member-badge pro">
                专业会员
              </span>
              <span v-else class="member-badge vip">
                VIP会员
              </span>
            </div>
            <el-button 
              v-if="userStore.user?.membership_type === 'free'"
              type="warning" 
              size="small" 
              @click="goToMembership"
            >
              开通会员
            </el-button>
            <div v-else class="expire-info">
              到期时间：{{ formatDate(userStore.user?.membership_expires_at) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="status-card activity-card">
          <div class="card-header">
            <el-icon class="card-icon"><Present /></el-icon>
            <span class="card-title">限时优惠</span>
          </div>
          <div class="card-content">
            <div class="activity-text">新用户首充送50%积分</div>
            <el-button type="danger" size="small" @click="goToRecharge">
              立即参与
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Coin, Trophy, Present } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const goToRecharge = () => {
  router.push('/credit/recharge')
}

const goToMembership = () => {
  router.push('/credit/membership')
}

const formatDate = (date: string | undefined) => {
  if (!date) return '未知'
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
.user-status-section {
  margin-bottom: 32px;

  .status-card {
    height: 100%;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;

      .card-icon {
        font-size: 20px;
      }

      .card-title {
        font-size: 14px;
        color: #666;
        font-weight: 500;
      }
    }

    .card-content {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .main-value {
        font-size: 32px;
        font-weight: 600;
        color: #333;
      }

      .member-status {
        .member-badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 500;

          &.free {
            background: #f0f0f0;
            color: #666;
          }

          &.basic {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
          }

          &.pro {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: #fff;
          }

          &.vip {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: #fff;
          }
        }
      }

      .expire-info {
        font-size: 12px;
        color: #999;
      }

      .activity-text {
        font-size: 14px;
        color: #333;
        font-weight: 500;
      }
    }
  }

  .credit-card {
    .card-icon {
      color: #f59e0b;
    }
  }

  .member-card {
    .card-icon {
      color: #8b5cf6;
    }
  }

  .activity-card {
    .card-icon {
      color: #ef4444;
    }
  }
}

@media (max-width: 768px) {
  .user-status-section {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }
}
</style>
