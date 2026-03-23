/**
 * PPTX转PPTist JSON工具
 */
import { parse } from 'pptxtojson'

export interface PPTistSlide {
  id: string
  elements: PPTistElement[]
  background?: {
    type: string
    color?: string
    image?: string
  }
  type?: 'cover' | 'contents' | 'transition' | 'content' | 'end'
}

export interface PPTistElement {
  type: 'text' | 'shape' | 'image' | 'table' | 'chart' | 'group'
  id: string
  left: number
  top: number
  width: number
  height: number
  content?: string
  fill?: string | { type: string; value: string }
  borderColor?: string
  borderWidth?: number
  rotate?: number
  [key: string]: any
}

export interface PPTistJSON {
  slides: PPTistSlide[]
  themeColors: string[]
  size: {
    width: number
    height: number
  }
}

/**
 * 将PPTX文件解析为PPTist JSON格式
 */
export async function convertPPTXToJSON(arrayBuffer: ArrayBuffer): Promise<PPTistJSON> {
  try {
    const result = await parse(arrayBuffer)
    return result as PPTistJSON
  } catch (error) {
    console.error('PPTX解析失败:', error)
    throw new Error('PPTX文件解析失败，请确保文件格式正确')
  }
}

/**
 * 从File对象读取为ArrayBuffer
 */
export function readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as ArrayBuffer)
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

/**
 * 检测幻灯片类型
 */
export function detectSlideType(slide: PPTistSlide, index: number, totalSlides: number): PPTistSlide['type'] {
  // 第一页通常是封面
  if (index === 0) {
    return 'cover'
  }
  
  // 最后一页通常是结尾
  if (index === totalSlides - 1) {
    return 'end'
  }
  
  // 检查是否是目录页
  const hasMultipleItems = slide.elements.filter(el => 
    el.type === 'text' && el.content && el.content.length > 0
  ).length > 4
  
  if (hasMultipleItems && index < 4) {
    return 'contents'
  }
  
  // 检查是否是过渡页（只有标题，没有太多内容）
  const textElements = slide.elements.filter(el => el.type === 'text')
  if (textElements.length <= 2 && slide.elements.length <= 5) {
    return 'transition'
  }
  
  // 默认为内容页
  return 'content'
}

/**
 * 为幻灯片添加类型标记
 */
export function enrichSlidesWithType(json: PPTistJSON): PPTistJSON {
  const enrichedSlides = json.slides.map((slide, index) => ({
    ...slide,
    type: detectSlideType(slide, index, json.slides.length)
  }))
  
  return {
    ...json,
    slides: enrichedSlides
  }
}
