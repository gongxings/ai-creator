"""
文章模板数据模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class ArticleTemplate(Base):
    """文章模板表"""
    __tablename__ = "article_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="模板ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(String(500), comment="模板描述")
    thumbnail = Column(String(500), comment="缩略图URL")

    # 样式配置 (JSON)
    # 包含: container, h1, h2, h3, p, blockquote, ul, ol, li, code, pre, img, a, hr
    styles = Column(JSON, nullable=False, comment="样式配置")

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
        return f"<ArticleTemplate(id={self.id}, name={self.name}, is_system={self.is_system})>"
