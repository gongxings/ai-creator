"""
OAuth账号管理API
"""
import os
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.deps import get_current_user
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.schemas.oauth import (
    OAuthAccountCreate,
    OAuthAccountManualCreate,
    OAuthAccountAuthorize,
    OAuthAccountResponse,
    OAuthAccountUpdate,
    OAuthUsageLogResponse,
    PlatformConfigResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from app.schemas.common import success_response
from app.services.oauth.oauth_service import oauth_service
from app.services.oauth.litellm_proxy import litellm_proxy
from app.services.oauth.oauth_session import oauth_session_manager
from app.models.platform_config import PlatformConfig
from app.services.oauth.adapters import get_supported_platforms, get_adapter, PLATFORM_ADAPTERS

router = APIRouter(tags=["OAuth"])


@router.get("/platforms", response_model=List[PlatformConfigResponse])
async def get_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取支持的平台列表
    """
    platforms = db.query(PlatformConfig).filter(
        PlatformConfig.is_enabled == True
    ).all()
    result = []
    for platform in platforms:
        adapter = get_adapter(platform.platform_id, {
            "oauth_config": platform.oauth_config,
            "litellm_config": platform.litellm_config,
            "quota_config": platform.quota_config,
        })
        oauth_meta = adapter.get_platform_config() if adapter else None

        data = PlatformConfigResponse.from_orm(platform).dict()
        data["oauth_meta"] = oauth_meta
        result.append(data)

    return result


@router.post("/accounts/authorize", response_model=OAuthAccountResponse)
async def authorize_account(
    data: OAuthAccountAuthorize,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    授权OAuth账号（一次性授权）

    这个接口会启动浏览器授权流程
    在 Windows 上会打开非 headless 浏览器窗口，用户需要手动登录
    """
    print(f"收到OAuth授权请求: platform={data.platform}, account_name={data.account_name}")
    print(f"当前用户ID: {current_user.id}")
    print(f"浏览器模式: {'非 headless 模式（可见）' if os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'false' else 'headless 模式'}")

    try:
        account = await oauth_service.authorize_account(
            db=db,
            user_id=current_user.id,
            platform=data.platform,
            account_name=data.account_name,
        )

        # 获取平台配置信息
        account_dict = OAuthAccountResponse.from_orm(account).dict()
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == account.platform
        ).first()
        if platform_config:
            account_dict["platform_name"] = platform_config.platform_name
            account_dict["platform_icon"] = platform_config.platform_icon

        return account_dict

    except Exception as e:
        print(f"OAuth授权失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/authorize/start")
