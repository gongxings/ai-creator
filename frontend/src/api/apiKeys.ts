import request from './request'
import type { APIKey, APIKeyForm, APIKeyDetail, APIKeyStats } from '@/types'

// 创建API Key
export function createAPIKey(data: APIKeyForm) {
  return request.post<APIKeyDetail>('/v1/api-keys', data)
}

// 获取API Key列表
export function getAPIKeys() {
  return request.get<{ api_keys: APIKey[] }>('/v1/api-keys')
}

// 获取API Key详情
export function getAPIKeyDetail(keyId: number) {
  return request.get<APIKey>(`/v1/api-keys/${keyId}`)
}

// 删除API Key
export function deleteAPIKey(keyId: number) {
  return request.delete(`/v1/api-keys/${keyId}`)
}

// 获取API Key使用统计
export function getAPIKeyStats(keyId: number) {
  return request.get<APIKeyStats>(`/v1/api-keys/${keyId}/stats`)
}
