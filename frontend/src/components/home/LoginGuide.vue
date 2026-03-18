<template>
  <div class="login-guide-section">
    <el-card class="guide-card">
      <div class="guide-content">
        <div class="guide-icon">
          <el-icon :size="64"><UserFilled /></el-icon>
        </div>
        <h2>开启你的 AI 创作之旅</h2>
        <p>登录后即可使用全部创作工具，新用户注册即可获得体验积分。</p>
        <div class="guide-actions">
          <el-button type="primary" size="large" @click="goToLogin">立即登录</el-button>
          <el-button size="large" @click="goToRegister">免费注册</el-button>
        </div>
        <div class="guide-benefits">
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>14种 AI 写作工具</span>
          </div>
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>图片、视频、PPT 一体生成</span>
          </div>
          <div class="benefit-item">
            <el-icon><Check /></el-icon>
            <span>多平台发布与管理</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Check, UserFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

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
  .guide-card {
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 28px;
    background:
      radial-gradient(520px circle at 0% 0%, rgba(255, 255, 255, 0.18), transparent 55%),
      linear-gradient(135deg, #1d4ed8 0%, #0f6cde 46%, #38bdf8 100%);
    box-shadow: 0 24px 46px rgba(37, 99, 235, 0.24);

    :deep(.el-card__body) {
      padding: 42px 30px;
    }
  }
}

.guide-content {
  text-align: center;
  color: #fff;
}

.guide-icon {
  margin-bottom: 22px;
  opacity: 0.92;
}

.guide-content h2 {
  margin-bottom: 14px;
  font-size: 34px;
  font-weight: 700;
}

.guide-content p {
  margin-bottom: 28px;
  font-size: 16px;
  line-height: 1.7;
  opacity: 0.92;
}

.guide-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-bottom: 28px;

  .el-button {
    min-width: 132px;
    border-radius: 12px;
  }
}

.guide-benefits {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.benefit-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

@media (max-width: 768px) {
  .login-guide-section .guide-card :deep(.el-card__body) {
    padding: 30px 18px;
  }

  .guide-content h2 {
    font-size: 26px;
  }

  .guide-content p {
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
    align-items: stretch;
  }
}
</style>
