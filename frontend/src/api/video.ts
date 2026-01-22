import request from './request'

export interface VideoGenerateRequest {
  prompt: string
  duration?: number
  fps?: number
  resolution?: string
}

export interface VideoGenerateResponse {
  task_id: string
  status: string
  video_url?: string
  progress?: number
}

export interface TextToVideoRequest {
  text: string
  voice?: string
  background_music?: boolean
  subtitle?: boolean
}

export interface ImageToVideoRequest {
  images: string[]
  transition?: string
  duration_per_image?: number
}

// 生成视频
export function generateVideo(data: VideoGenerateRequest) {
  return request.post<{ data: VideoGenerateResponse }>('/video/generate', data)
}

// 文本转视频
export function textToVideo(data: TextToVideoRequest) {
  return request.post<{ data: VideoGenerateResponse }>('/video/text-to-video', data)
}

// 图片转视频
export function imageToVideo(data: ImageToVideoRequest) {
  return request.post<{ data: VideoGenerateResponse }>('/video/image-to-video', data)
}

// 获取任务状态
export function getVideoTaskStatus(taskId: string) {
  return request.get<{ data: VideoGenerateResponse }>(`/video/task/${taskId}`)
}

// AI配音
export function generateVoiceover(data: { text: string; voice?: string }) {
  return request.post<{ data: { audio_url: string } }>('/video/voiceover', data)
}

// 生成字幕
export function generateSubtitles(data: { video_url: string }) {
  return request.post<{ data: { subtitles: any[] } }>('/video/subtitles', data)
}
