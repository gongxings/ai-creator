#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置加载
"""
import sys
from pathlib import Path

# 将backend目录添加到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings

print("=" * 60)
print("配置加载测试")
print("=" * 60)
print(f"APP_NAME: {settings.APP_NAME}")
print(f"APP_VERSION: {settings.APP_VERSION}")
print(f"DEBUG: {settings.DEBUG}")
print(f"HOST: {settings.HOST}")
print(f"PORT: {settings.PORT}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")
print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
print(f"LOG_FILE: {settings.LOG_FILE}")
print("=" * 60)
print("✓ 配置加载成功！")
