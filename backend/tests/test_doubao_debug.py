# -*- coding: utf-8 -*-
"""
豆包 API 调试测试 - 详细日志版本
"""
import sys
import io
import asyncio
import logging

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, '/backend')

# 配置日志级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.services.ai.doubao_service import DoubaoService
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials


async def debug_doubao_request():
    """详细调试豆包请求"""
    
    print("=" * 80)
    print("豆包 API 调试测试")
    print("=" * 80)
    
    # 从数据库获取 Cookie
    print("\n1. 从数据库获取豆包账号...")
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
        for key in list(cookies.keys())[:5]:
            value = cookies[key]
            print(f"  - {key}: {value[:30]}...")
            
    finally:
        db.close()
    
    # 创建服务实例
    print("\n2. 创建 DoubaoService 实例...")
    service = DoubaoService(cookies=cookies)
    print(f"✓ Device ID: {service.device_id}")
    print(f"✓ Web ID: {service.web_id}")
    
    # 准备测试提示词
    test_prompt = "你好"
    print(f"\n3. 测试提示词: {test_prompt}")
    
    # 手动构建请求
    print("\n4. 构建请求参数...")
    
    import random
    import time
    local_conv_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
    local_msg_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
    
    message_payload = {
        "content": test_prompt,
        "content_type": 2001,
        "role": "user",
        "create_time": int(time.time()),
        "sender_role": 0,
        "is_finish": True,
        "is_stop": False,
        "is_replace": False,
        "is_delete": False,
        "message_from": 0,
        "event_id": "0"
    }
    
    payload = {
        "message": message_payload,
        "conversation_id": "0",
        "local_conversation_id": local_conv_id,
        "local_message_id": local_msg_id
    }
    
    ms_token = service.generate_fake_ms_token()
    a_bogus = service.generate_fake_a_bogus()
    
    params = {
        "aid": service.DEFAULT_ASSISTANT_ID,
        "device_id": service.device_id,
        "device_platform": "web",
        "language": "zh",
        "pkg_type": "release_version",
        "real_aid": service.DEFAULT_ASSISTANT_ID,
        "region": "CN",
        "samantha_web": 1,
        "sys_region": "CN",
        "tea_uuid": service.web_id,
        "use_olympus_account": 1,
        "version_code": service.VERSION_CODE,
        "web_id": service.web_id,
        "msToken": ms_token,
        "a_bogus": a_bogus,
    }
    
    print("✓ Payload:")
    import json
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print("\n✓ Params (前 8 个):")
    for key, value in list(params.items())[:8]:
        print(f"  {key}: {value}")
    print(f"  ... 共 {len(params)} 个参数")
    
    # 构建请求头
    print("\n5. 构建请求头...")
    headers = service.get_headers()
    print(f"✓ 请求头数量: {len(headers)}")
    for key in ["Cookie", "User-Agent", "Accept", "Origin", "Referer"]:
        value = headers.get(key, "")
        display = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {display}")
    
    # 发送请求
    print("\n6. 发送请求...")
    print(f"URL: {service.CHAT_COMPLETIONS_API}")
    
    import httpx
    async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
        try:
            response = await client.post(
                service.CHAT_COMPLETIONS_API,
                params=params,
                headers=headers,
                json=payload,
            )
            
            print(f"\n7. 响应结果:")
            print(f"  状态码: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Content-Length: {response.headers.get('content-length')}")
            print(f"  响应文本长度: {len(response.text)}")
            
            if response.text:
                print(f"\n  响应内容 (前 1000 字符):")
                print("-" * 80)
                print(response.text[:1000])
                print("-" * 80)
            else:
                print("\n  ⚠️  响应为空!")
                
            # 显示所有响应头
            print(f"\n  响应头:")
            for key, value in list(response.headers.items())[:10]:
                print(f"    {key}: {value}")
                
        except Exception as e:
            print(f"\n❌ 请求失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_doubao_request())
