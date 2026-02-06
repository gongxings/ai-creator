import request from './request'

export interface PPTGenerateRequest {
  topic: string
  slides_count?: number
  style?: string
  language?: string
}

export interface PPTFromOutlineRequest {
  outline: string
  style?: string
}

export interface PPTGenerateResponse {
  task_id: string
  status: string
  ppt_url?: string
  preview_images?: string[]
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
