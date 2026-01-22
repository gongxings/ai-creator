"""
发布服务
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.publish import PublishRecord, PlatformAccount
from app.models.creation import Creation
from app.models.user import User
from app.services.publish.platforms import get_platform, PLATFORM_REGISTRY
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PublishService:
    """发布服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def publish_content(
        self,
        user: User,
        creation: Creation,
        platforms: List[str],
        publish_config: Optional[Dict[str, Any]] = None,
        scheduled_time: Optional[datetime] = None
    ) -> List[PublishRecord]:
        """
        发布内容到多个平台
        
        Args:
            user: 用户对象
            creation: 创作内容
            platforms: 目标平台列表
            publish_config: 发布配置
            scheduled_time: 定时发布时间
            
        Returns:
            List[PublishRecord]: 发布记录列表
        """
        publish_records = []
        
        for platform_name in platforms:
            # 获取平台账号
            account = self.db.query(PlatformAccount).filter(
                PlatformAccount.user_id == user.id,
                PlatformAccount.platform == platform_name,
                PlatformAccount.status == "active"
            ).first()
            
            if not account:
                # 创建失败记录
                record = PublishRecord(
                    user_id=user.id,
                    creation_id=creation.id,
                    platform=platform_name,
                    status="failed",
                    error_message=f"未绑定{platform_name}平台账号"
                )
                self.db.add(record)
                publish_records.append(record)
                continue
            
            # 创建发布记录
            record = PublishRecord(
                user_id=user.id,
                creation_id=creation.id,
                platform=platform_name,
                platform_account_id=account.id,
                scheduled_time=scheduled_time,
                status="pending" if scheduled_time else "publishing"
            )
            self.db.add(record)
            self.db.flush()
            
            # 如果是定时发布，不立即执行
            if scheduled_time:
                publish_records.append(record)
                continue
            
            # 立即发布
            try:
                # 获取平台实例
                platform = get_platform(platform_name)
                
                # 解析账号凭证
                credentials = json.loads(account.credentials)
                
                # 适配内容格式
                adapted_content = await self._adapt_content(
                    creation, platform_name, publish_config
                )
                
                # 执行发布
                result = await platform.publish_content(
                    content=adapted_content.get("content", creation.content),
                    title=adapted_content.get("title", creation.title),
                    credentials=credentials,
                    images=adapted_content.get("images"),
                    video_url=adapted_content.get("video_url"),
                    cover_url=adapted_content.get("cover_url"),
                    **adapted_content.get("extra", {})
                )
                
                # 更新记录
                record.status = "success"
                record.platform_post_id = result.get("article_id") or result.get("note_id") or result.get("item_id")
                record.platform_url = result.get("article_url") or result.get("note_url") or result.get("share_url")
                record.published_at = datetime.now()
                
            except Exception as e:
                logger.error(f"发布到{platform_name}失败: {str(e)}")
                record.status = "failed"
                record.error_message = str(e)
            
            publish_records.append(record)
        
        self.db.commit()
        return publish_records
    
    async def _adapt_content(
        self,
        creation: Creation,
        platform: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        适配内容格式到目标平台
        
        Args:
            creation: 创作内容
            platform: 目标平台
            config: 发布配置
            
        Returns:
            Dict: 适配后的内容
        """
        content = creation.content
        title = creation.title
        
        # 平台特定适配
        if platform == "wechat":
            # 微信公众号：保持HTML格式，添加样式
            return {
                "title": title,
                "content": self._format_wechat_content(content),
                "extra": {
                    "thumb_media_id": config.get("thumb_media_id") if config else None,
                    "author": config.get("author") if config else None,
                    "digest": config.get("digest") if config else content[:100]
                }
            }
        
        elif platform == "xiaohongshu":
            # 小红书：添加话题标签，emoji优化
            return {
                "title": self._format_xiaohongshu_title(title),
                "content": self._format_xiaohongshu_content(content),
                "images": config.get("images", []) if config else [],
                "extra": {
                    "tags": config.get("tags", []) if config else [],
                    "location": config.get("location") if config else None
                }
            }
        
        elif platform in ["douyin", "kuaishou"]:
            # 抖音/快手：视频平台，需要视频文件
            return {
                "title": title[:30],  # 标题限制
                "content": content[:1000],  # 描述限制
                "video_url": config.get("video_url") if config else None,
                "cover_url": config.get("cover_url") if config else None,
                "extra": {
                    "poi_id": config.get("poi_id") if config else None,
                    "micro_app_id": config.get("micro_app_id") if config else None
                }
            }
        
        elif platform in ["toutiao", "baijiahao"]:
            # 今日头条/百家号：文章平台
            return {
                "title": title,
                "content": self._format_html_content(content),
                "extra": {
                    "category": config.get("category") if config else "其他",
                    "tags": config.get("tags", []) if config else [],
                    "cover_images": config.get("cover_images", []) if config else []
                }
            }
        
        elif platform in ["zhihu", "jianshu"]:
            # 知乎/简书：支持Markdown
            return {
                "title": title,
                "content": self._format_markdown_content(content),
                "extra": {
                    "topics": config.get("topics", []) if config else [],
                    "column_id": config.get("column_id") if config else None
                }
            }
        
        # 默认格式
        return {
            "title": title,
            "content": content,
            "extra": {}
        }
    
    def _format_wechat_content(self, content: str) -> str:
        """格式化微信公众号内容"""
        # 添加微信公众号样式
        styled_content = f"""
        <section style="font-size: 16px; line-height: 1.75; color: #333;">
            {content}
        </section>
        """
        return styled_content
    
    def _format_xiaohongshu_title(self, title: str) -> str:
        """格式化小红书标题"""
        # 添加emoji和符号
        if not any(char in title for char in ['✨', '💕', '🔥', '⭐']):
            title = f"✨ {title}"
        return title[:20]  # 小红书标题限制
    
    def _format_xiaohongshu_content(self, content: str) -> str:
        """格式化小红书内容"""
        # 添加分段和emoji
        lines = content.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip():
                formatted_lines.append(line)
                formatted_lines.append('')  # 添加空行
        return '\n'.join(formatted_lines)[:1000]  # 小红书内容限制
    
    def _format_html_content(self, content: str) -> str:
        """格式化HTML内容"""
        # 简单的Markdown转HTML
        html_content = content.replace('\n\n', '</p><p>')
        html_content = f"<p>{html_content}</p>"
        return html_content
    
    def _format_markdown_content(self, content: str) -> str:
        """格式化Markdown内容"""
        # 保持Markdown格式
        return content
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """
        获取支持的平台列表
        
        Returns:
            List[Dict]: 平台信息列表
        """
        platforms = []
        for platform_key, platform_class in PLATFORM_REGISTRY.items():
            platform_info = {
                "platform": platform_key,
                "name": self._get_platform_name(platform_key),
                "icon": self._get_platform_icon(platform_key),
                "description": f"发布到{self._get_platform_name(platform_key)}",
                "content_types": self._get_platform_content_types(platform_key)
            }
            platforms.append(platform_info)
        
        return platforms
    
    def _get_platform_name(self, platform: str) -> str:
        """获取平台中文名称"""
        names = {
            "wechat": "微信公众号",
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "kuaishou": "快手",
            "toutiao": "今日头条",
            "baijiahao": "百家号",
            "zhihu": "知乎",
            "jianshu": "简书"
        }
        return names.get(platform, platform)
    
    def _get_platform_icon(self, platform: str) -> str:
        """获取平台图标"""
        icons = {
            "wechat": "📱",
            "xiaohongshu": "📕",
            "douyin": "🎵",
            "kuaishou": "⚡",
            "toutiao": "📰",
            "baijiahao": "📝",
            "zhihu": "🎓",
            "jianshu": "✍️"
        }
        return icons.get(platform, "📄")
    
    def _get_platform_content_types(self, platform: str) -> List[str]:
        """获取平台支持的内容类型"""
        types = {
            "wechat": ["article"],
            "xiaohongshu": ["note", "image"],
            "douyin": ["video"],
            "kuaishou": ["video"],
            "toutiao": ["article"],
            "baijiahao": ["article"],
            "zhihu": ["article", "answer"],
            "jianshu": ["article"]
        }
        return types.get(platform, ["article"])
    
    async def bind_platform_account(
        self,
        user: User,
        platform: str,
        credentials: Dict[str, Any]
    ) -> PlatformAccount:
        """
        绑定平台账号
        
        Args:
            user: 用户对象
            platform: 平台名称
            credentials: 平台凭证
            
        Returns:
            PlatformAccount: 平台账号对象
        """
        # 验证平台凭证
        platform_instance = get_platform(platform)
        is_valid = await platform_instance.validate_credentials(credentials)
        
        if not is_valid:
            raise ValueError("平台凭证验证失败")
        
        # 检查是否已绑定
        existing_account = self.db.query(PlatformAccount).filter(
            PlatformAccount.user_id == user.id,
            PlatformAccount.platform == platform
        ).first()
        
        if existing_account:
            # 更新凭证
            existing_account.credentials = json.dumps(credentials, ensure_ascii=False)
            existing_account.status = "active"
            existing_account.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing_account)
            return existing_account
        
        # 创建新账号
        account = PlatformAccount(
            user_id=user.id,
            platform=platform,
            platform_user_id=credentials.get("user_id") or credentials.get("open_id"),
            platform_username=credentials.get("username") or credentials.get("nickname"),
            credentials=json.dumps(credentials, ensure_ascii=False),
            status="active"
        )
        
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_publish_history(
        self,
        user: User,
        platform: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[PublishRecord]:
        """
        获取发布历史
        
        Args:
            user: 用户对象
            platform: 平台筛选（可选）
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            List[PublishRecord]: 发布记录列表
        """
        query = self.db.query(PublishRecord).filter(
            PublishRecord.user_id == user.id
        )
        
        if platform:
            query = query.filter(PublishRecord.platform == platform)
        
        records = query.order_by(
            PublishRecord.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return records
    
    async def get_publish_status(
        self,
        record: PublishRecord
    ) -> str:
        """
        获取发布状态
        
        Args:
            record: 发布记录
            
        Returns:
            str: 状态
        """
        if record.status in ["success", "failed"]:
            return record.status
        
        try:
            # 获取平台实例
            platform = get_platform(record.platform)
            
            # 解析账号凭证
            if not record.platform_account:
                return "failed"
            
            credentials = json.loads(record.platform_account.credentials)
            
            # 查询发布状态
            status = await platform.get_publish_status(
                post_id=record.platform_post_id,
                credentials=credentials
            )
            
            # 更新记录
            if status != record.status:
                record.status = status
                self.db.commit()
            
            return status
            
        except Exception as e:
            logger.error(f"获取发布状态失败: {str(e)}")
            return record.status
