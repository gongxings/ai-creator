"""
更新 qwen 平台配置到新地址 www.qianwen.com
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.platform_config import PlatformConfig
from loguru import logger


def update_qwen_platform():
    """更新 qwen 平台配置到新地址"""
    db = SessionLocal()
    
    try:
        # 查找 qwen 平台
        qwen_platform = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == "qwen"
        ).first()
        
        if not qwen_platform:
            logger.warning("qwen 平台配置不存在")
            return
        
        # 更新为新地址和新的 Cookie 要求
        qwen_platform.oauth_config = {
            "auth_url": "https://www.qianwen.com/",
            "login_selectors": {
                "login_button": "button:has-text('登录')",
                "scan_qr": ".qrcode-container",
            },
            "cookie_names": ["tongyi_sso_ticket"],
        }
        
        qwen_platform.litellm_config = {
            "provider": "qwen_web",
            "api_base": "https://www.qianwen.com/api/chat",
            "default_model": "qwen-turbo",
            "available_models": [
                "qwen-turbo",
                "qwen-plus",
                "qwen-max",
                "qwen-vl-max",
                "qwen2.5-72b",
            ],
        }
        
        db.commit()
        
        logger.info("成功更新 qwen 平台配置")
        logger.info(f"  平台名称: {qwen_platform.platform_name}")
        logger.info(f"  平台ID: {qwen_platform.platform_id}")
        logger.info(f"  新登录URL: https://www.qianwen.com/")
        logger.info(f"  必需Cookie: tongyi_sso_ticket")
        
    except Exception as e:
        logger.error(f"更新 qwen 平台配置失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("开始更新 qwen 平台配置...")
    update_qwen_platform()
    logger.info("完成")
