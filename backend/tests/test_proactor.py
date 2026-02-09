# -*- coding: utf-8 -*-
"""
使用ProactorEventLoop + nest_asyncio的解决方案
"""
import sys

# 导入nest_asyncio以支持嵌套事件循环
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("[WARNING] nest_asyncio not installed, install with: pip install nest_asyncio")
    pass

import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    """测试Playwright"""
    print(f"[EVENT LOOP TYPE] {asyncio.get_event_loop().__class__.__name__}")
    print(f"[EVENT LOOP POLICY] {asyncio.get_event_loop_policy().__class__.__name__}")
    
    try:
        async with async_playwright() as p:
            print("\n[PLAYWRIGHT] Starting...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            print("[PLAYWRIGHT] Browser launched successfully!")
            await browser.close()
            print("[PLAYWRIGHT] Browser closed successfully!")
    except Exception as e:
        print(f"[PLAYWRIGHT] Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"[PLATFORM] {sys.platform}")
    print(f"[PYTHON] {sys.version}\n")
    
    # 使用asyncio.run()创建新的事件循环
    asyncio.run(test_playwright())