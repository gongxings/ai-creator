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
  oauth_meta?: any
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
  return request.get<OAuthPlatform[]>('/v1/oauth/platforms')
}

/**
 * 授权OAuth账号
 */
export function authorizeAccount(data: {
  platform: string
  account_name: string
}) {
  return request.post<OAuthAccount>('/v1/oauth/accounts/authorize', data)
}

/**
 * 手动提交Cookie创建OAuth账号
 */
export function createAccountManual(data: {
  platform: string
  account_name?: string
  cookies: Record<string, string>
  tokens?: Record<string, string>
  user_agent?: string
}) {
  return request.post<OAuthAccount>('/v1/oauth/accounts/manual', data)
}

/**
 * 获取OAuth账号列表
 */
export function getAccounts(params?: {
  platform?: string
  is_active?: boolean
}) {
  return request.get<OAuthAccount[]>('/v1/oauth/accounts', { params })
}

/**
 * 获取OAuth账号详情
 */
export function getAccount(accountId: number) {
  return request.get<OAuthAccount>(`/v1/oauth/accounts/${accountId}`)
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
  return request.put<OAuthAccount>(`/v1/oauth/accounts/${accountId}`, data)
}

/**
 * 删除OAuth账号
 */
export function deleteAccount(accountId: number) {
  return request.delete(`/v1/oauth/accounts/${accountId}`)
}

/**
 * 检查账号有效性
 */
export function checkAccountValidity(accountId: number) {
  return request.post<{ is_valid: boolean; message: string }>(`/v1/oauth/accounts/${accountId}/check`)
}

/**
 * 获取账号使用日志
 */
export function getUsageLogs(accountId: number, limit = 100) {
  return request.get<OAuthUsageLog[]>(`/v1/oauth/accounts/${accountId}/usage`, { params: { limit } })
}

/**
 * 获取账号可用模型
 */
export function getAvailableModels(accountId: number) {
  return request.get<{ models: string[] }>(`/v1/oauth/accounts/${accountId}/models`)
}

/**
 * 聊天完成
 */
export function chatCompletion(data: ChatCompletionRequest) {
  return request.post('/v1/oauth/chat/completions', data)
}
