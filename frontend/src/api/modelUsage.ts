/**
 * 模型调用监控 API
 */
import request from './request'

export interface UsageLogItem {
  id: number
  user_id: number
  ai_model_id: number
  creation_id: number | null
  provider: string
  model_name: string
  tool: string | null
  request_type: string
  input_content: string | null
  output_content: string | null
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  status: string
  error_message: string | null
  response_time_ms: number | null
  extra_data: any
  created_at: string | null
}

export interface UsageLogListResponse {
  total: number
  page: number
  page_size: number
  items: UsageLogItem[]
}

export interface UsageStats {
  overview: {
    total_calls: number
    today_calls: number
    week_calls: number
    total_tokens: number
    today_tokens: number
    failed_calls: number
    success_rate: number
  }
  by_provider: {
    provider: string
    count: number
    total_tokens: number
  }[]
  by_tool: {
    tool: string
    count: number
    total_tokens: number
  }[]
}

/**
 * 获取模型调用日志
 */
export function getUsageLogs(params: {
  page?: number
  page_size?: number
  provider?: string
  tool?: string
  status?: string
  user_id?: number
}) {
  return request.get<{ data: UsageLogListResponse }>('/v1/admin/model-usage/logs', { params })
}

/**
 * 获取单条日志详情
 */
export function getUsageLogDetail(logId: number) {
  return request.get<{ data: UsageLogItem }>(`/v1/admin/model-usage/logs/${logId}`)
}

/**
 * 获取模型调用统计
 */
export function getUsageStats() {
  return request.get<{ data: UsageStats }>('/v1/admin/model-usage/stats')
}
