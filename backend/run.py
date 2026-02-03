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

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    print(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📝 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"📖 ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
