/**
 * 缩略图生成工具
 * 使用Canvas渲染PPTist JSON为缩略图
 */

interface PPTistSlide {
  id: string
  elements: any[]
  background?: any
  fill?: any
}

interface PPTistJSON {
  slides: PPTistSlide[]
  themeColors?: string[]
  size?: {
    width: number
    height: number
  }
  width?: number
  height?: number
  theme?: {
    themeColors?: string[]
    backgroundColor?: string
    [key: string]: any
  }
}

// 图片缓存
const imageCache = new Map<string, HTMLImageElement>()

/**
 * 加载图片并返回Promise（带缓存）
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  if (imageCache.has(src)) {
    return Promise.resolve(imageCache.get(src)!)
  }

  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      imageCache.set(src, img)
      resolve(img)
    }
    img.onerror = () => reject(new Error('图片加载失败'))
    img.src = src
  })
}

/**
 * 解析颜色值
 */
function parseColor(color: any): string | null {
  if (color === undefined || color === null) return null
  if (typeof color === 'string') {
    if (color === '' || color === 'none' || color === 'transparent') return null
    return color
  }
  if (typeof color === 'object') {
    if (color.type === 'color') {
      return color.value || '#cccccc'
    }
    if (color.type === 'gradient' || color.type === 'linearGradient' || color.type === 'radialGradient') {
      if (color.colors && color.colors.length > 0) {
        const firstColor = color.colors[0]
        if (typeof firstColor === 'string') return firstColor
        if (firstColor.color) return firstColor.color
        if (firstColor.value) return firstColor.value
      }
      if (color.value) return color.value
    }
    if (color.value) return parseColor(color.value)
    if (color.color) return parseColor(color.color)
    if (color.r !== undefined) {
      const r = Math.round(color.r || 0)
      const g = Math.round(color.g || 0)
      const b = Math.round(color.b || 0)
      const a = color.a !== undefined ? color.a : 1
      if (a < 1) {
        return `rgba(${r}, ${g}, ${b}, ${a})`
      }
      return `rgb(${r}, ${g}, ${b})`
    }
  }
  return null
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

  // 使用更高分辨率以获得更清晰的渲染
  const dpr = 2
  canvas.width = width * dpr
  canvas.height = height * dpr

  ctx.scale(dpr, dpr)

  // 获取第一页幻灯片
  const slide = json.slides?.[0]
  if (!slide) {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)
    return canvas.toDataURL('image/png')
  }
  
  // 优先使用 background 字段，格式如 { type: 'solid', color: '#ffffff' }
  const slideBackground = slide.background

  // 计算缩放比例
  const originalWidth = json.size?.width || json.width || 960
  const originalHeight = json.size?.height || json.height || 540
  const scaleX = width / originalWidth
  const scaleY = height / originalHeight
  const scale = Math.min(scaleX, scaleY)

  // 计算居中偏移
  const offsetX = (width - originalWidth * scale) / 2
  const offsetY = (height - originalHeight * scale) / 2

  // 绘制背景
  await drawBackground(ctx, slideBackground, width, height, offsetX, offsetY, originalWidth * scale, originalHeight * scale)

  // 绘制元素（按order排序）
  const elements = (slide.elements || []).sort((a: any, b: any) => (a.order || 0) - (b.order || 0))

  for (const element of elements) {
    try {
      await drawElement(ctx, element, scale, offsetX, offsetY)
    } catch (e) {
      console.warn('绘制元素失败:', element.type, element.name, e)
    }
  }

  return canvas.toDataURL('image/png', 0.95)
}

/**
 * 绘制背景
 */
async function drawBackground(
  ctx: CanvasRenderingContext2D,
  background: any,
  canvasWidth: number,
  canvasHeight: number,
  offsetX: number,
  offsetY: number,
  contentWidth: number,
  contentHeight: number
) {
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  if (!background) return

  let bgColor: string | null = null
  let bgImage: string | null = null

  if (typeof background === 'string') {
    bgColor = background
  } else if (typeof background === 'object') {
    if (background.type === 'solid' || background.type === 'color' || !background.type) {
      bgColor = parseColor(background.color || background.value || background.fill)
    } else if (background.type === 'image' || background.type === 'pic') {
      bgImage = background.src || background.url || background.image
    } else if (background.type === 'gradient' || background.type === 'linearGradient') {
      try {
        const gradient = ctx.createLinearGradient(offsetX, offsetY, offsetX + contentWidth, offsetY + contentHeight)
        const colors = background.colors || []
        colors.forEach((colorItem: any, index: number) => {
          const color = parseColor(colorItem) || '#000000'
          const position = colors.length > 1 ? index / (colors.length - 1) : 0
          gradient.addColorStop(position, color)
        })
        ctx.fillStyle = gradient
        ctx.fillRect(offsetX, offsetY, contentWidth, contentHeight)
        return
      } catch (e) {
        console.warn('渐变绘制失败:', e)
      }
    }
  }

  if (bgColor && bgColor !== '#cccccc') {
    ctx.fillStyle = bgColor
    ctx.fillRect(offsetX, offsetY, contentWidth, contentHeight)
  }

  if (bgImage) {
    try {
      const img = await loadImage(bgImage)
      ctx.drawImage(img, offsetX, offsetY, contentWidth, contentHeight)
    } catch (e) {
      console.warn('背景图片加载失败:', e)
    }
  }
}

