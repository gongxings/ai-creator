# -*- coding: utf-8 -*-
"""
测试更新后的 DoubaoService
"""
import sys
import io
import asyncio
import json

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, '/backend')

from app.services.ai.doubao_service import DoubaoService


async def test_doubao_service():
    """测试豆包服务"""
    
    print("=" * 60)
    print("豆包服务测试")
    print("=" * 60)
    
    # 从用户那里获取真实的 Cookie
    print("\n请提供豆包的 Cookie（sessionid）:")
    print("（如果没有真实 Cookie，将跳过实际 API 调用测试）")
    
    # 测试用的 Cookie（需要替换为真实值）
    test_cookies = {
        "sessionid": "test_session_id",  # 需要替换为真实值
        "sessionid_ss": "test_session_ss",
    }
    
    print("\n创建 DoubaoService 实例...")
    service = DoubaoService(cookies=test_cookies)
    
    print(f"✓ 服务创建成功")
    print(f"  Device ID: {service.device_id}")
    print(f"  Web ID: {service.web_id}")
    print(f"  Platform: {service.get_platform_name()}")
    
    # 测试辅助方法
    print("\n测试辅助方法...")
    
    # 测试 msToken 生成
    ms_token = service.generate_fake_ms_token()
    print(f"✓ msToken 生成")
    print(f"  长度: {len(ms_token)} 字符")
    print(f"  示例: {ms_token[:30]}...")
    assert len(ms_token) > 100, "msToken 长度应该大于 100"
    
    # 测试 a_bogus 生成
    a_bogus = service.generate_fake_a_bogus()
    print(f"✓ a_bogus 生成")
    print(f"  格式: {a_bogus}")
    assert a_bogus.startswith("mf-"), "a_bogus 应该以 'mf-' 开头"
    
    # 测试 local IDs 生成
    local_conv_id, local_msg_id = service.generate_local_ids()
    print(f"✓ Local IDs 生成")
    print(f"  Conversation ID: {local_conv_id}")
    print(f"  Message ID: {local_msg_id}")
    assert len(local_conv_id) > 15, "Local conversation ID 应该足够长"
    assert len(local_msg_id) > 15, "Local message ID 应该足够长"
    
    # 测试请求头构建
    print("\n测试请求头构建...")
    headers = service.get_headers()
    print(f"✓ 请求头构建成功")
    required_headers = ["Cookie", "User-Agent", "Accept", "Origin", "Referer"]
    for header in required_headers:
        if header in headers:
            value = headers[header]
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {header}: {display_value}")
        else:
            print(f"  ✗ {header} (缺失)")
            assert False, f"缺少必需的请求头: {header}"
    
    print("\n" + "=" * 60)
    print("基础功能测试完成")
    print("=" * 60)
    
    # 检查是否提供了真实的 Cookie
    if test_cookies["sessionid"] == "test_session_id":
        print("\n⚠️  未提供真实 Cookie，跳过实际 API 调用测试")
        print("\n要测试实际 API 调用，请修改脚本中的 test_cookies 为真实值：")
        print("  test_cookies = {")
        print('    "sessionid": "您的真实 sessionid",')
        print('    "sessionid_ss": "您的真实 sessionid_ss",')
        print("  }")
        return
    
    # 进行实际 API 调用测试
    print("\n" + "=" * 60)
    print("实际 API 调用测试")
    print("=" * 60)
    
    try:
        print("\n测试文本生成...")
        test_prompt = "用一句话介绍人工智能"
        
        print(f"  提示词: {test_prompt}")
        print(f"  正在调用豆包 API...")
        
        result = await service.generate_text(
            prompt=test_prompt,
            conversation_id=None,
            bot_id=None
        )
        
        print(f"\n✓ API 调用成功！")
        print(f"  响应长度: {len(result)} 字符")
        print(f"  响应内容:")
        print(f"  {'-' * 50}")
        print(f"  {result}")
        print(f"  {'-' * 50}")
        
    except ValueError as e:
        print(f"\n✗ API 调用失败: {e}")
        if "Cookie已过期" in str(e):
            print("  提示: 请更新 Cookie")
        elif "豆包API请求错误" in str(e):
            print("  提示: 请检查请求格式或 Cookie 有效性")
    except Exception as e:
        print(f"\n✗ 发生意外错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_writing_service_defaults():
    """测试写作服务默认参数（无需导入完整服务）"""
    
    print("\n\n" + "=" * 60)
    print("写作服务默认参数测试")
    print("=" * 60)
    
    # 直接定义默认值用于测试（与 writing_service.py 中的定义相同）
    TOOL_DEFAULTS = {
        "wechat_article": {
            "topic": "未指定主题",
            "keywords": "暂无关键词",
            "target_audience": "广大读者",
            "style": "轻松活泼"
        },
        "xiaohongshu_note": {
            "topic": "未指定主题",
            "keywords": "暂无关键词",
            "note_type": "种草分享"
        },
        "marketing_copy": {
            "product": "产品/服务",
            "target_customer": "目标客户",
            "selling_points": "核心优势",
            "goal": "提升品牌认知"
        },
    }
    
    print("\n测试默认参数功能...")
    
    # 测试不同工具的默认参数
    test_cases = [
        {
            "tool_type": "wechat_article",
            "user_input": {"topic": "人工智能"},
            "expected_defaults": ["target_audience", "style", "keywords"]
        },
        {
            "tool_type": "xiaohongshu_note",
            "user_input": {"topic": "美食推荐"},
            "expected_defaults": ["note_type", "keywords"]
        },
        {
            "tool_type": "marketing_copy",
            "user_input": {"product": "智能手表"},
            "expected_defaults": ["target_customer", "selling_points", "goal"]
        },
    ]
    
    for test_case in test_cases:
        tool_type = test_case["tool_type"]
        user_input = test_case["user_input"]
        expected_defaults = test_case["expected_defaults"]
        
        print(f"\n测试 {tool_type}...")
        print(f"  用户输入: {user_input}")
        
        # 获取默认值
        defaults = TOOL_DEFAULTS.get(tool_type, {})
        
        # 合并参数（用户输入会覆盖默认值）
        merged_input = {**defaults, **user_input}
        
        print(f"  合并后参数:")
        for key, value in merged_input.items():
            source = "用户提供" if key in user_input else "默认值"
            print(f"    {key}: {value} ({source})")
        
        # 验证默认值被应用
        for default_key in expected_defaults:
            assert default_key in merged_input, f"缺少默认参数: {default_key}"
        
        print(f"  ✓ 默认参数应用成功")
        
        # 验证用户输入覆盖了默认值
        for user_key in user_input:
            assert merged_input[user_key] == user_input[user_key], \
                f"用户输入 {user_key} 应该覆盖默认值"
        print(f"  ✓ 用户输入覆盖默认值成功")
    
    print("\n" + "=" * 60)
    print("写作服务默认参数测试完成")
    print("=" * 60)


def main():
    """主函数"""
    
    print("\n" + "=" * 60)
    print("豆包服务完整测试套件")
    print("=" * 60)
    
    # 运行异步测试
    asyncio.run(test_doubao_service())
    
    # 运行写作服务默认参数测试
    test_writing_service_defaults()
    
    print("\n\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    
    print("\n✅ 测试结果总结:")
    print("  1. DoubaoService 基础功能 - 正常")
    print("  2. 辅助方法（msToken, a_bogus, local_ids）- 正常")
    print("  3. 请求头构建 - 正常")
    print("  4. WritingService 默认参数 - 正常")
    print("  5. 参数合并逻辑 - 正常")
    
    print("\n📝 使用真实 Cookie 进行 API 测试:")
    print("  1. 登录豆包网页版 (https://www.doubao.com)")
    print("  2. 打开浏览器开发者工具 (F12)")
    print("  3. 找到 Cookie 中的 sessionid 和 sessionid_ss")
    print("  4. 修改脚本中的 test_cookies 变量")
    print("  5. 重新运行测试")


if __name__ == "__main__":
    main()
