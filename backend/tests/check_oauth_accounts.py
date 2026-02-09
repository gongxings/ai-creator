# -*- coding: utf-8 -*-
"""
检查数据库中的 OAuth 账号
"""
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, '/backend')

from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials


def list_oauth_accounts():
    """列出所有 OAuth 账号"""
    
    print("=" * 60)
    print("OAuth 账号列表")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 查询所有账号
        accounts = db.query(OAuthAccount).order_by(OAuthAccount.created_at.desc()).all()
        
        if not accounts:
            print("\n未找到任何 OAuth 账号")
            print("\n请先通过以下方式添加账号:")
            print("  1. 前端页面 - 账号管理")
            print("  2. API 接口 - POST /v1/oauth/accounts")
            return
        
        print(f"\n总共找到 {len(accounts)} 个账号:\n")
        
        # 按平台分组
        by_platform = {}
        for account in accounts:
            platform = account.platform
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(account)
        
        # 显示每个平台的账号
        for platform, platform_accounts in by_platform.items():
            print(f"\n📱 平台: {platform.upper()}")
            print("-" * 60)
            
            for account in platform_accounts:
                status_icon = "✓" if account.is_active and not account.is_expired else "✗"
                status_text = "激活" if account.is_active else "禁用"
                if account.is_expired:
                    status_text = "已过期"
                
                print(f"{status_icon} ID: {account.id} | 用户: {account.user_id} | {status_text}")
                print(f"  名称: {account.account_name or '(未命名)'}")
                print(f"  使用: {account.quota_used}/{account.quota_limit or '无限'}")
                
                # 尝试解密并显示 Cookie 信息
                try:
                    credentials = decrypt_credentials(account.credentials)
                    cookies = credentials.get("cookies", {})
                    print(f"  Cookies: {len(cookies)} 个")
                    
                    # 显示主要的 Cookie 键（不显示值，保护隐私）
                    if cookies:
                        cookie_keys = list(cookies.keys())
                        print(f"  Cookie 键: {', '.join(cookie_keys[:5])}")
                        if len(cookie_keys) > 5:
                            print(f"           ... 还有 {len(cookie_keys) - 5} 个")
                    
                    # 对于豆包，显示 sessionid 前缀
                    if platform == "doubao" and "sessionid" in cookies:
                        sessionid = cookies["sessionid"]
                        print(f"  sessionid: {sessionid[:20]}...")
                        
                except Exception as e:
                    print(f"  ⚠️ 无法解密凭证: {e}")
                
                print(f"  创建时间: {account.created_at}")
                if account.last_used_at:
                    print(f"  最后使用: {account.last_used_at}")
                print()
        
        # 统计信息
        print("\n" + "=" * 60)
        print("统计信息")
        print("=" * 60)
        
        active_count = sum(1 for a in accounts if a.is_active and not a.is_expired)
        expired_count = sum(1 for a in accounts if a.is_expired)
        inactive_count = sum(1 for a in accounts if not a.is_active)
        
        print(f"激活账号: {active_count}")
        print(f"已过期: {expired_count}")
        print(f"已禁用: {inactive_count}")
        print(f"总计: {len(accounts)}")
        
        # 豆包账号特别提示
        doubao_active = len([a for a in by_platform.get("doubao", []) if a.is_active and not a.is_expired])
        if doubao_active > 0:
            print(f"\n✅ 找到 {doubao_active} 个可用的豆包账号，可以运行测试")
            print("   运行: python3 test_doubao_api_real.py")
        else:
            print(f"\n⚠️  没有可用的豆包账号")
            print("   请先添加豆包 OAuth 账号")
        
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    list_oauth_accounts()
