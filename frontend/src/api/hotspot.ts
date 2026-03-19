/**
 * 热点追踪 API
 */
import request from './request'

// 热点条目
export interface HotspotItem {
  title: string
  url?: string
  hot?: number
  index?: number
  mobile_url?: string
}

// 热点列表响应
export interface HotspotListResponse {
  platform: string
  platform_name: string
  update_time?: string
  items: HotspotItem[]
}

// 分类信息
export interface CategoryInfo {
  code: string
  name: string
  order: number
}

// 分类列表响应
export interface CategoryListResponse {
  categories: CategoryInfo[]
}

// 平台信息
export interface PlatformInfo {
  code: string
  name: string
  category: string // 所属分类
  icon?: string
  color?: string
  subtypes?: Record<string, string> // 子类型（如百度的热搜/汽车/游戏等）
}

// 平台列表响应
export interface PlatformListResponse {
  platforms: PlatformInfo[]
}

// 选题建议请求
export interface TopicSuggestRequest {
  hot_title: string
  user_domain?: string
  target_platforms?: string[]
}

// 创作角度
export interface WritingAngle {
  angle: string
  title_suggestion: string
  content_direction: string
  recommended_tools: string[]
  target_audience: string
}

// 选题建议响应
export interface TopicSuggestResponse {
  hot_title: string
  background: string
  angles: WritingAngle[]
  keywords: string[]
}

/**
 * 获取热点分类列表
 */
export function getCategories() {
  return request.get<CategoryListResponse>('/v1/hotspot/categories')
}

/**
 * 获取支持的热点平台列表
 */
export function getPlatforms() {
  return request.get<PlatformListResponse>('/v1/hotspot/platforms')
}

/**
 * 获取指定平台的热点列表
 * @param platform 平台代码
 * @param limit 返回数量
 * @param type 子类型（百度专用：realtime/car/game/movie/novel/teleplay）
 */
export function getHotList(platform: string, limit: number = 20, type?: string) {
  return request.get<HotspotListResponse>('/v1/hotspot/list', {
    params: { platform, limit, type },
  })
}

/**
 * 获取多个平台的热点列表
 * @param platforms 平台代码数组
 * @param limit 每个平台返回数量
 */
export function getMultiPlatformHotList(platforms: string[], limit: number = 10) {
  return request.get<HotspotListResponse[]>('/v1/hotspot/multi', {
    params: {
      platforms: platforms.join(','),
      limit,
    },
  })
}

/**
 * 获取 AI 选题建议
 * @param data 选题建议请求
 */
export function getTopicSuggestions(data: TopicSuggestRequest) {
  return request.post<TopicSuggestResponse>('/v1/hotspot/suggest', data)
}

// 提取关键词响应
export interface ExtractKeywordsResponse {
  title: string
  keywords: string[]
}

/**
 * 从热点标题中提取关键词
 * @param title 热点标题
 */
export function extractKeywords(title: string) {
  return request.post<ExtractKeywordsResponse>('/v1/hotspot/extract-keywords', null, {
    params: { title },
  })
}
