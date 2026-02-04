import { get, post, put, del } from '@/utils/request'
import type { AIModel, AIModelForm, AvailableModel, ChatRequest, ChatResponse } from '@/types'

// 获取AI模型列表
export function getAIModels() {
  return get<AIModel[]>('/v1/models')
}

// 获取可用模型列表（包括OAuth和API Key模型）
export function getAvailableModels(sceneType?: string) {
  const params = sceneType ? { scene_type: sceneType } : {}
  return get<{ models: AvailableModel[] }>('/v1/models/available', params)
}

// 统一AI调用接口
export function chatWithModel(data: ChatRequest) {
  return post<ChatResponse>('/v1/ai/chat', data)
}

// 添加AI模型
export function addAIModel(data: AIModelForm) {
  return post<AIModel>('/v1/models', data)
}

// 更新AI模型
export function updateAIModel(id: number, data: Partial<AIModelForm>) {
  return put<AIModel>(`/v1/models/${id}`, data)
}

// 删除AI模型
export function deleteAIModel(id: number) {
  return del(`/v1/models/${id}`)
}
