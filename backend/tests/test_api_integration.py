# -*- coding: utf-8 -*-
"""
API Key功能集成测试
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# 测试用户凭证（需要先注册或使用已有用户）
TEST_USER = {
    "username": "test_user",
    "password": "test123456"
}

def print_response(title, response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def test_auth():
    """测试认证"""
    print("\n开始测试认证...")
    
    # 1. 注册用户（如果不存在）
    register_data = {
        "username": TEST_USER["username"],
        "email": f"{TEST_USER['username']}@test.com",
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{API_V1}/auth/register", json=register_data)
    print_response("注册用户", response)
    
    # 2. 登录
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{API_V1}/auth/login", json=login_data)
    print_response("用户登录", response)
    
    if response.status_code == 200:
        token = response.json()["data"]["access_token"]
        return token
    else:
        print("登录失败，无法继续测试")
        return None


def test_api_keys(token):
    """测试API Key管理"""
    print("\n开始测试API Key管理...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 创建API Key
    create_data = {
        "key_name": "测试API Key",
        "expires_days": 30,
        "rate_limit": 60,
        "allowed_models": []
    }
    response = requests.post(f"{API_V1}/api-keys", json=create_data, headers=headers)
    print_response("创建API Key", response)
    
    if response.status_code != 200:
        print("创建API Key失败，无法继续测试")
        return None
    
    api_key_id = response.json()["data"]["id"]
    api_key = response.json()["data"]["api_key"]
    
    # 2. 获取API Key列表
    response = requests.get(f"{API_V1}/api-keys", headers=headers)
    print_response("获取API Key列表", response)
    
    # 3. 获取单个API Key详情
    response = requests.get(f"{API_V1}/api-keys/{api_key_id}", headers=headers)
    print_response("获取API Key详情", response)
    
    # 4. 更新API Key
    update_data = {
        "key_name": "更新后的API Key",
        "rate_limit": 120
    }
    response = requests.put(f"{API_V1}/api-keys/{api_key_id}", json=update_data, headers=headers)
    print_response("更新API Key", response)
    
    # 5. 获取API Key统计
    response = requests.get(f"{API_V1}/api-keys/{api_key_id}/stats", headers=headers)
    print_response("获取API Key统计", response)
    
    return api_key, api_key_id


def test_models(token):
    """测试模型管理"""
    print("\n开始测试模型管理...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取可用模型列表
    response = requests.get(f"{API_V1}/ai/models/available", headers=headers)
    print_response("获取可用模型列表", response)
    
    # 2. 获取写作场景的模型
    response = requests.get(f"{API_V1}/ai/models/available?scene_type=writing", headers=headers)
    print_response("获取写作场景模型", response)


def test_openapi_proxy(api_key):
    """测试OpenAPI代理"""
    print("\n开始测试OpenAPI代理...")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 1. 获取模型列表
    response = requests.get(f"{BASE_URL}/v1/models", headers=headers)
    print_response("OpenAPI - 获取模型列表", response)
    
    # 2. 聊天完成（需要有可用的模型）
    # 注意：这个测试可能会失败，因为需要实际的OAuth账号或AI模型配置
    chat_data = {
        "model": "test-model",  # 需要替换为实际的模型ID
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=chat_data, headers=headers)
    print_response("OpenAPI - 聊天完成", response)


def test_delete_api_key(token, api_key_id):
    """测试删除API Key"""
    print("\n开始测试删除API Key...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{API_V1}/api-keys/{api_key_id}", headers=headers)
    print_response("删除API Key", response)


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("API Key功能集成测试")
    print("="*60)
    
    # 1. 测试认证
    token = test_auth()
    if not token:
        return
    
    # 2. 测试模型管理
    test_models(token)
    
    # 3. 测试API Key管理
    result = test_api_keys(token)
    if not result:
        return
    
    api_key, api_key_id = result
    
    # 4. 测试OpenAPI代理
    test_openapi_proxy(api_key)
    
    # 5. 测试删除API Key
    test_delete_api_key(token, api_key_id)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()
