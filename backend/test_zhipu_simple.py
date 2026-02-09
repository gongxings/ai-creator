# -*- coding: utf-8 -*-
"""
智谱清言适配器优化测试脚本
"""
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import uuid


class SimpleZhipuAdapter:
    """简化的智谱清言适配器 - 用于测试"""
    
    API_BASE = "https://chatglm.cn"
    CHAT_ENDPOINT = "/chatglm/backend-api/assistant/stream"
    
    SUPPORTED_MODELS = [
        "glm-4-flash",      # 免费快速模型
        "glm-4",            # 标准模型
        "glm-4v",           # 视觉模型
        "glm-4-plus",       # Plus 模型
        "glm-4-air",        # Air 模型
        "glm-4-flashx",     # FlashX 模型
        "glm-zero",         # 思考模型
    ]
    
    def build_request_headers(self, cookies: dict):
        """构建请求头"""
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        return {
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": cookie_str,
            "Origin": "https://chatglm.cn",
            "Pragma": "no-cache",
            "Referer": "https://chatglm.cn/main/alltoolsdetail",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-App-Platform": "pc",
            "X-App-Version": "0.0.1",
            "X-Device-Id": str(uuid.uuid4()),
            "X-Request-Id": str(uuid.uuid4()),
        }
    
    def build_request_body(self, message: str, conversation_id: str = "", assistant_id: str = "65940acff94777010aa6b796"):
        """构建请求体"""
        return {
            "assistant_id": assistant_id,
            "conversation_id": conversation_id,
            "messages": [{"role": "user", "content": [{"type": "text", "text": message}]}],
            "meta_data": {
                "channel": "",
                "draft_id": "",
                "input_question_type": "xxxx",
                "is_test": False,
            },
        }


def test_adapter():
    """测试适配器"""
    
    print("=" * 60)
    print("智谱清言适配器测试 - 基于 glm-free-api 优化")
    print("=" * 60)
    
    # 创建适配器实例
    adapter = SimpleZhipuAdapter()
    
    print(f"\n✓ 适配器创建成功")
    print(f"  API Base: {adapter.API_BASE}")
    print(f"  Chat Endpoint: {adapter.CHAT_ENDPOINT}")
    
    # 测试支持的模型
    print(f"\n✓ 支持的模型 ({len(adapter.SUPPORTED_MODELS)} 个):")
    for i, model in enumerate(adapter.SUPPORTED_MODELS, 1):
        print(f"  {i}. {model}")
    
    # 测试请求头构建
    test_cookies = {
        "chatglm_token": "test_token_12345",
        "chatglm_refresh_token": "test_refresh_token_67890",
        "chatglm_user_id": "test_user_id",
    }
    headers = adapter.build_request_headers(test_cookies)
    print(f"\n✓ 请求头构建成功")
    print(f"  共 {len(headers)} 个请求头")
    
    important_headers = [
        "Accept",
        "Content-Type",
        "Cookie",
        "Origin",
        "Referer",
        "X-App-Platform",
        "X-Device-Id",
        "X-Request-Id",
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
    body = adapter.build_request_body("你好，智谱清言！")
    print(f"\n✓ 请求体构建成功")
    print(f"  assistant_id: {body['assistant_id']}")
    print(f"  conversation_id: {body['conversation_id']}")
    print(f"  messages 数量: {len(body['messages'])}")
    print(f"  message role: {body['messages'][0]['role']}")
    print(f"  message content: {body['messages'][0]['content'][0]['text']}")
    print(f"  meta_data.is_test: {body['meta_data']['is_test']}")
    
    # 完整请求示例
    print(f"\n" + "=" * 60)
    print("完整请求示例")
    print("=" * 60)
    print(f"\nPOST {adapter.API_BASE}{adapter.CHAT_ENDPOINT}")
    print(f"\n请求头:")
    for key in ["Accept", "Content-Type", "Cookie", "Origin", "X-App-Platform"]:
        value = headers[key]
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {display_value}")
    print(f"  ... 共 {len(headers)} 个请求头")
    
    print(f"\n请求体:")
    print(f"  assistant_id: {body['assistant_id']}")
    print(f"  messages[0].content[0].text: {body['messages'][0]['content'][0]['text']}")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n✅ 优化内容对比：")
    print("  1. 完整的浏览器指纹请求头 (19个字段)")
    print("  2. 添加 X-App-Platform、X-Device-Id、X-Request-Id")
    print("  3. 支持 7 种模型（包括 glm-zero 思考模型）")
    print("  4. 优化 SSE 流解析，添加错误处理")
    print("  5. Accept 头设置为 text/event-stream")
    
    print(f"\n⚠️ 重要提示：")
    print("  - 这只是格式测试，未进行实际 API 调用")
    print("  - 实际使用需要真实的 chatglm_token")
    print("  - glm-free-api 项目已归档，可能随时失效")
    print("  - 建议仅用于个人测试，商用请使用官方 API")
    
    print(f"\n📝 主要改进：")
    print("  1. 添加更多模型支持 (7种)")
    print("  2. 完善请求头，包含完整的浏览器指纹")
    print("  3. 添加 X-Device-Id 和 X-Request-Id 追踪")
    print("  4. 优化 SSE 流解析错误处理")
    print("  5. Referer 更新为 /main/alltoolsdetail")


if __name__ == "__main__":
    test_adapter()
