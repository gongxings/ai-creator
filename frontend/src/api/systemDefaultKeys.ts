/**
 * 系统默认APIKey管理 API
 */
import request from './request'

export interface SystemDefaultKey {
  id: number
  key_name: string
  key_display: string
  provider: string
  model_name: string
  base_url: string | null
  system_default_order: number
  total_assigned_users: number
  is_active: boolean
  created_at: string
}

export interface UsageStats {
  total_requests: number
  total_tokens: number
  period_days: number
  user_breakdown: Array<{
    user_id: number
    requests: number
    tokens: number
  }>
}

/**
 * 获取所有系统默认APIKey 列表
 */
export function getSystemDefaultKeys() {
  return request({
    url: '/system-default-keys/list',
    method: 'get'
  })
}

/**
 * 将 API Key 设为系统默认
 */
export function setAsSystemDefault(keyId: number, order: number = 99) {
  return request({
    url: `/system-default-keys/${keyId}/set-system-default?order=${order}`,
    method: 'post'
  })
}

/**
 * 取消系统默认标记
 */
export function unsetSystemDefault(keyId: number) {
  return request({
    url: `/system-default-keys/${keyId}/unset-system-default`,
    method: 'post'
  })
}

/**
 * 获取使用统计
 */
export function getKeyUsageStats(keyId: number, days: number = 30) {
  return request({
    url: `/system-default-keys/${keyId}/usage-stats?days=${days}`,
    method: 'get'
  })
}

/**
 * 解密获取 API Key 明文
 */
export function decryptApiKey(keyId: number) {
  return request({
    url: `/system-default-keys/${keyId}/decrypt`,
    method: 'get'
  })
}
