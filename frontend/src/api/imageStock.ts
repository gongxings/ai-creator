/**
 * 图库搜索 API
 */
import request from './request'

// 图片来源枚举
export enum ImageSource {
  UNSPLASH = 'unsplash',
  PEXELS = 'pexels',
  AI_GENERATED = 'ai_generated',
}

// 图片方向枚举
export enum ImageOrientation {
  LANDSCAPE = 'landscape',   // 横向
  PORTRAIT = 'portrait',     // 纵向
  SQUARE = 'square',         // 正方形
}

// 图库搜索请求
export interface ImageSearchRequest {
  query: string              // 搜索关键词
  source?: ImageSource       // 图库来源
  orientation?: ImageOrientation // 图片方向
  page?: number              // 页码
  per_page?: number          // 每页数量
  color?: string             // 主色调
}

// 图片项
export interface ImageItem {
  id: string                 // 图片ID
  source: ImageSource        // 图片来源
  url: string                // 图片URL
  thumb_url: string          // 缩略图URL
  width: number              // 图片宽度
  height: number             // 图片高度
  alt?: string               // 图片描述
  photographer?: string      // 摄影师
  photographer_url?: string  // 摄影师主页
  download_url?: string      // 下载链接
  color?: string             // 主色调
}

// 图库搜索响应
export interface ImageSearchResponse {
  query: string              // 搜索关键词
  total: number              // 总数量
  page: number               // 当前页码
  per_page: number           // 每页数量
  images: ImageItem[]        // 图片列表
}

// 关键词建议请求
export interface KeywordSuggestRequest {
  content: string            // 文章内容或主题
  count?: number             // 建议数量
}

// 关键词建议响应
export interface KeywordSuggestResponse {
  keywords: string[]         // 中文关键词
  keywords_en: string[]      // 英文关键词
}

// 图库源状态
export interface SourceStatus {
  configured: boolean
  name: string
  rate_limit: string
}

/**
 * 获取图库源配置状态
 */
export function getSourcesStatus() {
  return request.get<Record<string, SourceStatus>>('/v1/image-stock/sources')
}

/**
 * 搜索图库
 * @param params 搜索参数
 */
export function searchImages(params: ImageSearchRequest) {
  return request.get<ImageSearchResponse>('/v1/image-stock/search', { params })
}

/**
 * 搜索图库 (POST)
 * @param data 搜索参数
 */
export function searchImagesPost(data: ImageSearchRequest) {
  return request.post<ImageSearchResponse>('/v1/image-stock/search', data)
}

/**
 * 根据内容建议搜索关键词
 * @param data 关键词建议请求
 */
export function suggestKeywords(data: KeywordSuggestRequest) {
  return request.post<KeywordSuggestResponse>('/v1/image-stock/suggest-keywords', data)
}

// 图库来源标签
export const SOURCE_LABELS: Record<ImageSource, string> = {
  [ImageSource.UNSPLASH]: 'Unsplash',
  [ImageSource.PEXELS]: 'Pexels',
  [ImageSource.AI_GENERATED]: 'AI 生成',
}

// 图片方向标签
export const ORIENTATION_LABELS: Record<ImageOrientation, string> = {
  [ImageOrientation.LANDSCAPE]: '横向',
  [ImageOrientation.PORTRAIT]: '纵向',
  [ImageOrientation.SQUARE]: '正方形',
}