/**
 * 绘制元素
 */
async function drawElement(ctx: CanvasRenderingContext2D, element: any, scale: number, offsetX: number, offsetY: number) {
  if (element.hidden || element.visible === false) return

  ctx.save()

  // 计算元素位置和大小
  const x = offsetX + (element.left || 0) * scale
  const y = offsetY + (element.top || 0) * scale
  const w = (element.width || 100) * scale
  const h = (element.height || 100) * scale

  // 处理旋转
  if (element.rotate && element.rotate !== 0) {
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate((element.rotate * Math.PI) / 180)
    ctx.translate(-(x + w / 2), -(y + h / 2))
  }

  // 处理透明度
  const opacity = element.opacity !== undefined ? element.opacity : 1
  if (opacity < 1) {
    ctx.globalAlpha = opacity
  }

  const elementType = element.type || ''

  switch (elementType) {
    case 'shape':
      drawShape(ctx, element, x, y, w, h, scale)
      break
    case 'text':
      drawText(ctx, element, x, y, w, h, scale)
      break
    case 'image':
    case 'pic':
      await drawImage(ctx, element, x, y, w, h)
      break
    case 'table':
      drawTable(ctx, element, x, y, w, h, scale)
      break
    case 'chart':
      drawChartPlaceholder(ctx, x, y, w, h)
      break
    case 'latex':
    case 'formula':
      drawFormula(ctx, element, x, y, w, h, scale)
      break
    case 'audio':
    case 'video':
      drawMediaPlaceholder(ctx, element, x, y, w, h)
      break
    case 'group':
      if (element.elements && Array.isArray(element.elements)) {
        for (const subElement of element.elements) {
          await drawElement(ctx, subElement, scale, x, y)
        }
      }
      break
    default:
      if (element.path || element.shapType || element.fill || element.background) {
        drawShape(ctx, element, x, y, w, h, scale)
      } else if (element.content !== undefined) {
        drawText(ctx, element, x, y, w, h, scale)
      }
  }

  ctx.restore()
}

/**
 * 绘制形状
 */
function drawShape(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number, scale: number) {
  const fill = element.fill || element.background || element.color
  const fillColor = parseColor(fill) || '#cccccc'

  // 保存当前状态
  ctx.save()

  if (element.path) {
    drawSVGPath(ctx, element.path, x, y, w, h, element.width, element.height, fillColor)
  } else {
    const shapeType = element.shapType || 'rect'

    if (fillColor) {
      ctx.fillStyle = fillColor
    } else {
      ctx.fillStyle = '#cccccc'
    }

    if (shapeType === 'ellipse') {
      ctx.beginPath()
      ctx.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2)
      ctx.fill()
    } else if (shapeType === 'triangle') {
      ctx.beginPath()
      ctx.moveTo(x + w / 2, y)
      ctx.lineTo(x + w, y + h)
      ctx.lineTo(x, y + h)
      ctx.closePath()
      ctx.fill()
    } else if (shapeType === 'roundRect' || shapeType === 'roundRectangle') {
      const r = Math.min(element.radius || 10, w / 4, h / 4)
      drawRoundedRect(ctx, x, y, w, h, r)
      ctx.fill()
    } else {
      ctx.fillRect(x, y, w, h)
    }
  }

  // 绘制边框
  const borderColor = parseColor(element.borderColor || element.lineColor)
  const borderWidth = element.borderWidth || element.lineWidth
  if (borderColor && borderWidth && borderWidth > 0) {
    ctx.strokeStyle = borderColor
    ctx.lineWidth = borderWidth * scale

    if (element.path) {
      drawSVGPath(ctx, element.path, x, y, w, h, element.width, element.height, null, borderColor, borderWidth * scale)
    } else {
      ctx.strokeRect(x, y, w, h)
    }
  }

  ctx.restore()
}

/**
 * 绘制SVG路径
 */
