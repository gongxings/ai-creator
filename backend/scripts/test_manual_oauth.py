"""
测试手动添加 OAuth 账号（qianwen 平台）
"""
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.oauth.oauth_service import oauth_service
from loguru import logger


def test_manual_oauth():
    """测试手动添加 OAuth 账号"""
    
    # 测试用的 Cookie
    test_cookies = {
        "tongyi_sso_ticket": "eYV*trtMUHEnF6AFvL_vsYhJBESvBCIVyBREsOWlURSV06Ys0x40jVkgVXAPGpXc0",
        "UM_distinctid": "19abe1ff58b10a-0b0a5c3321b9af8-26061b51-e1000-19abe1ff58c972",
        "cna": "lVytIcBAGUwCAW/NUgTbkZt/",
        "xlly_s": "1",
        "_qk_bx_um_v1": "eyJ1ZCI6IlQyZ0E2SmdiSXM1R0trLXpkQ0hqYlpfWURqbDJZbnRld2hJaHlFRFNLRmV6UGJoM3pSODB2b3ZpZEVxOXBMcUxCdzg9IiwiZXAiOjE3NzAzODczMjIxMjR9",
        "_ON_EXT_DVIDN": "eCy#AAOH4SK1lcC6xninXc6/wb67k9LhazE4Pb6xQop2CWPZB+aZWDug12u1od9WtPS9fk4=",
        "_qk_bx_ck_v1": "eyJkZXZpY2VJZCI6ImVDeSNBQU9INFNLMWxjQzZ4bmluWGM2L3diNjdrOUxoYXpFNFBiNnhRb3AyQ1dQWkIrYVpXRHVnMTJ1MW9kOVd0UFM5Zms0PSIsImRldmljZUZpbmdlcnByaW50IjoiM2VmNmJlMjlhMGNiMDZkMjI0YmUxN2UyODNiNGNjZDQifQ==",
        "tfstk": "ghzxlV6I7TXDymb5pEjls0MZTpCoWgV4P-PBSADDf8e8OWJmfmqmWlFQpcm13q4TeRwfgF0j5LitsjUDhtlXWbwnOd9s1n9SPX29515ZGYgSgRpXljaT4FFU_rfqSsu4gVu1K9b3WSPq75mDjhUvF4GUNjGscg07KHMaJ9bh-SSjgVV5KofcvMlt1VGjhji5wfGv5VisG71-1fvXfEw_N_Hr6f9jhVOSVXlnCVg_C71-_YGj5mw_N_hZFAM92EH9Gv8T27oxE_sWyE84yjnxBFDXWXa6-cHQGYL1QPcvQvNjeFTtd_1ZE7FcHePouy2Kt-bWkJF_Tli8WL6KQzF7llNyHOGzf-0Sn2sXwq44Gki_RO-_pqetAriJ1E3SyAg-Ny1MYY4-nRaxV6YKj4anAqZl4tmikXe_u-d95JNutrozW9pSQocEPfUNOhHtfgo3-ypfspDKsn1Rwh-ZcbkzuL2jGIeZBbHha8-wb0hrwvfRwh-Zcbl-K_oybho-a",
        "isg": "BK-vfQWoGqMnEh483_eWuT11PsO5VAN2j8VU7ME6vJ4GEMcSzCZZxtSClgAub9vu",
    }
    
    db = SessionLocal()
    
    try:
        # 获取第一个用户用于测试
        user = db.query(User).first()
        
        if not user:
            logger.error("数据库中没有用户，请先创建用户")
            return
        
        logger.info(f"使用测试用户: {user.username} (ID: {user.id})")
        logger.info(f"测试平台: qianwen")
        logger.info(f"Cookie 数量: {len(test_cookies)}")
        logger.info(f"必需 Cookie tongyi_sso_ticket: {'✓' if 'tongyi_sso_ticket' in test_cookies else '✗'}")
        
        # 准备凭证
        credentials = {
            "cookies": test_cookies,
            "tokens": {},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        logger.info("\n开始创建 OAuth 账号...")
        
        # 调用服务创建账号
        account = oauth_service.create_or_update_account_with_credentials(
            db=db,
            user_id=user.id,
            platform="qianwen",
            account_name="通义千问测试账号",
            credentials=credentials,
        )
        
        logger.success(f"\n✅ 成功创建 OAuth 账号!")
        logger.info(f"  账号ID: {account.id}")
        logger.info(f"  平台: {account.platform}")
        logger.info(f"  账号名称: {account.account_name}")
        logger.info(f"  是否激活: {account.is_active}")
        logger.info(f"  是否过期: {account.is_expired}")
        logger.info(f"  配额使用: {account.quota_used}/{account.quota_limit}")
        logger.info(f"  创建时间: {account.created_at}")
        
    except Exception as e:
        logger.error(f"\n❌ 创建账号失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("开始测试 OAuth 手动账号创建")
    logger.info("=" * 60)
    test_manual_oauth()
    logger.info("=" * 60)
