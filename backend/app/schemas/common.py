"""
通用Schema模型
"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }
