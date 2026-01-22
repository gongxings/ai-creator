"""
应用配置
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "AI创作者平台"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://root:password@localhost:3306/ai_creator",
        description="数据库连接URL"
    )
    
    # Redis配置
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )
    
    # JWT配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7天
    
    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx"}
    
    # AI服务配置
    DEFAULT_AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    ANTHROPIC_API_KEY: Optional[str] = None
    ZHIPU_API_KEY: Optional[str] = None
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery消息代理URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery结果后端URL"
    )
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 平台发布配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
