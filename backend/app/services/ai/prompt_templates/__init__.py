"""
平台提示词模板模块
"""
from .wechat import WECHAT_PROMPTS
from .xiaohongshu import XIAOHONGSHU_PROMPTS
from .toutiao import TOUTIAO_PROMPTS
from .ppt import PPT_PROMPTS

__all__ = [
    "WECHAT_PROMPTS",
    "XIAOHONGSHU_PROMPTS",
    "TOUTIAO_PROMPTS",
    "PPT_PROMPTS",
    "get_platform_prompt"
]


def get_platform_prompt(platform: str, category: str, style: str = None) -> str:
    """
    获取指定平台和场景的提示词模板
    
    Args:
        platform: 平台类型 (wechat/xiaohongshu/toutiao/ppt)
        category: 场景分类
        style: 风格类型
    
    Returns:
        提示词模板字符串
    """
    prompts_map = {
        "wechat": WECHAT_PROMPTS,
        "xiaohongshu": XIAOHONGSHU_PROMPTS,
        "toutiao": TOUTIAO_PROMPTS,
        "ppt": PPT_PROMPTS
    }
    
    platform_prompts = prompts_map.get(platform, {})
    prompt = platform_prompts.get(category, platform_prompts.get("default", ""))
    
    # 如果有风格要求，添加风格提示
    if style:
        style_prompt = f"\n\n【风格要求】\n请使用{style}风格来撰写。"
        prompt += style_prompt
    
    return prompt
