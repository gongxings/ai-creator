"""
详细测试豆包图片生成和 Cookie 验证
"""
import asyncio
import json
import httpx

async def test_doubao_cookies(cookies_str: str):
    """测试豆包 Cookie 是否有效"""
    headers = {
        "Cookie": cookies_str,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.doubao.com/",
        "Origin": "https://www.doubao.com",
        "Content-Type": "application/json",
    }

    # 测试 1: 访问首页
    print("\n=== 测试 1: 访问豆包首页 ===")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            "https://www.doubao.com/",
            headers=headers,
            timeout=30.0
        )
        print(f"首页状态码: {response.status_code}")
        print(f"首页URL: {response.url}")
        
        content = response.text
        if "登录" in content and "请先登录" in content:
            print("❌ Cookie 无效 - 需要登录")
            return False
        elif "用户" in content or "console" in content or "chat" in content:
            print("✅ Cookie 有效 - 已登录")
        else:
            print("⚠️  无法确定 Cookie 状态")

    # 测试 2: 调用聊天接口
    print("\n=== 测试 2: 调用豆包聊天接口 ===")
    chat_payload = {
        "user_input": "你好",
        "bot_id": "7358044466096914465",
        "stream": False,
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.post(
                "https://www.doubao.com/api/chat/completions",
                headers=headers,
                json=chat_payload,
                timeout=60.0
            )
            print(f"聊天接口状态码: {response.status_code}")
            
            if response.status_code == 401:
                print("❌ Cookie 无效 - 401 Unauthorized")
                print(f"响应: {response.text[:200]}")
                return False
            elif response.status_code == 200:
                print("✅ Cookie 有效 - 200 OK")
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                return True
            else:
                print(f"⚠️  状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

    # 测试 3: 尝试生成图片
    print("\n=== 测试 3: 尝试生成图片 ===")
    image_payload = {
        "user_input": "画一张图片，一只可爱的猫咪",
        "bot_id": "7358044466096914465",
        "stream": False,
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.post(
                "https://www.doubao.com/api/chat/completions",
                headers=headers,
                json=image_payload,
                timeout=120.0
            )
            print(f"图片生成状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 图片生成请求成功")
                data = response.json()
                print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}...")
                
                # 提取图片 URL
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    print(f"\n响应内容: {content[:500]}...")
                    
                    import re
                    image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                    if image_urls:
                        print(f"\n✅ 找到 {len(image_urls)} 张图片:")
                        for i, url in enumerate(image_urls):
                            print(f"  {i+1}. {url}")
                    else:
                        print("\n⚠️  未找到图片 URL")
                else:
                    print("⚠️  响应格式不符合预期")
            else:
                print(f"❌ 图片生成失败 - 状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 图片生成失败: {e}")
            import traceback
            traceback.print_exc()

    return True


if __name__ == "__main__":
    # 示例 Cookie 字符串（替换为实际的 Cookie）
    cookies_str = input("请输入豆包 Cookie 字符串 (格式: name1=value1; name2=value2): ").strip()
    
    if not cookies_str:
        print("Cookie 不能为空")
        exit(1)
    
    print(f"\n测试 Cookie: {cookies_str[:100]}...")
    asyncio.run(test_doubao_cookies(cookies_str))
