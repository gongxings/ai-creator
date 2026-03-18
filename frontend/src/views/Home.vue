<template>
  <div class="home">
    <StatsSection />

    <div class="welcome-section">
      <div class="welcome-content">
        <h1>欢迎使用 AI 创作者平台</h1>
        <p>从写作到多媒体生成，用一套统一的工作台提升内容创作效率与发布节奏。</p>
        <div class="welcome-benefits">
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
    </div>

    <UserStatusCards v-if="userStore.isLoggedIn" />
    <ToolsSection />
    <MembershipBenefits />
  </div>
</template>

<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import MembershipBenefits from '@/components/home/MembershipBenefits.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import ToolsSection from '@/components/home/ToolsSection.vue'
import UserStatusCards from '@/components/home/UserStatusCards.vue'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.welcome-section {
  position: relative;
  overflow: hidden;
  padding: 42px 34px;
  border-radius: 28px;
  color: #fff;
  background:
    radial-gradient(520px circle at 0% 0%, rgba(255, 255, 255, 0.2), transparent 55%),
    linear-gradient(135deg, #1d4ed8 0%, #0f6cde 44%, #38bdf8 100%);
  box-shadow: 0 24px 48px rgba(37, 99, 235, 0.24);

  &::after {
    content: '';
    position: absolute;
    inset: 18px;
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.22);
    pointer-events: none;
  }
}

.welcome-content {
  position: relative;
  z-index: 1;

  h1 {
    margin-bottom: 14px;
    font-size: 42px;
    font-weight: 700;
    letter-spacing: -0.04em;
  }

  p {
    max-width: 720px;
    margin: 0 0 28px;
    font-size: 17px;
    line-height: 1.7;
    opacity: 0.94;
  }
}

.welcome-benefits {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.benefit-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(8px);
  font-size: 14px;
}

@media (max-width: 768px) {
  .home {
    gap: 22px;
  }

  .welcome-section {
    padding: 28px 22px;
    border-radius: 22px;
  }

  .welcome-content {
    h1 {
      font-size: 30px;
    }

    p {
      margin-bottom: 20px;
      font-size: 15px;
    }
  }

  .welcome-benefits {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
