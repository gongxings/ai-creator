import request from './request'
import type { Platform, PlatformAccount, PublishRecord, PublishParams } from '@/types'

// 获取支持的平台列表
export function getPlatforms() {
  return request.get<Platform[]>('/v1/publish/platforms')
}

// 获取平台登录信息
export function getPlatformLoginInfo(platform: string) {
  return request.get<{ platform: string; name: string; login_url: string; instructions: string }>(
    `/v1/publish/platforms/${platform}/login-info`
  )
}

// 创建平台账号
export function createPlatformAccount(data: { platform: string; account_name: string }) {
  return request.post<PlatformAccount>('/v1/publish/platforms/accounts', data)
}

// 获取平台账号列表
export function getPlatformAccounts(platform?: string) {
  return request.get<PlatformAccount[]>('/v1/publish/platforms/accounts', { params: { platform } })
}

// 更新平台账号Cookie
export function updatePlatformCookies(id: number, cookies: Record<string, string>) {
  return request.post<{ valid: boolean; message: string; cookies_updated_at?: string }>(
    `/v1/publish/platforms/accounts/${id}/cookies`,
    { cookies }
  )
}

// 验证平台账号Cookie
export function validatePlatformCookies(id: number) {
  return request.post<{ valid: boolean; message: string; cookies_updated_at?: string }>(
    `/v1/publish/platforms/accounts/${id}/validate`
  )
}

// 删除平台账号
export function deletePlatformAccount(id: number) {
  return request.delete(`/v1/publish/platforms/accounts/${id}`)
}

// 发布内容
export function publishContent(data: PublishParams) {
  return request.post<PublishRecord[]>('/v1/publish', data)
}

// 获取发布历史
export function getPublishHistory(params: { skip?: number; limit?: number; platform?: string; status?: string }) {
  return request.get<{ items: PublishRecord[]; total: number }>('/v1/publish/history', { params })
}

// 获取发布状态
export function getPublishStatus(id: number) {
  return request.get<PublishRecord>(`/v1/publish/publish/${id}/status`)
}

// 删除发布记录
export function deletePublishRecord(id: number) {
  return request.delete(`/v1/publish/history/${id}`)
}
