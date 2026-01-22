<template>
  <el-container class="main-layout">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-left">
        <div class="logo" @click="router.push('/')">
          <img src="/logo.svg" alt="Logo" />
          <span>AI创作者</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          router
          class="nav-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/writing">
            <el-icon><Edit /></el-icon>
            <span>AI写作</span>
          </el-menu-item>
          <el-menu-item index="/image">
            <el-icon><Picture /></el-icon>
            <span>图片生成</span>
          </el-menu-item>
          <el-menu-item index="/video">
            <el-icon><VideoCamera /></el-icon>
            <span>视频生成</span>
          </el-menu-item>
          <el-menu-item index="/ppt">
            <el-icon><Document /></el-icon>
            <span>PPT生成</span>
          </el-menu-item>
          <el-sub-menu v-if="userStore.isAdmin" index="/operation">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>运营管理</span>
            </template>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </el-menu-item>
            <el-menu-item index="/publish">
              <el-icon><Upload /></el-icon>
              <span>发布管理</span>
            </el-menu-item>
            <el-sub-menu index="/credit">
              <template #title>
                <el-icon><Wallet /></el-icon>
                <span>积分会员</span>
              </template>
              <el-menu-item index="/credit/recharge">积分充值</el-menu-item>
              <el-menu-item index="/credit/membership">会员购买</el-menu-item>
              <el-menu-item index="/credit/transactions">交易记录</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/operation/activities">活动管理</el-menu-item>
            <el-menu-item index="/operation/coupons">优惠券</el-menu-item>
            <el-menu-item index="/operation/referral">推广管理</el-menu-item>
            <el-menu-item index="/operation/statistics">数据统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </div>

      <div class="header-right">
        <template v-if="userStore.isLoggedIn">
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
        </template>
        <template v-else>
          <el-button @click="router.push('/login')">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Edit,
  Picture,
  VideoCamera,
  Document,
  Clock,
  Upload,
  Setting,
  User,
  ArrowDown,
  SwitchButton,
  Wallet,
  CreditCard,
  Medal,
  DataAnalysis,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return '/'
  if (path.startsWith('/writing')) return '/writing'
  if (path.startsWith('/credit')) return '/credit'
  if (path.startsWith('/operation') || path === '/history' || path === '/publish') return '/operation'
  return path
})

const handleCommand = async (command: string) => {
  switch (command) {
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
        router.push('/')
      } catch (error) {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  height: 60px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 24px;
    flex: 1;

    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      font-size: 20px;
      font-weight: 600;
      color: #1890ff;
      white-space: nowrap;

      img {
        width: 36px;
        height: 36px;
      }

      &:hover {
        opacity: 0.8;
      }
    }

    .nav-menu {
      flex: 1;
      border: none;
      background: transparent;

      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        border-bottom: 2px solid transparent;
        
        &:hover {
          background-color: rgba(24, 144, 255, 0.1);
          border-bottom-color: #1890ff;
        }

        &.is-active {
          color: #1890ff;
          border-bottom-color: #1890ff;
        }
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
  flex: 1;
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

@media (max-width: 1200px) {
  .header {
    .header-left {
      .nav-menu {
        :deep(.el-menu-item),
        :deep(.el-sub-menu__title) {
          padding: 0 12px;
          
          span {
            display: none;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;

    .header-left {
      gap: 12px;

      .logo {
        span {
          display: none;
        }
      }
    }

    .header-right {
      .credit-info {
        display: none;
      }

      .user-info {
        .username {
          display: none;
        }
      }
    }
  }

  .main-content {
    padding: 16px;
  }
}
</style>
