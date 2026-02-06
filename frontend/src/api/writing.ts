import request from './request'
import type { WritingTool, Creation, GenerateContentParams, CreationVersion, PaginationParams, PaginationResponse } from '@/types'

// 获取所有写作工具列表
export function getWritingTools() {
  return request.get<WritingTool[]>('/v1/writing/tools')
}

// 生成内容
export function generateContent(data: GenerateContentParams) {
  return request.post<Creation>(`/v1/writing/generate`, {
    tool_type: data.tool_type,
    parameters: data.params,
    model_id: data.ai_model_id,
    platform: data.platform  // 新增：支持Cookie模式
  })
}

// 重新生成内容
export function regenerateContent(creationId: number, params?: Record<string, any>) {
  return request.post<Creation>(`/v1/writing/${creationId}/regenerate`, { params })
}

// 优化内容
export function optimizeContent(creationId: number, optimizationType: string, requirements?: string) {
  return request.post<Creation>(`/v1/writing/${creationId}/optimize`, {
    optimization_type: optimizationType,
    requirements
  })
}

// 获取创作列表
export function getCreations(params: PaginationParams & { content_type?: string; tool_type?: string }) {
  return request.get<PaginationResponse<Creation>>('/v1/creations', { params })
}

// 获取创作详情
export function getCreation(id: number) {
  return request.get<Creation>(`/v1/creations/${id}`)
}

// 更新创作内容
export function updateCreation(id: number, data: { title?: string; content?: string }) {
  return request.put<Creation>(`/v1/creations/${id}`, data)
}

// 删除创作
export function deleteCreation(id: number) {
  return request.delete(`/v1/creations/${id}`)
}

// 获取版本历史
export function getVersions(creationId: number) {
  return request.get<CreationVersion[]>(`/v1/creations/${creationId}/versions`)
}
