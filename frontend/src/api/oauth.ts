/**
 * OAuth账号管理API
 */
import request from './request'

export interface OAuthPlatform {
  id: number
  platform_id: string
  platform_name: string
  description: string
  oauth_config: any
  litellm_config: any
  quota_config: any
  is_enabled: boolean
}

export interface OAuthAccount {
  id: number
  user_id: number
  platform: string
  platform_name: string
  account_name: string
  credentials: any
  quota_used: number
  quota_limit: number
  is_active: boolean
  last_used_at: string
  expires_at: string
  created_at: string
  updated_at: string
}

export interface OAuthUsageLog {
  id: number
  account_id: number
  model: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  request_data: any
  response_data: any
  error_message: string
  created_at: string
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatCompletionRequest {
  account_id: number
  messages: ChatMessage[]
  model?: string
  stream?: boolean
  temperature?: number
  max_tokens?: number
  top_p?: number
}

/**
 * 获取支持的平台列表
 */
export function getPlatforms() {
  return request<OAuthPlatform[]>({
    url: '/oauth/platforms',
    method: 'get',
  })
}

/**
 * 授权OAuth账号
 */
export function authorizeAccount(data: {
  platform: string
  account_name: string
}) {
  return request<OAuthAccount>({
    url: '/oauth/accounts/authorize',
    method: 'post',
    data,
  })
}

/**
 * 获取OAuth账号列表
 */
export function getAccounts(params?: {
  platform?: string
  is_active?: boolean
}) {
  return request<OAuthAccount[]>({
    url: '/oauth/accounts',
    method: 'get',
    params,
  })
}

/**
 * 获取OAuth账号详情
 */
export function getAccount(accountId: number) {
  return request<OAuthAccount>({
    url: `/oauth/accounts/${accountId}`,
    method: 'get',
  })
}

/**
 * 更新OAuth账号
 */
export function updateAccount(
  accountId: number,
  data: {
    account_name?: string
    is_active?: boolean
  }
) {
  return request<OAuthAccount>({
    url: `/oauth/accounts/${accountId}`,
    method: 'put',
    data,
  })
}

/**
 * 删除OAuth账号
 */
export function deleteAccount(accountId: number) {
  return request({
    url: `/oauth/accounts/${accountId}`,
    method: 'delete',
  })
}

/**
 * 检查账号有效性
 */
export function checkAccountValidity(accountId: number) {
  return request<{ is_valid: boolean; message: string }>({
    url: `/oauth/accounts/${accountId}/check`,
    method: 'post',
  })
}

/**
 * 获取账号使用日志
 */
export function getUsageLogs(accountId: number, limit = 100) {
  return request<OAuthUsageLog[]>({
    url: `/oauth/accounts/${accountId}/usage`,
    method: 'get',
    params: { limit },
  })
}

/**
 * 获取账号可用模型
 */
export function getAvailableModels(accountId: number) {
  return request<{ models: string[] }>({
    url: `/oauth/accounts/${accountId}/models`,
    method: 'get',
  })
}

/**
 * 聊天完成
 */
export function chatCompletion(data: ChatCompletionRequest) {
  return request({
    url: '/oauth/chat/completions',
    method: 'post',
    data,
  })
}
