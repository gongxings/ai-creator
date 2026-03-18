/**
 * AI 厂商配置
 * 支持 16 个主流 AI 厂商
 */

import type { ProviderOption, ModelCapability } from '@/types'

export const providerOptions: ProviderOption[] = [
  // ======================== 国外厂商 ========================
  {
    value: 'openai',
    label: 'OpenAI',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.openai.com/v1',
    capabilities: ['text', 'image'],
    supportsCustomUrl: true,
  },
  {
    value: 'anthropic',
    label: 'Anthropic',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.anthropic.com/v1',
    capabilities: ['text'],
    supportsCustomUrl: true,
  },
  {
    value: 'google',
    label: 'Google Gemini',
    authType: 'api_key',
    defaultBaseUrl: 'https://generativelanguage.googleapis.com/v1beta',
    capabilities: ['text', 'image', 'video'],
    supportsCustomUrl: true,
  },
  {
    value: 'stability',
    label: 'Stability AI',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.stability.ai/v2beta',
    capabilities: ['image', 'video'],
    supportsCustomUrl: true,
  },
  {
    value: 'replicate',
    label: 'Replicate',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.replicate.com/v1',
    capabilities: ['text', 'image', 'video'],
    supportsCustomUrl: true,
  },

  // ======================== 国内厂商 ========================
  {
    value: 'zhipu',
    label: '智谱 AI',
    authType: 'api_key',
    defaultBaseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    capabilities: ['text', 'image', 'video'],
    supportsCustomUrl: true,
  },
  {
    value: 'qwen',
    label: '阿里通义',
    authType: 'api_key',
    defaultBaseUrl: 'https://dashscope.aliyuncs.com/api/v1',
    capabilities: ['text', 'image', 'video'],
    supportsCustomUrl: true,
  },
  {
    value: 'baidu',
    label: '百度文心',
    authType: 'dual_key',
    defaultBaseUrl: 'https://aip.baidubce.com',
    capabilities: ['text', 'image'],
    supportsCustomUrl: false,
  },
  {
    value: 'doubao',
    label: '火山引擎/豆包',
    authType: 'api_key',
    defaultBaseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    capabilities: ['text', 'image', 'video'],
    supportsCustomUrl: true,
  },
  {
    value: 'hunyuan',
    label: '腾讯混元',
    authType: 'dual_key',
    defaultBaseUrl: 'https://hunyuan.tencentcloudapi.com',
    capabilities: ['text', 'image'],
    supportsCustomUrl: false,
  },
  {
    value: 'minimax',
    label: 'MiniMax',
    authType: 'api_key_group',
    defaultBaseUrl: 'https://api.minimax.chat/v1',
    capabilities: ['text', 'video', 'audio'],
    supportsCustomUrl: true,
  },
  {
    value: 'spark',
    label: '讯飞星火',
    authType: 'triple_key',
    defaultBaseUrl: 'wss://spark-api.xf-yun.com',
    capabilities: ['text'],
    supportsCustomUrl: false,
  },
  {
    value: 'moonshot',
    label: '月之暗面',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.moonshot.cn/v1',
    capabilities: ['text'],
    supportsCustomUrl: true,
  },
  {
    value: 'deepseek',
    label: 'DeepSeek',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.deepseek.com',
    capabilities: ['text'],
    supportsCustomUrl: true,
  },
  {
    value: 'baichuan',
    label: '百川',
    authType: 'api_key',
    defaultBaseUrl: 'https://api.baichuan-ai.com/v1',
    capabilities: ['text'],
    supportsCustomUrl: true,
  },
]

// 根据 provider value 获取配置
export function getProviderConfig(provider: string): ProviderOption | undefined {
  return providerOptions.find(p => p.value === provider)
}

// 获取支持特定能力的厂商
export function getProvidersByCapability(capability: ModelCapability): ProviderOption[] {
  return providerOptions.filter(p => p.capabilities.includes(capability))
}

// 能力标签映射
export const capabilityLabels: Record<ModelCapability, string> = {
  text: '文本',
  image: '图片',
  video: '视频',
  audio: '音频',
}

// 认证类型说明
export const authTypeLabels: Record<string, string> = {
  api_key: 'API Key',
  dual_key: 'API Key + Secret Key',
  triple_key: 'App ID + API Key + API Secret',
  api_key_group: 'API Key + Group ID',
}
