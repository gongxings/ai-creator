/**
 * 管理员用户管理 API
 */
import request from './request'

export interface UserInfo {
  id: number
  username: string
  email: string
  nickname: string | null
  avatar: string | null
  phone: string | null
  role: string
  status: string
  credits: number
  daily_quota: number
  used_quota: number
  total_creations: number
  is_member: number
  member_expired_at: string | null
  last_login_at: string | null
  last_login_ip: string | null
  created_at: string
  referral_code: string
}

export interface AIModel {
  id: number
  name: string
  provider: string
  model_name: string
  is_default: boolean
  is_active: boolean
  system_default_source: boolean
  source_api_key_id: number | null
  created_at: string
}

export interface UserDetail {
  user: UserInfo
  ai_models: AIModel[]
  usage_stats: {
    total_requests: number
    total_tokens: number
  }
}

export interface UserListResponse {
  users: UserInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 获取用户列表
 */
export function getUserList(params: {
  page?: number
  page_size?: number
  keyword?: string
}) {
  return request({
    url: '/admin/users/list',
    method: 'get',
    params
  })
}

/**
 * 获取用户详情
 */
export function getUserDetail(userId: number) {
  return request({
    url: `/admin/users/${userId}`,
    method: 'get'
  })
}

/**
 * 重置用户模型为系统默认
 */
export function resetUserModels(userId: number) {
  return request({
    url: `/admin/users/${userId}/reset-models`,
    method: 'post'
  })
}

/**
 * 切换用户模型状态
 */
export function toggleModelStatus(
  userId: number,
  modelId: number,
  isActive: boolean
) {
  return request({
    url: `/admin/users/${userId}/toggle-model-status`,
    method: 'post',
    data: { model_id: modelId, is_active: isActive }
  })
}

/**
 * 删除用户
 */
export function deleteUser(userId: number) {
  return request({
    url: `/admin/users/${userId}`,
    method: 'delete'
  })
}
