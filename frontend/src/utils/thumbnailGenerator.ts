/**
 * 缩略图生成工具
 * 使用Canvas渲染PPTist JSON为缩略图
 */

interface PPTistSlide {
  id: string
  elements: any[]
  background?: {
    type: string
    color?: string
  }
}

interface PPTistJSON {
  slides: PPTistSlide[]
  themeColors: string[]
  size: {
    width: number
    height: number
  }
}

/**
 * 将PPTist JSON的第一页渲染为缩略图
 */
export async function generateThumbnail(json: PPTistJSON, width: number = 320, height: number = 180): Promise<string> {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) {
    throw new Error('Canvas不支持')
  }
  
  canvas.width = width
  canvas.height = height
  
  // 获取第一页幻灯片
  const slide = json.slides[0]
  if (!slide) {
    // 没有幻灯片，返回空白
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)
    return canvas.toDataURL('image/png')
  }
  
  // 计算缩放比例
  const originalWidth = json.size.width || 960
  const originalHeight = json.size.height || 540
  const scaleX = width / originalWidth
  const scaleY = height / originalHeight
  const scale = Math.min(scaleX, scaleY)
  
  // 绘制背景
  const bgColor = slide.background?.color || '#ffffff'
  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)
  
  // 绘制元素
  for (const element of slide.elements || []) {
    try {
      ctx.save()
      
      const x = (element.left || 0) * scale
      const y = (element.top || 0) * scale
      const w = (element.width || 100) * scale
      const h = (element.height || 100) * scale
      
      // 处理旋转
      if (element.rotate) {
        ctx.translate(x + w / 2, y + h / 2)
        ctx.rotate((element.rotate * Math.PI) / 180)
        ctx.translate(-(x + w / 2), -(y + h / 2))
      }
      
      switch (element.type) {
        case 'shape':
          drawShape(ctx, element, x, y, w, h)
          break
        case 'text':
          drawText(ctx, element, x, y, w, h, scale)
          break
        case 'image':
          // 图片元素暂时跳过（需要异步加载）
          break
      }
      
      ctx.restore()
    } catch (e) {
      console.warn('绘制元素失败:', e)
    }
  }
  
  return canvas.toDataURL('image/png')
}

/**
 * 绘制形状
 */
function drawShape(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number) {
  // 填充颜色
  const fill = element.fill
  if (fill) {
    if (typeof fill === 'string') {
      ctx.fillStyle = fill
    } else if (fill.type === 'color') {
      ctx.fillStyle = fill.value || '#cccccc'
    } else {
      ctx.fillStyle = '#cccccc'
    }
  } else {
    ctx.fillStyle = '#cccccc'
  }
  
  // 绘制矩形
  ctx.fillRect(x, y, w, h)
  
  // 绘制边框
  if (element.borderColor) {
    ctx.strokeStyle = element.borderColor
    ctx.lineWidth = element.borderWidth || 1
    ctx.strokeRect(x, y, w, h)
  }
}

/**
 * 绘制文本
 */
function drawText(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number, scale: number) {
  // 解析HTML内容提取文本
  const content = element.content || ''
  const text = extractTextFromHTML(content)
  
  if (!text) return
  
  // 设置字体
  const fontSize = Math.max(8, 14 * scale)
  ctx.font = `${fontSize}px sans-serif`
  ctx.fillStyle = '#333333'
  ctx.textBaseline = 'top'
  
  // 绘制文本
  const maxWidth = w - 4
  const lines = wrapText(ctx, text, maxWidth)
  const lineHeight = fontSize * 1.2
  
  lines.forEach((line, index) => {
    if (y + index * lineHeight + lineHeight < y + h) {
      ctx.fillText(line, x + 2, y + 2 + index * lineHeight)
    }
  })
}

/**
 * 从HTML中提取纯文本
 */
function extractTextFromHTML(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

/**
 * 文本换行
 */
function wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
  const words = text.split('')
  const lines: string[] = []
  let currentLine = ''
  
  for (const char of words) {
    const testLine = currentLine + char
    const metrics = ctx.measureText(testLine)
    
    if (metrics.width > maxWidth && currentLine) {
      lines.push(currentLine)
      currentLine = char
    } else {
      currentLine = testLine
    }
    
    // 限制行数
    if (lines.length >= 3) break
  }
  
  if (currentLine && lines.length < 4) {
    lines.push(currentLine)
  }
  
  return lines
}

/**
 * 将dataURL转换为Blob
 */
export function dataURLToBlob(dataURL: string): Blob {
  const arr = dataURL.split(',')
  const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/png'
  const bstr = atob(arr[1])
  const n = bstr.length
  const u8arr = new Uint8Array(n)
  
  for (let i = 0; i < n; i++) {
    u8arr[i] = bstr.charCodeAt(i)
  }
  
  return new Blob([u8arr], { type: mime })
}
