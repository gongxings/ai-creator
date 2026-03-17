<template>
  <el-container class="main-layout">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-left">
        <!-- 移动端汉堡菜单按钮 -->
        <el-button 
          class="mobile-menu-btn" 
          :icon="Menu" 
          @click="showMobileMenu = true"
        />
        
        <div class="logo" @click="router.push('/')">
          <img src="/logo.svg" alt="Logo" />
          <span class="logo-text">AI创作者</span>
        </div>
        
        <!-- PC端导航菜单 -->
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
          
          <!-- AI创作相关 - 一级菜单 -->
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
          
          <!-- 内容管理 子菜单 (登录后显示) -->
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
          
          <!-- 积分会员 子菜单 (登录后显示) -->
          <el-sub-menu v-if="userStore.isLoggedIn" index="/credit">
            <template #title>
              <el-icon><Wallet /></el-icon>
              <span>积分会员</span>
            </template>
            <el-menu-item index="/credit/recharge">积分充值</el-menu-item>
            <el-menu-item index="/credit/membership">会员购买</el-menu-item>
            <el-menu-item index="/credit/transactions">交易记录</el-menu-item>
          </el-sub-menu>
          
          <!-- 运营管理 子菜单 (管理员显示) -->
          <el-sub-menu v-if="userStore.isAdmin" index="/operation">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>运营管理</span>
            </template>
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
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item command="plugins">
                  <el-icon><Connection /></el-icon>
                  我的插件
                </el-dropdown-item>
<!--                <el-dropdown-item command="api-keys">-->
<!--                  <el-icon><Key /></el-icon>-->
<!--                  API密钥-->
<!--                </el-dropdown-item>-->
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

    <!-- 移动端抽屉导航 -->
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
      
      <!-- 移动端用户信息 -->
      <div v-if="userStore.isLoggedIn" class="mobile-user-section">
        <div class="mobile-user-info">
          <el-avatar :size="48" :src="userStore.user?.avatar">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-detail">
            <span class="username">{{ userStore.user?.username }}</span>
            <div class="credit-tags">
              <el-tag v-if="userStore.user?.is_member" type="success" size="small" effect="dark">会员</el-tag>
              <el-tag type="warning" size="small" effect="plain">{{ userStore.user?.credits || 0 }} 积分</el-tag>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 移动端菜单 -->
      <el-menu
        :default-active="activeMenu"
        class="mobile-nav-menu"
        @select="handleMobileMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <!-- AI创作相关 - 一级菜单 -->
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
<!--            <el-menu-item index="/settings/api-keys">-->
<!--              <el-icon><Key /></el-icon>-->
<!--              API密钥-->
<!--            </el-menu-item>-->
          </el-menu-item-group>
        </template>
      </el-menu>
      
      <!-- 移动端底部操作 -->
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
import { ref, computed } from 'vue'
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
  ArrowDown,
  SwitchButton,
  Wallet,
  CreditCard,
  Medal,
  DataAnalysis,
  Connection,
  Key,
  Files,
  Menu,
  FolderOpened,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 移动端菜单状态
const showMobileMenu = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return '/'
  // AI创作相关
  if (path.startsWith('/writing')) return '/writing'
  if (path.startsWith('/image')) return '/image'
  if (path.startsWith('/video')) return '/video'
  if (path.startsWith('/ppt')) return '/ppt'
  // 内容管理相关
  if (path.startsWith('/history')) return '/history'
  if (path.startsWith('/publish')) return '/publish'
  if (path.startsWith('/templates')) return '/templates'
  // 积分会员
  if (path.startsWith('/credit')) return path
  // 运营管理
  if (path.startsWith('/operation')) return path
  // 设置
  if (path.startsWith('/settings')) return path
  if (path.startsWith('/plugins')) return path
  return path
})

// 移动端菜单选择
const handleMobileMenuSelect = (index: string) => {
  router.push(index)
  showMobileMenu.value = false
}

