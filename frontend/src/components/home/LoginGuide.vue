<template>
  <div class="login-guide-section">
    <el-card class="guide-card">
      <div class="guide-content">
        <div class="guide-icon">
          <el-icon :size="64"><UserFilled /></el-icon>
        </div>
        <h2>开启您的AI创作之旅</h2>
        <p>登录后即可使用所有创作工具，新用户注册即送100积分</p>
        <div class="guide-actions">
          <el-button type="primary" size="large" @click="goToLogin">
            立即登录
          </el-button>
          <el-button size="large" @click="goToRegister">
            免费注册
          </el-button>
        </div>
        <div class="guide-benefits">
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>14种AI写作工具</span>
          </div>
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>AI图片/视频生成</span>
          </div>
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>一键多平台发布</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { UserFilled, Check } from '@element-plus/icons-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped lang="scss">
.login-guide-section {
  margin-bottom: 32px;

  .guide-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    :deep(.el-card__body) {
      padding: 48px 32px;
    }

    .guide-content {
      text-align: center;
      color: #fff;

      .guide-icon {
        margin-bottom: 24px;
        opacity: 0.9;
      }

      h2 {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 16px;
      }

      p {
        font-size: 16px;
        opacity: 0.9;
        margin-bottom: 32px;
      }

      .guide-actions {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 32px;

        .el-button {
          min-width: 120px;
        }
      }

      .guide-benefits {
        display: flex;
        justify-content: center;
        gap: 32px;
        flex-wrap: wrap;

        .benefit-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          opacity: 0.9;

          .el-icon {
            font-size: 18px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .login-guide-section {
    .guide-card {
      :deep(.el-card__body) {
        padding: 32px 16px;
      }

      .guide-content {
        h2 {
          font-size: 24px;
        }

        p {
          font-size: 14px;
        }

        .guide-actions {
          flex-direction: column;

          .el-button {
            width: 100%;
          }
        }

        .guide-benefits {
          flex-direction: column;
          gap: 16px;
        }
      }
    }
  }
}
</style>
