#!/usr/bin/env python3
"""
检查平台登录后的 localStorage 键
用于配置登录检测逻辑

使用方法:
    python scripts/check_platform_login_keys.py <platform_url>

示例:
    python scripts/check_platform_login_keys.py https://www.doubao.com/
    python scripts/check_platform_login_keys.py https://jimeng.jianying.com/
"""

import asyncio
import sys
from playwright.async_api import async_playwright


async def check_platform_keys(url: str, timeout: int = 60):
    """
    打开平台页面，等待用户手动登录，然后显示 localStorage 键值
    
    Args:
        url: 平台 URL
        timeout: 等待超时时间（秒）
    """
    print(f"正在检查平台: {url}")
    print(f"等待时间: {timeout} 秒")
    print("-" * 60)
    
    async with async_playwright() as p:
        # 启动浏览器（非 headless 模式，让用户可以手动登录）
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        page = await context.new_page()
        
        # 打开页面
        await page.goto(url)
        print(f"✓ 已打开页面: {url}")
        print("\n请在浏览器中完成登录...")
        print("(支持扫码登录或账号密码登录)\n")
        
        # 记录登录前的 localStorage 键
        await asyncio.sleep(3)
        initial_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
        initial_keys = set(initial_storage.keys())
        print(f"登录前 localStorage 键数量: {len(initial_keys)}")
        if initial_keys:
            print(f"登录前的键: {sorted(initial_keys)}\n")
        
        # 轮询检测登录状态
        check_interval = 2
        elapsed = 0
        logged_in = False
        
        while elapsed < timeout:
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            try:
                # 获取当前 localStorage
                current_storage = await page.evaluate("() => Object.assign({}, window.localStorage)")
                current_keys = set(current_storage.keys())
                
                # 检查是否有新增或变化的键
                new_keys = current_keys - initial_keys
                changed_keys = []
                
                for key in initial_keys & current_keys:
                    if initial_storage.get(key) != current_storage.get(key):
                        changed_keys.append(key)
                
                # 如果有新增或变化的键，可能登录成功了
                if new_keys or changed_keys:
                    logged_in = True
                    print("=" * 60)
                    print("检测到 localStorage 变化，可能已登录！")
                    print("=" * 60)
                    
                    if new_keys:
                        print(f"\n新增的键 ({len(new_keys)} 个):")
                        for key in sorted(new_keys):
                            value = current_storage.get(key, "")
                            # 截断长值
                            display_value = value[:100] + "..." if len(str(value)) > 100 else value
                            print(f"  - {key}: {display_value}")
                    
                    if changed_keys:
                        print(f"\n值发生变化的键 ({len(changed_keys)} 个):")
                        for key in sorted(changed_keys):
                            old_value = initial_storage.get(key, "")
                            new_value = current_storage.get(key, "")
                            print(f"  - {key}:")
                            print(f"      旧值: {str(old_value)[:80]}")
                            print(f"      新值: {str(new_value)[:80]}")
                    
                    # 显示所有 localStorage 键
                    print(f"\n当前所有 localStorage 键 ({len(current_keys)} 个):")
                    for key in sorted(current_keys):
                        print(f"  - {key}")
                    
                    # 检查 Cookie
                    cookies = await context.cookies()
                    print(f"\n当前 Cookie 数量: {len(cookies)}")
                    print("Cookie 名称:")
                    for cookie in sorted(cookies, key=lambda c: c.get('name', '')):
                        print(f"  - {cookie.get('name')}")
                    
                    break
                
                # 显示进度
                if elapsed % 10 == 0:
                    print(f"等待中... ({elapsed}/{timeout} 秒)")
            
            except Exception as e:
                print(f"错误: {e}")
        
        if not logged_in:
            print(f"\n超时 ({timeout} 秒)，未检测到登录。")
            print("请确保在浏览器中完成了登录操作。")
        else:
            print("\n" + "=" * 60)
            print("建议配置:")
            print("=" * 60)
            
            # 分析哪些键可能是登录标识
            potential_login_keys = []
            for key in new_keys | set(changed_keys):
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in ['user', 'login', 'auth', 'token', 'session', 'uid', 'passport']):
                    potential_login_keys.append(key)
            
            if potential_login_keys:
                print("\n可能的登录标识键:")
                for key in potential_login_keys:
                    print(f"  '{key}',")
                
                print("\n将这些键添加到 playwright_service.py 的 login_keys 列表中:")
                print("```python")
                print("login_keys = [")
                print("    'user_info', 'token', 'auth', 'session', 'user', 'userId', 'userInfo',")
                print("    'flow_web_has_login',  # 即梦平台")
                print("    'uid', 'passport_user',  # 豆包平台")
                for key in potential_login_keys:
                    print(f"    '{key}',  # {url}")
                print("]")
                print("```")
        
        print("\n按任意键关闭浏览器...")
        await asyncio.sleep(5)
        
        await browser.close()


def main():
    if len(sys.argv) < 2:
        print("使用方法: python check_platform_login_keys.py <platform_url>")
        print("\n示例:")
        print("  python check_platform_login_keys.py https://www.doubao.com/")
        print("  python check_platform_login_keys.py https://jimeng.jianying.com/")
        print("  python check_platform_login_keys.py https://tongyi.aliyun.com/")
        print("  python check_platform_login_keys.py https://chatglm.cn/")
        print("  python check_platform_login_keys.py https://chat.deepseek.com/")
        sys.exit(1)
    
    url = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 120  # 默认 120 秒
    
    asyncio.run(check_platform_keys(url, timeout))


if __name__ == "__main__":
    main()
