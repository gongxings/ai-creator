"""
修复后的图片生成处理函数
"""
import logging
from sqlalchemy.orm import Session
from app.models.creation import Creation

logger = logging.getLogger(__name__)

# Background task processing functions
async def process_image_generation(db: Session, creation_id: int, request_data: dict):
    """后台处理图片生成任务"""
    try:
        from app.models.oauth_account import OAuthAccount
        from app.models.platform_config import PlatformConfig
        from app.services.oauth.adapters import PLATFORM_ADAPTERS

        logger.info(f"Starting image generation for creation {creation_id}")
        logger.info(f"Request data: {request_data}")

        creation = db.query(Creation).filter(Creation.id == creation_id).first()

        if not creation:
            logger.error(f"Creation {creation_id} not found")
            return

        logger.info(f"Creation found: user_id={creation.user_id}, status={creation.status}")

        # 获取用户可用的 OAuth 账号
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == "doubao"
        ).first()

        if not platform_config:
            logger.error("Doubao platform config not found")
            raise ValueError("平台配置未找到")

        logger.info(f"Platform config found: {platform_config.platform_id}")

        # 获取用户的豆包 OAuth 账号
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == creation.user_id,
            OAuthAccount.platform == "doubao",
            OAuthAccount.is_active == True,
            OAuthAccount.is_expired == False
        ).first()

        if not oauth_account:
            logger.error(f"No active OAuth account for user {creation.user_id}")
            # 标记任务失败
            creation.status = "failed"
            creation.error_message = "未找到有效的豆包 OAuth 账号"
            creation.output_data = {"error": "未找到有效的豆包 OAuth 账号"}
            db.commit()
            return

        logger.info(f"OAuth account found: {oauth_account.id}, name={oauth_account.account_name}")
        logger.info(f"Account created_at: {oauth_account.created_at}")
        logger.info(f"Account expired status: {oauth_account.is_expired}")

        # 解密凭证
        from app.services.oauth.encryption import decrypt_credentials
        try:
            credentials = decrypt_credentials(str(oauth_account.credentials))
            cookies = credentials.get("cookies", {})
            logger.info(f"Cookies decrypted: {list(cookies.keys())} cookies")
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            # 标记任务失败
            creation.status = "failed"
            creation.error_message = f"解密凭证失败: {str(e)}"
            creation.output_data = {"error": f"解密凭证失败: {str(e)}"}
            db.commit()
            return

        # 获取豆包适配器
        adapter_class = PLATFORM_ADAPTERS.get("doubao")
        if not adapter_class:
            logger.error("Doubao adapter not found")
            raise ValueError("平台适配器未找到")

        adapter = adapter_class("doubao", {
            "oauth_config": platform_config.oauth_config or {},
            "litellm_config": platform_config.litellm_config or {},
            "quota_config": platform_config.quota_config or {},
        })

        # 调用图片生成
        prompt = request_data.get("prompt", "")
        negative_prompt = request_data.get("negative_prompt")
        style = request_data.get("style")
        size = f"{request_data.get('width', 1024)}x{request_data.get('height', 1024)}"

        logger.info(f"Generating image with doubao adapter: prompt={prompt}, size={size}")

        result = await adapter.generate_image(
            prompt=prompt,
            cookies=cookies,
            negative_prompt=negative_prompt,
            style=style,
            size=size
        )

        logger.info(f"Image generation result: {result}")

        # 处理结果
        if "error" in result:
            error_msg = result.get("error", "图片生成失败")
            logger.error(f"Image generation error: {error_msg}")
            raise ValueError(error_msg)

        images = result.get("images", [])
        logger.info(f"Generated {len(images)} images: {images}")

        if not images:
            logger.error("No images generated")
            raise ValueError("未生成任何图片")

        # 更新创作记录
        creation.status = "completed"
        creation.output_data = {"images": images}
        creation.error_message = None
        db.commit()

        logger.info(f"Image generation completed for creation {creation_id}, {len(images)} images generated")

    except ValueError as e:
        logger.error(f"Image generation failed: {e}")
        # 标记任务失败
        creation = db.query(Creation).filter(Creation.id == creation_id).first()
        if creation:
            creation.status = "failed"
            creation.error_message = str(e)
            creation.output_data = {"error": str(e)}
            db.commit()
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # 标记任务失败
        try:
            creation = db.query(Creation).filter(Creation.id == creation_id).first()
            if creation:
                creation.status = "failed"
                creation.error_message = str(e)
                creation.output_data = {"error": str(e)}
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update creation status: {db_error}")
