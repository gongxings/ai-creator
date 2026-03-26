"""
FastAPI应用主入口
"""
import sys
import asyncio
from pathlib import Path

# 确保backend目录在Python路径中
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartParser
import logging

# 在创建应用前设置multipart解析器最大大小 (50MB)
MultiPartParser.max_part_size = 50 * 1024 * 1024
MultiPartParser.spool_max_size = 50 * 1024 * 1024

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, writing, image, video, ppt, creations, publish, models as models_api, credit, operation, oauth, ai, plugins, templates, hotspot, title, image_stock, platform_converter, viral_analyzer, admin_users, traffic, ppt_templates

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

# 挂载静态文件目录
import os
os.makedirs("uploads/images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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

    # 初始化数据库
    if settings.AUTO_CREATE_TABLES:
        init_db()
        logger.info("数据库初始化完成")

    # 启动埋点数据后台同步任务
    try:
        from app.tasks.background_tracker import start_tracker_background
        start_tracker_background()
        logger.info("埋点后台同步任务已启动")
    except Exception as e:
        logger.error(f"启动埋点后台任务失败: {e}")

    # 同步插件到数据库
    try:
        from app.services.plugins.plugin_manager import PluginManager
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            pm = PluginManager()
            pm.discover_builtin_plugins()
            count = pm.sync_to_database(db)
            logger.info(f"插件同步完成，共 {count} 个插件")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"插件同步失败: {e}")

    logger.info("应用启动完成")


@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {
        "code": 200,
        "message": "AI创作者平台API服务正在运行",
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs_url": "/docs",
            "api_prefix": settings.API_V1_PREFIX
        }
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"code": 200, "message": "healthy", "data": None}


# 认证相关路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["认证与授权"]
)

# 创作工具相关路由
app.include_router(
    writing.router,
    prefix=f"{settings.API_V1_PREFIX}/writing",
    tags=["AI写作"]
)

# 图片生成路由
app.include_router(
    image.router,
    prefix=f"{settings.API_V1_PREFIX}/image",
    tags=["图片生成"]
)

# 视频生成路由
app.include_router(
    video.router,
    prefix=f"{settings.API_V1_PREFIX}/video",
    tags=["视频生成"]
)

# PPT生成路由
app.include_router(
    ppt.router,
    prefix=f"{settings.API_V1_PREFIX}/ppt",
    tags=["PPT生成"]
)

# 创作管理路由
app.include_router(
    creations.router,
    prefix=f"{settings.API_V1_PREFIX}/creations",
    tags=["创作管理"]
)

# 发布管理路由
app.include_router(
    publish.router,
    prefix=f"{settings.API_V1_PREFIX}/publish",
    tags=["发布管理"]
)

# AI模型管理路由
app.include_router(
    models_api.router,
    prefix=f"{settings.API_V1_PREFIX}/models",
    tags=["AI模型管理"]
)

# 积分和会员路由
app.include_router(
    credit.router,
    prefix=f"{settings.API_V1_PREFIX}/credit",
    tags=["积分与会员"]
)

# 运营管理路由
app.include_router(
    operation.router,
    prefix=f"{settings.API_V1_PREFIX}/operation",
    tags=["运营管理"]
)

# OAuth平台管理路由
app.include_router(
    oauth.router,
    prefix=f"{settings.API_V1_PREFIX}/oauth",
    tags=["OAuth平台"]
)

# 统一AI调用路由
app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["统一AI调用"]
)

# 插件系统路由
app.include_router(
    plugins.router,
    prefix=f"{settings.API_V1_PREFIX}/plugins",
    tags=["插件系统"]
)

# 模板管理路由
app.include_router(
    templates.router,
    prefix=f"{settings.API_V1_PREFIX}/templates",
    tags=["模板管理"]
)

# 热点追踪路由
app.include_router(
    hotspot.router,
    prefix=f"{settings.API_V1_PREFIX}/hotspot",
    tags=["热点追踪"]
)

# 标题优化路由
app.include_router(
    title.router,
    prefix=f"{settings.API_V1_PREFIX}/title",
    tags=["标题优化"]
)

# 图片素材路由
app.include_router(
    image_stock.router,
    prefix=f"{settings.API_V1_PREFIX}/image-stock",
    tags=["图片素材"]
)

# 平台转换路由
app.include_router(
    platform_converter.router,
    prefix=f"{settings.API_V1_PREFIX}/converter",
    tags=["平台转换"]
)

# 爆款模仿路由
app.include_router(
    viral_analyzer.router,
    prefix=f"{settings.API_V1_PREFIX}/viral",
    tags=["爆款模仿"]
)

# 管理员接口
app.include_router(
    admin_users.router,
    prefix=f"{settings.API_V1_PREFIX}/admin/users",
    tags=["管理员 - 用户管理"]
)

# 流量统计
app.include_router(
    traffic.router,
    prefix=f"{settings.API_V1_PREFIX}/traffic",
    tags=["流量统计"]
)

# PPT模板管理
app.include_router(
    ppt_templates.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["PPT模板管理"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
