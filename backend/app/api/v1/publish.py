"""
发布管理API
"""
from typing import List, Dict, Optional
from urllib.parse import urlparse
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.models.publish import PlatformAccount, PublishRecord
from app.schemas.publish import (
    PlatformInfo,
    PlatformLoginInfo,
    PlatformAccountCreate,
    PlatformAccountUpdate,
    PlatformAccountResponse,
    CookieUpdateRequest,
    CookieValidationResponse,
    PublishCreate,
    PublishRecordResponse,
    PublishRecordListResponse,
    PublishStatusResponse
)
from app.services.publish.platforms import get_platform, PLATFORM_REGISTRY
from app.services.publish.playwright_service import publish_playwright_service
from app.schemas.common import success_response

router = APIRouter()


def _build_cookie_list(login_url: str, cookies: dict) -> List[dict]:
    parsed = urlparse(login_url)
    host = parsed.netloc
    parts = host.split(".")
    root = ".".join(parts[-2:]) if len(parts) >= 2 else host
    domain = f".{root}"
    return [
        {"name": name, "value": value, "domain": domain, "path": "/"}
        for name, value in cookies.items()
    ]


async def _validate_cookies_with_publisher(publisher, account: PlatformAccount) -> bool:
    try:
        return await publisher.validate_cookies(account)
    except TypeError:
        cookie_dict = publisher.get_cookies(account)
        if not cookie_dict:
            return False
        cookie_list = _build_cookie_list(publisher.get_login_url(), cookie_dict)
        return await publisher.validate_cookies(cookie_list)


@router.get("/platforms", response_model=List[PlatformInfo])
async def get_platforms():
    """获取支持的平台列表"""
    platforms = []
    for name, publisher_class in PLATFORM_REGISTRY.items():
        publisher = publisher_class()
        platforms.append(PlatformInfo(
            platform=name,
            name=publisher.get_platform_name(),
            login_url=publisher.get_login_url(),
            supported_types=getattr(publisher, "supported_types", [])
        ))
    return platforms


