<template>
  <div class="home">
    <!-- 统计数据 -->
    <StatsSection />
    <!-- 欢迎横幅 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1>欢迎使用 AI 创作者平台</h1>
        <p>从写作到多媒体生成，一站式提升内容创作效率。</p>
        <div class="welcome-benefits">
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
    </div>

    <!-- 用户状态卡片 -->
    <UserStatusCards v-if="userStore.isLoggedIn" />

    <!-- 创作工具 -->
    <ToolsSection />

    <!-- 会员权益 -->
    <MembershipBenefits />
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "@/store/user";
import { Check } from "@element-plus/icons-vue";
import UserStatusCards from "@/components/home/UserStatusCards.vue";
import StatsSection from "@/components/home/StatsSection.vue";
import MembershipBenefits from "@/components/home/MembershipBenefits.vue";
import ToolsSection from "@/components/home/ToolsSection.vue";

const userStore = useUserStore();
</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  gap: 28px;
  .welcome-section {
    text-align: center;
    padding: 30px 24px;
    background: linear-gradient(135deg, #736ae6 0%, #7c3aed 100%);
    color: #fff;
    border-radius: 16px;
    margin-bottom: 0;
    box-shadow: 0 16px 36px rgba(37, 99, 235, 0.24);

    .welcome-content {
      h1 {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
      }

      p {
        font-size: 18px;
        opacity: 0.95;
        font-weight: 400;
        margin-bottom: 32px;
      }

      .welcome-benefits {
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
  .home {
    .welcome-section {
      padding: 40px 20px;
      border-radius: 12px;

      .welcome-content {
        h1 {
          font-size: 28px;
        }

        p {
          font-size: 16px;
        }

        .welcome-benefits {
          flex-direction: column;
          gap: 16px;
        }
      }
    }
  }
}
</style>
