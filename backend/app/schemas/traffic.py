"""
流量统计 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class TrafficOverview(BaseModel):
    """流量概览"""
    today_pv: int = Field(0, description="今日PV")
    today_uv: int = Field(0, description="今日UV")
    today_new_users: int = Field(0, description="今日新用户")
    total_users: int = Field(0, description="总用户数")
    total_creations: int = Field(0, description="总创作数")
    week_pv: int = Field(0, description="本周PV")
    week_uv: int = Field(0, description="本周UV")
    month_pv: int = Field(0, description="本月PV")
    month_uv: int = Field(0, description="本月UV")


class DailyStatItem(BaseModel):
    """每日统计项"""
    date: str = Field(..., description="日期")
    pv: int = Field(0, description="页面访问量")
    uv: int = Field(0, description="独立访客数")
    new_users: int = Field(0, description="新注册用户数")
    active_users: int = Field(0, description="活跃用户数")
    total_requests: int = Field(0, description="AI请求总数")


class TrafficOverviewResponse(BaseModel):
    """流量概览响应"""
    overview: TrafficOverview
    daily_stats: List[DailyStatItem] = Field(default=[], description="每日统计列表")