@router.get("/platforms/{platform}/login-info", response_model=PlatformLoginInfo)
async def get_platform_login_info(platform: str):
    """获取平台登录信息"""
    try:
        publisher = get_platform(platform)
        return PlatformLoginInfo(
            platform=platform,
            name=publisher.get_platform_name(),
            login_url=publisher.get_login_url(),
            instructions=f"请在浏览器中登录{publisher.get_platform_name()}，然后返回此页面更新Cookie"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class PublishCookieSubmit(BaseModel):
    """发布平台Cookie提交请求"""
    platform: str
    cookies: Dict[str, str]
    account_name: Optional[str] = None
    user_agent: Optional[str] = None


@router.post("/platforms/accounts/cookie-submit", response_model=PlatformAccountResponse)
async def submit_publish_cookies(
    data: PublishCookieSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交发布平台Cookie（前端自动获取）
    
    这个接口接收前端获取的Cookie并保存
    """
    try:
        # 验证平台是否支持
        publisher = get_platform(data.platform)
        
        # 检查是否已存在账号
        from sqlalchemy import and_
        existing_account = db.query(PlatformAccount).filter(
            and_(
                PlatformAccount.user_id == current_user.id,
                PlatformAccount.platform == data.platform,
                PlatformAccount.account_name == data.account_name
            )
        ).first()
        
        if existing_account:
            # 更新现有账号的Cookie
            publisher.set_cookies(existing_account, data.cookies)
            existing_account.cookies_updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_account)
            account = existing_account
        else:
            # 创建新账号
            account = PlatformAccount(
                user_id=current_user.id,
                platform=data.platform,
                account_name=data.account_name or f"{data.platform}_account",
                cookies_valid="unknown",
                is_active="active"
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            
            # 设置Cookie
            publisher.set_cookies(account, data.cookies)
            db.commit()
            db.refresh(account)
        
        # 验证Cookie有效性
        is_valid = await _validate_cookies_with_publisher(publisher, account)
        account.cookies_valid = "valid" if is_valid else "invalid"
        db.commit()
        db.refresh(account)
        
        return PlatformAccountResponse(
            id=account.id,
            platform=account.platform,
            account_name=account.account_name,
            cookies_valid=account.cookies_valid,
            cookies_updated_at=account.cookies_updated_at,
            is_active=account.is_active,
            created_at=account.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cookie提交失败: {str(e)}")


@router.get("/platforms/accounts/cookie-validate/{platform}")
async def validate_publish_cookies_page(request: Request, platform: str):
    """
    返回Cookie验证页面（前端打开的授权窗口）
    """
    try:
        publisher = get_platform(platform)
        platform_name = publisher.get_platform_name()
        login_url = publisher.get_login_url()
        base_url = str(request.url).replace(f"/api/v1/publish/platforms/accounts/cookie-validate/{platform}", "")
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{platform_name} 授权</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .info {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
            border-radius: 4px;
        }}
        
        .info p {{
            color: #666;
            line-height: 1.6;
            margin: 0;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 10px 5px;
            width: 100%;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }}
        
        .success {{
            display: none;
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        
        .error {{
            display: none;
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        
        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{platform_name} 授权</h1>
        
        <div class="info">
            <p><strong>说明：</strong></p>
            <p>1. 点击下方按钮打开{platform_name}登录页面</p>
            <p>2. 在新页面中扫码或输入账号密码完成登录</p>
            <p>3. 登录成功后，返回此页面</p>
            <p>4. 点击"获取Cookie并提交"按钮</p>
            <p>5. Cookie会自动提取并提交到后端</p>
        </div>
        
        <div id="loading" class="loading">
            <div class="spinner"></div>
            <p>正在获取Cookie...</p>
        </div>
        
        <div id="success" class="success">
            <p>✓ Cookie提交成功！窗口即将关闭...</p>
        </div>
        
        <div id="error" class="error">
            <p>✗ 获取Cookie失败，请重试</p>
            <p id="error-message"></p>
        </div>
        
        <div id="buttons">
            <button class="btn" onclick="openLogin()">打开登录页面</button>
            <button class="btn" onclick="submitCookies()">获取Cookie并提交</button>
        </div>
    </div>
    
    <script>
        const platform = '{platform}';
        const loginUrl = '{login_url}';
        const openerUrl = window.opener ? document.referrer : '*';
        
        function openLogin() {{
            window.open(loginUrl, '_blank');
        }}
        
        async function submitCookies() {{
            try {{
                document.getElementById('loading').style.display = 'block';
                document.getElementById('buttons').style.display = 'none';
                document.getElementById('error').style.display = 'none';
                
                const cookies = await getCookiesFromPage();
                
                // 发送Cookie到后端
                const response = await fetch('{base_url}/api/v1/publish/platforms/accounts/cookie-submit', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    credentials: 'include',
                    body: JSON.stringify({{
                        platform: platform,
                        cookies: cookies,
                        user_agent: navigator.userAgent,
                        account_name: prompt('请输入账号名称：', platform + '_account')
                    }})
                }});
                
                if (response.ok) {{
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('success').style.display = 'block';
                    
                    // 通知父窗口
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'publish_cookies_success',
                            platform: platform
                        }}, openerUrl);
                    }}
                    
                    // 3秒后关闭窗口
                    setTimeout(() => {{
                        window.close();
                    }}, 3000);
                }} else {{
                    throw new Error('提交失败');
                }}
                
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error-message').textContent = error.message;
                document.getElementById('buttons').style.display = 'block';
            }}
        }}
        
        async function getCookiesFromPage() {{
            // 尝试读取Cookie
            const cookies = document.cookie;
            
            if (cookies) {{
                const cookieObj = {{}};
                const cookiePairs = cookies.split(';');
                cookiePairs.forEach(pair => {{
                    const [name, value] = pair.trim().split('=');
                    if (name && value) {{
                        cookieObj[name.trim()] = value.trim();
                    }}
                }});
                return cookieObj;
            }}
            
            // 提示用户手动复制粘贴
            const cookieString = prompt(
                '由于浏览器安全限制，请手动复制Cookie并粘贴到此处。\\n\\n' +
                '如何获取Cookie：\\n' +
                '1. 在' + loginUrl + '页面完成登录\\n' +
                '2. 按F12打开开发者工具\\n' +
                '3. 点击Application或存储标签\\n' +
                '4. 在左侧找到Cookies\\n' +
                '5. 复制所有Cookie值（格式：name1=value1; name2=value2）'
            );
            
            if (!cookieString) {{
                throw new Error('未提供Cookie');
            }}
            
            const cookieObj = {{}};
            const cookiePairs = cookieString.split(';');
            cookiePairs.forEach(pair => {{
                const [name, value] = pair.trim().split('=');
                if (name && value) {{
                    cookieObj[name.trim()] = value.trim();
                }}
            }});
            
            return cookieObj;
        }}
        
        // 监听来自父窗口的消息
        window.addEventListener('message', (event) => {{
            if (event.data && event.data.type === 'extract_cookies') {{
                submitCookies();
            }}
        }});
    </script>
</body>
</html>
    """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"平台 {platform} 不存在")


@router.post("/platforms/accounts/authorize", response_model=PlatformAccountResponse)
async def authorize_platform_account(
    account_data: PlatformAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    自动打开浏览器登录并抓取Cookie（后端Playwright方式）
    """
    try:
        publisher = get_platform(account_data.platform)

        # upsert account by platform + account_name
        account = db.query(PlatformAccount).filter(
            PlatformAccount.user_id == current_user.id,
            PlatformAccount.platform == account_data.platform,
            PlatformAccount.account_name == account_data.account_name
        ).first()

        if not account:
            account = PlatformAccount(
                user_id=current_user.id,
                platform=account_data.platform,
                account_name=account_data.account_name,
                cookies_valid="unknown",
                is_active="active"
            )
            db.add(account)
            db.commit()
            db.refresh(account)

        success_pattern = getattr(publisher, "get_success_pattern", None)
        cookie_domain = getattr(publisher, "get_cookie_domain", None)

        credentials = await publish_playwright_service.authorize_platform(
            login_url=publisher.get_login_url(),
            success_pattern=success_pattern() if callable(success_pattern) else None,
            cookie_domain=cookie_domain() if callable(cookie_domain) else None,
        )

        publisher.set_cookies(account, credentials.get("cookies", {}))
        db.commit()
        db.refresh(account)

        is_valid = await _validate_cookies_with_publisher(publisher, account)
        account.cookies_valid = "valid" if is_valid else "invalid"
        db.commit()
        db.refresh(account)

        return PlatformAccountResponse(
            id=account.id,
            platform=account.platform,
            account_name=account.account_name,
            cookies_valid=account.cookies_valid,
            cookies_updated_at=account.cookies_updated_at,
            is_active=account.is_active,
            created_at=account.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"授权失败: {str(e)}")


@router.post("/platforms/accounts", response_model=PlatformAccountResponse)
async def create_platform_account(
    account_data: PlatformAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建平台账号"""
    # 检查是否已存在
    existing = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.platform == account_data.platform,
        PlatformAccount.account_name == account_data.account_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该平台账号已存在"
        )
    
    # 创建账号
    account = PlatformAccount(
        user_id=current_user.id,
        platform=account_data.platform,
        account_name=account_data.account_name,
        cookies_valid="unknown"
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return PlatformAccountResponse(
        id=account.id,
        platform=account.platform,
        account_name=account.account_name,
        cookies_valid=account.cookies_valid,
        cookies_updated_at=account.cookies_updated_at,
        is_active=account.is_active,
        created_at=account.created_at
    )


@router.get("/platforms/accounts", response_model=List[PlatformAccountResponse])
async def get_platform_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的平台账号列表"""
    accounts = db.query(PlatformAccount).filter(
        PlatformAccount.user_id == current_user.id
    ).all()
    
    return [
        PlatformAccountResponse(
            id=account.id,
            platform=account.platform,
            account_name=account.account_name,
            cookies_valid=account.cookies_valid,
            cookies_updated_at=account.cookies_updated_at,
            is_active=account.is_active,
            created_at=account.created_at
        )
        for account in accounts
    ]


@router.put("/platforms/accounts/{account_id}", response_model=PlatformAccountResponse)
async def update_platform_account(
    account_id: int,
    account_data: PlatformAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    if account_data.account_name is not None:
        account.account_name = account_data.account_name
    if account_data.is_active is not None:
        account.is_active = account_data.is_active
    
    db.commit()
    db.refresh(account)
    
    return PlatformAccountResponse(
        id=account.id,
        platform=account.platform,
        account_name=account.account_name,
        cookies_valid=account.cookies_valid,
        cookies_updated_at=account.cookies_updated_at,
        is_active=account.is_active,
        created_at=account.created_at
    )


@router.delete("/platforms/accounts/{account_id}")
async def delete_platform_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除平台账号"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    db.delete(account)
    db.commit()
    
    return {"message": "删除成功"}


@router.post("/platforms/accounts/{account_id}/cookies", response_model=CookieValidationResponse)
async def update_cookies(
    account_id: int,
    cookie_data: CookieUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新平台账号Cookie"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    try:
        # 获取平台发布器
        publisher = get_platform(account.platform)
        
        # 保存Cookie
        publisher.set_cookies(account, cookie_data.cookies)
        db.commit()
        db.refresh(account)
        
        # 验证Cookie
        is_valid = await _validate_cookies_with_publisher(publisher, account)
        
        return CookieValidationResponse(
            valid=is_valid,
            message="Cookie验证成功" if is_valid else "Cookie验证失败，请重新登录",
            cookies_updated_at=account.cookies_updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新Cookie失败: {str(e)}"
        )


@router.post("/platforms/accounts/{account_id}/validate", response_model=CookieValidationResponse)
async def validate_cookies(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证平台账号Cookie"""
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == account_id,
        PlatformAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在")
    
    try:
        publisher = get_platform(account.platform)
        is_valid = await _validate_cookies_with_publisher(publisher, account)
        
        return CookieValidationResponse(
            valid=is_valid,
            message="Cookie有效" if is_valid else "Cookie已失效，请重新登录",
            cookies_updated_at=account.cookies_updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证Cookie失败: {str(e)}"
        )


@router.post("/publish", response_model=PublishStatusResponse)
async def publish_content(
    publish_data: PublishCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布内容到平台（创建草稿）"""
    # 获取平台账号
    account = db.query(PlatformAccount).filter(
        PlatformAccount.id == publish_data.account_id,
        PlatformAccount.user_id == current_user.id,
        PlatformAccount.is_active == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="平台账号不存在或未激活")
    
    try:
        if publish_data.scheduled_at:
            history = PublishRecord(
                user_id=current_user.id,
                platform_account_id=account.id,
                creation_id=publish_data.creation_id,
                platform=account.platform,
                content_type=publish_data.content_type,
                title=publish_data.title,
                status="scheduled",
                scheduled_at=publish_data.scheduled_at
            )
            db.add(history)
            db.commit()
            db.refresh(history)

            return PublishStatusResponse(
                id=history.id,
                platform=history.platform,
                status=history.status,
                message="已加入定时发布队列",
                published_at=history.published_at
            )

        # 获取平台发布器
        publisher = get_platform(account.platform)
        
        # 检查Cookie有效性
        publisher.check_cookies_or_raise(account)
        
        # 创建草稿
        result = await publisher.create_draft(
            account=account,
            content=publish_data.content,
            title=publish_data.title,
            cover_image=publish_data.cover_image,
            images=publish_data.images,
            video_url=publish_data.video_url,
            tags=publish_data.tags,
            location=publish_data.location
        )
        
        # 保存发布历史
        history = PublishRecord(
            user_id=current_user.id,
            platform_account_id=account.id,
            creation_id=publish_data.creation_id,
            platform=account.platform,
            content_type=publish_data.content_type,
            title=publish_data.title,
            status="draft",
            platform_post_id=result.get("draft_id"),
            platform_url=result.get("draft_url")
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return PublishStatusResponse(
            id=history.id,
            platform=history.platform,
            status=history.status,
            platform_post_id=history.platform_post_id,
            platform_url=history.platform_url,
            message=result.get("message", "草稿创建成功"),
            published_at=history.published_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建草稿失败: {str(e)}"
        )


@router.get("/publish/{publish_id}/status", response_model=PublishStatusResponse)
async def get_publish_status(
    publish_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发布状态"""
    record = db.query(PublishRecord).filter(
        PublishRecord.id == publish_id,
        PublishRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="发布记录不存在")

    return PublishStatusResponse(
        id=record.id,
        platform=record.platform,
        status=record.status,
        platform_post_id=record.platform_post_id,
        platform_url=record.platform_url,
        message=record.error_message,
        published_at=record.published_at
    )


@router.get("/history", response_model=PublishRecordListResponse)
async def get_publish_history(
    platform: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发布历史"""
    query = db.query(PublishRecord).filter(
        PublishRecord.user_id == current_user.id
    )
    
    if platform:
        query = query.filter(PublishRecord.platform == platform)
    if status:
        query = query.filter(PublishRecord.status == status)
    
    total = query.count()
    histories = query.order_by(
        PublishRecord.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return PublishRecordListResponse(
        total=total,
        items=[
            PublishRecordResponse(
                id=h.id,
                platform=h.platform,
                account_name=h.platform_account.account_name if h.platform_account else None,
                content_type=h.content_type,
                title=h.title,
                status=h.status,
                platform_post_id=h.platform_post_id,
                platform_url=h.platform_url,
                error_message=h.error_message,
                published_at=h.published_at,
                created_at=h.created_at
            )
            for h in histories
        ]
    )


@router.get("/history/{history_id}", response_model=PublishRecordResponse)
async def get_publish_history_detail(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发布历史详情"""
    history = db.query(PublishRecord).filter(
        PublishRecord.id == history_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="发布历史不存在")
    
    return PublishRecordResponse(
        id=history.id,
        platform=history.platform,
        account_name=history.platform_account.account_name if history.platform_account else None,
        content_type=history.content_type,
        title=history.title,
        status=history.status,
        platform_post_id=history.platform_post_id,
        platform_url=history.platform_url,
        error_message=history.error_message,
        published_at=history.published_at,
        created_at=history.created_at
    )


@router.delete("/history/{history_id}")
async def delete_publish_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除发布历史"""
    history = db.query(PublishRecord).filter(
        PublishRecord.id == history_id,
        PublishRecord.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="发布历史不存在")
    
    db.delete(history)
    db.commit()
    
    return {"message": "删除成功"}
