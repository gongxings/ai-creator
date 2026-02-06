"""
添加新版通义千问 (chatqwen) 平台配置
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.platform_config import PlatformConfig
from loguru import logger


def add_chatqwen_platform():
    """添加 chatqwen 平台配置"""
    db = SessionLocal()
    
    try:
        # 创建所有表（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        # 检查是否已存在 chatqwen 平台
        existing = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == "chatqwen"
        ).first()
        
        if existing:
            logger.info("chatqwen 平台配置已存在，跳过添加")
            return
        
        # 创建新平台配置
        platform = PlatformConfig(
            platform_id="chatqwen",
            platform_name="通义千问(新版)",
            platform_icon="https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1O0zuCC7osS_!!6000000001644-55-tps-83-82.svg",
            priority=1,
            oauth_config={
                "auth_url": "https://chat.qwen.ai/",
                "login_selectors": {
                    "login_button": "button:has-text('登录')",
                    "scan_qr": ".qrcode-container",
                },
                "cookie_names": ["login_aliyunid_ticket", "t"],
            },
            litellm_config={
                "provider": "qwen_web",
                "api_base": "https://chat.qwen.ai/api/chat",
                "default_model": "qwen-turbo",
                "available_models": [
                    "qwen-turbo",
                    "qwen-plus",
                    "qwen-max",
                ],
            },
            quota_config={
                "daily_limit": 1000000,
                "rate_limit": 60,
            },
            is_enabled=True,
        )
        
        db.add(platform)
        db.commit()
        
        logger.info("成功添加 chatqwen 平台配置")
        logger.info(f"  平台名称: {platform.platform_name}")
        logger.info(f"  平台ID: {platform.platform_id}")
        logger.info(f"  登录URL: https://chat.qwen.ai/")
        
    except Exception as e:
        logger.error(f"添加 chatqwen 平台配置失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("开始添加 chatqwen 平台配置...")
    add_chatqwen_platform()
    logger.info("完成")
