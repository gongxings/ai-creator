/**
 * 文章模板 API
 */
import request from './request'
import type {
  ArticleTemplate,
  TemplateCreate,
  TemplateUpdate,
  TemplateListResponse,
  TemplateCloneRequest
} from '@/types/template'

// 获取模板列表
export function getTemplates(params?: {
  skip?: number
  limit?: number
  is_system?: boolean
  search?: string
}) {
  return request.get<TemplateListResponse>('/v1/templates', { params })
}

// 获取模板详情
export function getTemplate(id: number) {
  return request.get<ArticleTemplate>(`/v1/templates/${id}`)
}

// 创建模板
export function createTemplate(data: TemplateCreate) {
  return request.post<ArticleTemplate>('/v1/templates', data)
}

// 更新模板
export function updateTemplate(id: number, data: TemplateUpdate) {
  return request.put<ArticleTemplate>(`/v1/templates/${id}`, data)
}

// 删除模板
export function deleteTemplate(id: number) {
  return request.delete(`/v1/templates/${id}`)
}

// 克隆模板
export function cloneTemplate(id: number, data?: TemplateCloneRequest) {
  return request.post<ArticleTemplate>(`/v1/templates/${id}/clone`, data || {})
}

// 记录模板使用
export function useTemplate(id: number) {
  return request.post<{ message: string; use_count: number }>(`/v1/templates/${id}/use`)
}
