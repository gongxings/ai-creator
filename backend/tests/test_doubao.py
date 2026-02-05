"""
测试豆包 OAuth 账号是否可用
"""
import asyncio
import httpx
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials


async def test_doubao_account():
    """测试豆包账号"""
    db = SessionLocal()
    try:
        # 查询豆包账号
        account = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao"
        ).first()

        if not account:
            print("未找到豆包账号")
            return

        print(f"找到账号: ID={account.id}, Name={account.account_name}, Active={account.is_active}, Expired={account.is_expired}")

        # 更新账号状态为未过期
        account.is_expired = False
        db.commit()

        # 解密凭证
        credentials = decrypt_credentials(account.credentials)
        cookies = credentials.get("cookies", {})
        print(f"Cookies: {list(cookies.keys())}")

        # 测试访问豆包网站
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        headers = {
            "Cookie": cookie_str,
            "User-Agent": credentials.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            "Referer": "https://www.doubao.com/",
            "Origin": "https://www.doubao.com",
        }

        print("\n测试 1: 访问豆包首页")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get("https://www.doubao.com/", headers=headers, timeout=30)
            print(f"状态码: {response.status_code}")
            print(f"响应URL: {response.url}")

            # 检查是否需要登录
            content = response.text
            if "登录" in content and "请先登录" in content:
                print("需要登录 - 凭证可能已过期")
                account.is_expired = True
                db.commit()
            elif "user" in content.lower() or "console" in content.lower():
                print("已登录 - 凭证有效")
                account.is_expired = False
                db.commit()
            else:
                print("无法确定登录状态")
                # 检查是否有localStorage中的用户信息
                if "localStorage" in content or "userInfo" in content:
                    print("页面包含用户信息 - 可能已登录")
                    account.is_expired = False
                    db.commit()

        print("\n测试 2: 访问豆包聊天页面")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get("https://www.doubao.com/chat/", headers=headers, timeout=30)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                print("聊天页面访问成功 - 凭证有效")
                account.is_expired = False
                db.commit()
            else:
                print(f"聊天页面访问失败 - 状态码: {response.status_code}")

        print("\n测试 3: 检查账号状态")
        print(f"账号状态: Active={account.is_active}, Expired={account.is_expired}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_doubao_account())
