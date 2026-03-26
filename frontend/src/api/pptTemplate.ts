/**
 * PPT模板API
 */
import request from './request'

export interface PPTTemplate {
  id: number
  name: string
  description?: string
  thumbnail?: string
  category?: string
  style?: string
  is_system: boolean
  user_id?: number
  use_count: number
  created_at: string
}

export interface PPTTemplateDetail extends PPTTemplate {
  ppt_layout?: any
}

export interface PPTTemplateListResponse {
  total: number
  items: PPTTemplate[]
}

// 获取PPT模板列表
export function getPPTTemplates(skip: number = 0, limit: number = 20) {
  return request.get<{ data: PPTTemplateListResponse }>('/v1/ppt-templates', { params: { skip, limit } })
}

// 获取PPT模板详情
export function getPPTTemplateDetail(id: number) {
  return request.get<{ data: PPTTemplateDetail }>(`/v1/ppt-templates/${id}`)
}

// 上传PPTX模板
export function uploadPPTTemplate(data: {
  name: string
  description?: string
  pptx_file: File
  thumbnail?: string
  layout_file: File
}) {
  const formData = new FormData()
  formData.append('name', data.name)
  if (data.description) {
    formData.append('description', data.description)
  }
  formData.append('pptx_file', data.pptx_file)
  if (data.thumbnail) {
    formData.append('thumbnail', data.thumbnail)
  }
  formData.append('layout_file', data.layout_file)
  
  return request.post<{ data: { id: number; name: string; thumbnail?: string } }>('/v1/ppt-templates/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 删除PPT模板
export function deletePPTTemplate(id: number) {
  return request.delete(`/v1/ppt-templates/${id}`)
}
