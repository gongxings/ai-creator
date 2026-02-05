# -*- coding: utf-8 -*-
"""
自定义Uvicorn配置，确保Windows上的Playwright可以正常工作
"""
import os

def apply_nest_asyncio():
    """应用nest_asyncio"""
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass

# 在进程启动时应用
apply_nest_asyncio()

# 设置环境变量，通知子进程也要应用nest_asyncio
os.environ["APPLY_NEST_ASYNCIO"] = "1"

from uvicorn.config import Config
from uvicorn.supervisors import ChangeReload

class CustomChangeReload(ChangeReload):
    """自定义ChangeReload，确保子进程应用nest_asyncio"""
    
    def startup(self):
        # 设置子进程环境
        os.environ["APPLY_NEST_ASYNCIO"] = "1"
        return super().startup()
    
    def run(self, target):
        # 确保在运行前应用nest_asyncio
        apply_nest_asyncio()
        return super().run(target)