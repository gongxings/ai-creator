"""
测试豆包图片生成（使用数据库中的 Cookie）
"""
import asyncio
import sys
import json
sys.path.insert(0, '.')
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_with_database_cookies():
    """使用数据库中的 Cookie 测试豆包图片生成"""
    from app.core.database import SessionLocal
    from app.models.oauth_account import OAuthAccount
    from app.services.oauth.encryption import decrypt_credentials

    db = SessionLocal()
    try:
        # 查询豆包账号
        account = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True
        ).first()

        if not account:
            print("No doubao account found")
            return

        print(f"Account found: ID={account.id}, Name={account.account_name}")

        # 解密凭证
        credentials = decrypt_credentials(account.credentials)
        cookies = credentials.get("cookies", {})
        user_agent = credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        print(f"\nCookies:")
        print(f"  Count: {len(cookies)}")
        for key, value in cookies.items():
            print(f"  {key}: {value[:80] if len(value) > 80 else value}")

        print(f"\nUser-Agent: {user_agent}")

        # 测试豆包 API
        import httpx

        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()]),
            "User-Agent": user_agent,
            "Referer": "https://www.doubao.com/",
            "Origin": "https://www.doubao.com",
            "Content-Type": "application/json",
        }

        print("\n" + "="*60)
        print("Test 1: Visit Doubao Home Page")
        print("="*60)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                "https://www.doubao.com/",
                headers=headers,
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            print(f"URL: {response.url}")
            content = response.text
            if "Login" in content and "Please Login" in content:
                print("Cookie may be expired - need to re-login")
            else:
                print("Cookie is valid")

        print("\n" + "="*60)
        print("Test 2: Call Doubao Chat API")
        print("="*60)
        chat_payload = {
            "user_input": "Hello",
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
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("Chat API call successful")
                    data = response.json()
                    print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                else:
                    print(f"Chat API failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
            except Exception as e:
                print(f"Chat API exception: {e}")

        print("\n" + "="*60)
        print("Test 3: Try Image Generation")
        print("="*60)
        image_payload = {
            "user_input": "Generate an image, a cute cat",
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
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("Image generation request successful")
                    data = response.json()
                    print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0].get("message", {}).get("content", "")
                        print(f"\nResponse Content: {content[:300]}...")
                        
                        import re
                        image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                        if image_urls:
                            print(f"\nFound {len(image_urls)} image(s):")
                            for i, url in enumerate(image_urls):
                                print(f"  {i+1}. {url}")
                        else:
                            print("No image URLs found")
                    else:
                        print("Response format not as expected")
                elif response.status_code == 401:
                    print("401 Unauthorized - Cookie invalid or expired")
                    print(f"Response: {response.text[:200]}...")
                else:
                    print(f"Image generation failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    
            except httpx.HTTPStatusError as e:
                print(f"HTTP Error: {e}")
                if e.response:
                    print(f"Status Code: {e.response.status_code}")
                    print(f"Response: {e.response.text[:200]}...")
            except Exception as e:
                print(f"Exception: {e}")
                import traceback
                traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_with_database_cookies())