function drawSVGPath(ctx: CanvasRenderingContext2D, pathData: string, x: number, y: number, w: number, h: number, originalWidth: number, originalHeight: number, fillColor: string | null, strokeColor?: string, strokeWidth?: number) {
  if (!pathData) return

  ctx.save()
  ctx.translate(x, y)

  const scaleX = w / (originalWidth || 1)
  const scaleY = h / (originalHeight || 1)
  ctx.scale(scaleX, scaleY)

  try {
    const path = new Path2D(pathData)

    if (fillColor) {
      ctx.fillStyle = fillColor
      ctx.fill(path)
    }

    if (strokeColor && strokeWidth) {
      ctx.strokeStyle = strokeColor
      ctx.lineWidth = strokeWidth / Math.min(scaleX, scaleY)
      ctx.stroke(path)
    }
  } catch (e) {
    if (fillColor) {
      ctx.fillStyle = fillColor
      ctx.fillRect(0, 0, originalWidth, originalHeight)
    }
  }

  ctx.restore()
}

/**
 * 绘制圆角矩形路径
 */
function drawRoundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  r = Math.min(r, w / 2, h / 2)
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.quadraticCurveTo(x + w, y, x + w, y + r)
  ctx.lineTo(x + w, y + h - r)
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
  ctx.lineTo(x + r, y + h)
  ctx.quadraticCurveTo(x, y + h, x, y + h - r)
  ctx.lineTo(x, y + r)
  ctx.quadraticCurveTo(x, y, x + r, y)
  ctx.closePath()
}

/**
 * 绘制文本
 */
function drawText(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number, scale: number) {
  let text = ''
  if (typeof element.content === 'string') {
    text = extractTextFromHTML(element.content)
  } else if (typeof element.text === 'string') {
    text = element.text
  }

  if (!text || text.trim() === '') return

  // 计算字体大小（保持原始大小，按比例缩放）
  let fontSize = element.fontSize || element.size || 18
  // 限制字体大小范围
  fontSize = Math.max(6, Math.min(fontSize, 72))
  // 应用缩放
  const scaledFontSize = fontSize * scale

  const fontFamily = element.fontFamily || element.font || 'Microsoft YaHei, PingFang SC, Arial, sans-serif'
  const fontColor = parseColor(element.fontColor || element.color) || '#333333'

  let fontWeight = 'normal'
  const bold = element.bold || element.fontWeight
  if (bold === true || bold === 'bold' || bold === '700' || (typeof bold === 'number' && bold >= 700)) {
    fontWeight = 'bold'
  }

  const italic = element.italic || element.fontStyle === 'italic'
  const fontStyle = italic ? 'italic' : 'normal'

  ctx.font = `${fontStyle} ${fontWeight} ${scaledFontSize}px ${fontFamily}`
  ctx.fillStyle = fontColor

  const align = element.align || element.textAlign || 'left'
  ctx.textAlign = align as CanvasTextAlign
  ctx.textBaseline = 'top'

  const padding = 4 * scale
  let textX = x
  if (align === 'center') {
    textX = x + w / 2
  } else if (align === 'right') {
    textX = x + w - padding
  } else {
    textX = x + padding
  }

  const maxWidth = w - padding * 2
  const lineHeight = (element.lineHeight || 1.4) * scaledFontSize
  const lines = wrapText(ctx, text, maxWidth, lineHeight, h)

  const startY = y + padding
  lines.forEach((line, index) => {
    const lineY = startY + index * lineHeight
    if (lineY + lineHeight < y + h) {
      ctx.fillText(line, textX, lineY)
    }
  })
}

/**
 * 绘制图片
 */
async function drawImage(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number) {
  const src = element.src || element.url || element.image
  if (!src) {
    drawImagePlaceholder(ctx, x, y, w, h)
    return
  }

  try {
    const img = await loadImage(src)

    ctx.save()
    ctx.beginPath()
    ctx.rect(x, y, w, h)
    ctx.clip()

    const imgRatio = img.width / img.height
    const boxRatio = w / h

    let drawWidth = w
    let drawHeight = h
    let drawX = x
    let drawY = y

    const fit = element.fit || 'contain'

    if (fit === 'cover') {
      if (imgRatio > boxRatio) {
        drawHeight = h
        drawWidth = h * imgRatio
        drawX = x + (w - drawWidth) / 2
      } else {
        drawWidth = w
        drawHeight = w / imgRatio
        drawY = y + (h - drawHeight) / 2
      }
    } else {
      if (imgRatio > boxRatio) {
        drawWidth = w
        drawHeight = w / imgRatio
        drawY = y + (h - drawHeight) / 2
      } else {
        drawHeight = h
        drawWidth = h * imgRatio
        drawX = x + (w - drawWidth) / 2
      }
    }

    ctx.drawImage(img, drawX, drawY, drawWidth, drawHeight)
    ctx.restore()
  } catch (e) {
    drawImagePlaceholder(ctx, x, y, w, h)
  }
}

/**
 * 绘制图片占位符
 */
