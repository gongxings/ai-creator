/**
 * Markdown 渲染服务
 * 
 * 负责将 Markdown 转换为 HTML 并应用模板样式
 */
import { marked } from 'marked'
import type { ArticleTemplate, TemplateStyles, CSSProperties } from '@/types/template'

// 配置 marked
marked.setOptions({
  gfm: true,        // GitHub Flavored Markdown
  breaks: true,     // 换行符转为 <br>
})

/**
 * 将 CSS 属性对象转换为内联样式字符串
 */
export function cssPropertiesToInlineStyle(props: CSSProperties | undefined): string {
  if (!props) return ''
  
  const styleMap: Record<string, string> = {
    fontSize: 'font-size',
    fontWeight: 'font-weight',
    fontFamily: 'font-family',
    fontStyle: 'font-style',
    color: 'color',
    backgroundColor: 'background-color',
    lineHeight: 'line-height',
    marginTop: 'margin-top',
    marginBottom: 'margin-bottom',
    marginLeft: 'margin-left',
    marginRight: 'margin-right',
    paddingTop: 'padding-top',
    paddingBottom: 'padding-bottom',
    paddingLeft: 'padding-left',
    paddingRight: 'padding-right',
    padding: 'padding',
    margin: 'margin',
    borderLeft: 'border-left',
    borderBottom: 'border-bottom',
    borderTop: 'border-top',
    border: 'border',
    borderRadius: 'border-radius',
    textAlign: 'text-align',
    textIndent: 'text-indent',
    textDecoration: 'text-decoration',
    letterSpacing: 'letter-spacing',
    maxWidth: 'max-width',
    display: 'display',
    overflow: 'overflow',
    boxShadow: 'box-shadow',
  }
  
  const styles: string[] = []
  
  for (const [key, value] of Object.entries(props)) {
    if (value !== undefined && value !== null && value !== '') {
      const cssKey = styleMap[key] || key.replace(/([A-Z])/g, '-$1').toLowerCase()
      styles.push(`${cssKey}: ${value}`)
    }
  }
  
  return styles.join('; ')
}

/**
 * 将 Markdown 转换为 HTML
 */
export function markdownToHtml(markdown: string): string {
  if (!markdown) return ''
  return marked.parse(markdown) as string
}

/**
 * 为 HTML 元素应用模板样式
 */
export function applyTemplateStyles(html: string, styles: TemplateStyles): string {
  if (!html || !styles) return html
  
  // 定义元素和对应的样式
  const elementStyles: [string, keyof TemplateStyles][] = [
    ['h1', 'h1'],
    ['h2', 'h2'],
    ['h3', 'h3'],
    ['h4', 'h3'],  // h4 使用 h3 样式
    ['h5', 'h3'],  // h5 使用 h3 样式
    ['h6', 'h3'],  // h6 使用 h3 样式
    ['p', 'p'],
    ['blockquote', 'blockquote'],
    ['ul', 'ul'],
    ['ol', 'ol'],
    ['li', 'li'],
    ['pre', 'pre'],
    ['img', 'img'],
    ['a', 'a'],
    ['hr', 'hr'],
    ['strong', 'strong'],
    ['b', 'strong'],
    ['em', 'em'],
    ['i', 'em'],
  ]
  
  let result = html
  
  // 为每种元素添加内联样式
  for (const [tag, styleKey] of elementStyles) {
    const style = styles[styleKey]
    if (style) {
      const inlineStyle = cssPropertiesToInlineStyle(style)
      if (inlineStyle) {
        // 匹配开始标签，支持已有属性
        const regex = new RegExp(`<${tag}(\\s[^>]*)?>`, 'gi')
        result = result.replace(regex, (match, attrs) => {
          // 检查是否已有 style 属性
          if (attrs && attrs.includes('style=')) {
            // 合并样式
            return match.replace(/style="([^"]*)"/, `style="$1; ${inlineStyle}"`)
          }
          return `<${tag}${attrs || ''} style="${inlineStyle}">`
        })
      }
    }
  }
  
  // 处理行内代码 (code 不在 pre 内的情况)
  if (styles.code) {
    const codeStyle = cssPropertiesToInlineStyle(styles.code)
    if (codeStyle) {
      // 只处理不在 <pre> 中的 <code>
      result = result.replace(/<code(?![^>]*class="[^"]*language)([^>]*)>/gi, (match, attrs) => {
        if (attrs && attrs.includes('style=')) {
          return match.replace(/style="([^"]*)"/, `style="$1; ${codeStyle}"`)
        }
        return `<code${attrs || ''} style="${codeStyle}">`
      })
    }
  }
  
  return result
}

/**
 * 渲染 Markdown 并应用模板样式
 */
export function renderWithTemplate(markdown: string, template: ArticleTemplate | null): string {
  // 先将 Markdown 转换为 HTML
  const html = markdownToHtml(markdown)
  
  // 如果没有模板，直接返回原始 HTML
  if (!template) return html
  
  // 应用模板样式
  const styledHtml = applyTemplateStyles(html, template.styles)
  
  // 如果有容器样式，包裹在容器中
  if (template.styles.container) {
    const containerStyle = cssPropertiesToInlineStyle(template.styles.container)
    return `<div class="template-container" style="${containerStyle}">${styledHtml}</div>`
  }
  
  return styledHtml
}

/**
 * 生成用于微信公众号的 HTML
 * 微信公众号需要所有样式都是内联的
 */
export function renderForWechat(markdown: string, template: ArticleTemplate | null): string {
  const html = renderWithTemplate(markdown, template)
  
  // 移除可能不支持的 CSS 属性
  // 微信公众号对某些 CSS 属性支持有限
  return html
    .replace(/letter-spacing:[^;]+;?/gi, '')  // 移除 letter-spacing（部分版本不支持）
}

/**
 * 示例 Markdown 内容（用于模板预览）
 */
export const sampleMarkdown = `# 文章标题

这是一段普通的正文内容。这里演示了基本的段落样式，包括字体大小、行高、颜色等。

## 二级标题

### 三级标题

这是另一段正文。**加粗文字** 和 *斜体文字* 的样式也会被应用。

> 这是一段引用文字。引用块通常用于突出显示重要的信息或名人名言。

#### 列表示例

无序列表：
- 第一项
- 第二项
- 第三项

有序列表：
1. 第一步
2. 第二步
3. 第三步

#### 代码示例

行内代码：\`const hello = "world"\`

代码块：
\`\`\`javascript
function greet(name) {
  console.log(\`Hello, \${name}!\`);
}
\`\`\`

---

这是分隔线后的内容。[这是一个链接](https://example.com)。

![示例图片](https://via.placeholder.com/600x300)
`

export default {
  markdownToHtml,
  applyTemplateStyles,
  renderWithTemplate,
  renderForWechat,
  cssPropertiesToInlineStyle,
  sampleMarkdown
}
