"""
AI模型调用监控日志模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, JSON, Index
from sqlalchemy.orm import relationship, foreign

from app.core.database import Base


class AIModelUsageLog(Base):
    """AI模型调用监控日志表"""
    __tablename__ = "ai_model_usage_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    ai_model_id = Column(BigInteger, nullable=False, index=True, comment="AI模型ID")
    creation_id = Column(BigInteger, nullable=True, index=True, comment="关联创作ID")
    
    provider = Column(String(50), nullable=False, index=True, comment="厂商")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    tool = Column(String(50), nullable=True, index=True, comment="调用步骤标识")
    
    request_type = Column(String(20), nullable=False, index=True, comment="请求类型 chat/image/video")
    input_content = Column(Text, nullable=True, comment="完整输入 prompt")
    output_content = Column(Text, nullable=True, comment="完整输出内容")
    
    prompt_tokens = Column(Integer, default=0, comment="输入 token 数")
    completion_tokens = Column(Integer, default=0, comment="输出 token 数")
    total_tokens = Column(Integer, default=0, comment="总 token 数")
    
    status = Column(String(20), nullable=False, default="success", index=True, comment="状态 success/failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    response_time_ms = Column(Integer, nullable=True, comment="响应时间毫秒")
    
    extra_data = Column(JSON, nullable=True, comment="额外数据")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")

    # 关系（不使用外键）
    user = relationship("User", primaryjoin="AIModelUsageLog.user_id == foreign(User.id)")
    ai_model = relationship("AIModel", primaryjoin="AIModelUsageLog.ai_model_id == foreign(AIModel.id)")
    creation = relationship("Creation", primaryjoin="AIModelUsageLog.creation_id == foreign(Creation.id)")

    def __repr__(self):
        return f"<AIModelUsageLog(id={self.id}, provider={self.provider}, status={self.status}, tokens={self.total_tokens})>"
