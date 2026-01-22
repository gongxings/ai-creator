/**
 * Vue Router配置
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { requiresAuth: false },
      },
      {
        path: 'writing',
        name: 'WritingTools',
        component: () => import('@/views/writing/WritingTools.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'writing/:toolType',
        name: 'WritingEditor',
        component: () => import('@/views/writing/WritingEditor.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'history',
        name: 'CreationHistory',
        component: () => import('@/views/history/CreationHistory.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'image',
        name: 'ImageGeneration',
        component: () => import('@/views/image/ImageGeneration.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'video',
        name: 'VideoGeneration',
        component: () => import('@/views/video/VideoGeneration.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'ppt',
        name: 'PPTGeneration',
        component: () => import('@/views/ppt/PPTGeneration.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'publish',
        name: 'PublishManagement',
        component: () => import('@/views/publish/PublishManagement.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'settings',
        name: 'UserSettings',
        component: () => import('@/views/settings/UserSettings.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'credit/recharge',
        name: 'CreditRecharge',
        component: () => import('@/views/credit/CreditRecharge.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'credit/membership',
        name: 'MembershipPurchase',
        component: () => import('@/views/credit/MembershipPurchase.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'credit/transactions',
        name: 'TransactionHistory',
        component: () => import('@/views/credit/TransactionHistory.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'operation/activities',
        name: 'ActivityManagement',
        component: () => import('@/views/operation/ActivityManagement.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'operation/coupons',
        name: 'CouponManagement',
        component: () => import('@/views/operation/CouponManagement.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'operation/referral',
        name: 'ReferralManagement',
        component: () => import('@/views/operation/ReferralManagement.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'operation/statistics',
        name: 'OperationStatistics',
        component: () => import('@/views/operation/OperationStatistics.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 是否正在显示登录提示
let isShowingLoginPrompt = false

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)

  if (requiresAuth && !userStore.isLoggedIn) {
    // 需要登录但未登录，提示用户
    if (!isShowingLoginPrompt) {
      isShowingLoginPrompt = true
      
      try {
        await ElMessageBox.confirm(
          '此功能需要登录后才能使用，是否前往登录？',
          '需要登录',
          {
            confirmButtonText: '去登录',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // 用户确认跳转到登录页
        isShowingLoginPrompt = false
        next({
          path: '/login',
          query: { redirect: to.fullPath },
        })
      } catch {
        // 用户取消，停留在当前页面
        isShowingLoginPrompt = false
        next(false)
      }
    } else {
      next(false)
    }
  } else if (requiresAdmin && !userStore.isAdmin) {
    // 需要管理员权限但不是管理员，跳转到首页
    ElMessageBox.alert('您没有权限访问此页面', '权限不足', {
      confirmButtonText: '确定',
      type: 'warning',
    })
    next('/')
  } else if (!requiresAuth && userStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    // 已登录但访问登录/注册页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
