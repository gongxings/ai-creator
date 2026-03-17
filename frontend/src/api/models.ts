import request from './request'
import type { AIModel, AIModelForm, AvailableModel, ChatRequest, ChatResponse, ModelCapability } from '@/types'

// 获取AI模型列表
export function getAIModels(capability?: ModelCapability) {
  return request.get<AIModel[]>('/v1/models', {
    params: capability ? { capability } : {}
  })
}

// 获取可用模型列表（包括OAuth和API Key模型）
export function getAvailableModels(sceneType?: string) {
  return request.get<{ data: { models: AvailableModel[] } }>('/v1/ai/models/available', {
    params: sceneType ? { scene_type: sceneType } : {}
  }).then((res: any) => res.data)
}

// 统一AI调用接口
export function chatWithModel(data: ChatRequest) {
  return request.post<ChatResponse>('/v1/ai/chat', data)
}

// 添加AI模型
export function addAIModel(data: AIModelForm) {
  return request.post<AIModel>('/v1/models', data)
}

// 更新AI模型
export function updateAIModel(id: number, data: Partial<AIModelForm>) {
  return request.put<AIModel>(`/v1/models/${id}`, data)
}

// 删除AI模型
export function deleteAIModel(id: number) {
  return request.delete(`/v1/models/${id}`)
}
