# -*- coding: utf-8 -*-
"""
API Key功能手动测试脚本
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

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

def test_auth():
    """测试用户认证"""
    print("\n[TEST 1] 用户注册和登录")
    
    # # 注册用户
    # register_data = {
    #     "username": "testuser",
    #     "email": "test@example.com",
    #     "password": "Test123456"
    # }
    # response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    # print_response("注册用户", response)
    
    # 登录
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print_response("用户登录", response)
    
    if response.status_code == 200:
        token = response.json()["data"]["access_token"]
        return token
    return None

def test_create_api_key(token):
    """测试创建API Key"""
    print("\n[TEST 2] 创建API Key")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "key_name": "测试API Key",
        "expires_days": 30,
        "rate_limit": 60,
        "allowed_models": ["oauth_1_qwen-max", "ai_model_1"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/api-keys", json=data, headers=headers)
    print_response("创建API Key", response)
    
    if response.status_code == 200:
        api_key = response.json()["data"]["api_key"]
        key_id = response.json()["data"]["id"]
        return api_key, key_id
    return None, None

def test_list_api_keys(token):
    """测试获取API Key列表"""
    print("\n[TEST 3] 获取API Key列表")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/api-keys", headers=headers)
    print_response("API Key列表", response)

def test_get_api_key_stats(token, key_id):
    """测试获取API Key统计"""
    print("\n[TEST 4] 获取API Key统计")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/api-keys/{key_id}/stats", headers=headers)
    print_response("API Key统计", response)

def test_get_available_models(token):
    """测试获取可用模型列表"""
    print("\n[TEST 5] 获取可用模型列表")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/models/available", headers=headers)
    print_response("可用模型列表", response)

def test_openapi_models(api_key):
    """测试OpenAPI模型列表接口"""
    print("\n[TEST 6] OpenAPI - 获取模型列表")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{BASE_URL}/v1/models", headers=headers)
    print_response("OpenAPI模型列表", response)

def test_openapi_chat(api_key):
    """测试OpenAPI聊天接口"""
    print("\n[TEST 7] OpenAPI - 聊天完成（非流式）")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "oauth_1_qwen-max",
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ],
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data, headers=headers)
    print_response("OpenAPI聊天完成", response)

def test_ai_chat(token):
    """测试内部AI聊天接口"""
    print("\n[TEST 8] 内部API - AI聊天")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "model_id": "oauth_1_qwen-max",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "scene_type": "writing",
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/ai/chat", json=data, headers=headers)
    print_response("内部AI聊天", response)

def test_delete_api_key(token, key_id):
    """测试删除API Key"""
    print("\n[TEST 9] 删除API Key")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/v1/api-keys/{key_id}", headers=headers)
    print_response("删除API Key", response)

def main():
    """主测试流程"""
    print("="*60)
    print("API Key功能测试")
    print("="*60)
    
    try:
        # 1. 认证测试
        token = test_auth()
        if not token:
            print("\n[ERROR] 认证失败，无法继续测试")
            return
        
        # 2. 创建API Key
        api_key, key_id = test_create_api_key(token)
        if not api_key:
            print("\n[ERROR] 创建API Key失败，无法继续测试")
            return
        
        print(f"\n[INFO] 生成的API Key: {api_key}")
        
        # 3. 获取API Key列表
        test_list_api_keys(token)
        
        # 4. 获取API Key统计
        test_get_api_key_stats(token, key_id)
        
        # 5. 获取可用模型
        test_get_available_models(token)
        
        # 6. OpenAPI模型列表
        test_openapi_models(api_key)
        
        # 7. OpenAPI聊天（如果有可用的OAuth账号）
        # test_openapi_chat(api_key)
        
        # 8. 内部AI聊天（如果有可用的OAuth账号）
        # test_ai_chat(token)
        
        # 9. 删除API Key
        test_delete_api_key(token, key_id)
        
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
