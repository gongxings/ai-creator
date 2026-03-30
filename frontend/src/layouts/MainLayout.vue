<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <el-button class="mobile-menu-btn" :icon="Menu" @click="showMobileMenu = true" />

        <div class="logo" @click="router.push('/')">
          <img src="/logo.svg" alt="Logo" />
          <div class="logo-copy">
            <span class="logo-text">AI创作者</span>
            <span class="logo-subtitle">一体化创作工作台</span>
          </div>
        </div>

        <div class="nav-wrap">
          <el-menu :default-active="activeMenu" mode="horizontal" :ellipsis="false" router class="nav-menu">
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

            <el-sub-menu v-if="userStore.isLoggedIn" index="/content">
              <template #title>
                <el-icon><FolderOpened /></el-icon>
                <span>内容管理</span>
              </template>
              <el-menu-item index="/history">
                <el-icon><Clock /></el-icon>
                历史记录
              </el-menu-item>
              <el-menu-item index="/publish">
                <el-icon><Upload /></el-icon>
                发布管理
              </el-menu-item>
              <el-menu-item index="/templates">
                <el-icon><Files /></el-icon>
                模板管理
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu v-if="userStore.isLoggedIn" index="/credit">
              <template #title>
                <el-icon><Wallet /></el-icon>
                <span>积分会员</span>
              </template>
              <el-menu-item index="/credit/recharge">积分充值</el-menu-item>
              <el-menu-item index="/credit/membership">会员购买</el-menu-item>
              <el-menu-item index="/credit/transactions">交易记录</el-menu-item>
            </el-sub-menu>

            <el-sub-menu v-if="userStore.isAdmin" index="/operation">
              <template #title>
                <el-icon><DataAnalysis /></el-icon>
                <span>运营管理</span>
              </template>
              <el-menu-item index="/operation/activities">活动管理</el-menu-item>
              <el-menu-item index="/operation/coupons">优惠券</el-menu-item>
              <el-menu-item index="/operation/referral">推广管理</el-menu-item>
              <el-menu-item index="/operation/statistics">数据统计</el-menu-item>
              <el-menu-item index="/admin/users">用户管理</el-menu-item>
              <el-menu-item index="/admin/traffic">流量统计</el-menu-item>
              <el-menu-item index="/admin/model-usage">调用监控</el-menu-item>
            </el-sub-menu>

