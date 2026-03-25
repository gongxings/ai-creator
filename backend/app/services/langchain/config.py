"""
LangChain 服务配置
支持 16 个主流 AI 厂商的统一配置
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class Capability(Enum):
    """模型能力类型"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class AuthType(Enum):
    """认证方式"""
    API_KEY = "api_key"                    # 单密钥
    DUAL_KEY = "dual_key"                  # 双密钥 (API Key + Secret Key)
    TRIPLE_KEY = "triple_key"              # 三元组 (讯飞: AppID + APIKey + APISecret)
    OAUTH2 = "oauth2"                      # OAuth2 (Google)
    API_KEY_GROUP = "api_key_group"        # API Key + Group ID (MiniMax)


@dataclass
class ProviderConfig:
    """厂商配置"""
    name: str                                      # 厂商标识符
    display_name: str                              # 显示名称
    base_url: str                                  # 默认 API 地址
    auth_type: AuthType                            # 认证方式
    capabilities: List[Capability]                 # 支持的能力
    langchain_class: Optional[str] = None          # LangChain 类名，None 表示需自定义
    supports_custom_url: bool = True               # 是否支持自定义 URL
    models: Dict[str, List[str]] = field(default_factory=dict)    # 各能力支持的模型
    endpoints: Dict[str, str] = field(default_factory=dict)       # 各能力的端点


# ============================================================================
# 完整厂商配置（16个厂商）
# ============================================================================

