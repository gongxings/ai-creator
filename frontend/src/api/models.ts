import { get, post, put, del } from '@/utils/request'
import type { AIModel, AIModelForm } from '@/types'

// 获取AI模型列表
export function getAIModels() {
  return get<AIModel[]>('/v1/models')
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
