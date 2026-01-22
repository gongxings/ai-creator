"""
自定义异常
"""
from typing import Any, Optional
from fastapi import HTTPException, status


class BusinessException(HTTPException):
    """业务异常"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(HTTPException):
    """资源不存在异常"""
    
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class UnauthorizedException(HTTPException):
    """未授权异常"""
    
    def __init__(self, detail: str = "未授权"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """禁止访问异常"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationException(HTTPException):
    """验证异常"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class RateLimitException(HTTPException):
    """限流异常"""
    
    def __init__(self, detail: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class AIServiceException(BusinessException):
    """AI服务异常"""
    
    def __init__(self, detail: str = "AI服务调用失败"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class PlatformPublishException(BusinessException):
    """平台发布异常"""
    
    def __init__(self, detail: str = "平台发布失败"):
        super().__init__(detail=detail)