PROVIDERS: Dict[str, ProviderConfig] = {
    # ======================== 国外厂商 ========================
    
    "openai": ProviderConfig(
        name="openai",
        display_name="OpenAI",
        base_url="https://api.openai.com/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE],
        langchain_class="langchain_openai.ChatOpenAI",
        models={
            "text": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "image": ["dall-e-3", "dall-e-2"],
        },
        endpoints={
            "chat": "/chat/completions",
            "image": "/images/generations",
        }
    ),
    
    "anthropic": ProviderConfig(
        name="anthropic",
        display_name="Anthropic",
        base_url="https://api.anthropic.com/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT],
        langchain_class="langchain_anthropic.ChatAnthropic",
        models={
            "text": [
                "claude-opus-4-20250514", 
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022", 
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
        },
        endpoints={
            "chat": "/messages",
        }
    ),
    
    "google": ProviderConfig(
        name="google",
        display_name="Google Gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class="langchain_google_genai.ChatGoogleGenerativeAI",
        models={
            "text": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "image": ["imagen-3.0-generate-001"],
            "video": ["veo-001"],
        },
        endpoints={
            "chat": "/models/{model}:generateContent",
            "image": "/models/{model}:predict",
        }
    ),
    
    "stability": ProviderConfig(
        name="stability",
        display_name="Stability AI",
        base_url="https://api.stability.ai/v2beta",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.IMAGE, Capability.VIDEO],
        langchain_class=None,  # 需自定义
        models={
            "image": ["sd3-large", "sd3-medium", "sd3-large-turbo", "stable-diffusion-xl-1024-v1-0"],
            "video": ["stable-video-diffusion"],
        },
        endpoints={
            "image": "/stable-image/generate/sd3",
            "video": "/video/stable-video-diffusion",
        }
    ),
    
    "replicate": ProviderConfig(
        name="replicate",
        display_name="Replicate",
        base_url="https://api.replicate.com/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class="langchain_community.llms.Replicate",
        models={
            "text": ["meta/llama-2-70b-chat", "meta/llama-3-70b-instruct"],
            "image": ["stability-ai/sdxl", "black-forest-labs/flux-schnell", "black-forest-labs/flux-dev"],
            "video": ["anotherjesse/zeroscope-v2-xl"],
        },
        endpoints={
            "predictions": "/predictions",
        }
    ),
    
    # ======================== 国内厂商 ========================
    
    "zhipu": ProviderConfig(
        name="zhipu",
        display_name="智谱 AI",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class="langchain_community.chat_models.ChatZhipuAI",
        models={
            "text": ["glm-4-plus", "glm-4", "glm-4-air", "glm-4-airx", "glm-4-flash", "glm-3-turbo"],
            "image": ["cogview-3-plus", "cogview-3"],
            "video": ["cogvideox"],
        },
        endpoints={
            "chat": "/chat/completions",
            "image": "/images/generations",
            "video": "/videos/generations",
        }
    ),
    
    "qwen": ProviderConfig(
        name="qwen",
        display_name="阿里通义",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class="langchain_community.chat_models.ChatTongyi",
        models={
            "text": ["qwen-max", "qwen-max-longcontext", "qwen-plus", "qwen-turbo"],
            "image": ["wanx-v1", "wanx2.1-t2i-turbo", "wanx2.1-t2i-plus"],
            "video": ["wanx2.1-t2v-turbo", "wanx2.1-t2v-plus"],
        },
        endpoints={
            "chat": "/services/aigc/text-generation/generation",
            "image": "/services/aigc/text2image/image-synthesis",
            "video": "/services/aigc/video-generation/generation",
        }
    ),
    
    "baidu": ProviderConfig(
        name="baidu",
        display_name="百度文心",
        base_url="https://aip.baidubce.com",
        auth_type=AuthType.DUAL_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE],
        langchain_class="langchain_community.chat_models.QianfanChatEndpoint",
        supports_custom_url=False,  # 百度结构特殊，不建议自定义
        models={
            "text": ["ernie-4.0-8k", "ernie-4.0-turbo-8k", "ernie-3.5-8k", "ernie-3.5-128k", "ernie-speed-8k", "ernie-lite-8k"],
            "image": ["sd_xl"],
        },
        endpoints={
            "token": "/oauth/2.0/token",
            "chat_ernie4": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
            "chat_ernie35": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
            "chat_ernie_speed": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_speed",
            "image": "/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl",
        }
    ),
    
    "doubao": ProviderConfig(
        name="doubao",
        display_name="火山引擎/豆包",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class=None,  # 需自定义
        models={
            "text": [
                "doubao-1.5-pro-256k", "doubao-1.5-pro-32k", 
                "doubao-pro-256k", "doubao-pro-32k", "doubao-pro-4k",
                "doubao-lite-32k", "doubao-lite-4k"
            ],
            "image": [
                "seedream-5.0-lite", "seedream-4.5", "seedream-4.0", "seedream-3.0",
                "seededit-3.0"  # 图片编辑
            ],
            "video": [
                "seedance-2.0-pro", "seedance-1.5-pro", 
                "seedance-1.0-pro", "seedance-1.0-lite"
            ],
        },
        endpoints={
            "chat": "/chat/completions",
            "image": "/images/generations",
            "video": "/videos/generations",
        }
    ),
    
    "hunyuan": ProviderConfig(
        name="hunyuan",
        display_name="腾讯混元",
        base_url="https://hunyuan.tencentcloudapi.com",
        auth_type=AuthType.DUAL_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE],
        langchain_class="langchain_community.chat_models.ChatHunyuan",
        models={
            "text": ["hunyuan-pro", "hunyuan-standard", "hunyuan-lite", "hunyuan-turbo"],
            "image": ["hunyuan-image"],
        },
        endpoints={
            "chat": "/",  # 腾讯云 API 格式特殊，使用 Action 参数
            "image": "/",
        }
    ),
    
    "minimax": ProviderConfig(
        name="minimax",
        display_name="MiniMax",
        base_url="https://api.minimax.chat/v1",
        auth_type=AuthType.API_KEY_GROUP,
        capabilities=[Capability.TEXT, Capability.VIDEO, Capability.AUDIO],
        langchain_class="langchain_community.chat_models.MiniMaxChat",
        models={
            "text": ["abab6.5s-chat", "abab6.5-chat", "abab6-chat", "abab5.5s-chat", "abab5.5-chat"],
            "video": ["video-01", "video-01-live2d"],
            "audio": ["speech-01", "speech-02"],
        },
        endpoints={
            "chat": "/text/chatcompletion_v2",
            "video": "/video_generation",
            "audio": "/t2a_v2",
        }
    ),
    
    "spark": ProviderConfig(
        name="spark",
        display_name="讯飞星火",
        base_url="wss://spark-api.xf-yun.com",
        auth_type=AuthType.TRIPLE_KEY,
        capabilities=[Capability.TEXT],
        langchain_class=None,  # 需自定义 (WebSocket)
        supports_custom_url=False,
        models={
            "text": ["spark-4.0-ultra", "spark-max", "spark-pro", "spark-lite"],
        },
        endpoints={
            "chat_ultra": "/v4.0/chat",
            "chat_max": "/v3.5/chat",
            "chat_pro": "/v3.1/chat",
            "chat_lite": "/v1.1/chat",
        }
    ),
    
    "moonshot": ProviderConfig(
        name="moonshot",
        display_name="月之暗面",
        base_url="https://api.moonshot.cn/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT],
        langchain_class="langchain_community.chat_models.MoonshotChat",
        models={
            "text": ["moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k"],
        },
        endpoints={
            "chat": "/chat/completions",
        }
    ),
    
    "deepseek": ProviderConfig(
        name="deepseek",
        display_name="DeepSeek",
        base_url="https://api.deepseek.com",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT],
        langchain_class="langchain_openai.ChatOpenAI",  # OpenAI 兼容接口
        models={
            "text": ["deepseek-chat", "deepseek-reasoner"],
        },
        endpoints={
            "chat": "/chat/completions",
        }
    ),
    
    "baichuan": ProviderConfig(
        name="baichuan",
        display_name="百川",
        base_url="https://api.baichuan-ai.com/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT],
        langchain_class="langchain_community.chat_models.ChatBaichuan",
        models={
            "text": ["Baichuan4", "Baichuan3-Turbo", "Baichuan3-Turbo-128k", "Baichuan2-Turbo"],
        },
        endpoints={
            "chat": "/chat/completions",
        }
    ),
    
    # ======================== 开源模型平台 ========================
    
    "huggingface": ProviderConfig(
        name="huggingface",
        display_name="Hugging Face",
        base_url="https://api-inference.huggingface.co/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class=None,  # 需自定义实现（使用OpenAI兼容接口）
        models={
            "text": [
                "meta-llama/Llama-3.1-8B-Instruct",
                "microsoft/Phi-3-mini-4k-instruct",
                "mistralai/Mistral-7B-Instruct-v0.3",
                "Qwen/Qwen2.5-7B-Instruct",
            ],
            "image": [
                "stabilityai/stable-diffusion-xl-base-1.0",
                "stabilityai/stable-diffusion-2-1",
                "runwayml/stable-diffusion-v1-5",
                "CompVis/stable-diffusion-v1-4",
                "stabilityai/sdxl-turbo",
            ],
            "video": [
                "stabilityai/stable-video-diffusion-img2vid-xt",
                "stabilityai/stable-video-diffusion-img2vid",
                "cerspense/zeroscope_v2_576w",
            ],
        },
        endpoints={
            "chat": "/chat/completions",
            "image": "/models/{model_id}",
            "video": "/models/{model_id}",
        }
    ),
    
    "modelscope": ProviderConfig(
        name="modelscope",
        display_name="ModelScope",
        base_url="https://api-inference.modelscope.cn/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.TEXT, Capability.IMAGE, Capability.VIDEO],
        langchain_class=None,  # 需自定义实现（使用OpenAI兼容接口）
        models={
            "text": [
                "Qwen/Qwen2.5-7B-Instruct",
                "Qwen/Qwen2.5-14B-Instruct",
                "iic/nlp_gpt3_text-generation_chinese-base",
            ],
            "image": [
                "stabilityai/stable-diffusion-xl-base-1.0",
                "iic/Colorize-SD",
                "AI-ModelScope/dreamshaper-xl-v2-turbo",
                "iic/GroundingDINO_SwinT",
            ],
            "video": [
                "iic/text-to-video-synthesis",
                "iic/VideoComposer",
                "AI-ModelScope/video-crafter",
            ],
        },
        endpoints={
            "chat": "/chat/completions",
            "image": "/models/{model_id}",
            "video": "/models/{model_id}",
        }
    ),
    
    "leonardo": ProviderConfig(
        name="leonardo",
        display_name="Leonardo AI",
        base_url="https://cloud.leonardo.ai/api/rest/v1",
        auth_type=AuthType.API_KEY,
        capabilities=[Capability.IMAGE],
        langchain_class=None,  # 需自定义实现
        models={
            "image": [
                "leonardo-phoenix",
                "leonardo-lightning-xl",
                "leonardo-kinexl",
                "leonardo-diffusion-xl",
                "sd-1.5",
                "playground-v2-5",
            ],
        },
        endpoints={
            "image": "/generations",
        }
    ),
}


