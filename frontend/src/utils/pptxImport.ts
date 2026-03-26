/**
 * PPTX 转换工具 - 使用简化的转换逻辑
 * 将 pptxtojson 解析结果转换为 PPTist 可用的格式
 */

const RATIO = 96 / 72

function convertTextContent(html: string): string {
  return html.replace(/font-size:\s*([\d.]+)pt/g, (match, p1) => {
    return `font-size: ${Math.floor(parseFloat(p1) * RATIO)}px`
  }).replace(/&nbsp;/g, ' ')
}

function processSlideFill(fill: any): any {
  if (!fill) return { type: 'solid', color: '#ffffff' }
  
  // 处理 image 类型
  if (fill.type === 'image' && fill.value?.picBase64) {
    return {
      type: 'image',
      image: {
        src: fill.value.picBase64,
        size: 'cover',
      },
    }
  }
  
  // 处理 gradient 类型
  if (fill.type === 'gradient' && fill.value?.colors?.length) {
    return {
      type: 'gradient',
      gradient: {
        type: fill.value.path === 'line' ? 'linear' : 'radial',
        colors: fill.value.colors.map((c: any) => ({
          ...c,
          pos: parseInt(c.pos),
        })),
        rotate: fill.value.rot || 0,
      },
    }
  }
  
  // 处理 color 类型 - 关键：确保返回正确的颜色值
  if (fill.type === 'color') {
    const colorValue = fill.value
    if (colorValue && typeof colorValue === 'string' && colorValue.trim()) {
      return {
        type: 'solid',
        color: colorValue,
      }
    }
  }
  
  // 如果 value 是字符串颜色值
  if (fill.value && typeof fill.value === 'string' && fill.value.trim()) {
    return {
      type: 'solid',
      color: fill.value,
    }
  }
  
  return { type: 'solid', color: '#ffffff' }
}

function processElementFill(fill: any): string {
  if (!fill) return ''
  
  if (fill.type === 'color') {
    return fill.value || ''
  }
  
  if (fill.type === 'gradient') {
    return ''
  }
  
  return ''
}

export async function importPPTX(arrayBuffer: ArrayBuffer): Promise<{
  slides: any[]
  theme: any
  width: number
  height: number
}> {
  const { parse } = await import('pptxtojson')
  const json = await parse(arrayBuffer)
  
  const width = json.size?.width || 960
  const height = json.size?.height || 540
  const themeColors = json.themeColors || ['#1677ff']
  
  const theme = {
    themeColors,
    fontColor: '#333333',
    fontName: 'Microsoft YaHei',
    backgroundColor: '#ffffff',
    shadow: { h: 3, v: 3, blur: 2, color: '#808080' },
    outline: { width: 2, color: '#525252', style: 'solid' },
  }
  
  const slides = (json.slides || []).map((slide: any, slideIndex: number) => {
    const elements = (slide.elements || []).sort((a: any, b: any) => (a.order || 0) - (b.order || 0))
    
    const convertedElements = elements.map((el: any) => {
      const originWidth = el.width || 1
      const originHeight = el.height || 1
      
      const convertedEl: any = {
        id: `el_${slideIndex}_${Math.random().toString(36).substr(2, 9)}`,
        left: (el.left || 0) * RATIO,
        top: (el.top || 0) * RATIO,
        width: (el.width || 100) * RATIO,
        height: (el.height || 100) * RATIO,
        rotate: el.rotate || 0,
      }
      
      if (el.type === 'text') {
        convertedEl.type = 'text'
        convertedEl.content = convertTextContent(el.content || '')
        convertedEl.defaultFontName = theme.fontName
        convertedEl.defaultColor = el.fontColor || theme.fontColor
        convertedEl.vertical = el.isVertical || false
        convertedEl.lineHeight = 1
        
        const fill = processElementFill(el.fill)
        if (fill) {
          convertedEl.fill = fill
        }
        
        if (el.borderColor) {
          convertedEl.outline = {
            color: el.borderColor,
            width: (el.borderWidth || 1) * RATIO,
            style: el.borderType || 'solid',
          }
        }
      }
      else if (el.type === 'shape') {
        convertedEl.type = 'shape'
        
        const fill = processElementFill(el.fill)
        convertedEl.fill = fill || '#cccccc'
        convertedEl.fixedRatio = false
        
        if (el.borderColor) {
          convertedEl.outline = {
            color: el.borderColor,
            width: (el.borderWidth || 1) * RATIO,
            style: el.borderType || 'solid',
          }
        }
        
        // 处理路径
        if (el.path && el.path.indexOf('NaN') === -1) {
          convertedEl.path = el.path
          convertedEl.viewBox = [originWidth, originHeight]
        } else {
          convertedEl.viewBox = [200, 200]
          convertedEl.path = 'M 0 0 L 200 0 L 200 200 L 0 200 Z'
        }
        
        // 处理形状内的文本
        if (el.content) {
          convertedEl.text = {
            content: convertTextContent(el.content),
            defaultFontName: theme.fontName,
            defaultColor: theme.fontColor,
            align: 'middle',
          }
        }
      }
      else if (el.type === 'image') {
        convertedEl.type = 'image'
        convertedEl.src = el.src || ''
        convertedEl.fixedRatio = true
      }
      
      return convertedEl
    })
    
    return {
      id: `slide_${slideIndex}_${Math.random().toString(36).substr(2, 9)}`,
      elements: convertedElements,
      background: processSlideFill(slide.fill),
    }
  })
  
  return { slides, theme, width, height }
}

export function createPPTTemplate(data: {
  slides: any[]
  theme: any
  width: number
  height: number
}) {
  return {
    title: '未命名演示文稿',
    width: 1000,
    height: 562.5,
    theme: {
      ...data.theme,
      ...data.theme,
    },
    slides: data.slides,
  }
}
