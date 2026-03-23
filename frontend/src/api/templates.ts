/**
 * 内容模板 API - 支持多平台
 */
import request from './request'
import type {
  ContentTemplate,
  ArticleTemplate,
  TemplateCreate,
  TemplateUpdate,
  TemplateListResponse,
  TemplateCloneRequest,
  PlatformsResponse,
  PlatformType
} from '@/types/template'

// 获取平台列表
export function getPlatforms() {
  return request.get<PlatformsResponse>('/v1/templates/platforms')
}

// 获取模板列表（支持平台筛选）
export function getTemplates(params?: {
  skip?: number
  limit?: number
  platform?: PlatformType
  category?: string
  style?: string
  is_system?: boolean
  search?: string
}) {
  return request.get<TemplateListResponse>('/v1/templates', { params })
}

// 获取模板详情
export function getTemplate(id: number) {
  return request.get<ContentTemplate>(`/v1/templates/${id}`)
}

// 创建模板
export function createTemplate(data: TemplateCreate) {
  return request.post<ContentTemplate>('/v1/templates', data)
}

// 更新模板
export function updateTemplate(id: number, data: TemplateUpdate) {
  return request.put<ContentTemplate>(`/v1/templates/${id}`, data)
}

// 删除模板
export function deleteTemplate(id: number) {
  return request.delete(`/v1/templates/${id}`)
}

// 克隆模板
export function cloneTemplate(id: number, data?: TemplateCloneRequest) {
  return request.post<ContentTemplate>(`/v1/templates/${id}/clone`, data || {})
}

// 记录模板使用
export function useTemplate(id: number) {
  return request.post<{ message: string; use_count: number }>(`/v1/templates/${id}/use`)
}