# ============================================================================
# 辅助函数
# ============================================================================

def get_provider_config(provider: str) -> Optional[ProviderConfig]:
    """获取厂商配置"""
    return PROVIDERS.get(provider.lower())


def get_providers_by_capability(capability: Capability) -> List[str]:
    """获取支持特定能力的厂商列表"""
    return [
        name for name, config in PROVIDERS.items()
        if capability in config.capabilities
    ]


def get_all_providers() -> Dict[str, ProviderConfig]:
    """获取所有厂商配置"""
    return PROVIDERS.copy()


def get_text_providers() -> List[str]:
    """获取支持文本生成的厂商"""
    return get_providers_by_capability(Capability.TEXT)


def get_image_providers() -> List[str]:
    """获取支持图片生成的厂商"""
    return get_providers_by_capability(Capability.IMAGE)


def get_video_providers() -> List[str]:
    """获取支持视频生成的厂商"""
    return get_providers_by_capability(Capability.VIDEO)


def get_default_model(provider: str, capability: str = "text") -> Optional[str]:
    """获取厂商的默认模型"""
    config = get_provider_config(provider)
    if config and capability in config.models and config.models[capability]:
        return config.models[capability][0]
    return None


def get_endpoint(provider: str, capability: str) -> Optional[str]:
    """获取厂商特定能力的端点"""
    config = get_provider_config(provider)
    if config and capability in config.endpoints:
        return config.endpoints[capability]
    return None


