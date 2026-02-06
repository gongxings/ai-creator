import request from './request'

export interface ImageGenerateRequest {
  prompt: string
  negative_prompt?: string
  width?: number
  height?: number
  num_images?: number
  style?: string
}

export interface ImageGenerateResponse {
  task_id: string
  status: string
  images?: string[]
}

export interface ImageEditRequest {
  image: string
  prompt: string
  mask?: string
}

export interface ImageUpscaleRequest {
  image: string
  scale: number
}

// 文本生成图片
export function generateImage(data: ImageGenerateRequest) {
  return request.post<{ data: ImageGenerateResponse }>('/v1/image/generate', data)
}

// 图片变体
export function createImageVariation(data: { image: string; num_variations?: number }) {
  return request.post<{ data: ImageGenerateResponse }>('/v1/image/variation', data)
}

// 图片编辑
export function editImage(data: ImageEditRequest) {
  return request.post<{ data: ImageGenerateResponse }>('/v1/image/edit', data)
}

// 图片放大
export function upscaleImage(data: ImageUpscaleRequest) {
  return request.post<{ data: ImageGenerateResponse }>('/v1/image/upscale', data)
}

// 获取任务状态
export function getImageTaskStatus(taskId: string) {
  return request.get<{ data: ImageGenerateResponse }>(`/v1/image/task/${taskId}`)
}

// 优化提示词
export function optimizePrompt(data: { prompt: string }) {
  return request.post<{ data: { optimized_prompt: string } }>('/v1/image/optimize-prompt', data)
}
