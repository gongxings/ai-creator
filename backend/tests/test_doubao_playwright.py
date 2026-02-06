async def test_doubao_with_playwright():
    """使用 Playwright 测试豆包图片生成"""
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

        print(f"\nCookies: {list(cookies.keys())}")
        for key, value in cookies.items():
            print(f"  {key}: {value[:80] if len(value) > 80 else value}")

        # 使用 Playwright 启动浏览器
        async with async_playwright(headless=False) as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )

            # 设置 Cookie
            for name, value in cookies.items():
                await context.add_cookies([{
                    'name': name,
                    'value': value,
                    'domain': '.doubao.com',
                    'path': '/',
                }])

            page = await context.new_page()

            print("\n" + "="*60)
            print("Test 1: Visit Doubao Home Page")
            print("="*60)
            try:
                await page.goto("https://www.doubao.com/", timeout=30000)
                print(f"Home page loaded: {page.url}")
                print(f"Page title: {await page.title()}")
            except Exception as e:
                print(f"Failed to load home page: {e}")

            print("\n" + "="*60)
            print("Test 2: Visit Doubao Chat Page")
            print("="*60)
            try:
                await page.goto("https://www.doubao.com/chat/", timeout=30000)
                print(f"Chat page loaded: {page.url}")
                print(f"Page title: {await page.title()}")

                # 获取 localStorage 中的数据
                local_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
                print(f"\nLocalStorage keys: {list(local_storage.keys())}")
                for key, value in local_storage.items():
                    print(f"  {key}: {str(value)[:100] if len(str(value)) > 100 else value}")

            except Exception as e:
                print(f"Failed to load chat page: {e}")

            print("\n" + "="*60)
            print("Test 3: Try Image Generation via Chat")
            print("="*60)

            # 尝试通过聊天请求生成图片
            try:
                script = """
                const payload = {
                    user_input: "画一张图片，一只可爱的猫咪",
                    bot_id: "7358044466096914465",
                    stream: false,
                };

                const response = await fetch('/api/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                return await response.json();
                """

                result = await page.evaluate(script)
                print(f"Chat API Response: {result}")

                if result and "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    print(f"\nResponse Content: {content[:300]}...")

                    import re
                    image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
                    if image_urls:
                        print(f"\nFound {len(image_urls)} image(s):")
                        for i, url in enumerate(image_urls):
                            print(f"  {i+1}. {url}")
                    else:
                        print("\nNo image URLs found")
                else:
                    print("Response format not as expected")

            except Exception as e:
                print(f"Failed to call chat API: {e}")
                import traceback
                traceback.print_exc()

            # 等待用户查看结果（给10秒时间）
            print("\n" + "="*60)
            print("Waiting 10 seconds before closing...")
            print("="*60)
            await asyncio.sleep(10)

            await browser.close()

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_doubao_with_playwright())