# ============================================================================
# 厂商分组信息（用于前端展示）
# ============================================================================

PROVIDER_GROUPS = {
    "international": {
        "name": "国际厂商",
        "providers": ["openai", "anthropic", "google", "stability", "replicate", "leonardo"]
    },
    "domestic": {
        "name": "国内厂商",
        "providers": ["zhipu", "qwen", "baidu", "doubao", "hunyuan", "minimax", "spark", "moonshot", "deepseek", "baichuan"]
    },
    "opensource": {
        "name": "开源模型平台",
        "providers": ["huggingface", "modelscope"]
    }
}


# ============================================================================
# 能力说明
# ============================================================================

CAPABILITY_INFO = {
    Capability.TEXT: {
        "name": "文本生成",
        "description": "生成文本内容，支持对话和创作",
        "providers_count": len(get_text_providers())
    },
    Capability.IMAGE: {
        "name": "图片生成",
        "description": "根据文本描述生成图片",
        "providers_count": len(get_image_providers())
    },
    Capability.VIDEO: {
        "name": "视频生成",
        "description": "根据文本描述或图片生成视频",
        "providers_count": len(get_video_providers())
    },
    Capability.AUDIO: {
        "name": "音频生成",
        "description": "文本转语音、音乐生成等",
        "providers_count": len(get_providers_by_capability(Capability.AUDIO))
    }
}
