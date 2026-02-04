import { get, post, put, del } from '@/utils/request'
import type { Platform, PlatformAccount, PublishRecord, PublishParams, PaginationParams, PaginationResponse } from '@/types'

// 获取支持的平台列表
export function getPlatforms() {
  return get<Platform[]>('/v1/publish/platforms')
}

// 绑定平台账号
export function bindPlatformAccount(data: { platform: string; account_name: string; credentials: Record<string, any> }) {
  return post<PlatformAccount>('/v1/publish/platforms/bind', data)
}

// 获取平台账号列表
export function getPlatformAccounts(platform?: string) {
  return get<PlatformAccount[]>('/v1/publish/platforms/accounts', { platform })
}

// 更新平台账号
export function updatePlatformAccount(id: number, data: { account_name?: string; credentials?: Record<string, any>; is_active?: boolean }) {
  return put<PlatformAccount>(`/v1/publish/platforms/accounts/${id}`, data)
}

// 删除平台账号
export function deletePlatformAccount(id: number) {
  return del(`/v1/publish/platforms/accounts/${id}`)
}

// 发布内容
export function publishContent(data: PublishParams) {
  return post<PublishRecord[]>('/v1/publish', data)
}

// 获取发布历史
export function getPublishHistory(params: PaginationParams & { platform?: string; status?: string }) {
  return get<PaginationResponse<PublishRecord>>('/v1/publish/history', params)
}

// 获取发布状态
export function getPublishStatus(id: number) {
  return get<PublishRecord>(`/v1/publish/${id}/status`)
}

// 删除发布记录
export function deletePublishRecord(id: number) {
  return del(`/v1/publish/history/${id}`)
}
