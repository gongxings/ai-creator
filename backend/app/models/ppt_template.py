"""
PPT模板数据模型
支持用户上传PPTX模板，系统解析布局元数据
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func

from app.core.database import Base


class PPTTemplate(Base):
    """PPT模板表"""
    __tablename__ = "ppt_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="模板ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(String(500), comment="模板描述")
    thumbnail = Column(String(500), comment="缩略图URL")
    
    # 文件信息
    file_path = Column(String(500), nullable=False, comment="PPTX文件路径")
    file_size = Column(Integer, comment="文件大小(bytes)")
    
    # 平台和分类
    platform = Column(String(20), default="ppt", comment="平台类型")
    category = Column(String(50), index=True, comment="场景分类：report/training/roadshow/teaching")
    style = Column(String(50), index=True, comment="风格类型：商务/简约/科技/创意")
    
    # 布局元数据 (JSON)
    # 包含每页slide的布局信息、占位符位置和类型
    layout_metadata = Column(JSON, comment="布局元数据")
    # 示例:
    # {
    #   "slide_count": 10,
    #   "slides": [
    #     {
    #       "index": 0,
    #       "type": "title",
    #       "layout_name": "Title Slide",
    #       "placeholders": [
    #         {"idx": 0, "type": "title", "label": "主标题", "bounds": {"x": 0, "y": 0, "width": 100, "height": 50}},
    #         {"idx": 1, "type": "subtitle", "label": "副标题", "bounds": {"x": 0, "y": 50, "width": 100, "height": 30}}
    #       ]
    #     },
    #     {
    #       "index": 1,
    #       "type": "content",
    #       "layout_name": "Title and Content",
    #       "placeholders": [
    #         {"idx": 0, "type": "title", "label": "页标题"},
    #         {"idx": 1, "type": "body", "label": "正文内容", "supports_bullets": true}
    #       ]
    #     }
    #   ]
    # }
    
    # 模板类型
    is_system = Column(Boolean, default=False, index=True, comment="是否系统预设")
    is_public = Column(Boolean, default=False, index=True, comment="是否公开")
    
    # 所有者
    user_id = Column(BigInteger, nullable=True, index=True, comment="用户ID（自定义模板的所有者）")
    
    # 统计
    use_count = Column(Integer, default=0, comment="使用次数")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<PPTTemplate(id={self.id}, name={self.name}, category={self.category})>"
