# -*- coding: utf-8 -*-
"""
后端应用启动脚本
用于开发环境直接运行，无需Docker
"""
import sys
from pathlib import Path

# 将backend目录添加到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 在 Python 3.13+ 上 nest_asyncio 可能与 uvicorn 不兼容，跳过
if sys.version_info < (3, 13):
    try:
        import nest_asyncio
        nest_asyncio.apply()
        print("[NEST-ASYNCIO] Applied")
    except ImportError:
        print("[WARNING] nest_asyncio not installed. Run: pip install nest-asyncio")
else:
    print(f"[NEST-ASYNCIO] Skipped (Python {sys.version_info.major}.{sys.version_info.minor})")

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    print("[START] {} v{}".format(settings.APP_NAME, settings.APP_VERSION))
    print("[DOCS] API: http://{}:{}/docs".format(settings.HOST, settings.PORT))
    print("[DOCS] ReDoc: http://{}:{}/redoc".format(settings.HOST, settings.PORT))
    print(f"[PLATFORM] {sys.platform}")
    
    # Windows + Playwright 暂时禁用 reload，避免子进程事件循环问题
    use_reload = settings.DEBUG and sys.platform != "win32"
    print(f"[RELOAD] {use_reload}")
    if not use_reload and settings.DEBUG:
        print("[INFO] Reload disabled on Windows for Playwright compatibility")
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=use_reload,
        log_level=settings.LOG_LEVEL.lower()
    )
