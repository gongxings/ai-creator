import request from './request'
import type { WritingTool, Creation, GenerateContentParams, CreationVersion, PaginationParams, PaginationResponse } from '@/types'

export function getWritingTools() {
  return request.get<WritingTool[]>('/v1/writing/tools')
}

export function generateContent(data: GenerateContentParams) {
  return request.post<Creation>('/v1/writing/generate', {
    tool_type: data.tool_type,
    parameters: data.params,
    model_id: data.ai_model_id,
  })
}

export function regenerateContent(creationId: number, params?: Record<string, any>) {
  return request.post<Creation>(`/v1/writing/${creationId}/regenerate`, { params })
}

export function optimizeContent(creationId: number, optimizationType: string, requirements?: string) {
  return request.post<Creation>(`/v1/writing/${creationId}/optimize`, {
    optimization_type: optimizationType,
    requirements
  })
}

export function getCreations(params: PaginationParams & { content_type?: string; tool_type?: string }) {
  return request.get<PaginationResponse<Creation>>('/v1/creations', { params })
}

export function getCreation(id: number) {
  return request.get<Creation>(`/v1/creations/${id}`)
}

export function updateCreation(id: number, data: { title?: string; content?: string }) {
  return request.put<Creation>(`/v1/creations/${id}`, data)
}

export function deleteCreation(id: number) {
  return request.delete(`/v1/creations/${id}`)
}

export function getVersions(creationId: number) {
  return request.get<CreationVersion[]>(`/v1/creations/${creationId}/versions`)
}