<!--            <el-sub-menu v-if="userStore.isAdmin" index="/admin">-->
<!--              <template #title>-->
<!--                <el-icon><User /></el-icon>-->
<!--                <span>系统管理</span>-->
<!--              </template>-->
<!--              <el-menu-item index="/admin/users">-->
<!--                <el-icon><UserFilled /></el-icon>-->
<!--                用户管理-->
<!--              </el-menu-item>-->
<!--              <el-menu-item index="/admin/traffic">-->
<!--                <el-icon><TrendCharts /></el-icon>-->
<!--                流量统计-->
<!--              </el-menu-item>-->
<!--            </el-sub-menu>-->
          </el-menu>
        </div>
      </div>

      <div class="header-right">
        <template v-if="userStore.isLoggedIn">
          <div class="credit-info">
            <el-tag v-if="userStore.user?.is_member" type="success" effect="dark">
              <el-icon><Medal /></el-icon>
              <span>会员</span>
            </el-tag>
            <el-tag type="warning" effect="plain" @click="router.push('/credit/transactions')" style="cursor: pointer;">
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
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item command="plugins">
                  <el-icon><Connection /></el-icon>
                  我的插件
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

    <el-drawer
      v-model="showMobileMenu"
      direction="ltr"
      size="280px"
      :show-close="false"
      class="mobile-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <div class="logo" @click="router.push('/'); showMobileMenu = false">
            <img src="/logo.svg" alt="Logo" />
            <span>AI创作者</span>
          </div>
        </div>
      </template>

      <div v-if="userStore.isLoggedIn" class="mobile-user-section">
        <div class="mobile-user-info">
          <el-avatar :size="48" :src="userStore.user?.avatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-detail">
            <span class="username">{{ userStore.user?.username }}</span>
            <div class="credit-tags">
              <el-tag v-if="userStore.user?.is_member" type="success" size="small" effect="dark">会员</el-tag>
              <el-tag
                type="warning"
                size="small"
                effect="plain"
                @click="router.push('/credit/transactions'); showMobileMenu = false"
                style="cursor: pointer;"
              >
                {{ userStore.user?.credits || 0 }} 积分
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <el-menu :default-active="activeMenu" class="mobile-nav-menu" @select="handleMobileMenuSelect">
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

        <template v-if="userStore.isLoggedIn">
          <el-sub-menu index="/content">
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>内容管理</span>
            </template>
            <el-menu-item index="/history">历史记录</el-menu-item>
            <el-menu-item index="/publish">发布管理</el-menu-item>
            <el-menu-item index="/templates">模板管理</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/credit">
            <template #title>
              <el-icon><Wallet /></el-icon>
              <span>积分会员</span>
            </template>
            <el-menu-item index="/credit/recharge">积分充值</el-menu-item>
            <el-menu-item index="/credit/membership">会员购买</el-menu-item>
            <el-menu-item index="/credit/transactions">交易记录</el-menu-item>
          </el-sub-menu>

          <el-sub-menu v-if="userStore.isAdmin" index="/operation">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>运营管理</span>
            </template>
            <el-menu-item index="/operation/activities">活动管理</el-menu-item>
            <el-menu-item index="/operation/coupons">优惠券</el-menu-item>
            <el-menu-item index="/operation/referral">推广管理</el-menu-item>
            <el-menu-item index="/operation/statistics">数据统计</el-menu-item>
            <el-menu-item index="/admin/users">用户管理</el-menu-item>
            <el-menu-item index="/admin/traffic">流量统计</el-menu-item>
            <el-menu-item index="/admin/model-usage">调用监控</el-menu-item>
          </el-sub-menu>

          <el-menu-item-group>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              个人设置
            </el-menu-item>
            <el-menu-item index="/plugins/my-plugins">
              <el-icon><Connection /></el-icon>
              我的插件
            </el-menu-item>
          </el-menu-item-group>
        </template>
      </el-menu>

      <div class="mobile-footer">
        <template v-if="userStore.isLoggedIn">
          <el-button type="danger" plain @click="handleMobileLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="router.push('/login'); showMobileMenu = false">登录</el-button>
          <el-button @click="router.push('/register'); showMobileMenu = false">注册</el-button>
        </template>
      </div>
    </el-drawer>

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
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  Clock,
  Connection,
  CreditCard,
  DataAnalysis,
  Document,
  Edit,
  Files,
  FolderOpened,
  Medal,
  Menu,
  Picture,
  Setting,
  SwitchButton,
  TrendCharts,
  Upload,
  User,
  UserFilled,
  VideoCamera,
  Wallet,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const showMobileMenu = ref(false)

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await userStore.updateCreditInfo()
  }
})

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/writing')) return '/writing'
  if (path.startsWith('/image')) return '/image'
  if (path.startsWith('/video')) return '/video'
  if (path.startsWith('/ppt')) return '/ppt'
  if (path.startsWith('/history')) return '/history'
  if (path.startsWith('/publish')) return '/publish'
  if (path.startsWith('/templates')) return '/templates'
  if (path.startsWith('/credit')) return path
  if (path.startsWith('/operation')) return path
  if (path.startsWith('/admin')) return path
  if (path.startsWith('/settings')) return path
  if (path.startsWith('/plugins')) return path
  return ''
})

const handleMobileMenuSelect = (index: string) => {
  router.push(index)
  showMobileMenu.value = false
}

const handleMobileLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await userStore.logout()
    ElMessage.success('已退出登录')
    showMobileMenu.value = false
    router.push('/')
  } catch {
    // 用户取消
  }
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'settings':
      router.push('/settings')
      break
    case 'plugins':
      router.push('/plugins/my-plugins')
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
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  background: transparent;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  height: 82px;
  padding: 0 22px;
  margin: 14px 14px 0;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.1);
  backdrop-filter: blur(18px) saturate(1.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  flex: 1;
  padding: 8px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.82), rgba(241, 245, 249, 0.9));
  border: 1px solid rgba(37, 99, 235, 0.08);
}

.mobile-menu-btn {
  display: none;
  border: 1px solid rgba(37, 99, 235, 0.14);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 16px;
  cursor: pointer;
  flex-shrink: 0;
  position: relative;
  transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.8);
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(37, 99, 235, 0.08);
  }

  img {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.12);
  }
}

