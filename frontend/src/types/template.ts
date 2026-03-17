/**
 * 文章模板类型定义
 */

// CSS 属性配置
export interface CSSProperties {
  fontSize?: string
  fontWeight?: string
  color?: string
  backgroundColor?: string
  lineHeight?: string
  marginTop?: string
  marginBottom?: string
  marginLeft?: string
  marginRight?: string
  paddingTop?: string
  paddingBottom?: string
  paddingLeft?: string
  paddingRight?: string
  padding?: string
  margin?: string
  borderLeft?: string
  borderBottom?: string
  borderRadius?: string
  textAlign?: string
  textIndent?: string
  textDecoration?: string
  fontFamily?: string
  maxWidth?: string
  display?: string
  overflow?: string
  border?: string
  borderTop?: string
  fontStyle?: string
  letterSpacing?: string
  boxShadow?: string
  [key: string]: string | undefined
}

// 模板样式配置
export interface TemplateStyles {
  container?: CSSProperties
  h1?: CSSProperties
  h2?: CSSProperties
  h3?: CSSProperties
  p?: CSSProperties
  blockquote?: CSSProperties
  ul?: CSSProperties
  ol?: CSSProperties
  li?: CSSProperties
  code?: CSSProperties
  pre?: CSSProperties
  img?: CSSProperties
  a?: CSSProperties
  hr?: CSSProperties
  strong?: CSSProperties
  em?: CSSProperties
  [key: string]: CSSProperties | undefined
}

// 文章模板
export interface ArticleTemplate {
  id: number
  name: string
  description?: string
  thumbnail?: string
  styles: TemplateStyles
  is_system: boolean
  is_public: boolean
  user_id?: number
  use_count: number
  created_at: string
  updated_at: string
}

// 创建模板请求
export interface TemplateCreate {
  name: string
  description?: string
  thumbnail?: string
  styles: TemplateStyles
  is_public?: boolean
}

// 更新模板请求
export interface TemplateUpdate {
  name?: string
  description?: string
  thumbnail?: string
  styles?: TemplateStyles
  is_public?: boolean
}

// 模板列表响应
export interface TemplateListResponse {
  total: number
  items: ArticleTemplate[]
}

// 克隆模板请求
export interface TemplateCloneRequest {
  name?: string
}
