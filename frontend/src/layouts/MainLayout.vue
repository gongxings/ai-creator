<template>
  <el-container class="main-layout">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-shell">
        <div class="header-left">
          <div class="logo" @click="router.push('/')">
            <img src="/logo.svg" alt="Logo" />
            <span>AI创作者</span>
          </div>
          <div class="nav-scroll">
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
        </div>

        <div class="header-right">
          <template v-if="userStore.isLoggedIn">
            <div class="right-shell">
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
                  <el-avatar :size="30" :src="userStore.user?.avatar">
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
            </div>
          </template>
          <template v-else>
            <div class="right-shell auth-shell">
              <div class="auth-actions">
                <el-button @click="router.push('/login')">登录</el-button>
                <el-button type="primary" @click="router.push('/register')">注册</el-button>
              </div>
            </div>
          </template>
        </div>
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
  padding: 0 18px;
  background: transparent;
  border-bottom: none;
  box-shadow: none;
  height: 76px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: none;

  .header-shell {
    width: 100%;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 0 14px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(37, 99, 235, 0.14);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
    backdrop-filter: blur(18px);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
    min-width: 0;

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      font-size: 18px;
      font-weight: 700;
      color: #1e3a8a;
      white-space: nowrap;
      padding: 2px 6px;
      border-radius: 10px;

      img {
        width: 30px;
        height: 30px;
        padding: 6px;
        background: rgba(37, 99, 235, 0.1);
        border-radius: 10px;
        box-shadow: 0 6px 14px rgba(37, 99, 235, 0.18);
        filter: none;
      }

      &:hover {
        opacity: 0.9;
      }
    }

    .nav-scroll {
      flex: 1;
      display: flex;
      align-items: center;
      min-width: 0;
      padding: 2px 0;
      overflow-x: auto;
      scrollbar-width: none;

      &::-webkit-scrollbar {
        display: none;
      }
    }

    .nav-menu {
      flex: 1;
      border: none;
      background: transparent;
      min-width: max-content;

      :deep(.el-menu--horizontal) {
        border-bottom: none;
        display: flex;
        align-items: center;
        height: 40px;
      }

      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        border-bottom: none;
        border-radius: 999px;
        padding: 0 16px;
        margin: 0 2px;
        height: 36px;
        line-height: 36px;
        font-weight: 600;
        color: #334155;
        transition: all 0.25s ease;
        
        &:hover {
          background-color: rgba(37, 99, 235, 0.12);
          color: #1d4ed8;
        }

        &.is-active {
          color: #ffffff;
          background: linear-gradient(135deg, #2563eb, #6366f1);
          box-shadow: 0 8px 16px rgba(37, 99, 235, 0.28);
        }
      }

      :deep(.el-sub-menu__title .el-icon) {
        margin-right: 6px;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;

    .right-shell {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 4px 6px;
      border-radius: 999px;
      border: 1px solid rgba(37, 99, 235, 0.14);
      background: rgba(15, 23, 42, 0.04);
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.6);
    }

    .credit-info {
      display: flex;
      align-items: center;
      gap: 6px;

      :deep(.el-tag) {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        height: 28px;
        line-height: 28px;
        padding: 0 12px;
        border-radius: 999px;
        border: 1px solid rgba(37, 99, 235, 0.18);
        background: rgba(37, 99, 235, 0.08);
        color: #1d4ed8;

        &:hover {
          opacity: 0.8;
        }
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 8px;
      cursor: pointer;
      border-radius: 999px;
      transition: background 0.2s ease;

      &:hover {
        background: rgba(37, 99, 235, 0.12);
      }

      .username {
        font-size: 13px;
        color: #334155;
      }
    }

    .auth-actions {
      display: flex;
      align-items: center;
      gap: 8px;

      :deep(.el-button) {
        border-radius: 999px;
        height: 32px;
        padding: 0 14px;
        font-weight: 600;
      }
    }
  }
}

.main-content {
  flex: 1;
  background: #f0f4ff;
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
    height: 70px;

    .header-shell {
      height: 52px;
      padding: 0 10px;
    }

    .header-left {
      gap: 12px;

      .logo {
        padding: 2px 6px;

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
