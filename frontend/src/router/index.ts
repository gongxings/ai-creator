/**
 * Vue Router配置
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
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
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/writing',
      },
      {
        path: 'writing',
        name: 'WritingTools',
        component: () => import('@/views/writing/WritingTools.vue'),
      },
      {
        path: 'writing/:toolType',
        name: 'WritingEditor',
        component: () => import('@/views/writing/WritingEditor.vue'),
      },
      {
        path: 'history',
        name: 'CreationHistory',
        component: () => import('@/views/history/CreationHistory.vue'),
      },
      {
        path: 'image',
        name: 'ImageGeneration',
        component: () => import('@/views/image/ImageGeneration.vue'),
      },
      {
        path: 'video',
        name: 'VideoGeneration',
        component: () => import('@/views/video/VideoGeneration.vue'),
      },
      {
        path: 'ppt',
        name: 'PPTGeneration',
        component: () => import('@/views/ppt/PPTGeneration.vue'),
      },
      {
        path: 'publish',
        name: 'PublishManagement',
        component: () => import('@/views/publish/PublishManagement.vue'),
      },
      {
        path: 'settings',
        name: 'UserSettings',
        component: () => import('@/views/settings/UserSettings.vue'),
      },
      {
        path: 'credit/recharge',
        name: 'CreditRecharge',
        component: () => import('@/views/credit/CreditRecharge.vue'),
      },
      {
        path: 'credit/membership',
        name: 'MembershipPurchase',
        component: () => import('@/views/credit/MembershipPurchase.vue'),
      },
      {
        path: 'credit/transactions',
        name: 'TransactionHistory',
        component: () => import('@/views/credit/TransactionHistory.vue'),
      },
      {
        path: 'operation/activities',
        name: 'ActivityManagement',
        component: () => import('@/views/operation/ActivityManagement.vue'),
      },
      {
        path: 'operation/coupons',
        name: 'CouponManagement',
        component: () => import('@/views/operation/CouponManagement.vue'),
      },
      {
        path: 'operation/referral',
        name: 'ReferralManagement',
        component: () => import('@/views/operation/ReferralManagement.vue'),
      },
      {
        path: 'operation/statistics',
        name: 'OperationStatistics',
        component: () => import('@/views/operation/OperationStatistics.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !userStore.isLoggedIn()) {
    // 需要登录但未登录，跳转到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  } else if (!requiresAuth && userStore.isLoggedIn() && (to.path === '/login' || to.path === '/register')) {
    // 已登录但访问登录/注册页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
