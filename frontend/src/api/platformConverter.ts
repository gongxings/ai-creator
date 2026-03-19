/**
 * 多平台内容转换 API
 */
import request from './request'

// 目标平台枚举
export enum TargetPlatform {
  WECHAT = 'wechat_article',           // 微信公众号
  XIAOHONGSHU = 'xiaohongshu_note',    // 小红书
  DOUYIN = 'video_script',             // 抖音短视频脚本
  ZHIHU = 'zhihu_answer',              // 知乎回答
  WEIBO = 'weibo_post',                // 微博
  TOUTIAO = 'toutiao_article',         // 今日头条
  BILIBILI = 'bilibili_dynamic',       // B站动态
}

// 平台信息
export interface PlatformInfo {
  code: string                    // 平台代码
  name: string                    // 平台中文名
  icon?: string                   // 平台图标
  max_length?: number             // 内容长度限制
  features: string[]              // 平台特点
  tips: string[]                  // 写作技巧
}

// 转换请求
export interface ConvertRequest {
  creation_id: number             // 原创作记录ID
  target_platform: TargetPlatform // 目标平台
  style_adjustment?: string       // 风格调整说明
  keep_structure?: boolean        // 是否保留原文结构
  add_emojis?: boolean            // 是否添加表情符号
  generate_tags?: boolean         // 是否生成平台标签
}

// 转换结果
export interface ConvertResult {
  original_platform: string       // 原始平台
  target_platform: string         // 目标平台
  original_title: string          // 原标题
  converted_title: string         // 转换后标题
  converted_content: string       // 转换后内容
  tags: string[]                  // 推荐标签
  word_count: number              // 字数统计
  conversion_notes: string[]      // 转换说明
  creation_id?: number            // 新创作记录ID
}

// 批量转换请求
export interface BatchConvertRequest {
  creation_id: number             // 原创作记录ID
  target_platforms: TargetPlatform[] // 目标平台列表
  style_adjustment?: string       // 风格调整说明
}

// 批量转换结果
export interface BatchConvertResult {
  original_creation_id: number    // 原创作记录ID
  results: ConvertResult[]        // 转换结果列表
  success_count: number           // 成功数量
  failed_count: number            // 失败数量
}

/**
 * 获取支持的目标平台列表
 */
export function getPlatforms() {
  return request.get<PlatformInfo[]>('/v1/converter/platforms')
}

/**
 * 获取指定平台的详细信息
 * @param platform 平台代码
 */
export function getPlatformInfo(platform: TargetPlatform) {
  return request.get<PlatformInfo>(`/v1/converter/platforms/${platform}`)
}

/**
 * 转换内容到目标平台
 * @param data 转换请求
 */
export function convertContent(data: ConvertRequest) {
  return request.post<ConvertResult>('/v1/converter/convert', data)
}

/**
 * 批量转换内容到多个平台
 * @param data 批量转换请求
 */
export function batchConvert(data: BatchConvertRequest) {
  return request.post<BatchConvertResult>('/v1/converter/batch-convert', data)
}

// 平台对应的中文名称
export const PLATFORM_LABELS: Record<TargetPlatform, string> = {
  [TargetPlatform.WECHAT]: '微信公众号',
  [TargetPlatform.XIAOHONGSHU]: '小红书',
  [TargetPlatform.DOUYIN]: '抖音脚本',
  [TargetPlatform.ZHIHU]: '知乎回答',
  [TargetPlatform.WEIBO]: '微博',
  [TargetPlatform.TOUTIAO]: '今日头条',
  [TargetPlatform.BILIBILI]: 'B站动态',
}

// 平台图标（使用 Element Plus icon 名称或 emoji）
export const PLATFORM_ICONS: Record<TargetPlatform, string> = {
  [TargetPlatform.WECHAT]: '💬',
  [TargetPlatform.XIAOHONGSHU]: '📕',
  [TargetPlatform.DOUYIN]: '🎵',
  [TargetPlatform.ZHIHU]: '❓',
  [TargetPlatform.WEIBO]: '📢',
  [TargetPlatform.TOUTIAO]: '📰',
  [TargetPlatform.BILIBILI]: '📺',
}

// 平台颜色
export const PLATFORM_COLORS: Record<TargetPlatform, string> = {
  [TargetPlatform.WECHAT]: '#07c160',
  [TargetPlatform.XIAOHONGSHU]: '#ff2442',
  [TargetPlatform.DOUYIN]: '#000000',
  [TargetPlatform.ZHIHU]: '#0066ff',
  [TargetPlatform.WEIBO]: '#ff8200',
  [TargetPlatform.TOUTIAO]: '#f85959',
  [TargetPlatform.BILIBILI]: '#00a1d6',
}
