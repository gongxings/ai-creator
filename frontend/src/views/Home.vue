<template>
  <div class="home">
    <!-- 欢迎横幅 -->
<!--    <div class="welcome-section">-->
<!--      <h1>欢迎使用AI创作者平台</h1>-->
<!--      <p>让AI助力您的创作，一键生成优质内容</p>-->
<!--    </div>-->

    <!-- 统计数据 -->
    <StatsSection />

    <!-- 未登录引导 -->
    <LoginGuide />

    <!-- 用户状态卡片 -->
    <UserStatusCards v-if="userStore.isLoggedIn" />

    <!-- 会员权益 -->
    <MembershipBenefits />

    <!-- 创作工具 -->
    <ToolsSection />
<!--    <LoginGuide v-if="!userStore.isLoggedIn" />-->

<!--    &lt;!&ndash; 已登录用户内容 &ndash;&gt;-->
<!--    <template v-else>-->
<!--      -->
<!--    </template>-->
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/store/user'
import LoginGuide from '@/components/home/LoginGuide.vue'
import UserStatusCards from '@/components/home/UserStatusCards.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import MembershipBenefits from '@/components/home/MembershipBenefits.vue'
import ToolsSection from '@/components/home/ToolsSection.vue'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.home {
  .welcome-section {
    text-align: center;
    padding: 60px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-radius: 16px;
    margin-bottom: 32px;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);

    h1 {
      font-size: 42px;
      font-weight: 700;
      margin-bottom: 16px;
      letter-spacing: -0.5px;
    }

    p {
      font-size: 20px;
      opacity: 0.95;
      font-weight: 400;
    }
  }
}

@media (max-width: 768px) {
  .home {
    .welcome-section {
      padding: 40px 20px;
      border-radius: 12px;

      h1 {
        font-size: 28px;
      }

      p {
        font-size: 16px;
      }
    }
  }
}
</style>
