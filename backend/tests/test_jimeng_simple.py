# -*- coding: utf-8 -*-
"""
即梦 AI 适配器优化测试脚本
"""
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import uuid


class SimpleJimengAdapter:
    """简化的即梦适配器 - 用于测试"""
    
    API_BASE = "https://jimeng.jianying.com"
    IMAGE_GEN_ENDPOINT = "/ai_tool/api/v1/public/multimodal/sync_text2image"
    
    SUPPORTED_MODELS = [
        "jimeng-3.0",       # 默认最新模型
        "jimeng-2.1",       # 2.1 版本
        "jimeng-2.0-pro",   # 2.0 专业版
        "jimeng-2.0",       # 2.0 版本
        "jimeng-1.4",       # 1.4 版本
        "jimeng-xl-pro",    # XL 专业版
    ]
    
    def build_request_headers(self, sessionid: str):
        """构建请求头"""
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": f"sessionid={sessionid}",
            "Origin": "https://jimeng.jianying.com",
            "Pragma": "no-cache",
            "Referer": "https://jimeng.jianying.com/ai-tool/image/generate",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Secsdk-Csrf-Token": str(uuid.uuid4()),
        }
    
    def build_image_request_body(
        self, 
        prompt: str, 
        model: str = "jimeng-3.0",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        sample_strength: float = 0.5
    ):
        """构建图像生成请求体"""
        return {
            "model_version": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "sample_strength": sample_strength,
            "task_type": "text2image",
            "batch_size": 4,  # 默认生成 4 张图片
        }


def test_adapter():
    """测试适配器"""
    
    print("=" * 60)
    print("即梦 AI 适配器测试 - 基于 jimeng-free-api 优化")
    print("=" * 60)
    
    # 创建适配器实例
    adapter = SimpleJimengAdapter()
    
    print(f"\n✓ 适配器创建成功")
    print(f"  API Base: {adapter.API_BASE}")
    print(f"  Image Gen Endpoint: {adapter.IMAGE_GEN_ENDPOINT}")
    
    # 测试支持的模型
    print(f"\n✓ 支持的模型 ({len(adapter.SUPPORTED_MODELS)} 个):")
    for i, model in enumerate(adapter.SUPPORTED_MODELS, 1):
        print(f"  {i}. {model}")
    
    # 测试请求头构建
    test_sessionid = "test_sessionid_12345"
    headers = adapter.build_request_headers(test_sessionid)
    print(f"\n✓ 请求头构建成功")
    print(f"  共 {len(headers)} 个请求头")
    
    important_headers = [
        "Accept",
        "Content-Type",
        "Cookie",
        "Origin",
        "Referer",
        "X-Secsdk-Csrf-Token",
    ]
    
    print(f"\n✓ 重要请求头检查:")
    for header in important_headers:
        if header in headers:
            value = headers[header]
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {header}: {display_value}")
        else:
            print(f"  ✗ {header} (缺失)")
    
    # 测试请求体构建
    body = adapter.build_image_request_body(
        prompt="可爱的熊猫漫画",
        model="jimeng-3.0",
        negative_prompt="模糊,低质量",
        width=1024,
        height=1024,
        sample_strength=0.5
    )
    print(f"\n✓ 图像生成请求体构建成功")
    print(f"  model_version: {body['model_version']}")
    print(f"  prompt: {body['prompt']}")
    print(f"  negative_prompt: {body['negative_prompt']}")
    print(f"  width: {body['width']}")
    print(f"  height: {body['height']}")
    print(f"  sample_strength: {body['sample_strength']}")
    print(f"  task_type: {body['task_type']}")
    print(f"  batch_size: {body['batch_size']}")
    
    # 完整请求示例
    print(f"\n" + "=" * 60)
    print("完整请求示例")
    print("=" * 60)
    print(f"\nPOST {adapter.API_BASE}{adapter.IMAGE_GEN_ENDPOINT}")
    print(f"\n请求头:")
    for key in ["Accept", "Content-Type", "Cookie", "Origin", "X-Secsdk-Csrf-Token"]:
        value = headers[key]
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {display_value}")
    print(f"  ... 共 {len(headers)} 个请求头")
    
    print(f"\n请求体:")
    print(f"  model_version: {body['model_version']}")
    print(f"  prompt: {body['prompt']}")
    print(f"  width x height: {body['width']} x {body['height']}")
    print(f"  batch_size: {body['batch_size']} 张")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n✅ 优化内容对比：")
    print("  1. 完整的浏览器指纹请求头 (17个字段)")
    print("  2. 添加 X-Secsdk-Csrf-Token 防护头")
    print("  3. 支持 6 种模型（jimeng-3.0 到 jimeng-xl-pro）")
    print("  4. 完整的图像生成参数（宽高、精细度、反向提示词）")
    print("  5. 默认批量生成 4 张图片")
    
    print(f"\n⚠️ 重要提示：")
    print("  - 这只是格式测试，未进行实际 API 调用")
    print("  - 实际使用需要真实的 sessionid")
    print("  - jimeng-free-api 项目已归档，可能随时失效")
    print("  - 即梦每日免费 66 积分（可生成 66 次）")
    print("  - 建议仅用于个人测试，商用请使用官方 API")
    
    print(f"\n📝 主要改进：")
    print("  1. 支持 6 种即梦模型")
    print("  2. 完善请求头，包含完整的浏览器指纹")
    print("  3. 支持自定义图像尺寸和精细度")
    print("  4. 支持反向提示词（negative_prompt）")
    print("  5. 默认批量生成 4 张图片提高效率")
    print("  6. 兼容 OpenAI 图像生成接口格式")
    
    print(f"\n🎨 即梦特色：")
    print("  - 字节跳动旗下图像生成顶流产品")
    print("  - 每日免费 66 积分，无需付费即可体验")
    print("  - 支持高质量图像生成（1024x1024）")
    print("  - 多种模型可选，满足不同需求")


if __name__ == "__main__":
    test_adapter()
