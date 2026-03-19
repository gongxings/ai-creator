/**
 * API 监控 API
 */
import request from './request'

export interface MonitorOverview {
  total_requests: number
  total_tokens: number
  active_users: number
  total_keys: number
  avg_daily_requests: number
  period_days: number
  top_models: Array<{
    model_name: string
    request_count: number
    token_count: number
  }>
}

export interface UsageLog {
  id: number
  username: string
  key_name: string
  model_name: string | null
  endpoint: string | null
  method: string | null
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  status_code: number | null
  error_message: string | null
  response_time: number | null
  created_at: string
}

export interface DailyStat {
  date: string
  requests: number
  tokens: number
  active_users: number
}

export interface ErrorAnalysis {
  total_errors: number
  error_rate: number
  period_days: number
  error_types: Array<{
    status_code: number
    count: number
    percentage: number
  }>
  top_errors: Array<{
    error_message: string
    count: number
    percentage: number
  }>
}

export interface UserUsageResponse {
  logs: UsageLog[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 获取监控概览
 */
export function getMonitorOverview(days: number = 7) {
  return request({
    url: '/api-monitor/overview',
    method: 'get',
    params: { days }
  })
}

/**
 * 获取用户使用详情
 */
export function getUserUsage(params: {
  user_id?: number
  key_id?: number
  days?: number
  page?: number
  page_size?: number
}) {
  return request({
    url: '/api-monitor/user-usage',
    method: 'get',
    params
  })
}

/**
 * 获取每日统计趋势
 */
export function getDailyStats(days: number = 30) {
  return request({
    url: '/api-monitor/daily-stats',
    method: 'get',
    params: { days }
  })
}

/**
 * 获取错误分析
 */
export function getErrorAnalysis(days: number = 7) {
  return request({
    url: '/api-monitor/error-analysis',
    method: 'get',
    params: { days }
  })
}
