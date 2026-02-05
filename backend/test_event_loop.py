# -*- coding: utf-8 -*-
"""
测试事件循环策略和Playwright
"""
import sys
import asyncio

# Windows平台：在导入任何其他模块之前设置事件循环策略
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_event_loop():
    """测试事件循环"""
    print(f"[EVENT LOOP TYPE] {asyncio.get_event_loop().__class__.__name__}")
    print(f"[EVENT LOOP POLICY] {asyncio.get_event_loop_policy().__class__.__name__}")
    
    # 测试subprocess
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        print("[SUBPROCESS TEST] Success")
        print(f"[PYTHON VERSION] {stdout.decode().strip()}")
    except NotImplementedError as e:
        print(f"[SUBPROCESS TEST] Failed: {e}")
    
    # 测试Playwright
    try:
        from playwright.async_api import async_playwright
        print("\n[PLAYWRIGHT TEST] Starting...")
        
        async with async_playwright() as p:
            # 只测试启动，不创建浏览器
            print("[PLAYWRIGHT TEST] Started successfully")
    except Exception as e:
        print(f"[PLAYWRIGHT TEST] Failed: {e}")

if __name__ == "__main__":
    print(f"[PLATFORM] {sys.platform}")
    print(f"[PYTHON VERSION] {sys.version}\n")
    
    asyncio.run(test_event_loop())