"""
流量统计模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date, func
from sqlalchemy.orm import relationship, foreign
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
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="访问时间")

    def __repr__(self):
        return f"<PageView(id={self.id}, path='{self.path}')>"


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
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<DailyStats(date={self.date}, pv={self.pv}, uv={self.uv})>"
