"""
内容模板数据模型 - 支持多平台模板
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class ContentTemplate(Base):
    """内容模板表 - 支持多平台（公众号、小红书、头条、PPT等）"""
    __tablename__ = "content_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="模板ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(String(500), comment="模板描述")
    thumbnail = Column(String(500), comment="缩略图URL")

    # 平台分类维度
    platform = Column(String(20), nullable=False, index=True, comment="平台类型：wechat/xiaohongshu/toutiao/ppt/douyin")
    category = Column(String(50), index=True, comment="场景分类：emotion/knowledge/marketing/news等")
    style = Column(String(50), index=True, comment="风格类型：文艺/活泼/专业/简约等")

    # 样式配置 (JSON)
    # 包含: container, h1, h2, h3, p, blockquote, ul, ol, li, code, pre, img, a, hr
    styles = Column(JSON, nullable=False, comment="样式配置")

    # 格式规范 (JSON) - 平台特有的格式要求
    # 如：标题长度、段落长度、emoji密度、标签数量等
    format_rules = Column(JSON, comment="平台格式规范")

    # AI提示词 - 针对该模板优化的生成提示词
    ai_prompt = Column(Text, comment="AI生成提示词")

    # 内容结构 (JSON) - 该模板的内容结构定义
    content_structure = Column(JSON, comment="内容结构定义")

    # PPT专用字段
    file_path = Column(String(500), comment="PPTX原始文件路径")
    ppt_layout = Column(JSON, comment="PPTist布局数据（JSON格式）")

    # 模板类型
    is_system = Column(Boolean, default=False, index=True, comment="是否系统预设")
    is_public = Column(Boolean, default=False, index=True, comment="是否公开")

    # 所有者（系统模板为NULL）
    # 注意：移除了 ForeignKey 约束以避免数据库权限问题，应用层会校验 user_id 的有效性
    user_id = Column(
        BigInteger,
        nullable=True,
        index=True,
        comment="用户ID（自定义模板的所有者）"
    )

    # 统计
    use_count = Column(Integer, default=0, comment="使用次数")

    # 时间戳
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    def __repr__(self):
        return f"<ContentTemplate(id={self.id}, name={self.name}, platform={self.platform}, is_system={self.is_system})>"


# 保持向后兼容的别名
ArticleTemplate = ContentTemplate
