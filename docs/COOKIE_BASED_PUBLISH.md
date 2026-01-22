# 基于Cookie的平台发布功能实现文档

## 概述

本文档描述了基于Cookie的平台发布功能实现，所有平台发布采用获取平台登录的cookies，然后使用Playwright模拟浏览器操作创建草稿。

## 核心特性

### 1. Cookie管理
- **用户隔离**：每个用户的Cookie独立存储，通过PlatformAccount与user_id绑定
- **加密存储**：使用Fernet对称加密算法加密存储Cookie
- **有效性验证**：自动验证Cookie是否有效，无效时提示用户重新登录
- **自动更新**：记录Cookie更新时间，支持Cookie刷新

### 2. 草稿创建
- **不直接发布**：所有平台都创建草稿，不直接发布
- **用户可编辑**：用户可以在平台草稿箱中修改内容后自己发布
- **封面图必填**：所有平台发布都需要提供封面图URL

### 3. 浏览器自动化
- **Playwright**：使用Playwright进行浏览器自动化操作
- **异步操作**：所有操作都是异步的，提高性能
- **临时文件管理**：下载媒体文件到临时目录，上传后自动清理

## 数据库模型

### PlatformAccount模型新增字段

```python
class PlatformAccount(Base):
    # ... 原有字段 ...
    
    # Cookie相关字段
    cookies = Column(Text, nullable=True, comment="加密的Cookie JSON")
    cookies_updated_at = Column(DateTime, nullable=True, comment="Cookie更新时间")
    cookies_valid = Column(
        Enum("valid", "invalid", "unknown", name="cookie_status"),
        default="unknown",
        comment="Cookie有效性状态"
    )
```

## 平台发布器实现

### 基类：BasePlatformPublisher

所有平台发布器的基类，提供通用功能：

```python
class BasePlatformPublisher(ABC):
    """平台发布器基类"""
    
    # Cookie管理
    def get_cookies(account: PlatformAccount) -> List[Dict[str, Any]]
    def set_cookies(account: PlatformAccount, cookies: List[Dict[str, Any]])
    def check_cookies_or_raise(account: PlatformAccount)
    
    # 抽象方法（子类必须实现）
    @abstractmethod
    async def create_draft(account, content) -> Dict[str, Any]
    
    @abstractmethod
    async def validate_cookies(cookies) -> bool
    
    @abstractmethod
    def get_platform_name() -> str
    
    @abstractmethod
    def get_login_url() -> str
```

### 1. 微信公众号（WeChatPublisher）

**支持内容类型**：图文

**必需字段**：
- title：标题
- content：正文HTML内容
- cover_url：封面图URL

**可选字段**：
- author：作者
- digest：摘要

**草稿地址**：https://mp.weixin.qq.com/

### 2. 小红书（XiaohongshuPublisher）

**支持内容类型**：图文

**必需字段**：
- title：标题
- content：正文内容
- cover_url：封面图URL
- images：图片列表（1-9张）

**可选字段**：
- tags：标签列表
- location：位置信息

**草稿地址**：https://creator.xiaohongshu.com/publish/publish

### 3. 抖音（DouyinPublisher）

**支持内容类型**：视频

**必需字段**：
- title：标题
- video_url：视频URL
- cover_url：封面图URL

**可选字段**：
- description：描述
- tags：话题标签列表
- location：位置信息

**草稿地址**：https://creator.douyin.com/creator-micro/content/manage

### 4. 快手（KuaishouPublisher）

**支持内容类型**：视频

**必需字段**：
- title：标题
- video_url：视频URL
- cover_url：封面图URL

**可选字段**：
- description：描述
- tags：标签列表
- location：位置信息

**草稿地址**：https://cp.kuaishou.com/article/manage/video

### 5. 今日头条（ToutiaoPublisher）

**支持内容类型**：图文、视频

**图文必需字段**：
- title：标题
- content：正文内容
- cover_url：封面图URL

**视频必需字段**：
- title：标题
- video_url：视频URL
- cover_url：封面图URL

**可选字段**：
- images：图片列表（图文）
- description：简介（视频）
- tags：标签列表
- content_type：内容类型（article/video）

**草稿地址**：
- 图文：https://mp.toutiao.com/profile_v4/graphic/content-manage
- 视频：https://mp.toutiao.com/profile_v4/xigua/content-manage

## API使用示例

### 1. 设置平台Cookie

```python
POST /api/v1/publish/platforms/{platform_name}/cookies

Request Body:
{
    "cookies": [
        {
            "name": "cookie_name",
            "value": "cookie_value",
            "domain": ".example.com",
            "path": "/",
            "expires": 1234567890,
            "httpOnly": true,
            "secure": true,
            "sameSite": "Lax"
        }
    ]
}

Response:
{
    "code": 200,
    "message": "Cookie设置成功",
    "data": {
        "platform": "wechat",
        "cookies_valid": "valid",
        "cookies_updated_at": "2026-01-22T12:00:00"
    }
}
```

### 2. 创建草稿

```python
POST /api/v1/publish/draft

Request Body:
{
    "platform": "xiaohongshu",
    "account_id": 1,
    "content": {
        "title": "我的小红书笔记",
        "content": "这是笔记内容...",
        "cover_url": "https://example.com/cover.jpg",
        "images": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ],
        "tags": ["美食", "探店"]
    }
}

Response:
{
    "code": 200,
    "message": "草稿创建成功",
    "data": {
        "success": true,
        "draft_url": "https://creator.xiaohongshu.com/publish/publish",
        "message": "草稿已保存到小红书创作者中心"
    }
}
```

### 3. 验证Cookie

```python
POST /api/v1/publish/platforms/{platform_name}/validate

Response:
{
    "code": 200,
    "message": "Cookie验
