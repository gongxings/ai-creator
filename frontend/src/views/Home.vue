<template>
  <div class="home flagship-page page-shell">
    <section class="page-hero home-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Creator Suite</span>
          <h1 class="hero-title">欢迎使用 AI 创作者平台</h1>
          <p class="hero-subtitle">从写作到多媒体生成，一站式提升内容创作效率。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="goToWriting">开始写作</el-button>
            <el-button @click="goToImage">生成图片</el-button>
            <el-button plain @click="goToPublish">发布管理</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">今日创作节奏</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">14</div>
              <div class="hero-stat-label">写作工具</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">5+</div>
              <div class="hero-stat-label">内容场景</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">3</div>
              <div class="hero-stat-label">多媒体能力</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ userStore.user?.credits || 0 }}</div>
              <div class="hero-stat-label">可用积分</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">文案</span>
            <span class="hero-tag">图片</span>
            <span class="hero-tag">视频</span>
            <span class="hero-tag">多平台发布</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">会员状态</div>
          <div class="value">{{ membershipLabel }}</div>
          <div class="delta">专属权益随时可用</div>
        </div>
        <div class="dashboard-card">
          <div class="label">当前积分</div>
          <div class="value">{{ userStore.user?.credits || 0 }}</div>
          <div class="delta">支持多种模型调用</div>
        </div>
        <div class="dashboard-card">
          <div class="label">内容节奏</div>
          <div class="value">高效模式</div>
          <div class="delta">多场景快速起稿</div>
        </div>
      </div>
      <StatsSection />
    </section>

    <section class="page-body">
      <div class="main-panel">
        <ToolsSection />
        <MembershipBenefits />
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">创作指挥台</h3>
          <p class="panel-subtitle">建议从高频任务开始，快速进入状态</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Check /></el-icon></div>
              <div>
                <div class="info-title">选定场景</div>
                <div class="info-desc">从工具库挑选你的写作或多媒体任务。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Check /></el-icon></div>
              <div>
                <div class="info-title">补充关键词</div>
                <div class="info-desc">加入目标受众、语气和核心卖点。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Check /></el-icon></div>
              <div>
                <div class="info-title">发布同步</div>
                <div class="info-desc">一键发布到多平台并追踪反馈。</div>
              </div>
            </div>
          </div>
        </div>
        <UserStatusCards v-if="userStore.isLoggedIn" />
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Check } from '@element-plus/icons-vue'
import UserStatusCards from '@/components/home/UserStatusCards.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import MembershipBenefits from '@/components/home/MembershipBenefits.vue'
import ToolsSection from '@/components/home/ToolsSection.vue'

const router = useRouter()
const userStore = useUserStore()

const membershipLabel = computed(() => {
  if (!userStore.isLoggedIn) return '访客'
  switch (userStore.user?.membership_type) {
    case 'basic':
      return '基础会员'
    case 'pro':
      return '专业会员'
    case 'vip':
      return 'VIP会员'
    default:
      return '免费用户'
  }
})

const goToWriting = () => router.push('/writing')
const goToImage = () => router.push('/image')
const goToPublish = () => router.push('/publish')
</script>

<style scoped lang="scss">
.home {
  background: linear-gradient(180deg, #f6f9ff 0%, #ffffff 45%);
  --hero-from: rgba(99, 102, 241, 0.18);
  --hero-to: rgba(56, 189, 248, 0.22);
  --page-accent: #4f46e5;

  .page-dashboard {
    gap: 20px;
  }

  .panel {
    background: rgba(255, 255, 255, 0.9);
  }
}

@media (max-width: 768px) {
  .home {
    .hero-title {
      font-size: 26px;
    }
  }
}
</style>