async def authorize_start(
    platform: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    开始OAuth授权（分步授权流程）
    
    1. 打开浏览器并导航到登录页
    2. 点击登录按钮
    3. 返回会话ID
    """
    # 获取平台配置
    platform_config = db.query(PlatformConfig).filter(
        PlatformConfig.platform_id == platform
    ).first()
    
    if not platform_config:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
    
    if not platform_config.is_enabled:
        raise HTTPException(status_code=400, detail=f"Platform {platform} is disabled")
    
    # 获取适配器
    adapter_class = PLATFORM_ADAPTERS.get(platform)
    if not adapter_class:
        raise HTTPException(status_code=404, detail=f"Adapter for platform {platform} not found")
    
    adapter = adapter_class(platform, {
        "oauth_config": platform_config.oauth_config,
        "litellm_config": platform_config.litellm_config,
        "quota_config": platform_config.quota_config,
    })
    
    # 构建平台配置
    playwright_config = adapter.get_platform_config()
    
    # 创建授权会话
    session = await oauth_session_manager.create_session(
        user_id=current_user.id,
        platform=platform,
        platform_config=playwright_config,
    )
    
    return {
        "session_id": f"{current_user.id}:{platform}",
        "websocket_url": f"ws://{request.url.netloc}/api/v1/oauth/ws/{current_user.id}:{platform}",
        "expires_in": 300,  # 5分钟
    }


class OAuthCookieSubmit(BaseModel):
    """OAuth Cookie提交请求"""
    platform: str
    cookies: Dict[str, str]
    account_name: Optional[str] = None
    user_agent: Optional[str] = None


@router.post("/accounts/cookie-submit")
async def submit_oauth_cookies(
    data: OAuthCookieSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交OAuth Cookie（前端自动获取）
    
    这个接口接收前端获取的Cookie并保存
    """
    print(f"收到Cookie提交请求: platform={data.platform}, user_id={current_user.id}")
    print(f"Cookie keys: {list(data.cookies.keys())}")
    
    try:
        # 验证平台是否支持
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == data.platform
        ).first()
        
        if not platform_config:
            raise HTTPException(status_code=404, detail=f"平台 {data.platform} 不存在")
        
        # 获取适配器
        adapter_class = PLATFORM_ADAPTERS.get(data.platform)
        if not adapter_class:
            raise HTTPException(status_code=404, detail=f"平台 {data.platform} 的适配器不存在")
        
        adapter = adapter_class(data.platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })
        
        # 验证Cookie有效性
        credentials = {
            "cookies": data.cookies,
            "user_agent": data.user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        
        if not adapter.validate_credentials(credentials):
            raise HTTPException(status_code=400, detail="Cookie验证失败，请重新登录")
        
        print(f"Cookie验证通过，准备保存")
        
        # 加密凭证
        from app.services.oauth.encryption import encrypt_credentials
        encrypted_credentials = encrypt_credentials(credentials)
        
        # 检查是否已存在账号
        from sqlalchemy import and_
        from app.models.oauth_account import OAuthAccount
        existing_account = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.platform == data.platform
            )
        ).first()
        
        quota_limit = adapter.get_quota_limit()
        
        from datetime import datetime
        
        if existing_account:
            # 更新现有账号
            existing_account.credentials = encrypted_credentials
            existing_account.account_name = data.account_name or existing_account.account_name
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_account)
            
            print(f"更新现有账号: {existing_account.id}")
            account_dict = OAuthAccountResponse.from_orm(existing_account).dict()
        else:
            # 创建新账号
            account = OAuthAccount(
                user_id=current_user.id,
                platform=data.platform,
                account_name=data.account_name or f"{data.platform}_account",
                credentials=encrypted_credentials,
                is_active=True,
                is_expired=False,
                quota_used=0,
                quota_limit=quota_limit,
            )
            
            db.add(account)
            db.commit()
            db.refresh(account)
            
            print(f"创建新账号: {account.id}")
            account_dict = OAuthAccountResponse.from_orm(account).dict()
        
        # 添加平台信息
        if platform_config:
            account_dict["platform_name"] = platform_config.platform_name
            account_dict["platform_icon"] = platform_config.platform_icon
        
        return success_response(message="Cookie提交成功", data=account_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Cookie提交失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Cookie提交失败: {str(e)}")


@router.get("/accounts/cookie-validate/{platform}")
async def validate_cookies_page(request: Request, platform: str, db: Session = Depends(get_db)):
    """
    返回Cookie验证页面（前端打开的授权窗口）
    """
    platform_names = {
        "doubao": "豆包",
        "qwen": "通义千问",
        "openai": "OpenAI",
        "baidu": "百度文心一言",
        "zhipu": "智谱清言",
        "spark": "讯飞星火",
        "claude": "Claude",
        "gemini": "Gemini",
    }
    
    platform_name_cn = platform_names.get(platform, platform)
    base_url = str(request.url).replace(f"/api/v1/oauth/accounts/cookie-validate/{platform}", "")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{platform_name_cn} 授权</title>
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
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .btn-secondary {{
            background: #e9ecef;
            color: #495057;
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
            border: 3px solid #f3f3f3f;
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
        <h1>{platform_name_cn} 授权</h1>
        
        <div class="info">
            <p><strong>说明：</strong></p>
            <p>1. 点击下方按钮打开{platform_name_cn}登录页面</p>
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
            <button class="btn btn-primary" onclick="openLogin()">打开登录页面</button>
            <button class="btn btn-secondary" onclick="submitCookies()">获取Cookie并提交</button>
        </div>
    </div>
    
    <script>
        const platform = '{platform}';
        const openerUrl = window.opener ? document.referrer : '*';
        
        function openLogin() {{
            const loginUrl = getLoginUrl(platform);
            window.open(loginUrl, '_blank');
        }}
        
        function getLoginUrl(platform) {{
            const urls = {{
                'doubao': 'https://www.doubao.com/',
                'qwen': 'https://tongyi.aliyun.com/qianwen/',
                'openai': 'https://chatgpt.com/',
                'baidu': 'https://yiyan.baidu.com/',
                'zhipu': 'https://chatglm.cn/',
                'spark': 'https://xinghuo.xfyun.cn/',
                'claude': 'https://claude.ai/',
                'gemini': 'https://gemini.google.com/',
            }};
            return urls[platform] || 'https://www.doubao.com/';
        }}
        
        async function submitCookies() {{
            try {{
                document.getElementById('loading').style.display = 'block';
                document.getElementById('buttons').style.display = 'none';
                document.getElementById('error').style.display = 'none';
                
                const cookies = await getCookiesFromPage();
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('success').style.display = 'block';
                
                // 发送Cookie到后端
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'oauth_cookies',
                        platform: platform,
                        cookies: cookies,
                        user_agent: navigator.userAgent
                    }}, openerUrl);
                }}
                
                // 3秒后关闭窗口
                setTimeout(() => {{
                    window.close();
                }}, 3000);
                
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error-message').textContent = error.message;
                document.getElementById('buttons').style.display = 'block';
            }}
        }}
        
        async function getCookiesFromPage() {{
            // 尝试从同一域名获取Cookie
            // 注意：由于同源策略，这需要在授权页面所在域名进行
            
            try {{
                // 方法1: 尝试读取Cookie（如果在同一域名）
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
            }} catch (e) {{
                console.error('读取Cookie失败:', e);
            }}
            
            // 方法2: 提示用户手动复制粘贴
            const cookieString = prompt(
                '由于浏览器安全限制，请手动复制Cookie并粘贴到此处。\\n\\n' +
                '如何获取Cookie：\\n' +
                '1. 在' + getLoginUrl(platform) + '页面完成登录\\n' +
                '2. 按F12打开开发者工具\\n' +
                '3. 点击Application或存储标签\\n' +
                '4. 在左侧找到Cookies\\n' +
                '5. 复制所有Cookie值（格式：name1=value1; name2=value2）'
            );
            
            if (!cookieString) {{
                throw new Error('未提供Cookie');
            }
            
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
            }
        }});
        
         // 自动尝试提取（5秒后）
         setTimeout(() => {{
             // console.log('授权窗口已准备就绪');
         }}}, 5000);
    </script>
