"""
FastAPI应用主入口
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, writing, image, video, ppt, creations, publish, models as models_api, credit, operation, oauth

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI创作者平台API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {"errors": exc.errors()}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("应用启动中...")
    
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志目录
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    logger.info("应用启动完成")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("应用关闭中...")


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "healthy",
            "version": settings.APP_VERSION
        }
    }


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# 注册路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["认证"]
)

app.include_router(
    writing.router,
    prefix=f"{settings.API_V1_PREFIX}/writing",
    tags=["AI写作"]
)

app.include_router(
    image.router,
    prefix=f"{settings.API_V1_PREFIX}/image",
    tags=["图片生成"]
)

app.include_router(
    video.router,
    prefix=f"{settings.API_V1_PREFIX}/video",
    tags=["视频生成"]
)

app.include_router(
    ppt.router,
    prefix=f"{settings.API_V1_PREFIX}/ppt",
    tags=["PPT生成"]
)

app.include_router(
    creations.router,
    prefix=f"{settings.API_V1_PREFIX}/creations",
    tags=["创作记录"]
)

app.include_router(
    publish.router,
    prefix=f"{settings.API_V1_PREFIX}/publish",
    tags=["发布管理"]
)

app.include_router(
    models_api.router,
    prefix=f"{settings.API_V1_PREFIX}/models",
    tags=["AI模型管理"]
)

app.include_router(
    credit.router,
    prefix=f"{settings.API_V1_PREFIX}/credit",
    tags=["积分会员"]
)

app.include_router(
    operation.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["运营管理"]
)

app.include_router(
    oauth.router,
    prefix=f"{settings.API_V1_PREFIX}/oauth",
    tags=["OAuth代理"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
