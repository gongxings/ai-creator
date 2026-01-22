// 通用类型定义

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// 用户相关
export interface User {
  id: number
  username: string
  email: string
  phone?: string
  avatar?: string
  is_active: boolean
  role: string  // 'admin' 或 'user'
  credits: number
  is_member: boolean
  member_expired_at?: string | null
  created_at: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
  confirm_password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// AI模型相关
export interface AIModel {
  id: number
  name: string
  provider: string
  model_name: string
  api_base?: string
  is_default: boolean
  is_active: boolean
  description?: string
}

export interface AIModelForm {
  name: string
  provider: string
  model_name: string
  api_key: string
  api_base?: string
  is_default?: boolean
  description?: string
}

// 创作相关
export interface Creation {
  id: number
  user_id: number
  content_type: string
  tool_type: string
  title: string
  content: string
  ai_model_id: number
  generation_params: Record<string, any>
  status: string
  created_at: string
  updated_at: string
}

export interface WritingTool {
  tool_type: string
  name: string
  description: string
}

export interface GenerateContentParams {
  tool_type: string
  params: Record<string, any>
  ai_model_id?: number
}

export interface CreationVersion {
  id: number
  creation_id: number
  version_number: number
  content: string
  change_description: string
  created_at: string
}

// 发布相关
export interface Platform {
  platform: string
  name: string
  description: string
}

export interface PlatformAccount {
  id: number
  user_id: number
  platform: string
  account_name: string
  credentials: Record<string, any>
  is_active: boolean
  created_at: string
}

export interface PublishRecord {
  id: number
  user_id: number
  creation_id: number
  platform: string
  platform_account_id: number
  publish_config: Record<string, any>
  status: string
  platform_url?: string
  error_message?: string
  published_at?: string
  created_at: string
}

export interface PublishParams {
  creation_id: number
  platforms: string[]
  platform_accounts: Record<string, number>
  publish_config?: Record<string, any>
  scheduled_time?: string
}
