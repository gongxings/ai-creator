"""
测试微信公众号 token 提取功能

验证通过访问根路径 / 获取重定向 URL 中的 token 的方式是否正确
"""
import asyncio
import httpx
import re
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从数据库获取 Cookie 或使用环境变量
async def get_test_cookies():
    """获取测试用的 Cookie"""
    # 尝试从数据库获取
    try:
        from app.core.database_async import AsyncSessionLocal
        from app.models.publish import PlatformAccount
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(PlatformAccount).where(
                    PlatformAccount.platform == "wechat",
                    PlatformAccount.is_active == True
                ).limit(1)
            )
            account = result.scalar_one_or_none()
            if account and account.cookies:
                import json
                return json.loads(account.cookies)
    except Exception as e:
        print(f"从数据库获取 Cookie 失败: {e}")
    
    return None


async def test_token_extraction():
    """测试 token 提取"""
    
    cookies = await get_test_cookies()
    if not cookies:
        print("错误：未找到有效的微信公众号 Cookie")
        print("请先在系统中添加微信公众号账号并配置 Cookie")
        return False
    
    print(f"获取到 Cookie，包含 {len(cookies)} 个键")
    print(f"Cookie 键: {list(cookies.keys())}")
    
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
        print("\n=== 测试方法：访问根路径 / ===")
        
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
            uin_match = re.search(r'uin:\s*["\']?(\d+)', response.text)
            if uin_match:
                print(f"✓ 成功提取 uin: {uin_match.group(1)}")
            
            return True
        else:
            print("✗ 未能从 URL 中提取 token")
            
            # 检查是否重定向到登录页
            if "scanlogin" in final_url.lower() or "login" in final_url.lower():
                print("原因：Cookie 已失效，重定向到登录页")
            else:
                print(f"页面内容片段: {response.text[:500]}")
            
            return False


async def main():
    print("=" * 60)
    print("微信公众号 Token 提取测试")
    print("=" * 60)
    
    success = await test_token_extraction()
    
    print("\n" + "=" * 60)
    if success:
        print("测试通过！Token 提取功能正常工作")
    else:
        print("测试失败！请检查 Cookie 是否有效")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
