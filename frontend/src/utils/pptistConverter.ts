/**
 * AI大纲转PPTist格式转换器
 */

// AI生成的大纲结构
export interface AIGeneratedOutline {
  title: string
  subtitle?: string
  slides: {
    slide_type: string
    title: string
    bullets?: string[]
    notes?: string
    enrichedItems?: { title: string; text: string }[]
  }[]
}

// PPTist AIPPT格式
export interface AIPPTSlide {
  type: 'cover' | 'contents' | 'transition' | 'content' | 'end'
  data: {
    title?: string
    text?: string
    items?: string[] | { title: string; text: string }[]
  }
  offset?: number
}

/**
 * 将大纲转换为PPTist的AIPPT格式
 * 这个格式会被PPTist的useAIPPT hook处理，根据模板生成最终PPT
 */
export function convertOutlineToAIPPT(outline: AIGeneratedOutline): AIPPTSlide[] {
  const slides: AIPPTSlide[] = []
  
  // 封面页 - 填充title和text
  slides.push({
    type: 'cover',
    data: {
      title: outline.title,
      text: outline.subtitle || ''
    }
  })
  
  // 收集所有内容页的标题，用于目录
  const contentTitles: string[] = []
  const contentSlides = outline.slides.filter(s => s.slide_type === 'content')
  contentSlides.forEach(s => {
    if (s.title) contentTitles.push(s.title)
  })
  
  // 目录页（如果有多个内容页）
  if (contentTitles.length > 2) {
    slides.push({
      type: 'contents',
      data: {
        items: contentTitles
      }
    })
  }
  
  // 内容页
  let sectionIndex = 0
  for (const slideData of outline.slides) {
    switch (slideData.slide_type) {
      case 'title':
        // 封面类型的页面
        slides.push({
          type: 'cover',
          data: {
            title: slideData.title,
            text: slideData.bullets?.[0] || ''
          }
        })
        break
      case 'section':
        // 章节过渡页
        sectionIndex++
        slides.push({
          type: 'transition',
          data: {
            title: slideData.title,
            text: slideData.bullets?.[0] || `第 ${sectionIndex} 章`
          }
        })
        break
      case 'ending':
        // 结尾页
        slides.push({
          type: 'end',
          data: {}
        })
        break
      case 'content':
      default:
        // 内容页 - 需要填充title和items
        // 如果有enrichedItems，使用它；否则从bullets生成
        let items: { title: string; text: string }[]
        
        if (slideData.enrichedItems && slideData.enrichedItems.length > 0) {
          // 使用AI丰富后的items
          items = slideData.enrichedItems
        } else {
          // 从bullets生成items
          items = (slideData.bullets || []).map((bullet, index) => ({
            title: `要点 ${index + 1}`,
            text: bullet
          }))
        }
        
        // 如果只有一个要点，直接作为text
        if (items.length === 1) {
          slides.push({
            type: 'content',
            data: {
              title: slideData.title,
              items: [{
                title: '',
                text: items[0].text
              }]
            }
          })
        } else {
          slides.push({
            type: 'content',
            data: {
              title: slideData.title,
              items: items
            }
          })
        }
        break
    }
  }
  
  // 结尾页
  if (outline.slides.length > 0 && outline.slides[outline.slides.length - 1].slide_type !== 'ending') {
    slides.push({
      type: 'end',
      data: {}
    })
  }
  
  return slides
}
