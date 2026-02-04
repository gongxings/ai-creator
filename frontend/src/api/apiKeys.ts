import { get, post, del } from '@/utils/request'
import type { APIKey, APIKeyForm, APIKeyDetail, APIKeyStats } from '@/types'

// 创建API Key
export function createAPIKey(data: APIKeyForm) {
  return post<APIKeyDetail>('/v1/api-keys', data)
}

// 获取API Key列表
export function getAPIKeys() {
  return get<{ api_keys: APIKey[] }>('/v1/api-keys')
}

// 获取API Key详情
export function getAPIKeyDetail(keyId: number) {
  return get<APIKey>(`/v1/api-keys/${keyId}`)
}

// 删除API Key
export function deleteAPIKey(keyId: number) {
  return del(`/v1/api-keys/${keyId}`)
}

// 获取API Key使用统计
export function getAPIKeyStats(keyId: number) {
  return get<APIKeyStats>(`/v1/api-keys/${keyId}/stats`)
}
