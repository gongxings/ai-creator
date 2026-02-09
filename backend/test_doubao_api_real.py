# -*- coding: utf-8 -*-
"""
豆包 API 真实调用测试
从数据库 oauth_accounts 表中获取 Cookie 进行测试
"""
import sys
import io
import asyncio

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
sys.path.insert(0, 'D:\\workspace\\openstudy\\ai-creator\\backend')

from app.services.ai.doubao_service import DoubaoService
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials


from typing import Optional, Tuple, Dict


def get_doubao_cookies_from_db(user_id: Optional[int] = None) -> Tuple[Optional[Dict], Optional[OAuthAccount]]:
    """
    从数据库获取豆包 Cookie
    
    Args:
        user_id: 用户ID，如果为空则获取第一个可用的豆包账号
        
    Returns:
        (Cookie 字典, OAuthAccount 对象)，如果没有找到则返回 (None, None)
    """
    db = SessionLocal()
    try:
        query = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True,
            OAuthAccount.is_expired == False
        )
        
        if user_id:
            query = query.filter(OAuthAccount.user_id == user_id)
        
        # 按最后使用时间排序，优先使用最近使用的
        account = query.order_by(OAuthAccount.last_used_at.desc()).first()
        
        if not account:
            return None, None
        
        # 解密凭证
        credentials = decrypt_credentials(account.credentials)
        cookies = credentials.get("cookies", {})
        
        return cookies, account
        
    except Exception as e:
        print(f"获取 Cookie 失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        db.close()


async def test_with_real_cookie():
    """使用真实 Cookie 测试"""
    
    print("=" * 60)
    print("豆包 API 真实调用测试")
    print("=" * 60)
    
    # 从数据库获取 Cookie
    print("\n正在从数据库获取豆包账号...")
    cookies, account = get_doubao_cookies_from_db()
    
    if not cookies or not account:
        print("\n❌ 错误: 未找到可用的豆包账号!")
        print("\n📝 请先添加豆包账号:")
        print("  方法 1: 通过前端页面添加")
        print("    - 访问前端应用")
        print("    - 进入账号管理页面")
        print("    - 添加豆包 OAuth 账号")
        print("\n  方法 2: 通过 API 添加")
        print("    POST /v1/oauth/accounts")
        print("    {")
        print('      "platform": "doubao",')
        print('      "cookies": {')
        print('        "sessionid": "your_sessionid",')
        print('        "sessionid_ss": "your_sessionid_ss"')
        print("      }")
        print("    }")
        print("\n  方法 3: 直接在脚本中填写（临时测试）")
        print("    取消下面的注释并填入真实 Cookie:")
        print("    # REAL_COOKIES = {")
        print('    #   "sessionid": "your_sessionid",')
        print('    #   "sessionid_ss": "your_sessionid_ss",')
        print("    # }")
        print("    # cookies = REAL_COOKIES")
        return
    
    print(f"\n✓ 已从数据库获取豆包账号")
    print(f"  账号 ID: {account.id}")
    print(f"  用户 ID: {account.user_id}")
    print(f"  账号名称: {account.account_name or '(未命名)'}")
    print(f"  已使用次数: {account.quota_used}")
    print(f"  Cookie 数量: {len(cookies)}")
    print(f"  sessionid: {cookies.get('sessionid', '')[:20]}...")
    
    REAL_COOKIES = cookies
    
    # 创建服务实例
    print("\n创建 DoubaoService 实例...")
    service = DoubaoService(cookies=REAL_COOKIES)
    print(f"✓ 服务创建成功")
    
    # 验证 Cookie
    print("\n验证 Cookie 有效性...")
    try:
        is_valid = await service.validate_cookies()
        if is_valid:
            print("✓ Cookie 验证成功")
        else:
            print("✗ Cookie 验证失败，可能已过期")
            print("  请重新获取 Cookie")
            return
    except Exception as e:
        print(f"✗ Cookie 验证出错: {e}")
        return
    
    # 测试文本生成
    print("\n" + "=" * 60)
    print("测试 1: 简单文本生成")
    print("=" * 60)
    
    test_prompts = [
        "用一句话介绍人工智能",
        "写一个关于春天的俳句",
        "列出学习编程的5个建议",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n测试 {i}/{len(test_prompts)}")
        print(f"提示词: {prompt}")
        print(f"正在调用 API...")
        
        try:
            result = await service.generate_text(prompt=prompt)
            
            print(f"✓ 调用成功！")
            print(f"响应长度: {len(result)} 字符")
            print(f"响应内容:")
            print("-" * 50)
            print(result)
            print("-" * 50)
            
            # 等待一下，避免请求过快
            if i < len(test_prompts):
                print("\n等待 2 秒后继续...")
                await asyncio.sleep(2)
            
        except ValueError as e:
            print(f"✗ 调用失败: {e}")
            if "Cookie已过期" in str(e):
                print("  提示: 请重新获取 Cookie")
                break
            elif "豆包API请求错误" in str(e) or "豆包API错误" in str(e):
                print("  提示: API 返回了错误，详细信息见上方日志")
                break
        except Exception as e:
            print(f"✗ 发生意外错误: {e}")
            import traceback
            traceback.print_exc()
            break
    
    # 测试写作场景
    print("\n\n" + "=" * 60)
    print("测试 2: 写作场景测试")
    print("=" * 60)
    
    writing_prompt = """你是一位专业的微信公众号文章写手。请根据以下信息创作一篇高质量的公众号文章：

主题：人工智能的未来
关键词：AI,机器学习,深度学习
目标读者：科技爱好者
文章风格：轻松活泼

要求：
1. 标题吸引人，包含关键词
2. 开头引人入胜，快速抓住读者注意力
3. 内容结构清晰，使用小标题分段
4. 语言生动有趣，贴近读者
5. 适当使用emoji表情
6. 结尾有互动引导（点赞、转发、评论）
7. 字数控制在500-800字（简短版本）

请直接输出文章内容，包含标题。"""
    
    print(f"\n提示词: (写作场景 - 公众号文章)")
    print(f"正在调用 API...")
    
    try:
        result = await service.generate_text(prompt=writing_prompt)
        
        print(f"\n✓ 调用成功！")
        print(f"响应长度: {len(result)} 字符")
        print(f"响应内容:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 调用失败: {e}")
    
    print("\n\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n✅ 测试总结:")
    print("  如果所有测试都成功，说明：")
    print("  1. Cookie 有效")
    print("  2. DoubaoService 工作正常")
    print("  3. API 请求格式正确")
    print("  4. 可以正常生成文本内容")
    
    print("\n📝 下一步:")
    print("  您现在可以通过前端或 API 测试完整的写作功能")
    print("  使用路径: POST /v1/writing/generate")
    print("  请求体示例:")
    print('  {')
    print('    "tool_type": "wechat_article",')
    print('    "parameters": {')
    print('      "topic": "人工智能"')
    print('    },')
    print('    "platform": "doubao"')
    print('  }')


if __name__ == "__main__":
    asyncio.run(test_with_real_cookie())
