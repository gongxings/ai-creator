"""
辅助工具函数
"""
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_random_string(length: int = 32) -> str:
    """
    生成随机字符串
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_file_hash(content: bytes) -> str:
    """
    生成文件哈希值
    """
    return hashlib.sha256(content).hexdigest()


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    计算阅读时间（分钟）
    """
    # 简单的中英文字数统计
    chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
    english_words = len([w for w in content.split() if w.isalpha()])
    
    total_words = chinese_chars + english_words
    reading_time = max(1, round(total_words / words_per_minute))
    
    return reading_time


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def is_valid_url(url: str) -> bool:
    """
    验证URL是否有效
    """
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    """
    import re
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    return filename


def get_date_range(period: str) -> tuple[datetime, datetime]:
    """
    获取日期范围
    period: today, yesterday, week, month, year
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == "today":
        return today_start, now
    elif period == "yesterday":
        yesterday_start = today_start - timedelta(days=1)
        return yesterday_start, today_start
    elif period == "week":
        week_start = today_start - timedelta(days=now.weekday())
        return week_start, now
    elif period == "month":
        month_start = today_start.replace(day=1)
        return month_start, now
    elif period == "year":
        year_start = today_start.replace(month=1, day=1)
        return year_start, now
    else:
        return today_start, now


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    提取关键词（简单实现）
    """
    import re
    from collections import Counter
    
    # 移除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    # 分词
    words = text.lower().split()
    # 过滤停用词（简化版）
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    words = [w for w in words if w not in stop_words and len(w) > 1]
    
    # 统计词频
    word_counts = Counter(words)
    keywords = [word for word, count in word_counts.most_common(max_keywords)]
    
    return keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算文本相似度（简单实现）
    """
    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1, text2).ratio()


def format_duration(seconds: float) -> str:
    """
    格式化时长
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
