/**
 * 前端埋点 SDK
 * 全埋点方案：页面访问 + 点击事件 + 滚动深度 + 停留时长
 */
import {batchTrack} from '@/api/traffic'
import {useUserStore} from "@/store/user.ts";

// 生成唯一ID
function generateId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

// 生成或获取 session ID
function getSessionId(): string {
    let sessionId = sessionStorage.getItem('tracking_session_id')
    if (!sessionId) {
        sessionId = `ses_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
        sessionStorage.setItem('tracking_session_id', sessionId)
    }
    return sessionId
}

// 获取当前用户ID
function getUserId(): number | null {
    try {
        const userStore = useUserStore()
        return userStore.user?.id || null
    } catch {
        return null
    }
}

// 批量上报队列
const batchQueue = {
    page_views: [] as any[],
    page_view_updates: [] as any[],
    user_events: [] as any[]
}

// 记录页面访问
export function trackPageView(path: string, pageViewId?: string) {
    const pvId = pageViewId || generateId()

    batchQueue.page_views.push({
        id: pvId,
        path,
        session_id: getSessionId(),
        user_id: getUserId(),
        user_agent: navigator.userAgent,
        referer: document.referrer,
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        created_at: new Date().toISOString()
    })

    // 延迟批量上报
    scheduleBatchUpload()

    return pvId
}

// 更新页面访问（停留时长、滚动深度）
export function trackPageViewUpdate(pageViewId: string, stayDuration: number, maxScrollDepth: number) {
    batchQueue.page_view_updates.push({
        page_view_id: pageViewId,
        stay_duration: stayDuration,
        max_scroll_depth: maxScrollDepth
    })

    scheduleBatchUpload()
}

// 记录用户事件（点击、滚动等）
export function trackEvent(
    eventType: 'click' | 'scroll' | 'custom',
    eventName: string,
    options: {
        eventTarget?: string
        eventData?: Record<string, any>
        pageViewId?: string
        pagePath?: string
    } = {}
) {
    const event = {
        session_id: getSessionId(),
        user_id: getUserId(),
        page_path: options.pagePath || window.location.pathname,
        event_type: eventType,
        event_name: eventName,
        event_target: options.eventTarget || null,
        event_data: options.eventData || null,
        page_view_id: options.pageViewId || null,
        created_at: new Date().toISOString()
    }

    batchQueue.user_events.push(event)

    // 事件数量多时立即上报
    if (batchQueue.user_events.length >= 5) {
        flushBatch()
    }
}

// 自动点击代理
export function setupAutoClickTracker() {
    document.addEventListener('click', (event) => {
        const target = event.target as HTMLElement

        // 获取元素信息
        const tagName = target.tagName.toLowerCase()
        const className = target.className || ''
        const id = target.id || ''

        // 构建事件名称
        let eventName = `${tagName}_${className.split(' ')[0] || 'element'}`
        if (id) {
            eventName = `${tagName}#${id}`
        }

        // data-track-id 属性优先
        const trackId = (target as any).getAttribute?.('data-track-id')
        if (trackId) {
            eventName = trackId
        }

        // data-track-name 属性
        const trackName = (target as any).getAttribute?.('data-track-name')
        if (trackName) {
            eventName = trackName
        }

        // 获取文本内容（前20字符）
        let text = ''
        if (target.childNodes.length > 0) {
            text = target.textContent?.trim().substring(0, 20) || ''
        }

        trackEvent('click', eventName, {
            eventTarget: `${tagName}.${className.split(' ')[0]}`.trim(),
            eventData: {
                text,
                id: id || null,
                href: (target as HTMLAnchorElement).href || null,
                track_id: trackId || null,
                track_name: trackName || null
            },
            pagePath: window.location.pathname
        })
    }, {capture: true})
}

// 自动滚动深度追踪
let scrollTimeout: number | null = null
let maxScrollDepth = 0

