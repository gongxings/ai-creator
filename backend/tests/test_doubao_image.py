"""
测试豆包图片生成 API
"""
import asyncio
import logging
from app.core.database import SessionLocal
from app.models.oauth_account import OAuthAccount
from app.services.oauth.encryption import decrypt_credentials
from app.services.oauth.adapters.doubao import DoubaoAdapter

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_doubao_image_generation():
    """测试豆包图片生成"""
    db = SessionLocal()
    try:
        # 查询豆包账号
        account = db.query(OAuthAccount).filter(
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True
        ).first()

        if not account:
            print("未找到豆包账号")
            return

        print(f"找到账号: ID={account.id}, Name={account.account_name}, Active={account.is_active}, Expired={account.is_expired}")
        print(f"凭证类型: {type(account.credentials)}, 长度: {len(str(account.credentials))}")

        # 解密凭证
        try:
            credentials = decrypt_credentials(account.credentials)
            print(f"解密成功: {list(credentials.keys())}")

            cookies = credentials.get("cookies", {})
            print(f"Cookies: {list(cookies.keys())}")
            for key, value in cookies.items():
                print(f"  {key}: {value[:50]}..." if len(value) > 50 else f"  {key}: {value}")

        except Exception as e:
            print(f"解密失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 创建适配器并测试图片生成
        adapter = DoubaoAdapter("doubao", {
            "oauth_config": {},
            "litellm_config": {},
            "quota_config": {},
        })

        print("\n开始测试图片生成...")
        result = await adapter.generate_image(
            prompt="一只可爱的猫咪",
            cookies=cookies,
            style="卡通风格",
            size="1024x1024"
        )

        print(f"\n图片生成结果: {result}")

        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            images = result.get("images", [])
            print(f"生成图片数量: {len(images)}")
            for i, img_url in enumerate(images):
                print(f"  图片 {i+1}: {img_url}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_doubao_image_generation())
