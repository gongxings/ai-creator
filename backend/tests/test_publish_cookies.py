# -*- coding: utf-8 -*-
from datetime import datetime


def _build_mock_publisher():
    class MockPublisher:
        def get_platform_name(self):
            return '΢Źƽ̨'

        def get_login_url(self):
            return 'https://mp.weixin.qq.com/'

        def set_cookies(self, account, cookies):
            account.cookies = 'encrypted-mock'
            account.cookies_updated_at = datetime.utcnow()
            account.cookies_valid = 'unknown'
            account._plain_cookies = cookies

        def get_cookies(self, account):
            return getattr(account, '_plain_cookies', None)

        async def validate_cookies(self, account):
            return bool(getattr(account, '_plain_cookies', None))

    return MockPublisher()


def test_submit_publish_cookies(client, auth_headers, monkeypatch):
    from app.api.v1 import publish as publish_api

    monkeypatch.setattr(publish_api, 'get_platform', lambda _platform: _build_mock_publisher())

    response = client.post(
        '/api/v1/publish/platforms/accounts/cookie-submit',
        headers=auth_headers,
        json={
            'platform': 'wechat',
            'account_name': 'test_wechat_account',
            'cookies': {'sessionid': 'abc123'},
            'user_agent': 'pytest-agent',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['platform'] == 'wechat'
    assert data['account_name'] == 'test_wechat_account'
    assert data['cookies_valid'] in ('valid', 'invalid', 'unknown')


def test_validate_publish_cookies_page_contains_query_support(client, auth_headers, monkeypatch):
    from app.api.v1 import publish as publish_api

    monkeypatch.setattr(publish_api, 'get_platform', lambda _platform: _build_mock_publisher())

    response = client.get('/api/v1/publish/platforms/accounts/cookie-validate/wechat?account_name=my_acc', headers=auth_headers)
    assert response.status_code == 200
    html = response.text
    assert 'account_name' in html
    assert 'URLSearchParams' in html
