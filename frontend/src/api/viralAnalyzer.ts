/**
 * 爆款模仿 API
 * 分析爆款文章风格并生成类似内容
 */
import request from './request'

// 内容类别枚举
export enum ContentCategory {
  EMOTION = 'emotion',           // 情感共鸣
  KNOWLEDGE = 'knowledge',       // 知识干货
  STORY = 'story',               // 故事叙事
  NEWS = 'news',                 // 新闻热点
  TUTORIAL = 'tutorial',         // 教程攻略
  REVIEW = 'review',             // 测评种草
  OPINION = 'opinion',           // 观点输出
}

// 爆款元素
export interface ViralElement {
  name: string                   // 元素名称
  description: string            // 元素说明
  score: number                  // 该元素的运用得分 (0-100)
  examples: string[]             // 文中示例
}

// 结构分析
export interface StructureAnalysis {
  sections: string[]             // 段落结构
  opening_hook: string           // 开头钩子
  closing_cta: string            // 结尾行动召唤
  transition_style: string       // 过渡风格
}

// 爆款分析请求
export interface AnalyzeRequest {
  content: string                // 要分析的爆款内容
  title?: string                 // 文章标题
  platform?: string              // 来源平台
}

// 爆款分析响应
export interface AnalyzeResponse {
  title: string                  // 文章标题
  category: ContentCategory      // 内容类别
  viral_score: number            // 爆款指数 (0-100)
  
  // 风格分析
  tone: string                   // 语气风格
  target_audience: string        // 目标受众
  emotional_triggers: string[]   // 情感触发点
  
  // 爆款元素
  viral_elements: ViralElement[] // 爆款元素分析
  
  // 结构分析
  structure: StructureAnalysis   // 结构分析
  
  // 写作技巧
  writing_techniques: string[]   // 写作技巧
  
  // 关键词
  keywords: string[]             // 核心关键词
  
  // 改进建议
  improvement_suggestions: string[] // 可改进的点
}

// 爆款模仿请求
export interface ImitateRequest {
  reference_content: string      // 参考的爆款内容
  reference_title?: string       // 参考文章标题
  new_topic: string              // 新的主题/话题
  platform?: string              // 目标平台
  style_strength?: number        // 风格模仿强度 (0-100)
  keep_structure?: boolean       // 是否保持相同结构
  additional_requirements?: string // 额外要求
}

// 爆款模仿响应
export interface ImitateResponse {
  title: string                  // 生成的标题
  content: string                // 生成的内容
  
  // 模仿说明
  imitation_notes: string[]      // 模仿说明
  elements_applied: string[]     // 应用的爆款元素
  
  // 统计信息
  word_count: number             // 字数
  estimated_viral_score: number  // 预估爆款指数
  
  // 创作记录ID
  creation_id?: number           // 创作记录ID
}

// 爆款元素信息
export interface ViralElementInfo {
  key: string                    // 元素键名
  name: string                   // 元素名称
  description: string            // 元素描述
}

/**
 * 获取爆款元素列表
 */
export function getViralElements() {
  return request.get<{ elements: ViralElementInfo[] }>('/v1/viral/elements')
}

/**
 * 分析爆款内容
 * @param data 分析请求
 */
export function analyzeContent(data: AnalyzeRequest) {
  return request.post<AnalyzeResponse>('/v1/viral/analyze', data)
}

/**
 * 模仿爆款生成内容
 * @param data 模仿请求
 */
export function imitateContent(data: ImitateRequest) {
  return request.post<ImitateResponse>('/v1/viral/imitate', data)
}

// 内容类别对应的中文名称
export const CATEGORY_LABELS: Record<ContentCategory, string> = {
  [ContentCategory.EMOTION]: '情感共鸣',
  [ContentCategory.KNOWLEDGE]: '知识干货',
  [ContentCategory.STORY]: '故事叙事',
  [ContentCategory.NEWS]: '新闻热点',
  [ContentCategory.TUTORIAL]: '教程攻略',
  [ContentCategory.REVIEW]: '测评种草',
  [ContentCategory.OPINION]: '观点输出',
}

// 内容类别对应的颜色
export const CATEGORY_COLORS: Record<ContentCategory, string> = {
  [ContentCategory.EMOTION]: '#f759ab',
  [ContentCategory.KNOWLEDGE]: '#1890ff',
  [ContentCategory.STORY]: '#722ed1',
  [ContentCategory.NEWS]: '#fa541c',
  [ContentCategory.TUTORIAL]: '#13c2c2',
  [ContentCategory.REVIEW]: '#52c41a',
  [ContentCategory.OPINION]: '#faad14',
}

// 爆款指数等级颜色
export function getViralScoreColor(score: number): string {
  if (score >= 90) return '#52c41a'  // 绿色 - 极佳
  if (score >= 70) return '#1890ff'  // 蓝色 - 优秀
  if (score >= 50) return '#faad14'  // 橙色 - 合格
  return '#f5222d'                    // 红色 - 需提升
}

// 爆款指数等级标签
export function getViralScoreLabel(score: number): string {
  if (score >= 90) return '爆款潜力'
  if (score >= 70) return '优质内容'
  if (score >= 50) return '合格内容'
  return '需要提升'
}
