"""
插件系统模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text, JSON, Boolean, DECIMAL, Index
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.user import User
from app.models.creation import Creation


class PluginMarket(Base):
    """插件市场表 - 预置插件元数据"""
    __tablename__ = "plugin_market"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="插件ID")
    name = Column(String(100), unique=True, nullable=False, index=True, comment="插件唯一标识符")
    display_name = Column(String(200), nullable=False, comment="显示名称")
    description = Column(Text, comment="详细描述")
    short_description = Column(String(500), comment="简短描述")
    version = Column(String(50), default="1.0.0", comment="版本号")
    author = Column(String(100), default="AI Creator", comment="作者/组织")
    author_url = Column(String(500), comment="作者链接")
    category = Column(String(50), nullable=False, index=True, comment="分类：writing, search, media, utility")
    icon = Column(String(100), comment="图标（emoji或图标名称）")
    icon_url = Column(String(500), comment="图标URL")
    screenshot_urls = Column(JSON, comment="截图展示 URL 列表")
    tags = Column(JSON, comment="标签列表")

    is_official = Column(Boolean, default=True, comment="是否官方插件")
    is_approved = Column(Boolean, default=True, comment="是否审核通过")
    is_active = Column(Boolean, default=True, index=True, comment="是否可用")

    download_count = Column(Integer, default=0, comment="安装次数")
    rating = Column(DECIMAL(3, 2), default=0, comment="评分（0-5）")
    review_count = Column(Integer, default=0, comment="评价数")

    config_schema = Column(JSON, comment="配置参数 JSON Schema")
    parameters_schema = Column(JSON, comment="插件参数 Schema（OpenAI function format）")
    entry_point = Column(String(200), nullable=False, comment="Python入口路径")
    requirements = Column(JSON, comment="依赖要求")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联 - 使用 primaryjoin 替代外键
    user_plugins = relationship(
        "UserPlugin",
        back_populates="plugin_market",
        primaryjoin="PluginMarket.name == UserPlugin.plugin_name",
        cascade="all, delete-orphan"
    )
    reviews = relationship(
        "PluginReview",
        back_populates="plugin_market",
        primaryjoin="PluginMarket.name == PluginReview.plugin_name",
        cascade="all, delete-orphan"
    )


class UserPlugin(Base):
    """用户已安装插件表"""
    __tablename__ = "user_plugins"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    plugin_name = Column(String(100), nullable=False, comment="插件名称")

    is_enabled = Column(Boolean, default=True, comment="用户是否启用")
    config = Column(JSON, comment="用户配置（API key、参数等）")
    is_auto_use = Column(Boolean, default=False, comment="是否自动加入创作")

    usage_count = Column(Integer, default=0, comment="使用次数")
    last_used_at = Column(DateTime, comment="最后使用时间")

    installed_at = Column(DateTime, server_default=func.now(), comment="安装时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联 - 使用 primaryjoin 替代外键
    user = relationship(
        "User",
        back_populates="plugins",
        primaryjoin="UserPlugin.user_id == foreign('User.id')",
        remote_side="User.id",
        viewonly=True
    )


plugin_market = relationship(
    "PluginMarket",
    back_populates="user_plugins",
    primaryjoin="UserPlugin.plugin_name == PluginMarket.name",
    viewonly=True
)

__table_args__ = (
    Index("uk_user_plugin", "user_id", "plugin_name", unique=True),
)


class CreationPluginSelection(Base):
    """用户创作插件选择记录表（按创作类型记忆）"""
    __tablename__ = "creation_plugin_selections"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    tool_type = Column(String(50), nullable=False, comment="写作类型（wechat_article等）")
    selected_plugins = Column(JSON, nullable=False, comment="选择的插件列表")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联 - 使用 primaryjoin 替代外键
    user = relationship(
        "User",
        back_populates="plugin_selections",
        primaryjoin="CreationPluginSelection.user_id == foreign('User.id')",
        remote_side="User.id",
        viewonly=True
    )


__table_args__ = (
    Index("uk_user_tool", "user_id", "tool_type", unique=True),
)


class PluginInvocation(Base):
    """插件调用日志表"""
    __tablename__ = "plugin_invocations"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    creation_id = Column(BigInteger, index=True, comment="关联创作记录")
    plugin_name = Column(String(100), nullable=False, index=True, comment="调用的插件")

    arguments = Column(JSON, comment="调用参数")
    result = Column(JSON, comment="返回结果")
    error = Column(Text, comment="错误信息")
    duration_ms = Column(Integer, comment="执行耗时（毫秒）")

    invoked_at = Column(DateTime, server_default=func.now(), comment="调用时间")

    # 关联 - 使用 primaryjoin 替代外键
    user = relationship(
        "User",
        back_populates="plugin_invocations",
        primaryjoin="PluginInvocation.user_id == foreign('User.id')",
        remote_side="User.id",
        viewonly=True
    )
    creation = relationship(
        "Creation",
        back_populates="plugin_invocations",
        primaryjoin="PluginInvocation.creation_id == foreign('Creation.id')",
        remote_side="Creation.id",
        viewonly=True
    )


__table_args__ = (
    Index("idx_user_plugin", "user_id", "plugin_name"),
)


class PluginReview(Base):
    """插件评价表"""
    __tablename__ = "plugin_reviews"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="评价ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    plugin_name = Column(String(100), nullable=False, comment="插件名称")

    rating = Column(Integer, nullable=False, comment="评分（1-5）")
    comment = Column(Text, comment="评论内容")

    created_at = Column(DateTime, server_default=func.now(), comment="评价时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联 - 使用 primaryjoin 替代外键
    user = relationship(
        "User",
        back_populates="plugin_reviews",
        primaryjoin="PluginReview.user_id == foreign('User.id')",
        remote_side="User.id",
        viewonly=True
    )


plugin_market = relationship(
    "PluginMarket",
    back_populates="reviews",
    primaryjoin="PluginReview.plugin_name == PluginMarket.name",
    viewonly=True
)

__table_args__ = (
    Index("uk_user_plugin_review", "user_id", "plugin_name", unique=True),
)
