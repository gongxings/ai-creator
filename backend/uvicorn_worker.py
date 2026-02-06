# -*- coding: utf-8 -*-
"""
Uvicorn worker启动脚本
使用nest_asyncio支持Windows上的Playwright
"""
import sys

# 应用nest_asyncio以支持Windows上的Playwright
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("[WARNING] nest_asyncio not installed. Run: pip install nest-asyncio")

def run_server():
    """运行服务器"""
    from app.core.config import settings
    import uvicorn
    import asyncio
    
    print("[START] {} v{}".format(settings.APP_NAME, settings.APP_VERSION))
    print("[DOCS] API: http://{}:{}/docs".format(settings.HOST, settings.PORT))
    print("[DOCS] ReDoc: http://{}:{}/redoc".format(settings.HOST, settings.PORT))
    print(f"[EVENT LOOP POLICY] {asyncio.get_event_loop_policy().__class__.__name__}")
    print(f"[PLATFORM] {sys.platform}")
    print(f"[NEST-ASYNCIO] Applied")
    print(f"[RELOAD] {settings.DEBUG}")
    print()
    
    # 使用字符串路径以支持reload模式
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    run_server()