</body>
</html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


@router.get("/authorize/qr")
async def authorize_get_qr(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取登录二维码
    
    返回base64编码的二维码图片
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 获取二维码
    qr_code = await session.get_qr_code()
    
    if qr_code:
        return {
            "qr_code": qr_code,
            "format": "base64",
            "message": "二维码获取成功，请扫码登录"
        }
    else:
        return {
            "qr_code": None,
            "message": "未找到二维码元素，可能需要账号密码登录"
        }


@router.get("/authorize/status")
async def authorize_check_status(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """
    检查登录状态
    
    轮询此接口检查是否已登录
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 检查登录状态
    is_logged_in = await session.check_login_status()
    
    return {
        "logged_in": is_logged_in,
        "message": "已登录，可以完成授权" if is_logged_in else "等待扫码登录..."
    }


@router.post("/authorize/complete", response_model=OAuthAccountResponse)
async def authorize_complete(
    platform: str,
    account_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    完成OAuth授权
    
    提取登录凭证并保存到数据库
    """
    # 获取会话
    session = await oauth_session_manager.get_session(current_user.id, platform)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始授权")
    
    # 检查是否已登录
    if not session.is_logged_in:
        raise HTTPException(status_code=400, detail="尚未登录，请先扫码登录")
    
    try:
        # 提取凭证
        credentials = await session.extract_credentials()
        
        # 验证凭证
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == platform
        ).first()
        
        if not platform_config:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
        
        adapter_class = PLATFORM_ADAPTERS.get(platform)
        if not adapter_class:
            raise HTTPException(status_code=404, detail=f"Adapter for platform {platform} not found")
        
        adapter = adapter_class(platform, {
            "oauth_config": platform_config.oauth_config,
            "litellm_config": platform_config.litellm_config,
            "quota_config": platform_config.quota_config,
        })
        
        if not adapter.validate_credentials(credentials):
            raise HTTPException(status_code=400, detail="凭证验证失败")
        
        # 加密凭证
        from app.services.oauth.encryption import encrypt_credentials
        encrypted_credentials = encrypt_credentials(credentials)
        
        # 检查是否已存在账号
        from sqlalchemy import and_
        from app.models.oauth_account import OAuthAccount
        existing_account = db.query(OAuthAccount).filter(
            and_(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.platform == platform
            )
        ).first()
        
        if existing_account:
            # 更新现有账号
            existing_account.credentials = encrypted_credentials
            existing_account.account_name = account_name or existing_account.account_name
            existing_account.is_active = True
            existing_account.is_expired = False
            existing_account.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_account)
            
            # 关闭会话
            await oauth_session_manager.remove_session(current_user.id, platform)
            
            return existing_account
        
        # 创建新账号
        quota_limit = adapter.get_quota_limit()
        
        from datetime import datetime
        account = OAuthAccount(
            user_id=current_user.id,
            platform=platform,
            account_name=account_name or f"{platform}_account",
            credentials=encrypted_credentials,
            is_active=True,
            is_expired=False,
            quota_used=0,
            quota_limit=quota_limit,
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        # 关闭会话
        await oauth_session_manager.remove_session(current_user.id, platform)
        
        return account
        
    except Exception as e:
        print(f"OAuth授权完成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts/manual", response_model=OAuthAccountResponse)
async def create_account_manual(
    data: OAuthAccountManualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manual cookie submit for OAuth account
    """
    try:
        credentials = {
            "cookies": data.cookies,
            "tokens": data.tokens or {},
            "user_agent": data.user_agent or "",
        }
        account = oauth_service.create_or_update_account_with_credentials(
            db=db,
            user_id=current_user.id,
            platform=data.platform,
            account_name=data.account_name,
            credentials=credentials,
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts", response_model=List[OAuthAccountResponse])
async def get_accounts(
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户的OAuth账号列表
    """
    accounts = oauth_service.get_user_accounts(
        db=db,
        user_id=current_user.id,
        platform=platform,
        is_active=is_active,
    )

    result = []
    for account in accounts:
        account_dict = OAuthAccountResponse.from_orm(account).dict()
        # 获取平台配置信息
        platform_config = db.query(PlatformConfig).filter(
            PlatformConfig.platform_id == account.platform
        ).first()
        if platform_config:
            account_dict["platform_name"] = platform_config.platform_name
            account_dict["platform_icon"] = platform_config.platform_icon
        result.append(account_dict)

    return result


@router.get("/accounts/{account_id}", response_model=OAuthAccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取OAuth账号详情
    """
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account_dict = OAuthAccountResponse.from_orm(account).dict()
    # 获取平台配置信息
    platform_config = db.query(PlatformConfig).filter(
        PlatformConfig.platform_id == account.platform
    ).first()
    if platform_config:
        account_dict["platform_name"] = platform_config.platform_name
        account_dict["platform_icon"] = platform_config.platform_icon

    return account_dict


@router.put("/accounts/{account_id}", response_model=OAuthAccountResponse)
async def update_account(
    account_id: int,
    data: OAuthAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新OAuth账号
    """
    try:
        account = oauth_service.update_account(
            db=db,
            account_id=account_id,
            user_id=current_user.id,
            **data.dict(exclude_unset=True),
        )
        
        return account
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除OAuth账号
    """
    success = oauth_service.delete_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"message": "Account deleted successfully"}


@router.post("/accounts/{account_id}/check")
async def check_account_validity(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    检查账号凭证是否有效
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    is_valid = await oauth_service.check_account_validity(
        db=db,
        account_id=account_id,
    )
    
    return {
        "is_valid": is_valid,
        "message": "Account is valid" if is_valid else "Account credentials expired"
    }


@router.get("/accounts/{account_id}/usage", response_model=List[OAuthUsageLogResponse])
async def get_usage_logs(
    account_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取账号使用日志
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    logs = oauth_service.get_usage_logs(
        db=db,
        account_id=account_id,
        limit=limit,
    )
    
    return logs


@router.get("/accounts/{account_id}/models")
async def get_available_models(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取账号可用的模型列表
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    models = litellm_proxy.get_available_models(
        db=db,
        account_id=account_id,
    )
    
    return {"models": models}


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    data: ChatCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    执行聊天完成（使用OAuth账号）
    
    这个接口使用用户绑定的OAuth账号调用AI模型
    """
    # 验证账号所有权
    account = oauth_service.get_account(
        db=db,
        account_id=data.account_id,
        user_id=current_user.id,
    )
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        response = await litellm_proxy.chat_completion(
            db=db,
            account_id=data.account_id,
            messages=data.messages,
            model=data.model,
            stream=data.stream,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            top_p=data.top_p,
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
