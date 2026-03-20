/**
 * 流量统计 API
 */
import request from './request'

// 批量埋点上报请求
export interface BatchTrackRequest {
    page_views: Array<{
        id?: string
        path: string
        session_id: string
        user_id?: number
        user_agent?: string
        referer?: string
        screen_width?: number
        screen_height?: number
        created_at?: string
    }>
    page_view_updates: Array<{
        page_view_id: string
        stay_duration: number
        max_scroll_depth: number
    }>
    user_events: Array<{
        session_id: string
        user_id?: number
        page_path: string
        event_type: 'click' | 'scroll' | 'custom'
        event_name?: string
        event_target?: string
        event_data?: Record<string, any>
        page_view_id?: string
        created_at?: string
    }>
}

export interface TrackStatsResponse {
    status: 'ok' | 'error' | 'redis_unavailable'
    page_views: number
    events: number
    updates: number
}

/**
 * 批量上报埋点数据
 */
export function batchTrack(data: BatchTrackRequest) {
    return request.post<{
        code: number;
        message: string;
        data: { page_views: number; events: number; updates: number }
    }>(
        '/v1/traffic/batch',
        data
    )
}

/**
 * 获取流量统计缓存状态（管理员）
 */
export function getTrackerStats() {
    return request.get<{ code: number; data: TrackStatsResponse }>('/v1/traffic/stats')
}

/**
 * 获取流量概览（管理员）
 */
export function getTrafficOverview() {
    return request.get<{ code: number; data: any }>('/v1/traffic/overview')
}

/**
 * 获取每日统计数据（管理员）
 */
export function getDailyStats(days: number = 30) {
    return request.get<{
        code: number;
        data: Array<{
            date: string;
            pv: number;
            uv: number;
            new_users: number;
            active_users: number;
            total_requests: number
        }>
    }>(
        '/v1/traffic/daily',
        {params: {days}}
    )
}

/**
 * 获取热门页面（管理员）
 */
export function getHotPages(days?: number, limit?: number) {
    return request.get<{ code: number; data: Array<{ path: string; pv: number; uv: number; avg_duration: number }> }>(
        '/v1/traffic/hot-pages',
        {params: {days, limit}}
    )
}

/**
 * 获取点击事件统计（管理员）
 */
export function getClickEvents(days?: number, limit?: number) {
    return request.get<{
        code: number;
        data: Array<{ event_name: string; event_target: string; page_path: string; click_count: number }>
    }>(
        '/v1/traffic/click-events',
        {params: {days, limit}}
    )
}
