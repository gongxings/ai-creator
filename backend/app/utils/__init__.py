"""
工具模块初始化
"""
from app.utils.deps import (
    get_current_user,
    get_current_active_user,
    get_admin_user,
    check_quota
)
from app.utils.helpers import (
    generate_random_string,
    generate_file_hash,
    calculate_reading_time,
    truncate_text,
    format_file_size,
    is_valid_url,
    sanitize_filename,
    get_date_range,
    extract_keywords,
    calculate_similarity,
    format_duration
)
from app.utils.cache import (
    Cache,
    get_user_cache_key,
    get_creation_cache_key,
    get_model_cache_key,
    get_platform_cache_key,
    check_rate_limit,
    cache_user_quota,
    get_cached_user_quota,
    clear_user_cache
)

__all__ = [
    # Deps
    "get_current_user",
    "get_current_active_user",
    "get_admin_user",
    "check_quota",
    # Helpers
    "generate_random_string",
    "generate_file_hash",
    "calculate_reading_time",
    "truncate_text",
    "format_file_size",
    "is_valid_url",
    "sanitize_filename",
    "get_date_range",
    "extract_keywords",
    "calculate_similarity",
    "format_duration",
    # Cache
    "Cache",
    "get_user_cache_key",
    "get_creation_cache_key",
    "get_model_cache_key",
    "get_platform_cache_key",
    "check_rate_limit",
    "cache_user_quota",
    "get_cached_user_quota",
    "clear_user_cache",
]
