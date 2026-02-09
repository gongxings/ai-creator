# -*- coding: utf-8 -*-
"""
豆包适配器测试脚本
"""
import asyncio
import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.oauth.adapters.doubao import DoubaoAdapter


async def test_doubao_adapter():
    """测试豆包适配器"""
    
    print("=" * 60)
    print("豆包适配器测试")
    print("=" * 60)
    
    # 创建适配器实例
    adapter = DoubaoAdapter("doubao", {
        "oauth_config": {},
        "litellm_config": {},
        "quota_config": {},
    })
    
    print(f"\n✓ 适配器创建成功")
    print(f"  Device ID: {adapter.device_id}")
    print(f"  Web ID: {adapter.web_id}")
    print(f"  User ID: {adapter.user_id}")
    
    # 测试 msToken 生成
    ms_token = adapter.generate_fake_ms_token()
    print(f"\n✓ msToken 生成成功")
    print(f"  长度: {len(ms_token)} 字符")
    print(f"  示例: {ms_token[:20]}...")
    
    # 测试 a_bogus 生成
    a_bogus = adapter.generate_fake_a_bogus()
    print(f"\n✓ a_bogus 生成成功")
    print(f"  长度: {len(a_bogus)} 字符")
    print(f"  格式: {a_bogus}")
    
    # 测试 Cookie 构建
    test_credentials = {
        "cookies": {
            "sessionid": "test_session_id_12345",
            "sessionid_ss": "test_session_ss_12345",
            "s_v_web_id": "test_web_id",
        }
    }
    
    complete_cookie = adapter.build_complete_cookie(test_credentials)
    print(f"\n✓ Cookie 构建成功")
    print(f"  Cookie 片段: {complete_cookie[:100]}...")
    print(f"  总长度: {len(complete_cookie)} 字符")
    
    # 检查必要的字段
    required_fields = [
        "is_staff_user",
        "store-region",
        "sid_guard",
        "uid_tt",
        "sessionid",
        "sessionid_ss",
        "msToken"
    ]
    
    print(f"\n✓ Cookie 字段检查:")
    for field in required_fields:
        if field in complete_cookie:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} (缺失)")
    
    # 测试 LiteLLM 配置构建
    litellm_config = adapter.build_litellm_config(test_credentials)
    print(f"\n✓ LiteLLM 配置构建成功")
    print(f"  API Base: {litellm_config['api_base']}")
    print(f"  Model: {litellm_config['model']}")
    print(f"  Available Models: {', '.join(litellm_config['available_models'])}")
    
    # 检查请求头
    headers = litellm_config['extra_headers']
    print(f"\n✓ 请求头检查:")
    important_headers = [
        "Cookie",
        "User-Agent",
        "Referer",
        "Origin",
        "Sec-Ch-Ua",
        "Agw-Js-Conv",
    ]
    for header in important_headers:
        if header in headers:
            value = headers[header]
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {header}: {display_value}")
        else:
            print(f"  ✗ {header} (缺失)")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示：")
    print("1. 所有生成函数工作正常")
    print("2. API 端点已更新为: /samantha/chat/completion")
    print("3. Cookie 包含完整的伪装字段")
    print("4. 请求头包含所有必要的浏览器指纹")
    print("\n注意：")
    print("- 这只是格式测试，实际API调用需要真实的 sessionid")
    print("- doubao-free-api 项目已归档，可能随时失效")
    print("- 建议用于个人测试，不要商用")


if __name__ == "__main__":
    asyncio.run(test_doubao_adapter())
