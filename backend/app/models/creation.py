"""
创作记录模型
"""
from sqlalchemy import Column, BigInteger, String, Enum, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.ai_model import AIModel
from app.models.user import User
import enum


class CreationType(str, enum.Enum):
    """创作类型枚举"""
    # 写作工具
    WECHAT_ARTICLE = "wechat_article"  # 公众号文章
    XIAOHONGSHU_NOTE = "xiaohongshu_note"  # 小红书笔记
    OFFICIAL_DOCUMENT = "official_document"  # 公文
    PAPER = "paper"  # 论文
    MARKETING_COPY = "marketing_copy"  # 营销文案
    NEWS_ARTICLE = "news_article"  # 新闻稿/软文
    VIDEO_SCRIPT = "video_script"  # 短视频脚本
    STORY = "story"  # 故事/小说
    BUSINESS_PLAN = "business_plan"  # 商业计划书
    WORK_REPORT = "work_report"  # 工作报告
    RESUME = "resume"  # 简历/求职信
    LESSON_PLAN = "lesson_plan"  # 教案/课件
    REWRITE = "rewrite"  # 改写/扩写/缩写
    TRANSLATION = "translation"  # 翻译

    # 其他创作类型
    IMAGE = "image"  # 图片生成
    VIDEO = "video"  # 视频生成
    PPT = "ppt"  # PPT生成


class CreationStatus(str, enum.Enum):
    """创作状态枚举"""
    PENDING = "pending"  # 等待中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class Creation(Base):
    """创作记录表"""
    __tablename__ = "creations"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="创作ID")
    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="用户ID"
    )

    creation_type = Column(
        Enum(CreationType),
        nullable=False,
        index=True,
        comment="创作类型"
    )

    tool_type = Column(String(50), index=True, comment="工具类型（细分类型）")
    task_id = Column(String(100), unique=True, index=True, comment="异步任务ID")

    title = Column(String(200), nullable=False, comment="标题")

    input_data = Column(JSON, comment="输入数据（JSON格式）")
    output_content = Column(Text, comment="输出内容")
    output_data = Column(JSON, comment="输出数据（JSON格式，用于图片/视频/PPT等）")

    model_id = Column(
        BigInteger,
        index=True,
        comment="使用的AI模型ID"
    )

    status = Column(
        Enum(CreationStatus),
        nullable=False,
        default=CreationStatus.PENDING,
        index=True,
        comment="创作状态"
    )

    error_message = Column(Text, comment="错误信息")

    tokens_used = Column(Integer, comment="使用的令牌数")
    generation_time = Column(Integer, comment="生成耗时（秒）")

    version_count = Column(Integer, nullable=False, default=1, comment="版本数量")
    current_version = Column(Integer, nullable=False, default=1, comment="当前版本")

    is_favorite = Column(Boolean, nullable=False, default=False, comment="是否收藏")

    # 多平台转换支持
    parent_id = Column(
        BigInteger,
        index=True,
        comment="父创作ID（用于多平台转换）"
    )
    source_platform = Column(String(50), comment="原始平台")

    # 配图支持
    cover_image = Column(String(500), comment="封面图URL")
    images = Column(JSON, comment="文章配图列表（JSON数组）")

    extra_data = Column(JSON, comment="额外数据（JSON格式）")

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    deleted_at = Column(DateTime, comment="删除时间（软删除）")

    # 关系（不使用外键，通过 primaryjoin 指定关联条件）
    user = relationship("User", back_populates="creations", primaryjoin="Creation.user_id == foreign('User.id')",
                        remote_side="User.id")
    model = relationship("AIModel", back_populates="creations",
                         primaryjoin="Creation.model_id == foreign('AIModel.id')", remote_side="AIModel.id")
    publish_records = relationship("PublishRecord", back_populates="creation",
                                   primaryjoin="Creation.id == foreign('PublishRecord.creation_id')")
    plugin_invocations = relationship("PluginInvocation", back_populates="creation",
                                      primaryjoin="Creation.id == foreign('PluginInvocation.creation_id')")

    def __repr__(self):
        return f"<Creation(id={self.id}, type={self.creation_type}, status={self.status})>"


class CreationVersion(Base):
    """创作版本表"""
    __tablename__ = "creation_versions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="版本ID")
    creation_id = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="创作ID"
    )

    version_number = Column(Integer, nullable=False, comment="版本号")
    content = Column(Text, nullable=False, comment="版本内容")

    change_description = Column(String(500), comment="变更描述")

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )

    # 关系
    creation = relationship("Creation", backref="versions",
                            primaryjoin="CreationVersion.creation_id == foreign('Creation.id')",
                            remote_side="Creation.id")

    def __repr__(self):
        return f"<CreationVersion(id={self.id}, creation_id={self.creation_id}, version={self.version_number})>"
