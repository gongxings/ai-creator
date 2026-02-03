"""
Redis缓存工具
"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis
from app.core.config import settings

# Create Redis connection safely
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Redis connection failed: {e}. Using memory cache.")
    REDIS_AVAILABLE = False
    redis_client = None

# Memory cache for fallback
_memory_cache = {}

class Cache:
    """Cache Management Class"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get cache"""
        try:
            if REDIS_AVAILABLE and redis_client:
                value = redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                # Fallback to memory cache
                data = _memory_cache.get(key)
                if data:
                    # Check expiration (simplified for memory cache)
                    # In a real implementation, we should store (value, expire_time)
                    return data
                return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 3600) -> bool:
        """Set cache"""
        try:
            if REDIS_AVAILABLE and redis_client:
                redis_client.setex(
                    key,
                    expire,
                    json.dumps(value, ensure_ascii=False)
                )
                return True
            else:
                # Fallback to memory cache
                _memory_cache[key] = value
                return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete cache"""
        try:
            if REDIS_AVAILABLE and redis_client:
                redis_client.delete(key)
                return True
            else:
                if key in _memory_cache:
                    del _memory_cache[key]
                return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """Check if cache exists"""
        try:
            if REDIS_AVAILABLE and redis_client:
                return redis_client.exists(key) > 0
            else:
                return key in _memory_cache
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
            
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Clear cache by pattern"""
        try:
            if REDIS_AVAILABLE and redis_client:
                keys = redis_client.keys(pattern)
                if keys:
                    return redis_client.delete(*keys)
                return 0
            else:
                # Simple pattern matching for memory cache (supports * at end)
                count = 0
                prefix = pattern.rstrip('*')
                keys_to_delete = [k for k in _memory_cache.keys() if k.startswith(prefix)]
                for k in keys_to_delete:
                    del _memory_cache[k]
                    count += 1
                return count
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
            
    @staticmethod
    def increment(key: str, amount: int = 1) -> int:
        """Increment value"""
        try:
            if REDIS_AVAILABLE and redis_client:
                return redis_client.incrby(key, amount)
            else:
                val = _memory_cache.get(key, 0)
                if isinstance(val, int):
                    _memory_cache[key] = val + amount
                    return _memory_cache[key]
                return 0
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0
    
    @staticmethod
    def decrement(key: str, amount: int = 1) -> int:
        """
        减少计数
        """
        try:
            return redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Cache decrement error: {e}")
            return 0


def get_user_cache_key(user_id: int, suffix: str = "") -> str:
    """
    获取用户缓存键
    """
    if suffix:
        return f"user:{user_id}:{suffix}"
    return f"user:{user_id}"


def get_creation_cache_key(creation_id: int) -> str:
    """
    获取创作内容缓存键
    """
    return f"creation:{creation_id}"


def get_model_cache_key(model_id: int) -> str:
    """
    获取AI模型缓存键
    """
    return f"model:{model_id}"


def get_platform_cache_key(platform_id: int) -> str:
    """
    获取平台缓存键
    """
    return f"platform:{platform_id}"


def get_rate_limit_key(user_id: int, action: str) -> str:
    """
    获取频率限制键
    """
    return f"rate_limit:{user_id}:{action}"


def check_rate_limit(user_id: int, action: str, max_requests: int = 10, window: int = 60) -> bool:
    """
    检查频率限制
    max_requests: 时间窗口内最大请求数
    window: 时间窗口（秒）
    """
    key = get_rate_limit_key(user_id, action)
    
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        if int(current) >= max_requests:
            return False
        
        redis_client.incr(key)
        return True
    except Exception as e:
        print(f"Rate limit check error: {e}")
        return True  # 出错时允许请求


def cache_user_quota(user_id: int, used_quota: int, daily_quota: int) -> bool:
    """
    缓存用户配额信息
    """
    key = get_user_cache_key(user_id, "quota")
    data = {
        "used_quota": used_quota,
        "daily_quota": daily_quota
    }
    return Cache.set(key, data, expire=3600)


def get_cached_user_quota(user_id: int) -> Optional[dict]:
    """
    获取缓存的用户配额信息
    """
    key = get_user_cache_key(user_id, "quota")
    return Cache.get(key)


def clear_user_cache(user_id: int) -> int:
    """
    清除用户相关的所有缓存
    """
    pattern = f"user:{user_id}:*"
    return Cache.clear_pattern(pattern)
