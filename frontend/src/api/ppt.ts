import request from './request'

export interface PPTGenerateRequest {
  topic: string
  slides_count?: number
  style?: string
  language?: string
  template_id?: number
  model_id?: number
}

export interface PPTFromOutlineRequest {
  outline: string
  style?: string
  template_id?: number
}

export interface PPTGenerateResponse {
  task_id: string
  status: string
  ppt_url?: string
  preview_images?: string[]
  outline?: PPTOutline
}

export interface PPTOutline {
  title: string
  subtitle?: string
  slides: {
    slide_type: string
    title: string
    bullets?: string[]
    notes?: string
    enrichedItems?: { title: string; text: string }[]
  }[]
  creation_id?: number
  created_at?: string
}

export interface PPTOutlineItem {
  id: number
  title: string
  topic: string
  slides_count: number
  style: string
  created_at: string
  status: string
}

export interface PPTOutlineListResponse {
  total: number
  items: PPTOutlineItem[]
}

// 主题生成PPT
export function generatePPT(data: PPTGenerateRequest) {
  return request.post<{ data: PPTGenerateResponse }>('/v1/ppt/generate', data)
}

// 大纲生成PPT
export function generatePPTFromOutline(data: PPTFromOutlineRequest) {
  return request.post<{ data: PPTGenerateResponse }>('/v1/ppt/from-outline', data)
}

// 文档转PPT
export function convertDocToPPT(data: { file: File; style?: string }) {
  const formData = new FormData()
  formData.append('file', data.file)
  if (data.style) {
    formData.append('style', data.style)
  }
  
  return request.post<{ data: PPTGenerateResponse }>('/v1/ppt/from-document', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 获取任务状态
export function getPPTTaskStatus(taskId: string) {
  return request.get<{ data: PPTGenerateResponse }>(`/v1/ppt/task/${taskId}`)
}

// 下载PPT
export function downloadPPT(pptId: string) {
  return request.get(`/v1/ppt/${pptId}/download`, {
    responseType: 'blob',
  })
}

// 获取PPT模板列表
export function getPPTTemplates() {
  return request.get<{ data: any[] }>('/v1/ppt/templates')
}

// 生成PPT大纲（不生成PPT文件，只返回大纲用于前端渲染）
export function generatePPTOutline(data: PPTGenerateRequest) {
  return request.post<{ data: PPTOutline }>('/v1/ppt/generate-outline', data)
}

// 获取PPT大纲历史记录
export function getPPTOutlines(skip: number = 0, limit: number = 20) {
  return request.get<{ data: PPTOutlineListResponse }>('/v1/ppt/outlines', { params: { skip, limit } })
}

// 获取PPT大纲详情
export function getPPTOutline(outlineId: number) {
  return request.get<{ data: PPTOutline }>(`/v1/ppt/outlines/${outlineId}`)
}

// 删除PPT大纲
export function deletePPTOutline(outlineId: number) {
  return request.delete(`/v1/ppt/outlines/${outlineId}`)
}

// 保存PPT
export interface SavePPTRequest {
  title: string
  slides: any[]
  template_id?: string
  outline_id?: number
}

export function savePPT(data: SavePPTRequest) {
  return request.post<{ data: { id: number; title: string; created_at: string } }>('/v1/ppt/save', data)
}

// 获取已保存的PPT列表
export function getSavedPPTs(skip: number = 0, limit: number = 20) {
  return request.get<{ data: { total: number; items: { id: number; title: string; created_at: string }[] } }>('/v1/ppt/saved', { params: { skip, limit } })
}

// 获取已保存的PPT详情
export function getSavedPPT(pptId: number) {
  return request.get<{ data: { id: number; title: string; slides: any[]; template_id?: string; created_at: string } }>(`/v1/ppt/saved/${pptId}`)
}

// 删除已保存的PPT
export function deleteSavedPPT(pptId: number) {
  return request.delete(`/v1/ppt/saved/${pptId}`)
}
