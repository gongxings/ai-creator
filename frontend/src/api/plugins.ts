/**
 * 插件系统 API
 */
import request from './request'

// ==================== 类型定义 ====================

export interface PluginMarketItem {
  id: number
  name: string
  display_name: string
  short_description?: string
  category: string
  icon?: string
  tags: string[]
  is_official: boolean
  download_count: number
  rating: number
  review_count: number
  is_installed: boolean
}

export interface PluginMarketDetail {
  id: number
  name: string
  display_name: string
  description?: string
  short_description?: string
  version: string
  author: string
  author_url?: string
  category: string
  icon?: string
  icon_url?: string
  tags: string[]
  screenshot_urls: string[]
  is_official: boolean
  is_approved: boolean
  is_active: boolean
  download_count: number
  rating: number
  review_count: number
  config_schema: Record<string, any>
  parameters_schema: Record<string, any>
  created_at: string
  updated_at: string
  is_installed: boolean
  user_config?: Record<string, any>
}

export interface PluginCategory {
  key: string
  name: string
  description: string
  count: number
}

export interface UserPluginItem {
  id: number
  plugin_name: string
  display_name: string
  category: string
  icon?: string
  is_enabled: boolean
  is_auto_use: boolean
  usage_count: number
  last_used_at?: string
}

export interface UserPluginDetail {
  id: number
  plugin_name: string
  is_enabled: boolean
  config: Record<string, any>
  is_auto_use: boolean
  usage_count: number
  last_used_at?: string
  installed_at: string
  display_name: string
  description?: string
  category: string
  icon?: string
  config_schema: Record<string, any>
}

export interface PluginForCreation {
  name: string
  display_name: string
  description: string
  icon?: string
  is_enabled: boolean
  is_selected: boolean
}

export interface PluginReview {
  id: number
  user_id: number
  plugin_name: string
  rating: number
  comment?: string
  created_at: string
  username?: string
}

export interface PluginStats {
  plugin_name: string
  display_name: string
  total_calls: number
  success_calls: number
  failed_calls: number
  avg_duration_ms?: number
  last_used_at?: string
}

// ==================== 插件市场 API ====================

/**
 * 获取插件市场列表
 */
export function getPluginMarket(params?: {
  category?: string
  search?: string
  sort_by?: string
  sort_order?: string
  skip?: number
  limit?: number
}) {
  return request.get<{ data: { total: number; items: PluginMarketItem[] } }>('/v1/plugins/market', { params })
}

/**
 * 获取插件分类列表
 */
export function getPluginCategories() {
  return request.get<{ data: PluginCategory[] }>('/v1/plugins/market/categories')
}

/**
 * 获取插件详情
 */
export function getPluginDetail(pluginName: string) {
  return request.get<{ data: PluginMarketDetail }>(`/v1/plugins/market/${pluginName}`)
}

// ==================== 用户插件 API ====================

/**
 * 安装插件
 */
export function installPlugin(data: {
  plugin_name: string
  config?: Record<string, any>
}) {
  return request.post<{ data: { id: number; plugin_name: string; installed_at: string } }>('/v1/plugins/install', data)
}

/**
 * 卸载插件
 */
export function uninstallPlugin(pluginName: string) {
  return request.delete(`/v1/plugins/uninstall/${pluginName}`)
}

/**
 * 获取我的插件列表
 */
export function getMyPlugins() {
  return request.get<{ data: UserPluginItem[] }>('/v1/plugins/my-plugins')
}

/**
 * 获取我的插件详情
 */
export function getMyPluginDetail(pluginName: string) {
  return request.get<{ data: UserPluginDetail }>(`/v1/plugins/my-plugins/${pluginName}`)
}

/**
 * 更新插件配置
 */
export function updateMyPlugin(pluginName: string, data: {
  config?: Record<string, any>
  is_enabled?: boolean
  is_auto_use?: boolean
}) {
  return request.put(`/v1/plugins/my-plugins/${pluginName}`, data)
}

// ==================== 插件选择 API ====================

/**
 * 保存插件选择
 */
export function savePluginSelection(data: {
  tool_type: string
  selected_plugins: string[]
}) {
  return request.post('/v1/plugins/selection', data)
}

/**
 * 获取插件选择
 */
export function getPluginSelection(toolType: string) {
  return request.get<{ data: { tool_type: string; selected_plugins: string[]; updated_at?: string } }>(`/v1/plugins/selection/${toolType}`)
}

/**
 * 获取创作时可用的插件
 */
export function getPluginsForCreation(toolType: string) {
  return request.get<{ data: { plugins: PluginForCreation[]; has_previous_selection: boolean } }>(`/v1/plugins/for-creation/${toolType}`)
}

// ==================== 插件评价 API ====================

/**
 * 提交插件评价
 */
export function createPluginReview(data: {
  plugin_name: string
  rating: number
  comment?: string
}) {
  return request.post('/v1/plugins/reviews', data)
}

/**
 * 获取插件评价列表
 */
export function getPluginReviews(pluginName: string, params?: {
  skip?: number
  limit?: number
}) {
  return request.get<{ data: { total: number; items: PluginReview[] } }>(`/v1/plugins/reviews/${pluginName}`, { params })
}

// ==================== 插件统计 API ====================

/**
 * 获取插件使用统计
 */
export function getPluginStats() {
  return request.get<{ data: PluginStats[] }>('/v1/plugins/stats')
}
