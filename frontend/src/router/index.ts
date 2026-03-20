/**
 * Vue Router配置
 */
import {createRouter, createWebHistory, type RouteRecordRaw} from 'vue-router'
import {ElMessageBox} from 'element-plus'
import {useUserStore} from '@/store/user'

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue'),
        meta: {requiresAuth: false},
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/auth/Register.vue'),
        meta: {requiresAuth: false},
    },
    {
        path: '/',
        component: () => import('@/layouts/MainLayout.vue'),
        children: [
            {
                path: '',
                name: 'Home',
                component: () => import('@/views/Home.vue'),
                meta: {requiresAuth: false},
            },
            {
                path: 'writing',
                name: 'WritingTools',
                component: () => import('@/views/writing/WritingTools.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'writing/:toolType',
                name: 'WritingEditor',
                component: () => import('@/views/writing/WritingEditor.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'history',
                name: 'CreationHistory',
                component: () => import('@/views/history/CreationHistory.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'image',
                name: 'ImageGeneration',
                component: () => import('@/views/image/ImageGeneration.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'video',
                name: 'VideoGeneration',
                component: () => import('@/views/video/VideoGeneration.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'ppt',
                name: 'PPTGeneration',
                component: () => import('@/views/ppt/PPTGeneration.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'publish',
                name: 'PublishManagement',
                component: () => import('@/views/publish/PublishManagement.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'settings',
                name: 'UserSettings',
                component: () => import('@/views/settings/UserSettings.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'settings/oauth',
                name: 'OAuthAccounts',
                component: () => import('@/views/oauth/OAuthAccounts.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'credit/recharge',
                name: 'CreditRecharge',
                component: () => import('@/views/credit/CreditRecharge.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'credit/membership',
                name: 'MembershipPurchase',
                component: () => import('@/views/credit/MembershipPurchase.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'credit/transactions',
                name: 'TransactionHistory',
                component: () => import('@/views/credit/TransactionHistory.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'templates',
                name: 'TemplateManager',
                component: () => import('@/views/templates/TemplateManager.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'plugins/market',
                name: 'PluginMarket',
                component: () => import('@/views/plugins/Market.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'plugins/my-plugins',
                name: 'MyPlugins',
                component: () => import('@/views/plugins/MyPlugins.vue'),
                meta: {requiresAuth: true},
            },
            {
                path: 'operation/activities',
                name: 'ActivityManagement',
                component: () => import('@/views/operation/ActivityManagement.vue'),
                meta: {requiresAdmin: true},
            },
            {
                path: 'operation/coupons',
                name: 'CouponManagement',
                component: () => import('@/views/operation/CouponManagement.vue'),
                meta: {requiresAdmin: true},
            },
            {
                path: 'operation/referral',
                name: 'ReferralManagement',
                component: () => import('@/views/operation/ReferralManagement.vue'),
                meta: {requiresAdmin: true},
            },
            {
                path: 'operation/statistics',
                name: 'OperationStatistics',
                component: () => import('@/views/operation/OperationStatistics.vue'),
                meta: {requiresAdmin: true},
            },
            // 管理员页面
            {
                path: 'admin/users',
                name: 'UserManagement',
                component: () => import('@/views/admin/UserManagement.vue'),
                meta: {requiresAdmin: true, requiresAuth: true},
            },
            {
                path: 'admin/traffic',
                name: 'TrafficStats',
                component: () => import('@/views/admin/TrafficStats.vue'),
                meta: {requiresAdmin: true, requiresAuth: true},
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

// 埋点：追踪离开页面
// @ts-ignore
let previousRoute: ReturnType<typeof router.currentRoute.value> | null = null
let trackerModule: { trackPageLeave: (() => void) | null } | null = null

const loadTrackerModule = async () => {
    if (!trackerModule) {
        try {
            const mod = await import('@/utils/tracker')
            trackerModule = {trackPageLeave: mod.trackPageLeave}
        } catch {
            trackerModule = {trackPageLeave: null}
        }
    }
    return trackerModule.trackPageLeave
}

// 路由守卫
router.beforeEach(async (to, _from) => {
    const userStore = useUserStore()
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
    const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)

    // 埋点：页面离开追踪
    if (previousRoute) {
        const trackLeave = await loadTrackerModule()
        if (trackLeave) trackLeave()
    }
    previousRoute = to

    if (requiresAuth && !userStore.isLoggedIn) {
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
                isShowingLoginPrompt = false
                return {path: '/login', query: {redirect: to.fullPath}}
            } catch {
                isShowingLoginPrompt = false
                return false
            }
        }
        return false
    }
    if (requiresAdmin && !userStore.isAdmin) {
        ElMessageBox.alert('您没有权限访问此页面', '权限不足', {
            confirmButtonText: '确定',
            type: 'warning',
        })
        return '/'
    }
    if (!requiresAuth && userStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
        return '/'
    }
})

// 埋点：页面访问追踪
router.afterEach((to) => {
    import('@/utils/tracker').then(({initTracker, trackPageView}) => {
        if (!sessionStorage.getItem('tracking_initialized')) {
            initTracker()
            sessionStorage.setItem('tracking_initialized', 'true')
        }
        trackPageView(to.fullPath)
    }).catch(console.error)
})

export default router
