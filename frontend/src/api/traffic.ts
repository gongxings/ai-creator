/**
 * 流量统计 API
 */
import request from './request'

// 流量概览数据
export interface TrafficOverview {
  today_pv: number
  today_uv: number
  today_new_users: number
  total_users: number
  total_creations: number
  week_pv: number
  week_uv: number
  month_pv: number
  month_uv: number
}

// 每日统计数据
export interface DailyStat {
  date: string
  pv: number
  uv: number
  new_users: number
  active_users: number
  total_requests: number
}

/**
 * 获取流量概览
 */
export function getTrafficOverview() {
  return request<{ code: number; data: TrafficOverview }>('/traffic/overview')
}

/**
 * 获取每日统计数据
 */
export function getDailyStats(days: number = 30) {
  return request<{ code: number; data: DailyStat[] }>('/traffic/daily', {
    params: { days }
  })
}