.logo-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.logo-subtitle {
  font-size: 11px;
  color: #64748b;
}

.nav-wrap {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.nav-menu {
  background: transparent;
  border-style: none;
  border-radius: 16px;
  padding: 0;

  :deep(.el-menu) {
    border-bottom: none;
    background: transparent;
  }

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 42px;
    line-height: 42px;
    margin: 0 2px;
    padding: 0 14px;
    border-radius: 12px;
    color: #475569;
    border-bottom: none !important;
    transition: all 0.25s ease;
  }

  :deep(.el-menu-item span),
  :deep(.el-sub-menu__title span) {
    display: inline-block;
  }

  :deep(.el-sub-menu__title) {
    padding-right: 34px;
  }

  :deep(.el-sub-menu .el-sub-menu__icon-arrow) {
    right: 12px;
    margin-top: -5px;
  }

  :deep(.el-menu-item:hover),
  :deep(.el-sub-menu__title:hover) {
    color: #2563eb;
    background: rgba(255, 255, 255, 0.72);
  }

  :deep(.is-active) {
    color: #2563eb !important;
    background: #fff !important;
    box-shadow: 0 10px 10px rgba(37, 99, 235, 0.12), inset 0 0 0 1px rgba(37, 99, 235, 0.12);
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;

  :deep(.el-button) {
    border-radius: 12px;
    min-height: 40px;
  }

  :deep(.el-button--primary) {
    border: none;
    background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 48%, #38bdf8 100%);
    box-shadow: 0 10px 10px rgba(37, 99, 235, 0.2);
  }
}

.credit-info {
  display: flex;
  align-items: center;
  gap: 8px;

  .el-tag {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px;
    border-radius: 999px;
    cursor: pointer;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 16px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(37, 99, 235, 0.12);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.08);
  transition: all 0.25s ease;

  &:hover {
    background: rgba(37, 99, 235, 0.08);
  }

  .username {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #0f172a;
    font-size: 14px;
    font-weight: 600;
  }
}

.main-content {
  padding: 18px 16px 16px;
  background: transparent;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.28s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.mobile-drawer {
  :deep(.el-drawer) {
    background: rgba(245, 249, 255, 0.96);
    backdrop-filter: blur(18px);
  }

  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 18px 18px 14px;
    border-bottom: 1px solid rgba(37, 99, 235, 0.1);
  }

  :deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.drawer-header .logo {
  padding: 0;
}

.mobile-user-section {
  margin: 16px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 55%, #38bdf8 100%);
  box-shadow: 0 16px 28px rgba(37, 99, 235, 0.22);

  .mobile-user-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .user-detail {
    flex: 1;
  }

  .username {
    display: block;
    margin-bottom: 6px;
    color: #fff;
    font-size: 16px;
    font-weight: 700;
  }

  .credit-tags {
    display: flex;
    gap: 6px;
  }
}

.mobile-nav-menu {
  flex: 1;
  border: none;
  background: transparent;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;
    margin: 0 12px 4px;
    border-radius: 14px;
  }
}

.mobile-footer {
  padding: 16px;
  display: flex;
  gap: 12px;
  border-top: 1px solid rgba(37, 99, 235, 0.1);

  .el-button {
    flex: 1;
    min-height: 42px;
    border-radius: 12px;
  }
}

@media (max-width: 1280px) {
  .logo-subtitle {
    display: none;
  }

  .nav-menu {
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding: 0 12px;
      font-size: 14px;
    }
  }
}

@media (max-width: 1100px) {
  .logo-copy {
    display: none;
  }

  .credit-info .el-tag span,
  .user-info .username {
    display: none;
  }
}

@media (max-width: 768px) {
  .header {
    height: 66px;
    padding: 0 12px;
    margin: 12px 12px 0;
    border-radius: 18px;
  }

  .header-left {
    gap: 12px;
    padding: 0;
    background: transparent;
    border: none;
  }

  .mobile-menu-btn {
    display: inline-flex;
  }

  .logo {
    padding: 0;
  }

  .logo-copy,
  .nav-wrap,
  .credit-info,
  .user-info .el-icon,
  .user-info .username {
    display: none;
  }

  .main-content {
    padding: 12px;
  }

  .header-right :deep(.el-button) {
    padding: 8px 12px;
    min-height: 36px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .header {
    height: 62px;
  }

  .main-content {
    padding: 10px;
  }
}
</style>
