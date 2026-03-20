"""
流量统计模型
全埋点：页面访问 + 用户行为事件
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date, Boolean, Text, JSON
from datetime import datetime

from app.core.database import Base


class PageView(Base):
    """页面访问记录表"""
    __tablename__ = "page_views"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    path = Column(String(500), nullable=False, index=True, comment="访问路径")
    user_id = Column(BigInteger, index=True, comment="用户ID（可为空，未登录用户）")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="User-Agent")
    referer = Column(String(500), comment="来源页面")
    session_id = Column(String(100), index=True, comment="会话ID")
    # 新增字段：停留时长和滚动深度
    stay_duration = Column(Integer, default=0, comment="停留时长（秒）")
    max_scroll_depth = Column(Integer, default=0, comment="最大滚动深度（百分比0-100）")
    is_bounce = Column(Boolean, default=True, comment="是否跳出（单页访问）")
    screen_width = Column(Integer, comment="屏幕宽度")
    screen_height = Column(Integer, comment="屏幕高度")
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="访问时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<PageView(id={self.id}, path='{self.path}')>"


class UserEvent(Base):
    """用户行为事件表"""
    __tablename__ = "user_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    session_id = Column(String(100), nullable=False, index=True, comment="会话ID")
    user_id = Column(BigInteger, index=True, comment="用户ID")
    page_path = Column(String(500), index=True, comment="所在页面路径")
    event_type = Column(String(50), nullable=False, index=True, comment="事件类型: click/scroll/custom")
    event_name = Column(String(100), comment="事件名称: button_click/form_submit")
    event_target = Column(String(200), comment="目标元素: el-button.primary")
    event_data = Column(JSON, comment="附加数据（文字、ID、href等）")
    page_view_id = Column(BigInteger, index=True, comment="关联的PageView ID")
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="事件时间")

    def __repr__(self):
        return f"<UserEvent(id={self.id}, type='{self.event_type}', name='{self.event_name}')>"


class DailyStats(Base):
    """每日统计表"""
    __tablename__ = "daily_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    date = Column(Date, nullable=False, unique=True, index=True, comment="统计日期")
    pv = Column(Integer, default=0, comment="页面访问量")
    uv = Column(Integer, default=0, comment="独立访客数")
    new_users = Column(Integer, default=0, comment="新注册用户数")
    active_users = Column(Integer, default=0, comment="活跃用户数")
    total_requests = Column(Integer, default=0, comment="AI请求总数")
    avg_stay_duration = Column(Integer, default=0, comment="平均停留时长（秒）")
    avg_scroll_depth = Column(Integer, default=0, comment="平均滚动深度（百分比）")
    bounce_rate = Column(Integer, default=0, comment="跳出率（百分比）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<DailyStats(date={self.date}, pv={self.pv}, uv={self.uv})>"
