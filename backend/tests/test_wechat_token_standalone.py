"""
独立测试微信公众号 token 提取功能

不依赖数据库，直接测试 HTTP 请求逻辑
"""
import asyncio
import httpx
import re
import os

# 测试用的 Cookie - 需要手动设置或从环境变量读取
# 你可以将有效的 Cookie 粘贴到这里进行测试
TEST_COOKIES_STR = os.environ.get("WECHAT_COOKIES", "")

def parse_cookies_from_string(cookies_str: str) -> dict:
    """从 Cookie 字符串解析为字典"""
    if not cookies_str:
        return {}
    
    cookies = {}
    for item in cookies_str.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    
    return cookies


async def test_token_extraction_methods(cookies: dict):
    """测试不同的 token 提取方法"""
    
    BASE_URL = "https://mp.weixin.qq.com"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://mp.weixin.qq.com/",
    }
    
    async with httpx.AsyncClient(
        headers=DEFAULT_HEADERS,
        cookies=cookies,
        follow_redirects=True,
        timeout=30.0
    ) as client:
        print("\n" + "=" * 60)
        print("方法1: 访问根路径 / (推荐方法)")
        print("=" * 60)
        
        try:
            response = await client.get(f"{BASE_URL}/")
            final_url = str(response.url)
            print(f"状态码: {response.status_code}")
            print(f"最终URL: {final_url}")
            
            # 从 URL 中提取 token
            url_token_match = re.search(r'token=(\d+)', final_url)
            if url_token_match:
                token = url_token_match.group(1)
                print(f"✓ 成功从 URL 提取 token: {token}")
                
                # 提取 uin
                uin_match = re.search(r'uin[=:][\s"\']*(\d+)', response.text)
                if uin_match:
                    print(f"✓ 成功提取 uin: {uin_match.group(1)}")
            else:
                print("✗ 未能从 URL 中提取 token")
                if "scanlogin" in final_url.lower() or "login" in final_url.lower():
                    print("原因：Cookie 已失效，重定向到登录页")
        except Exception as e:
            print(f"✗ 请求失败: {e}")
        
        print("\n" + "=" * 60)
        print("方法2: 直接访问 /cgi-bin/home (旧方法)")
        print("=" * 60)
        
        try:
            response2 = await client.get(
                f"{BASE_URL}/cgi-bin/home",
                params={"t": "home/index", "lang": "zh_CN"}
            )
            final_url2 = str(response2.url)
            print(f"状态码: {response2.status_code}")
            print(f"最终URL: {final_url2}")
            
            url_token_match2 = re.search(r'token=(\d+)', final_url2)
            if url_token_match2:
                print(f"✓ 成功从 URL 提取 token: {url_token_match2.group(1)}")
            else:
                print("✗ 未能从 URL 中提取 token")
        except Exception as e:
            print(f"✗ 请求失败: {e}")


async def main():
    print("=" * 60)
    print("微信公众号 Token 提取方法对比测试")
    print("=" * 60)
    
    # 尝试从环境变量获取 Cookie
    cookies = parse_cookies_from_string(TEST_COOKIES_STR)
    
    if not cookies:
        print("\n错误：未设置测试 Cookie")
        print("\n请通过以下方式之一提供 Cookie:")
        print("1. 设置环境变量 WECHAT_COOKIES")
        print("2. 直接修改脚本中的 TEST_COOKIES_STR 变量")
        print("\nCookie 格式示例:")
        print("slavesid=xxx; slave_user=xxx; data_ticket=xxx; bizuin=xxx")
        return
    
    print(f"\n获取到 Cookie，包含 {len(cookies)} 个键")
    print(f"Cookie 键: {list(cookies.keys())}")
    
    await test_token_extraction_methods(cookies)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
