"""
AI创作者平台应用包
"""
__version__ = "1.0.0"

# 应用nest_asyncio以支持Windows上的Playwright
# 只在未应用过的情况下应用（避免重复应用）
try:
    import nest_asyncio
    if not getattr(nest_asyncio, '_applied', False):
        nest_asyncio.apply()
        nest_asyncio._applied = True
except ImportError:
    pass
