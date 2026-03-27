/**
 * PPTX转换工具 - 将pptxtojson结果转换为PPTist slides格式
 * 核心转换逻辑参考自PPTist的useImport.ts
 */
import { nanoid } from 'nanoid'

const shapeVAlignMap: Record<string, string> = {
  'mid': 'middle',
  'down': 'bottom',
  'up': 'top',
}

const fontFamilyAliasMap: Record<string, string> = {
  '优设标题黑': 'YousheTitleBlack',
  '阿里巴巴普惠体': 'AlibabaPuHuiTi',
  '阿里巴巴普惠体 2.0 65 Medium': 'AlibabaPuHuiTi',
  '阿里巴巴普惠体 2.0': 'AlibabaPuHuiTi',
  'HarmonyOS Sans SC Light': 'MiSans',
  'HarmonyOS Sans SC': 'MiSans',
}

const normalizeFontFamily = (fontFamily: string) => {
  const cleaned = fontFamily.trim().replace(/^['"]|['"]$/g, '')
  return fontFamilyAliasMap[cleaned] || cleaned
}

const replaceFontFamilies = (html: string) => {
  return html.replace(/font-family:\s*([^;"]+|'[^']+'|"[^"]+")/gi, (_match, family) => {
    return `font-family: ${normalizeFontFamily(family)}`
  })
}

const getPreferredFontName = (html: string, fallback: string) => {
  const match = html.match(/font-family:\s*([^;"]+|'[^']+'|"[^"]+")/i)
  if (!match || !match[1]) return fallback
  return normalizeFontFamily(match[1])
}

const convertTextContent = (html: string, ratio: number): string => {
  return replaceFontFamilies(html).replace(/font-size:\s*([\d.]+)pt/g, (_match, p1) => {
    return `font-size: ${Math.floor(parseFloat(p1) * ratio)}px`
  }).replace(/&nbsp;/g, ' ')
}

const getParagraphMetrics = (html: string, ratio: number) => {
  const tagRegex = /<(div|p|li)(?![a-z0-9])[^>]*>/gi
  const lineHeights: number[] = []
  const margins: number[] = []
  let paragraphCount = 0

  let match
  let paragraphIndex = 0
  while ((match = tagRegex.exec(html)) !== null) {
    const fullTag = match[0]
    paragraphCount++

    const styleRegex = /\bstyle\s*=\s*(['"])(.*?)\1/i
    const styleMatch = fullTag.match(styleRegex)

    let styleContent = ''
    if (styleMatch && styleMatch[2]) {
      styleContent = styleMatch[2]
    }

    const getProp = (propName: string) => {
      if (!styleContent) return null
      const propRegex = new RegExp(`${propName}\\s*:\\s*([^;]+)`, 'i')
      const propMatch = styleContent.match(propRegex)
      return propMatch ? propMatch[1].trim() : null
    }

    const marginTop = getProp('margin-top')
    const marginBottom = getProp('margin-bottom')
    const lineHeight = getProp('line-height')

    const tagStartIndex = match.index
    const tagName = match[1]
    let tagEndIndex = html.indexOf('</' + tagName + '>', tagStartIndex)
    if (tagEndIndex === -1) tagEndIndex = tagStartIndex + fullTag.length

    const paragraphHtml = html.substring(tagStartIndex, tagEndIndex)
    
    const fontSizeRegex = /font-size\s*:\s*(\d+(?:\.\d+)?)\s*pt/gi
    const fontSizes = [18]
    let fontMatch
    while ((fontMatch = fontSizeRegex.exec(paragraphHtml)) !== null) {
      fontSizes.push(parseFloat(fontMatch[1]))
    }
    const maxFontSize = Math.max(...fontSizes)

    let lineHeightValue = 1
    if (lineHeight) {
      if (lineHeight.indexOf('pt') !== -1) {
        lineHeightValue = parseFloat(lineHeight.replace('pt', '')) / maxFontSize
      } else {
        lineHeightValue = parseFloat(lineHeight)
      }
    }
    lineHeights.push(lineHeightValue)

    const isFirstParagraph = paragraphIndex === 0

    if (marginTop && !isFirstParagraph) {
      let marginTopValue = 0
      if (marginTop.indexOf('pt') !== -1) {
        marginTopValue = parseFloat(marginTop.replace('pt', ''))
      } else if (marginTop.indexOf('em') !== -1) {
        marginTopValue = parseFloat(marginTop.replace('em', '')) * maxFontSize
      }
      if (marginTopValue > 0) margins.push(marginTopValue)
    }

    paragraphIndex++
  }

  let lineHeight = 1
  if (lineHeights.length) {
    lineHeight = +(lineHeights.reduce((sum, height) => sum + height, 0) / paragraphCount).toFixed(2)
  }

  let margin = 0
  if (margins.length && paragraphCount > 1) {
    margin = margins.reduce((sum, m) => sum + m, 0) / (paragraphCount - 1)
  }

  return {
    lineHeight,
    margin: margin ? +(margin * ratio).toFixed(1) : null,
  }
}

const getMaxFontSize = (html: string, defaultFontSize = 18) => {
  const fontSizeRegex = /font-size\s*:\s*(\d+(?:\.\d+)?)\s*pt/gi
  const fontSizes = [defaultFontSize]

  let match
  while ((match = fontSizeRegex.exec(html)) !== null) {
    const size = parseFloat(match[1])
    if (size > 0) fontSizes.push(size)
  }

  return Math.max(...fontSizes)
}

const getSvgPathRange = (path: string) => {
  const coords = path.match(/[+-]?\d+(\.\d+)?/g) || []
  let maxX = 0, maxY = 0
  for (let i = 0; i < coords.length; i += 2) {
    const x = parseFloat(coords[i]) || 0
    const y = parseFloat(coords[i + 1]) || 0
    if (x > maxX) maxX = x
    if (y > maxY) maxY = y
  }
  return { maxX: maxX || 200, maxY: maxY || 200 }
}

const sanitizeSvgPath = (path: string) => {
  return path
    .replace(/NaN/g, '0')
    .replace(/z{2,}/gi, ' z')
    .trim()
}

const hasMeaningfulText = (content?: string) => {
  if (!content) return false
  const plainText = content
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .trim()
  return plainText.length > 0
}

const getClipShape = (el: any) => {
  const clipShapeTypes = ['rect', 'roundRect', 'ellipse', 'triangle', 'rhombus', 'pentagon', 'hexagon']
  const geom = (el.geom || el.shapType || 'rect').replace('custom:', '')
  return clipShapeTypes.includes(geom) ? geom : 'rect'
}

const useOriginViewBoxShapeTypes = new Set([
  'custom',
  'rect',
  'roundRect',
  'ellipse',
  'triangle',
  'rhombus',
  'pentagon',
  'hexagon',
])

const canConvertPatternShapeToImage = (el: any) => {
  if (el.type !== 'shape' || el.fill?.type !== 'image' || !el.fill.value?.picBase64) return false
  if (hasMeaningfulText(el.content)) return false
  return ['rect', 'roundRect', 'ellipse', 'triangle', 'rhombus', 'pentagon', 'hexagon'].includes(getClipShape(el))
}

const flipGroupElements = (elements: any[], axis: 'x' | 'y') => {
  const minX = Math.min(...elements.map(el => el.left))
  const maxX = Math.max(...elements.map(el => el.left + el.width))
  const minY = Math.min(...elements.map(el => el.top))
  const maxY = Math.max(...elements.map(el => el.top + el.height))

  const centerX = (minX + maxX) / 2
  const centerY = (minY + maxY) / 2

  return elements.map(element => {
    const next = { ...element }
    if (axis === 'y') next.left = 2 * centerX - element.left - element.width
    if (axis === 'x') next.top = 2 * centerY - element.top - element.height
    return next
  })
}

const getGroupBounds = (elements: any[]) => {
  const xs = elements.map(el => el.left || 0)
  const ys = elements.map(el => el.top || 0)
  const rs = elements.map(el => (el.left || 0) + (el.width || 0))
  const bs = elements.map(el => (el.top || 0) + (el.height || 0))

  const minX = Math.min(...xs)
  const minY = Math.min(...ys)
  const maxX = Math.max(...rs)
  const maxY = Math.max(...bs)

  return {
    minX,
    minY,
    width: maxX - minX,
    height: maxY - minY,
  }
}

const getElementBounds = (el: any) => {
  if (el?.type === 'group' && el.elements?.length) {
    const childBounds = el.elements.map((child: any) => {
      const bounds = getElementBounds(child)
      const left = (child.left || 0) + bounds.minX
      const top = (child.top || 0) + bounds.minY
      return {
        minX: left,
        minY: top,
        maxX: left + bounds.width,
        maxY: top + bounds.height,
      }
    })

    const minX = Math.min(...childBounds.map(item => item.minX))
    const minY = Math.min(...childBounds.map(item => item.minY))
    const maxX = Math.max(...childBounds.map(item => item.maxX))
    const maxY = Math.max(...childBounds.map(item => item.maxY))

    return {
      minX,
      minY,
      width: maxX - minX,
      height: maxY - minY,
    }
  }

  return {
    minX: 0,
    minY: 0,
    width: el?.width || 0,
    height: el?.height || 0,
  }
}

const calculateRotatedPosition = (
  ax: number,
  ay: number,
  aw: number,
  ah: number,
  bx: number,
  by: number,
  bw: number,
  bh: number,
  ak: number,
  bk: number
) => {
  const aRadians = ak * (Math.PI / 180)
  const aCos = Math.cos(aRadians)
  const aSin = Math.sin(aRadians)

  const aCenterX = ax + aw / 2
  const aCenterY = ay + ah / 2

  const corners = [
    { ox: bx, oy: by },
    { ox: bx + bw, oy: by },
    { ox: bx + bw, oy: by + bh },
    { ox: bx, oy: by + bh },
  ]

  let minX = Infinity
  let minY = Infinity

  for (const corner of corners) {
    const relativeX = corner.ox - aw / 2
    const relativeY = corner.oy - ah / 2

    const rotatedX = relativeX * aCos + relativeY * aSin
    const rotatedY = -relativeX * aSin + relativeY * aCos

    const graphicX = aCenterX + rotatedX
    const graphicY = aCenterY + rotatedY

    minX = Math.min(minX, graphicX)
    minY = Math.min(minY, graphicY)
  }

  return {
    x: minX,
    y: minY,
    globalRotation: (bk + ak) % 360,
  }
}

const calculateRotatedPositionByBounds = (
  ax: number,
  ay: number,
  minLocalX: number,
  minLocalY: number,
  aw: number,
  ah: number,
  bx: number,
  by: number,
  bw: number,
  bh: number,
  ak: number,
  bk: number
) => {
  const aRadians = ak * (Math.PI / 180)
  const aCos = Math.cos(aRadians)
  const aSin = Math.sin(aRadians)

  const localCenterX = minLocalX + aw / 2
  const localCenterY = minLocalY + ah / 2
  const globalCenterX = ax + localCenterX
  const globalCenterY = ay + localCenterY

  const corners = [
    { ox: bx, oy: by },
    { ox: bx + bw, oy: by },
    { ox: bx + bw, oy: by + bh },
    { ox: bx, oy: by + bh },
  ]

  let minX = Infinity
  let minY = Infinity

  for (const corner of corners) {
    const relativeX = corner.ox - localCenterX
    const relativeY = corner.oy - localCenterY

    const rotatedX = relativeX * aCos + relativeY * aSin
    const rotatedY = -relativeX * aSin + relativeY * aCos

    const graphicX = globalCenterX + rotatedX
    const graphicY = globalCenterY + rotatedY

    minX = Math.min(minX, graphicX)
    minY = Math.min(minY, graphicY)
  }

  return {
    x: minX,
    y: minY,
    globalRotation: (bk + ak) % 360,
  }
}

export interface PPtojsonSlide {
  fill?: { type: string; value?: any }
  elements?: PPtojsonElement[]
  background?: any
  note?: string
  layoutElements?: PPtojsonElement[]
}

export interface PPtojsonElement {
  type?: string
  left?: number
  top?: number
  width?: number
  height?: number
  order?: number
  content?: string
  fill?: any
  borderColor?: string
  borderWidth?: number
  borderType?: string
  rotate?: number
  isFlipV?: boolean
  isFlipH?: boolean
  isVertical?: boolean
  fontFamily?: string
  fontColor?: string
  fontSize?: number
  autoFit?: any
  vAlign?: string
  link?: string
  shapType?: string
  path?: string
  src?: string
  geom?: string
  rect?: any
  shadow?: any
  data?: any
  colWidths?: number[]
  rowHeights?: number[]
  borders?: any
  colors?: string[]
  chartType?: string
  barDir?: string
  grouping?: string
  keypoints?: any
}

export interface PPTistSlideElement {
  id: string
  type: string
  left: number
  top: number
  width: number
  height: number
  rotate?: number
  [key: string]: any
}

export interface ThemeColors {
  themeColors: string[]
  fontColor: string
  fontName: string
  backgroundColor: string
}

interface SlideBackground {
  type: string
  color?: string
  image?: any
  gradient?: any
  pattern?: any
}

interface ConvertedSlide {
  id: string
  elements: PPTistSlideElement[]
  background: SlideBackground
  remark?: string
  type?: string
}

interface TextElementMeta {
  element: PPTistSlideElement
  text: string
  fontSize: number
  centerX: number
  centerY: number
  isNumeric: boolean
  isShort: boolean
}

const stripHtml = (html: string): string => {
  return html
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<\/?(div|p|li|span|strong|em|u|s)[^>]*>/gi, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/\s+/g, ' ')
    .trim()
}

const getElementTextContent = (el: PPTistSlideElement): string => {
  if (el.type === 'text') return stripHtml(el.content || '')
  if (el.type === 'shape' && el.text?.content) return stripHtml(el.text.content)
  return ''
}

const getElementTextHtml = (el: PPTistSlideElement): string => {
  if (el.type === 'text') return el.content || ''
  if (el.type === 'shape' && el.text?.content) return el.text.content
  return ''
}

const getElementFontSize = (el: PPTistSlideElement): number => {
  const html = getElementTextHtml(el)
  const match = html.match(/font-size:\s*([\d.]+)px/i)
  return match ? parseFloat(match[1]) : 16
}

const setTextType = (el: PPTistSlideElement, type: string) => {
  if (el.type === 'text') el.textType = type
  if (el.type === 'shape' && el.text) el.text.type = type
}

const setGroupId = (el: PPTistSlideElement, groupId: string) => {
  el.groupId = groupId
}

const buildTextMetas = (slide: ConvertedSlide): TextElementMeta[] => {
  return slide.elements
    .filter(el => el.type === 'text' || (el.type === 'shape' && el.text?.content))
    .map(el => {
      const text = getElementTextContent(el)
      return {
        element: el,
        text,
        fontSize: getElementFontSize(el),
        centerX: el.left + el.width / 2,
        centerY: el.top + el.height / 2,
        isNumeric: /^\d+$/.test(text),
        isShort: text.length > 0 && text.length <= 26,
      }
    })
    .filter(item => item.text)
}

const findNearestMeta = (target: TextElementMeta, candidates: TextElementMeta[]) => {
  if (!candidates.length) return null

  return candidates.reduce((closest, current) => {
    const currentDistance = Math.hypot(target.centerX - current.centerX, target.centerY - current.centerY)
    const closestDistance = Math.hypot(target.centerX - closest.centerX, target.centerY - closest.centerY)
    return currentDistance < closestDistance ? current : closest
  })
}

const classifyImageType = (el: PPTistSlideElement) => {
  const areaRatio = (el.width * el.height) / (1000 * 562.5)
  if (areaRatio >= 0.55 || (el.width >= 900 && el.height >= 420)) return 'background'
  if (el.width >= 300 || el.height >= 250) return 'pageFigure'
  return 'itemFigure'
}

const tagImages = (slide: ConvertedSlide, contentGroups: TextElementMeta[][]) => {
  const images = slide.elements.filter(el => el.type === 'image')
  for (const image of images) {
    image.imageType = classifyImageType(image)

    if (image.imageType !== 'itemFigure' || !contentGroups.length) continue

    const targetGroup = contentGroups.reduce((closest, current) => {
      const currentCenterX = current.reduce((sum, item) => sum + item.centerX, 0) / current.length
      const currentCenterY = current.reduce((sum, item) => sum + item.centerY, 0) / current.length
      const currentDistance = Math.hypot(image.left + image.width / 2 - currentCenterX, image.top + image.height / 2 - currentCenterY)

      if (!closest) return { current, distance: currentDistance }
      return currentDistance < closest.distance ? { current, distance: currentDistance } : closest
    }, null as null | { current: TextElementMeta[]; distance: number })

    const groupId = targetGroup?.current.find(item => item.element.groupId)?.element.groupId
    if (groupId) image.groupId = groupId
  }
}

const annotateContentTexts = (slide: ConvertedSlide, metas: TextElementMeta[]) => {
  if (!metas.length) return [] as TextElementMeta[][]

  const title = metas
    .filter(item => item.centerY <= 220)
    .sort((a, b) => b.fontSize - a.fontSize || a.centerY - b.centerY)[0] || metas
    .sort((a, b) => b.fontSize - a.fontSize || a.centerY - b.centerY)[0]

  if (title) setTextType(title.element, 'title')

  const remaining = metas
    .filter(item => item.element.id !== title?.element.id)
    .sort((a, b) => a.centerY - b.centerY || a.centerX - b.centerX)

  const numbered = remaining.filter(item => item.isNumeric)
  const textCandidates = remaining.filter(item => !item.isNumeric)

  for (const meta of numbered) {
    setTextType(meta.element, 'itemNumber')
  }

  if (textCandidates.length === 1) {
    setTextType(textCandidates[0].element, 'content')
    return [[textCandidates[0]]]
  }

  const groups: TextElementMeta[][] = []
  let index = 0
  while (index < textCandidates.length) {
    const current = textCandidates[index]
    const next = textCandidates[index + 1]

    const looksLikePair = !!next &&
      current.isShort &&
      next.centerY >= current.centerY &&
      Math.abs(next.centerX - current.centerX) <= 180

    if (looksLikePair) {
      const groupId = nanoid(10)
      setTextType(current.element, 'itemTitle')
      setTextType(next.element, 'item')
      setGroupId(current.element, groupId)
      setGroupId(next.element, groupId)
      groups.push([current, next])
      index += 2
      continue
    }

    setTextType(current.element, 'item')
    groups.push([current])
    index += 1
  }

  for (const numberMeta of numbered) {
    const nearest = findNearestMeta(numberMeta, groups.flat())
    const groupId = nearest?.element.groupId || nanoid(10)
    setGroupId(numberMeta.element, groupId)
    if (nearest && !nearest.element.groupId) setGroupId(nearest.element, groupId)
  }

  return groups
}

const annotateContentsTexts = (slide: ConvertedSlide, metas: TextElementMeta[]) => {
  if (!metas.length) return [] as TextElementMeta[][]

  const title = metas
    .sort((a, b) => b.fontSize - a.fontSize || a.centerY - b.centerY)[0]

  if (title) setTextType(title.element, 'title')

  const remaining = metas
    .filter(item => item.element.id !== title?.element.id)
    .sort((a, b) => a.centerY - b.centerY || a.centerX - b.centerX)

  const groups: TextElementMeta[][] = []
  for (const meta of remaining) {
    if (meta.isNumeric) {
      setTextType(meta.element, 'itemNumber')
      const nearest = findNearestMeta(meta, remaining.filter(item => !item.isNumeric))
      const groupId = nearest?.element.groupId || nanoid(10)
      setGroupId(meta.element, groupId)
      if (nearest && !nearest.element.groupId) setGroupId(nearest.element, groupId)
      continue
    }

    setTextType(meta.element, 'item')
    if (!meta.element.groupId) setGroupId(meta.element, nanoid(10))
    groups.push([meta])
  }

  return groups
}

const annotateCoverLikeTexts = (slide: ConvertedSlide, metas: TextElementMeta[], slideType: string) => {
  if (!metas.length) return [] as TextElementMeta[][]

  const sorted = [...metas].sort((a, b) => b.fontSize - a.fontSize || a.centerY - b.centerY)
  const title = sorted.find(item => !item.isNumeric)
  if (title) setTextType(title.element, 'title')

  if (slideType === 'transition') {
    const partNumber = sorted.find(item => item.isNumeric)
    if (partNumber) setTextType(partNumber.element, 'partNumber')
  }

  const content = sorted.find(item =>
    item.element.id !== title?.element.id &&
    item.element.textType !== 'partNumber' &&
    item.centerY >= (title?.centerY || 0)
  )

  if (content) setTextType(content.element, 'content')
  return [] as TextElementMeta[][]
}

const annotateTemplateSemantics = (slides: ConvertedSlide[]) => {
  return slides.map((slide, index) => {
    const type = detectSlideType(slide, index, slides.length)
    slide.type = type

    const metas = buildTextMetas(slide)
    let groups: TextElementMeta[][] = []

    if (type === 'content') groups = annotateContentTexts(slide, metas)
    else if (type === 'contents') groups = annotateContentsTexts(slide, metas)
    else groups = annotateCoverLikeTexts(slide, metas, type)

    tagImages(slide, groups)
    return slide
  })
}

/**
 * 将pptxtojson解析结果转换为PPTist slides格式
 */
export function convertPPTXToSlides(
  json: any,
  options: { fixedViewport?: boolean; theme?: ThemeColors } = {}
): { slides: ConvertedSlide[]; theme: ThemeColors } {
  const { fixedViewport = false, theme } = options

  let ratio = 96 / 72
  const width = json.size?.width || 960

  if (fixedViewport) {
    ratio = 1000 / width
  }

  const themeColors = json.themeColors || theme?.themeColors || ['#1677ff']
  const fontColor = theme?.fontColor || '#333333'
  const fontName = theme?.fontName || 'Microsoft YaHei'

  const resultTheme: ThemeColors = {
    themeColors,
    fontColor,
    fontName,
    backgroundColor: '#ffffff',
  }

  const slides: ConvertedSlide[] = []

  for (const item of json.slides || []) {
    const slideFill = item.fill
    let background: SlideBackground = { type: 'solid', color: '#ffffff' }

    if (slideFill?.type === 'image' && slideFill.value?.picBase64) {
      background = {
        type: 'image',
        image: {
          src: slideFill.value.picBase64,
          size: 'cover',
        },
      }
    } else if (slideFill?.type === 'gradient' && slideFill.value?.colors?.length) {
      // @ts-ignore
      background = {
        type: 'gradient',
        gradient: {
          type: slideFill.value.path === 'line' ? 'linear' : 'radial',
          colors: (slideFill.value.colors || []).map((c: any) => ({
            ...c,
            pos: parseInt(c.pos),
          })),
          rotate: slideFill.value.rot || 0,
        },
      }
    } else if (slideFill?.type === 'color' || (slideFill?.value && typeof slideFill.value === 'string')) {
      const bgColor = slideFill?.value
      if (bgColor && typeof bgColor === 'string' && bgColor.trim()) {
        background = {
          type: 'solid',
          color: bgColor,
        }
      }
    }

    const slide: ConvertedSlide = {
      id: nanoid(10),
      elements: [],
      background,
      remark: item.note || '',
    }

    const viewportHeight = json.size?.height || 540
    const isCorruptedFullscreenShape = (el: any) => {
      return el.type === 'shape' &&
        typeof el.path === 'string' &&
        /z{8,}/i.test(el.path) &&
        (el.left || 0) <= 0.01 &&
        (el.top || 0) <= 0.01 &&
        (el.width || 0) >= width * 0.95 &&
        (el.height || 0) >= viewportHeight * 0.95
    }

    const parseElements = (elements: any[]) => {
      const sortedElements = [...elements].sort((a, b) => (a.order || 0) - (b.order || 0))

      for (const el of sortedElements) {
        const originWidth = el.width || 1
        const originHeight = el.height || 1
        const originLeft = el.left || 0
        const originTop = el.top || 0

        if (el.type === 'group') {
          const childBounds = el.elements?.length ? getGroupBounds(el.elements) : {
            minX: 0,
            minY: 0,
            width: originWidth,
            height: originHeight,
          }

          let groupElements = (el.elements || []).map((_el: any) => {
            const bounds = getElementBounds(_el)
            const localLeft = (_el.left || 0) - (el.__groupOffsetX || 0) + bounds.minX
            const localTop = (_el.top || 0) - (el.__groupOffsetY || 0) + bounds.minY
            const localWidth = bounds.width || (_el.width || 0)
            const localHeight = bounds.height || (_el.height || 0)

            let left = localLeft + originLeft
            let top = localTop + originTop
            let rotate = _el.rotate || 0

            if (el.rotate) {
              const position = calculateRotatedPositionByBounds(
                originLeft,
                originTop,
                childBounds.minX,
                childBounds.minY,
                childBounds.width || originWidth,
                childBounds.height || originHeight,
                localLeft,
                localTop,
                localWidth,
                localHeight,
                el.rotate,
                rotate
              )
              left = position.x
              top = position.y
              rotate = position.globalRotation
            }

            const element = {
              ..._el,
              left,
              top,
              width: localWidth,
              height: localHeight,
            }

            if (_el.type === 'group' && (bounds.minX || bounds.minY)) {
              element.__groupOffsetX = bounds.minX
              element.__groupOffsetY = bounds.minY
            }

            if (el.isFlipH && 'isFlipH' in element) element.isFlipH = true
            if (el.isFlipV && 'isFlipV' in element) element.isFlipV = true
            if ('rotate' in element && el.rotate) element.rotate = rotate
            return element
          })

          if (el.isFlipH) groupElements = flipGroupElements(groupElements, 'y')
          if (el.isFlipV) groupElements = flipGroupElements(groupElements, 'x')
          parseElements(groupElements)
          continue
        }

        if (el.type === 'diagram') {
          const diagramElements = (el.elements || []).map((_el: any) => ({
            ..._el,
            left: (_el.left || 0) - (el.__groupOffsetX || 0) + originLeft,
            top: (_el.top || 0) - (el.__groupOffsetY || 0) + originTop,
          }))
          parseElements(diagramElements)
          continue
        }

        if (isCorruptedFullscreenShape(el)) continue

        const convertedEl: any = {
          id: nanoid(10),
          left: originLeft * ratio,
          top: originTop * ratio,
          width: originWidth * ratio,
          height: originHeight * ratio,
          rotate: el.rotate || 0,
        }

        if (el.type === 'text') {
          const preferredFontName = getPreferredFontName(el.content || '', fontName)
          convertedEl.type = 'text'
          convertedEl.defaultFontName = preferredFontName
          convertedEl.defaultColor = fontColor
          convertedEl.content = convertTextContent(el.content || '', ratio)
          convertedEl.lineHeight = 1
          convertedEl.vertical = el.isVertical || false

          if (el.autoFit?.type === 'shape' && el.content) {
            const maxFontSize = getMaxFontSize(el.content)
            const widthPadding = Math.min(Math.max(maxFontSize * ratio * 0.35, 10), 40)
            convertedEl.width += widthPadding
          }

          if (el.fill?.type === 'color') {
            convertedEl.fill = el.fill.value
          }

          if ((el.borderWidth || 0) > 0 && el.borderColor) {
            convertedEl.outline = {
              color: el.borderColor,
              width: (el.borderWidth || 1) * ratio,
              style: el.borderType || 'solid',
            }
          }

          if (el.shadow) {
            convertedEl.shadow = {
              h: el.shadow.h * ratio,
              v: el.shadow.v * ratio,
              blur: el.shadow.blur * ratio,
              color: el.shadow.color,
            }
          }

          const metrics = getParagraphMetrics(el.content || '', ratio)
          if (metrics.lineHeight) convertedEl.lineHeight = metrics.lineHeight
          if (metrics.margin) convertedEl.paragraphSpace = metrics.margin
        }
        else if (el.type === 'shape') {
          if (canConvertPatternShapeToImage(el)) {
            convertedEl.type = 'image'
            convertedEl.src = el.fill.value.picBase64
            convertedEl.fixedRatio = true
            convertedEl.clip = {
              shape: getClipShape(el),
              range: el.rect ? [
                [el.rect.l || 0, el.rect.t || 0],
                [100 - (el.rect.r || 0), 100 - (el.rect.b || 0)],
              ] : [[0, 0], [100, 100]],
            }

            if ((el.borderWidth || 0) > 0 && el.borderColor) {
              convertedEl.outline = {
                color: el.borderColor,
                width: (el.borderWidth || 1) * ratio,
                style: el.borderType || 'solid',
              }
            }

            if (el.isFlipH) convertedEl.flipH = true
            if (el.isFlipV) convertedEl.flipV = true
          }
          else if (el.shapType === 'line' || /Connector/.test(el.shapType)) {
            convertedEl.type = 'line'
            let start: [number, number] = [0, 0]
            let end: [number, number] = [convertedEl.width, convertedEl.height]

            if (el.isFlipV && el.isFlipH) {
              start = [convertedEl.width, convertedEl.height]
              end = [0, 0]
            } else if (el.isFlipV) {
              start = [0, convertedEl.height]
              end = [convertedEl.width, 0]
            } else if (el.isFlipH) {
              start = [convertedEl.width, 0]
              end = [0, convertedEl.height]
            }

            convertedEl.start = start
            convertedEl.end = end
            convertedEl.style = el.borderType || 'solid'
            convertedEl.color = el.borderColor || '#000000'
            convertedEl.width = (el.borderWidth || 1) * ratio
            convertedEl.points = ['', /straightConnector/.test(el.shapType) ? 'arrow' : '']
          } else {
            convertedEl.type = 'shape'

            let fill = ''
            if (el.fill?.type === 'color' && el.fill.value) {
              fill = el.fill.value
            } else if (el.fill?.type === 'gradient' && el.fill.value?.colors?.length) {
              convertedEl.gradient = {
                type: el.fill.value.path === 'line' ? 'linear' : 'radial',
                colors: el.fill.value.colors.map((c: any) => ({
                  ...c,
                  pos: parseInt(c.pos),
                })),
                rotate: el.fill.value.rot || 0,
              }
            } else if (el.fill?.type === 'image' && el.fill.value?.picBase64) {
              convertedEl.pattern = el.fill.value.picBase64
            }

            convertedEl.fill = fill
            convertedEl.fixedRatio = false

            if ((el.borderWidth || 0) > 0 && el.borderColor) {
              convertedEl.outline = {
                color: el.borderColor,
                width: (el.borderWidth || 1) * ratio,
                style: el.borderType || 'solid',
              }
            }

            if (el.shadow) {
              convertedEl.shadow = {
                h: el.shadow.h * ratio,
                v: el.shadow.v * ratio,
                blur: el.shadow.blur * ratio,
                color: el.shadow.color,
              }
            }

            if (el.path) {
              const cleanPath = sanitizeSvgPath(el.path)
              if (cleanPath.indexOf('0') >= 0 || cleanPath.length > 10) {
                convertedEl.path = cleanPath

                if (useOriginViewBoxShapeTypes.has(el.shapType || '')) {
                  convertedEl.viewBox = [originWidth, originHeight]
                } else {
                  const { maxX, maxY } = getSvgPathRange(cleanPath)
                  if (maxX > 0 && maxY > 0) {
                    if ((maxX / maxY) > (originWidth / originHeight)) {
                      convertedEl.viewBox = [maxX, maxX * originHeight / originWidth]
                    } else {
                      convertedEl.viewBox = [maxY * originWidth / originHeight, maxY]
                    }
                  } else {
                    convertedEl.viewBox = [originWidth, originHeight]
                  }
                }
              } else {
                convertedEl.viewBox = [200, 200]
                convertedEl.path = 'M 0 0 L 200 0 L 200 200 L 0 200 Z'
              }
            } else if (el.shapType === 'roundRect' || el.shapType === 'rect') {
              convertedEl.viewBox = [200, 200]
              convertedEl.path = 'M 0 0 L 200 0 L 200 200 L 0 200 Z'
            } else {
              convertedEl.viewBox = [200, 200]
              convertedEl.path = 'M 0 0 L 200 0 L 200 200 L 0 200 Z'
            }

            if (el.content) {
              const preferredFontName = getPreferredFontName(el.content, fontName)
              convertedEl.text = {
                content: convertTextContent(el.content, ratio),
                defaultFontName: preferredFontName,
                defaultColor: fontColor,
                align: shapeVAlignMap[el.vAlign || 'mid'] || 'middle',
              }

              const metrics = getParagraphMetrics(el.content, ratio)
              if (metrics.lineHeight) convertedEl.text.lineHeight = metrics.lineHeight
              if (metrics.margin) convertedEl.text.paragraphSpace = metrics.margin
            }

            if (el.isFlipH) convertedEl.flipH = true
            if (el.isFlipV) convertedEl.flipV = true
          }
        }
        else if (el.type === 'image') {
          convertedEl.type = 'image'
          convertedEl.src = el.src
          convertedEl.fixedRatio = true

          if ((el.borderWidth || 0) > 0 && el.borderColor) {
            convertedEl.outline = {
              color: el.borderColor,
              width: (el.borderWidth || 1) * ratio,
              style: el.borderType || 'solid',
            }
          }

          if (el.rect || el.geom) {
            convertedEl.clip = {
              shape: getClipShape(el),
              range: el.rect ? [
                [el.rect.l || 0, el.rect.t || 0],
                [100 - (el.rect.r || 0), 100 - (el.rect.b || 0)],
              ] : [[0, 0], [100, 100]],
            }
          }

          if (el.isFlipH) convertedEl.flipH = true
          if (el.isFlipV) convertedEl.flipV = true
        }
        else if (el.type === 'table') {
          convertedEl.type = 'table'

          const row = el.data?.length || 1
          const col = el.data?.[0]?.length || 1

          const cells: any[][] = []
          for (let i = 0; i < row; i++) {
            const rowCells: any[] = []
            for (let j = 0; j < col; j++) {
              const cellData = el.data?.[i]?.[j] || {}
              rowCells.push({
                id: nanoid(10),
                colspan: cellData.colSpan || 1,
                rowspan: cellData.rowSpan || 1,
                text: cellData.text || '',
                style: {
                  align: 'left',
                  color: cellData.fontColor || fontColor,
                  fontname: fontName,
                  bold: cellData.fontBold,
                  backcolor: cellData.fillColor || '#ffffff',
                },
              })
            }
            cells.push(rowCells)
          }

          convertedEl.data = cells
          convertedEl.rotate = 0

          const allWidth = (el.colWidths || []).reduce((a: number, b: number) => a + b, 0)
          convertedEl.colWidths = (el.colWidths || []).map((w: number) => w / allWidth)
          convertedEl.cellMinHeight = (el.rowHeights?.[0] || 36) * ratio

          convertedEl.outline = {
            width: 2,
            style: 'solid',
            color: '#cccccc',
          }
        }
        else if (el.type === 'chart') {
          convertedEl.type = 'chart'

          const chartTypeMap: Record<string, string> = {
            barChart: 'bar',
            bar3DChart: 'bar',
            lineChart: 'line',
            line3DChart: 'line',
            areaChart: 'area',
            pieChart: 'pie',
            pie3DChart: 'pie',
            doughnutChart: 'ring',
            radarChart: 'radar',
            scatterChart: 'scatter',
          }

          convertedEl.chartType = chartTypeMap[el.chartType || ''] || 'bar'
          convertedEl.themeColors = el.colors?.length ? el.colors : themeColors
          convertedEl.textColor = fontColor
          convertedEl.rotate = 0

          if (el.data) {
            const labels = Object.keys(el.data[0]?.xlabels || {})
            const legends = el.data?.map((chartItem: any) => chartItem.key) || []
            const series = el.data?.map((chartItem: any) => chartItem.values?.map((v: any) => v.y) || []) || []

            convertedEl.data = { labels, legends, series }
          }
        }

        if (convertedEl.type && convertedEl.width && convertedEl.height) {
          slide.elements.push(convertedEl)
        }
      }
    }

    parseElements([...(item.elements || []), ...(item.layoutElements || [])])

    slides.push(slide)
  }

  return { slides, theme: resultTheme }
}

/**
 * 检测幻灯片类型
 */
export function detectSlideType(slide: ConvertedSlide, index: number, totalSlides: number): string {
  if (index === 0) return 'cover'
  if (index === totalSlides - 1) return 'end'

  const textElements = buildTextMetas(slide)
  const numericTextCount = textElements.filter(el => el.isNumeric).length

  if (textElements.length >= 4 && (numericTextCount >= 2 || index <= Math.max(2, Math.floor(totalSlides / 3)))) {
    return 'contents'
  }

  if (textElements.length <= 2 && slide.elements?.length <= 5) {
    return 'transition'
  }

  return 'content'
}

/**
 * 为slides添加类型标记
 */
export function enrichSlidesWithType(slides: ConvertedSlide[]): ConvertedSlide[] {
  return annotateTemplateSemantics(slides)
}

/*

export function toPPTistTemplate(data: { slides: ConvertedSlide[]; theme: ThemeColors }) {
  const slides = enrichSlidesWithType(data.slides)

  return {
    title: '未命名演示文稿',
    width: 1000,
    height: 562.5,
    themeColors: data.theme.themeColors,
    theme: {
      ...data.theme,
      shadow: { h: 3, v: 3, blur: 2, color: '#808080' },
    },
    slides,
  }
}

/**
 * 转换为完整的PPTist模板格式
 */
// export function toPPTistTemplate(data: { slides: ConvertedSlide[]; theme: ThemeColors }) {
//   return {
//     title: '未命名演示文稿',
//     width: 1000,
//     height: 562.5,
//     theme: {
//       ...data.theme,
//       shadow: { h: 3, v: 3, blur: 2, color: '#808080' },
//       outline: { width: 2, color: '#525252', style: 'solid' },
//     },
//     slides: enrichSlidesWithType(data.slides),
//   }
// }

export function toPPTistTemplate(data: { slides: ConvertedSlide[]; theme: ThemeColors }) {
  const slides = enrichSlidesWithType(data.slides)

  return {
    title: '未命名演示文稿',
    width: 1000,
    height: 562.5,
    size: {
      width: 1000,
      height: 562.5,
    },
    themeColors: data.theme.themeColors,
    theme: {
      ...data.theme,
      shadow: { h: 3, v: 3, blur: 2, color: '#808080' },
    },
    slides,
  }
}