function drawImagePlaceholder(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number) {
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(x, y, w, h)

  ctx.strokeStyle = '#d0d0d0'
  ctx.lineWidth = 1
  ctx.strokeRect(x, y, w, h)

  ctx.fillStyle = '#999'
  const iconSize = Math.min(w, h) * 0.25
  ctx.font = `${iconSize}px sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('IMG', x + w / 2, y + h / 2)
}

/**
 * 绘制表格
 */
function drawTable(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number, scale: number) {
  const data = element.data || element.rows || []
  if (!data.length) return

  const rows = data.length
  const cols = data[0]?.length || data[0]?.cells?.length || 0
  if (!cols) return

  const cellWidth = w / cols
  const cellHeight = h / rows

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(x, y, w, h)

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const cellX = x + col * cellWidth
      const cellY = y + row * cellHeight

      let cellData = data[row]?.[col]
      if (typeof cellData === 'object' && cellData !== null) {
        cellData = cellData.text || cellData.content || cellData.value || ''
      }

      const cellBg = parseColor(data[row]?.[col]?.background || data[row]?.[col]?.bgColor)
      if (cellBg) {
        ctx.fillStyle = cellBg
        ctx.fillRect(cellX, cellY, cellWidth, cellHeight)
      }

      ctx.strokeStyle = '#ddd'
      ctx.lineWidth = 0.5
      ctx.strokeRect(cellX, cellY, cellWidth, cellHeight)

      if (cellData) {
        const text = String(cellData)
        ctx.fillStyle = '#333'
        ctx.font = `${Math.max(6, 10 * scale)}px sans-serif`
        ctx.textAlign = 'left'
        ctx.textBaseline = 'middle'

        const maxTextWidth = cellWidth - 4
        let displayText = text
        while (ctx.measureText(displayText).width > maxTextWidth && displayText.length > 0) {
          displayText = displayText.slice(0, -1)
        }
        if (displayText.length < text.length) {
          displayText += '...'
        }

        ctx.fillText(displayText, cellX + 2, cellY + cellHeight / 2)
      }
    }
  }
}

/**
 * 绘制图表占位符
 */
function drawChartPlaceholder(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number) {
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(x, y, w, h)

  ctx.strokeStyle = '#dee2e6'
  ctx.lineWidth = 1
  ctx.strokeRect(x, y, w, h)

  ctx.fillStyle = '#6c757d'
  ctx.font = `${Math.min(w, h) * 0.15}px sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('Chart', x + w / 2, y + h / 2)
}

/**
 * 绘制公式占位符
 */
function drawFormula(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number, scale: number) {
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(x, y, w, h)

  ctx.strokeStyle = '#dee2e6'
  ctx.lineWidth = 1
  ctx.strokeRect(x, y, w, h)

  ctx.fillStyle = '#333'
  ctx.font = `${Math.min(w, h) * 0.12}px serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(element.latex || element.content || '∑', x + w / 2, y + h / 2)
}

/**
 * 绘制媒体占位符
 */
function drawMediaPlaceholder(ctx: CanvasRenderingContext2D, element: any, x: number, y: number, w: number, h: number) {
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(x, y, w, h)

  ctx.strokeStyle = '#ccc'
  ctx.lineWidth = 1
  ctx.strokeRect(x, y, w, h)

  ctx.fillStyle = '#999'
  const iconSize = Math.min(w, h) * 0.25
  ctx.font = `${iconSize}px sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(element.type === 'audio' ? 'Audio' : 'Video', x + w / 2, y + h / 2)
}

/**
 * 从HTML中提取纯文本
 */
function extractTextFromHTML(html: string): string {
  if (!html) return ''
  const withLineBreaks = html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<\/li>/gi, '\n')
    .replace(/<li[^>]*>/gi, '• ')
  const div = document.createElement('div')
  div.innerHTML = withLineBreaks
  return (div.textContent || div.innerText || '').trim()
}

/**
 * 文本换行
 */
function wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number, lineHeight: number, maxHeight: number): string[] {
  const lines: string[] = []
  const maxLines = Math.max(1, Math.floor(maxHeight / lineHeight))

  const paragraphs = text.split(/\n|\r\n/)

  for (const paragraph of paragraphs) {
    if (lines.length >= maxLines) break

    if (!paragraph.trim()) {
      lines.push('')
      continue
    }

    let currentLine = ''

    for (const char of paragraph) {
      const testLine = currentLine + char
      const metrics = ctx.measureText(testLine)

      if (metrics.width > maxWidth && currentLine) {
        lines.push(currentLine)
        currentLine = char

        if (lines.length >= maxLines) {
          if (currentLine) {
            lines[lines.length - 1] = lines[lines.length - 1].slice(0, -1) + '...'
          }
          break
        }
      } else {
        currentLine = testLine
      }
    }

    if (currentLine && lines.length < maxLines) {
      lines.push(currentLine)
    }
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
