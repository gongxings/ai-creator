import { request } from '@/utils/request'
import type { Creation } from './writing'

export interface CreationListParams {
  page?: number
  page_size?: number
  tool_type?: string
  status?: string
}

export interface CreationListResponse {
  items: Creation[]
  total: number
  page: number
  page_size: number
}

// 获取创作列表
export function getCreations(params: CreationListParams) {
  return request.get<{ data: CreationListResponse }>('/creations', { params })
}

// 获取创作详情
export function getCreation(id: number) {
  return request.get<{ data: Creation }>(`/creations/${id}`)
}

// 更新创作内容
export function updateCreation(id: number, data: { title?: string; content?: string }) {
  return request.put<{ data: Creation }>(`/creations/${id}`, data)
}

// 删除创作
export function deleteCreation(id: number) {
  return request.delete(`/creations/${id}`)
}

// 获取版本历史
export function getCreationVersions(id: number) {
  return request.get<{ data: any[] }>(`/creations/${id}/versions`)
}
