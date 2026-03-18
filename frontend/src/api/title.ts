/**
 * 爆款标题生成 API
 */
import request from './request'

// 标题风格枚举
export enum TitleStyle {
  CURIOSITY = 'curiosity',     // 好奇心驱动
  BENEFIT = 'benefit',         // 利益驱动
  EMOTIONAL = 'emotional',     // 情感驱动
  TRENDING = 'trending',       // 热点借势
  LISTICLE = 'listicle',       // 数字清单
  QUESTION = 'question',       // 提问式
  HOW_TO = 'how_to',           // 教程式
  CONTRAST = 'contrast',       // 对比反差
}

// 目标平台枚举
export enum PlatformType {
  WECHAT = 'wechat',           // 微信公众号
  XIAOHONGSHU = 'xiaohongshu', // 小红书
  DOUYIN = 'douyin',           // 抖音
  ZHIHU = 'zhihu',             // 知乎
  WEIBO = 'weibo',             // 微博
  TOUTIAO = 'toutiao',         // 今日头条
  BILIBILI = 'bilibili',       // B站
}

// 标题生成请求
export interface TitleGenerateRequest {
  content: string              // 内容摘要或主题关键词
  platform?: PlatformType      // 目标平台
  style?: TitleStyle           // 标题风格
  count?: number               // 生成数量 (1-10)
  keywords?: string[]          // 必须包含的关键词
  tone?: string                // 语气
}

// 生成的标题项
export interface TitleItem {
  title: string                // 标题文本
  style: TitleStyle            // 标题风格
  score: number                // 爆款指数 (0-100)
  hooks: string[]              // 使用的钩子技巧
  explanation: string          // 标题解析
}

// 标题生成响应
export interface TitleGenerateResponse {
  titles: TitleItem[]          // 生成的标题列表
  analysis: string             // 整体分析建议
}

// 标题优化请求
export interface TitleOptimizeRequest {
  original_title: string       // 原标题
  platform?: PlatformType      // 目标平台
  optimization_goals?: string[] // 优化目标
}

// 标题优化响应
export interface TitleOptimizeResponse {
  original_title: string       // 原标题
  original_score: number       // 原标题爆款指数
  original_issues: string[]    // 原标题问题分析
  optimized_titles: TitleItem[] // 优化后的标题列表
  improvement_tips: string[]   // 改进建议
}

// 标题分析请求
export interface TitleAnalyzeRequest {
  title: string                // 要分析的标题
  platform?: PlatformType      // 目标平台
}

// 标题分析响应
export interface TitleAnalyzeResponse {
  title: string                // 分析的标题
  score: number                // 爆款指数
  style: TitleStyle            // 识别的标题风格
  strengths: string[]          // 标题优点
  weaknesses: string[]         // 标题缺点
  hooks_used: string[]         // 使用的钩子技巧
  improvement_suggestions: string[] // 改进建议
  platform_fit?: string        // 平台适配度分析
}

// 风格选项
export interface StyleOption {
  value: string
  label: string
}

// 平台选项
export interface PlatformOption {
  value: string
  label: string
  max_length: number
  tips: string[]
}

/**
 * 获取支持的标题风格列表
 */
export function getTitleStyles() {
  return request.get<{ styles: StyleOption[] }>('/v1/title/styles')
}

/**
 * 获取支持的目标平台列表
 */
export function getTitlePlatforms() {
  return request.get<{ platforms: PlatformOption[] }>('/v1/title/platforms')
}

/**
 * 生成爆款标题
 * @param data 标题生成请求
 */
export function generateTitles(data: TitleGenerateRequest) {
  return request.post<TitleGenerateResponse>('/v1/title/generate', data)
}

/**
 * 优化现有标题
 * @param data 标题优化请求
 */
export function optimizeTitle(data: TitleOptimizeRequest) {
  return request.post<TitleOptimizeResponse>('/v1/title/optimize', data)
}

/**
 * 分析标题质量
 * @param data 标题分析请求
 */
export function analyzeTitle(data: TitleAnalyzeRequest) {
  return request.post<TitleAnalyzeResponse>('/v1/title/analyze', data)
}

// 风格对应的中文名称
export const STYLE_LABELS: Record<TitleStyle, string> = {
  [TitleStyle.CURIOSITY]: '好奇心驱动',
  [TitleStyle.BENEFIT]: '利益驱动',
  [TitleStyle.EMOTIONAL]: '情感驱动',
  [TitleStyle.TRENDING]: '热点借势',
  [TitleStyle.LISTICLE]: '数字清单',
  [TitleStyle.QUESTION]: '提问式',
  [TitleStyle.HOW_TO]: '教程式',
  [TitleStyle.CONTRAST]: '对比反差',
}

// 平台对应的中文名称
export const PLATFORM_LABELS: Record<PlatformType, string> = {
  [PlatformType.WECHAT]: '微信公众号',
  [PlatformType.XIAOHONGSHU]: '小红书',
  [PlatformType.DOUYIN]: '抖音',
  [PlatformType.ZHIHU]: '知乎',
  [PlatformType.WEIBO]: '微博',
  [PlatformType.TOUTIAO]: '今日头条',
  [PlatformType.BILIBILI]: 'B站',
}

// 分数等级颜色
export function getScoreColor(score: number): string {
  if (score >= 90) return '#52c41a'  // 绿色 - 极佳
  if (score >= 70) return '#1890ff'  // 蓝色 - 优秀
  if (score >= 50) return '#faad14'  // 橙色 - 合格
  return '#f5222d'                    // 红色 - 需优化
}

// 分数等级标签
export function getScoreLabel(score: number): string {
  if (score >= 90) return '爆款潜力'
  if (score >= 70) return '优秀标题'
  if (score >= 50) return '合格标题'
  return '需要优化'
}