// 移动端退出登录
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
  } catch (error) {
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
    case 'oauth':
      router.push('/settings/oauth')
      break
    case 'api-keys':
      router.push('/settings/api-keys')
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
  overflow-x: hidden;
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
  min-width: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
    min-width: 0;
    overflow: hidden;

    .mobile-menu-btn {
      display: none;
      flex-shrink: 0;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      font-size: 18px;
      font-weight: 600;
      color: #1890ff;
      white-space: nowrap;
      flex-shrink: 0;

      img {
        width: 32px;
        height: 32px;
      }

      &:hover {
        opacity: 0.8;
      }
    }

    .nav-menu {
      flex: 1;
      min-width: 0;
      border: none;
      background: transparent;
      overflow-x: auto;
      overflow-y: hidden;
      
      // 隐藏滚动条但保留滚动功能
      &::-webkit-scrollbar {
        display: none;
      }
      -ms-overflow-style: none;
      scrollbar-width: none;

      :deep(.el-menu-item),
      :deep(.el-sub-menu__title) {
        border-bottom: 2px solid transparent;
        height: 58px;
        line-height: 58px;
        padding: 0 16px;
        
        &:hover {
          background-color: rgba(24, 144, 255, 0.1);
          border-bottom-color: #1890ff;
        }

        &.is-active {
          color: #1890ff;
          border-bottom-color: #1890ff;
        }
      }
      
      :deep(.el-sub-menu) {
        .el-sub-menu__title {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;

    .credit-info {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
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
      padding: 6px 10px;
      cursor: pointer;
      border-radius: 4px;
      transition: background 0.3s;

      &:hover {
        background: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}

.main-content {
  flex: 1;
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 移动端抽屉样式
.mobile-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  :deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.drawer-header {
  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    font-size: 18px;
    font-weight: 600;
    color: #1890ff;

    img {
      width: 32px;
      height: 32px;
    }
  }
}

.mobile-user-section {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .mobile-user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .user-detail {
      flex: 1;
      
      .username {
        display: block;
        font-size: 16px;
        font-weight: 500;
        color: #fff;
        margin-bottom: 6px;
      }
      
      .credit-tags {
        display: flex;
        gap: 6px;
      }
    }
  }
}

.mobile-nav-menu {
  flex: 1;
  border: none;
  overflow-y: auto;
  
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;
  }
  
  :deep(.el-menu-item-group__title) {
    padding: 12px 20px 8px;
    font-size: 12px;
    color: #909399;
  }
}

.mobile-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
  
  .el-button {
    flex: 1;
  }
}

// ============ 响应式断点 ============

// 大屏幕 (> 1200px) - 完整显示
@media (min-width: 1201px) {
  .header {
    .header-left {
      .nav-menu {
        :deep(.el-menu-item),
        :deep(.el-sub-menu__title) {
          padding: 0 18px;
        }
      }
    }
  }
}

// 中等屏幕 (992px - 1200px) - 紧凑显示
@media (max-width: 1200px) {
  .header {
    padding: 0 16px;
    
    .header-left {
      gap: 12px;
      
      .nav-menu {
        :deep(.el-menu-item),
        :deep(.el-sub-menu__title) {
          padding: 0 12px;
          font-size: 14px;
        }
      }
    }
    
    .header-right {
      .credit-info {
        .el-tag {
          padding: 4px 8px;
          font-size: 12px;
        }
      }
    }
  }
}

// 小屏幕 (768px - 992px) - 仅图标
@media (max-width: 992px) {
  .header {
    .header-left {
      .logo {
        .logo-text {
          display: none;
        }
      }
      
      .nav-menu {
        :deep(.el-menu-item),
        :deep(.el-sub-menu__title) {
          padding: 0 10px;
          
          span {
            display: none;
          }
          
          .el-icon {
            margin-right: 0;
          }
        }
      }
    }
    
    .header-right {
      gap: 8px;
      
      .credit-info {
        .el-tag {
          span {
            display: none;
          }
        }
      }
      
      .user-info {
        padding: 6px;
        
        .username {
          display: none;
        }
      }
    }
  }
}

// 移动端 (< 768px) - 汉堡菜单
@media (max-width: 768px) {
  .header {
    padding: 0 12px;
    
    .header-left {
      .mobile-menu-btn {
        display: flex;
      }
      
      .logo {
        .logo-text {
          display: none;
        }
      }
      
      .nav-menu {
        display: none;
      }
    }
    
    .header-right {
      .credit-info {
        display: none;
      }
      
      .user-info {
        .username,
        .el-icon {
          display: none;
        }
      }
      
      .el-button {
        padding: 8px 12px;
        font-size: 13px;
      }
    }
  }

  .main-content {
    padding: 12px;
  }
}

// 超小屏幕 (< 480px)
@media (max-width: 480px) {
  .header {
    .header-right {
      gap: 6px;
      
      .el-button {
        padding: 6px 10px;
        font-size: 12px;
      }
    }
  }
  
  .main-content {
    padding: 8px;
  }
}
</style>
