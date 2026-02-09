# -*- coding: utf-8 -*-
"""
豆包 API 测试 - 带重试和等待
"""
import sys
import io
import asyncio
import time

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, 'D:\\workspace\\openstudy\\ai-creator\\backend')

from app.services.ai.doubao_service import DoubaoService
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials


async def test_with_retry():
    """测试带重试机制的 API 调用"""
    
    print("=" * 60)
    print("豆包 API 测试（带重试）")
    print("=" * 60)
    
    # 从数据库获取 Cookie
    print("\n1. 获取豆包账号...")
    db = SessionLocal()
    try:
        account = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True,
            OAuthAccount.is_expired == False
        ).first()
        
        if not account:
            print("❌ 未找到可用的豆包账号")
            return
        
        credentials = decrypt_credentials(account.credentials)
        cookies = credentials.get("cookies", {})
        
        print(f"✓ 找到账号 ID: {account.id}")
        print(f"  Cookie 数量: {len(cookies)}")
            
    finally:
        db.close()
    
    # 创建服务实例
    print("\n2. 创建 DoubaoService...")
    service = DoubaoService(cookies=cookies)
    print(f"✓ 服务创建成功")
    print(f"  Device ID: {service.device_id}")
    print(f"  Web ID: {service.web_id}")
    print(f"  User ID: {service.user_id}")
    
    # 测试提示词
    test_prompts = [
        "你好",
        "用一句话介绍人工智能",
        "写一个关于春天的俳句"
    ]
    
    max_retries = 3
    retry_delay = 10  # 初始等待 10 秒
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}/{len(test_prompts)}: {prompt}")
        print('=' * 60)
        
        for attempt in range(max_retries):
            try:
                print(f"\n尝试 {attempt + 1}/{max_retries}...")
                result = await service.generate_text(prompt)
                
                print(f"\n✅ 成功！")
                print(f"响应长度: {len(result)} 字符")
                print(f"\n响应内容:")
                print("-" * 60)
                print(result)
                print("-" * 60)
                
                # 成功后等待一下再继续下一个
                if i < len(test_prompts):
                    wait_time = 5
                    print(f"\n等待 {wait_time} 秒后继续下一个测试...")
                    await asyncio.sleep(wait_time)
                
                break  # 成功，退出重试循环
                
            except ValueError as e:
                error_msg = str(e)
                
                # 检查是否是限流错误
                if "710022002" in error_msg or "访问频繁" in error_msg:
                    print(f"⚠️  触发限流")
                    
                    if attempt < max_retries - 1:
                        current_delay = retry_delay * (2 ** attempt)  # 指数退避
                        print(f"   等待 {current_delay} 秒后重试...")
                        await asyncio.sleep(current_delay)
                    else:
                        print(f"❌ 达到最大重试次数")
                        print(f"   错误: {error_msg}")
                        return
                else:
                    print(f"❌ 调用失败: {error_msg}")
                    return
                    
            except Exception as e:
                print(f"❌ 发生意外错误: {e}")
                import traceback
                traceback.print_exc()
                return
    
    print(f"\n{'=' * 60}")
    print("所有测试完成！")
    print('=' * 60)


async def test_single_request():
    """单次请求测试"""
    
    print("=" * 60)
    print("豆包 API 单次请求测试")
    print("=" * 60)
    
    # 从数据库获取 Cookie
    db = SessionLocal()
    try:
        account = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True
        ).first()
        
        if not account:
            print("❌ 未找到可用的豆包账号")
            return
        
        credentials = decrypt_credentials(account.credentials)
        cookies = credentials.get("cookies", {})
            
    finally:
        db.close()
    
    service = DoubaoService(cookies=cookies)
    
    print(f"\n完整 Cookie 构建测试:")
    print(f"  原始 cookies: {list(cookies.keys())}")
    
    ms_token = service.generate_fake_ms_token()
    complete_cookie = service.build_complete_cookie(ms_token)
    
    print(f"\n  完整 Cookie 字段:")
    for part in complete_cookie.split("; ")[:10]:
        key = part.split("=")[0]
        print(f"    - {key}")
    print(f"  总计: {len(complete_cookie.split('; '))} 个字段")
    
    print(f"\n发送请求...")
    try:
        result = await service.generate_text("你好")
        print(f"\n✅ 成功！")
        print(f"响应: {result}")
    except ValueError as e:
        print(f"\n❌ 失败: {e}")
        if "710022002" in str(e):
            print("\n💡 建议:")
            print("  1. 等待 5-10 分钟")
            print("  2. 运行重试测试: python3 test_doubao_with_retry.py")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--retry":
        asyncio.run(test_with_retry())
    else:
        asyncio.run(test_single_request())
        print("\n💡 提示: 使用 --retry 参数运行自动重试测试")
