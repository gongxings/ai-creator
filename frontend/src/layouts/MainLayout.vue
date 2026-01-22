<template>
  <el-container class="main-layout">
    <el-aside :width="collapsed ? '64px' : '240px'" class="sidebar">
      <div class="logo">
        <img v-if="!collapsed" src="/logo.svg" alt="Logo" />
        <span v-if="!collapsed">AI创作者</span>
        <el-icon v-else><Promotion /></el-icon>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :unique-opened="true"
        router
      >
        <el-menu-item index="/writing">
          <el-icon><Edit /></el-icon>
          <template #title>AI写作</template>
        </el-menu-item>

        <el-menu-item index="/image">
          <el-icon><Picture /></el-icon>
          <template #title>图片生成</template>
        </el-menu-item>

        <el-menu-item index="/video">
          <el-icon><VideoCamera /></el-icon>
          <template #title>视频生成</template>
        </el-menu-item>

        <el-menu-item index="/ppt">
          <el-icon><Document /></el-icon>
          <template #title>PPT生成</template>
        </el-menu-item>

        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <template #title>历史记录</template>
        </el-menu-item>

        <el-menu-item index="/publish">
          <el-icon><Upload /></el-icon>
          <template #title>发布管理</template>
        </el-menu-item>

        <el-sub-menu index="/credit">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>积分会员</span>
          </template>
          <el-menu-item index="/credit/recharge">
            <el-icon><CreditCard /></el-icon>
            <template #title>积分充值</template>
          </el-menu-item>
          <el-menu-item index="/credit/membership">
            <el-icon><Medal /></el-icon>
            <template #title>会员购买</template>
          </el-menu-item>
          <el-menu-item index="/credit/transactions">
            <el-icon><List /></el-icon>
            <template #title>交易记录</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/operation">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>运营管理</span>
          </template>
          <el-menu-item index="/operation/activities">
            <el-icon><Present /></el-icon>
            <template #title>活动管理</template>
          </el-menu-item>
          <el-menu-item index="/operation/coupons">
            <el-icon><Ticket /></el-icon>
            <template #title>优惠券</template>
          </el-menu-item>
          <el-menu-item index="/operation/referral">
            <el-icon><Share /></el-icon>
            <template #title>推广管理</template>
          </el-menu-item>
          <el-menu-item index="/operation/statistics">
            <el-icon><TrendCharts /></el-icon>
            <template #title>数据统计</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 积分和会员状态 -->
          <div class="credit-info">
            <el-tag v-if="userStore.user?.is_member" type="success" effect="dark">
              <el-icon><Medal /></el-icon>
              <span>会员</span>
            </el-tag>
            <el-tag type="warning" effect="plain">
              <el-icon><CreditCard /></el-icon>
              <span>{{ userStore.user?.credits || 0 }} 积分</span>
            </el-tag>
          </div>

          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar">
                {{ userStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit,
  Picture,
  VideoCamera,
  Document,
  Clock,
  Upload,
  Setting,
  Fold,
  Expand,
  User,
  ArrowDown,
  SwitchButton,
  Promotion,
  Wallet,
  CreditCard,
  Medal,
  List,
  DataAnalysis,
  Present,
  Ticket,
  Share,
  TrendCharts,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/writing')) return '/writing'
  return path
})

const breadcrumbs = computed(() => {
  const items = []
  const matched = route.matched.filter((item) => item.meta && item.meta.title)

  matched.forEach((item) => {
    items.push({
      path: item.path,
      title: item.meta.title as string,
    })
  })

  return items
})

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/settings')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        await userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
      break
  }
}

// 监听路由变化，自动收起移动端侧边栏
watch(
  () => route.path,
  () => {
    if (window.innerWidth < 768) {
      collapsed.value = true
    }
  }
)
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.sidebar {
  background: #001529;
  transition: width 0.3s;

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 64px;
    padding: 0 16px;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    img {
      width: 32px;
      height: 32px;
      margin-right: 12px;
    }

    .el-icon {
      font-size: 32px;
    }
  }

  :deep(.el-menu) {
    border-right: none;
    background: #001529;

    .el-menu-item {
      color: rgba(255, 255, 255, 0.65);

      &:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.08);
      }

      &.is-active {
        color: #fff;
        background: #1890ff;
      }
    }
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-icon {
      font-size: 20px;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: #1890ff;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .credit-info {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 6px 12px;
        cursor: pointer;

        &:hover {
          opacity: 0.8;
        }
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      cursor: pointer;
      border-radius: 4px;
      transition: background 0.3s;

      &:hover {
        background: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
  }

  .header {
    padding: 0 16px;

    .header-left {
      .el-breadcrumb {
        display: none;
      }
    }
  }

  .main-content {
    padding: 16px;
  }
}
</style>
