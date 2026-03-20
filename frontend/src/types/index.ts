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
export type ModelCapability = 'text' | 'image' | 'video' | 'audio'

export interface AIModel {
  id: number
  user_id: number
  name: string
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  is_default: boolean
  is_active: boolean
  is_system_builtin: boolean
  description?: string
  capabilities: ModelCapability[]
  created_at: string
  updated_at: string
  is_readonly?: boolean
}

export interface AIModelForm {
  id?: number
  name: string
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  is_default?: boolean
  is_active?: boolean
  is_system_builtin?: boolean
  description?: string
  capabilities: ModelCapability[]
}

// 创作相关
export interface Creation {
  id: number
  user_id: number
  content_type?: string
  creation_type?: string
  tool_type: string
  title: string
  content?: string
  output_content?: string
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  extra_data?: Record<string, any>
  ai_model_id?: number
  model_id?: number
  generation_params?: Record<string, any>
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
  enabled_plugins?: string[]
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
  login_url: string
  supported_types: string[]
}

export interface PlatformAccount {
  id: number
  user_id: number
  platform: string
  account_name: string
  is_active: string
  cookies_valid?: string | null
  cookies_updated_at?: string | null
  created_at: string
}

export interface PublishRecord {
  id: number
  platform: string
  status: string
  title?: string
  content?: string
  rendered_content?: string
  account_name?: string | null
  content_type?: string | null
  platform_url?: string
  platform_post_id?: string
  error_message?: string
  scheduled_at?: string
  published_at?: string
  created_at: string
}

export interface PublishParams {
  account_id: number
  creation_id: number
  content_type: string
  scheduled_at?: string
  title?: string
  content?: string
  rendered_content?: string
  cover_image?: string
  images?: string[]
  video_url?: string
  tags?: string[]
  location?: string
  template_id?: number
}

// 可用模型相关（仅 API Key 模型）
export interface AvailableModel {
  model_id: string  // ai_model_{model_id}
  model_name: string  // 实际模型名称
  display_name: string  // 显示名称
  provider: string  // 提供商
  source_type: 'api_key'  // 来源类型
  source_id: number  // 来源ID
  is_free: boolean  // 是否免费
  is_preferred: boolean  // 是否为用户偏好
  status: 'active' | 'expired' | 'quota_exceeded'  // 状态
  quota_info?: {
    used: number
    total: number
    percentage: number
  }
}

// 统一AI调用相关
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  model_id: string
  messages: ChatMessage[]
  scene_type?: string
  stream?: boolean
  temperature?: number
  max_tokens?: number
  top_p?: number
}

export interface ChatResponse {
  content: string
  model: string
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

// ============================================================================
// 写作工具表单相关类型
// ============================================================================

// 表单字段类型
export type FormFieldType = 'input' | 'textarea' | 'select' | 'radio' | 'number' | 'slider' | 'history_select' | 'url_fetch'

// 下拉选项
export interface SelectOption {
  label: string
  value: string | boolean
}

// 滑块配置
export interface SliderConfig {
  min?: number
  max?: number
  step?: number
  marks?: Record<number, string>
}

// 表单字段定义
export interface FormField {
  name: string
  label: string
  type: FormFieldType
  required: boolean
  placeholder?: string
  options?: SelectOption[]
  defaultValue?: any
  rows?: number
  maxLength?: number
  // slider 类型专用
  sliderConfig?: SliderConfig
  // history_select 类型专用
  historyConfig?: {
    contentField: string  // 选中后填充到哪个字段
    filterToolTypes?: string[]  // 筛选哪些工具类型的历史记录，不设置则显示全部
  }
  // url_fetch 类型专用
  urlFetchConfig?: {
    contentField: string  // 抓取后填充到哪个字段
  }
}

// 工具表单配置
export interface ToolFormConfig {
  toolType: string
  name: string
  description: string
  fields: FormField[]
}

// ============================================================================
// AI 厂商配置相关类型
// ============================================================================

// 厂商认证类型
export type AuthType = 'api_key' | 'dual_key' | 'triple_key' | 'api_key_group'

// 厂商配置（前端用）
export interface ProviderOption {
  value: string
  label: string
  authType: AuthType
  defaultBaseUrl: string
  capabilities: ModelCapability[]
  supportsCustomUrl: boolean
}

// 扩展 AIModelForm 以支持多种认证方式
export interface AIModelFormExtended extends Omit<AIModelForm, 'api_key'> {
  api_key?: string
  secret_key?: string      // 用于 dual_key (百度、腾讯)
  app_id?: string          // 用于 triple_key (讯飞)
  api_secret?: string      // 用于 triple_key (讯飞)
  group_id?: string        // 用于 api_key_group (MiniMax)
}