export function setupScrollTracker() {
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout)
        }

        // 更新最大滚动深度
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        )
        const winHeight = window.innerHeight
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop

        const scrollPercent = Math.round(((scrollTop + winHeight) / docHeight) * 100)
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = Math.min(scrollPercent, 100)
        }

        // 滚动停止后上报（防抖）
        scrollTimeout = window.setTimeout(() => {
            if (maxScrollDepth > 0) {
                trackPageViewUpdate(
                    getCurrentPageViewId(),
                    Math.round(getPageStayDuration()),
                    maxScrollDepth
                )
                maxScrollDepth = 0
            }
        }, 1000)
    })
}

// 停留时长追踪
let pageEnterTime = Date.now()

export function trackPageLeave() {
    const stayDuration = (Date.now() - pageEnterTime) / 1000 // 转为秒

    // 上报停留时长和滚动深度
    trackPageViewUpdate(getCurrentPageViewId(), Math.round(stayDuration), maxScrollDepth)

    // 判断是否跳出（停留时间<3秒且滚动深度<25%）
    const isBounce = stayDuration < 3 && maxScrollDepth < 25
    if (isBounce) {
        // 标记为跳出（在 updatePageView 时设置 is_bounce 字段）
        console.log('Bounce detected')
    }

    // 清空队列
    scheduleBatchUpload()
}

// 获取当前页面停留时长
function getPageStayDuration(): number {
    return (Date.now() - pageEnterTime) / 1000
}

// 当前页面的 PageView ID
let currentPageViewId: string | null = null

export function getCurrentPageViewId(): string {
    if (!currentPageViewId) {
        currentPageViewId = generateId()
    }
    return currentPageViewId
}

// 批量上报调度
let batchTimeout: number | null = null

function scheduleBatchUpload() {
    if (batchTimeout) {
        clearTimeout(batchTimeout)
    }

    // 延迟100ms上报，累积数据
    batchTimeout = window.setTimeout(() => {
        flushBatch()
    }, 100)
}

// 立即上报所有数据
async function flushBatch() {
    if (batchQueue.page_views.length === 0 &&
        batchQueue.page_view_updates.length === 0 &&
        batchQueue.user_events.length === 0) {
        return
    }

    try {
        const payload = {
            page_views: batchQueue.page_views,
            page_view_updates: batchQueue.page_view_updates,
            user_events: batchQueue.user_events
        }

        await batchTrack(payload)

        // 清空队列
        batchQueue.page_views = []
        batchQueue.page_view_updates = []
        batchQueue.user_events = []

        // 重置当前页面ID（页面离开时会重新生成）
        currentPageViewId = null
    } catch (error) {
        console.error('Tracking upload failed:', error)
        // 失败时保留数据，下次再试
    }
}

// 页面卸载时发送数据（使用 sendBeacon）
window.addEventListener('beforeunload', () => {
    trackPageLeave()

    // 使用 sendBeacon 确保数据发送
    if (navigator.sendBeacon && batchQueue.user_events.length > 0) {
        const data = JSON.stringify({
            page_views: batchQueue.page_views,
            page_view_updates: batchQueue.page_view_updates,
            user_events: batchQueue.user_events
        })

        const blob = new Blob([data], {type: 'application/json'})
        navigator.sendBeacon('/api/v1/traffic/batch', blob)
    }
})

// 初始化
export function initTracker() {
    console.log('[Tracker] Initializing...')

    // 生成 session ID
    getSessionId()

    // 设置自动点击代理
    setupAutoClickTracker()

    // 设置滚动追踪
    setupScrollTracker()

    // 监听页面离开
    window.addEventListener('pagehide', trackPageLeave)

    console.log('[Tracker] Initialized')
}

// 手动标记元素（用于关键转化点）
export function markTrackable(element: HTMLElement, options: {
    trackId?: string
    trackName?: string
}) {
    if (options.trackId) {
        element.setAttribute('data-track-id', options.trackId)
    }
    if (options.trackName) {
        element.setAttribute('data-track-name', options.trackName)
    }
}
