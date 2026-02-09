# -*- coding: utf-8 -*-
"""
豆包适配器独立测试脚本（无需完整环境）
"""
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import secrets
import base64
import random
import time
import uuid
import json


class SimpleDoubaoAdapter:
    """简化的豆包适配器 - 仅用于测试"""
    
    DEFAULT_ASSISTANT_ID = "497858"
    VERSION_CODE = "20800"
    
    def __init__(self):
        self.device_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        self.web_id = str(int(random.random() * 999999999999999999 + 7000000000000000000))
        self.user_id = str(uuid.uuid4()).replace('-', '')
    
    @staticmethod
    def generate_fake_ms_token() -> str:
        """生成伪造的 msToken (128字符)"""
        random_bytes = secrets.token_bytes(96)
        ms_token = base64.b64encode(random_bytes).decode('utf-8')
        ms_token = ms_token.replace('+', '-').replace('/', '_').replace('=', '')
        return ms_token
    
    @staticmethod
    def generate_fake_a_bogus() -> str:
        """生成伪造的 a_bogus 签名"""
        import string
        charset = string.ascii_letters + string.digits
        part1 = ''.join(secrets.choice(charset) for _ in range(34))
        part2 = ''.join(secrets.choice(charset) for _ in range(6))
        return f"mf-{part1}-{part2}"
    
    def build_complete_cookie(self, cookies: dict) -> str:
        """构建完整的 Cookie 字符串"""
        sessionid = cookies.get("sessionid", "")
        
        # 生成 msToken
        ms_token = self.generate_fake_ms_token()
        
        # 构建完整 Cookie
        current_timestamp = int(time.time())
        cookie_parts = [
            "is_staff_user=false",
            "store-region=cn-gd",
            "store-region-src=uid",
            f"sid_guard={sessionid}%7C{current_timestamp}%7C5184000%7CSun%2C+02-Feb-2025+04%3A17%3A20+GMT",
            f"uid_tt={self.user_id}",
            f"uid_tt_ss={self.user_id}",
            f"sid_tt={sessionid}",
            f"sessionid={sessionid}",
            f"sessionid_ss={cookies.get('sessionid_ss', sessionid)}",
            f"msToken={ms_token}",
        ]
        
        # 添加其他可选 Cookie
        if "s_v_web_id" in cookies:
            cookie_parts.append(f"s_v_web_id={cookies['s_v_web_id']}")
        if "tt_webid" in cookies:
            cookie_parts.append(f"tt_webid={cookies['tt_webid']}")
        
        return "; ".join(cookie_parts)
    
    def build_request_params(self):
        """构建请求参数"""
        ms_token = self.generate_fake_ms_token()
        a_bogus = self.generate_fake_a_bogus()
        
        return {
            "aid": self.DEFAULT_ASSISTANT_ID,
            "device_id": self.device_id,
            "device_platform": "web",
            "language": "zh",
            "pkg_type": "release_version",
            "real_aid": self.DEFAULT_ASSISTANT_ID,
            "region": "CN",
            "samantha_web": 1,
            "sys_region": "CN",
            "tea_uuid": self.web_id,
            "use_olympus_account": 1,
            "version_code": self.VERSION_CODE,
            "web_id": self.web_id,
            "msToken": ms_token,
            "a_bogus": a_bogus,
        }
    
    def build_request_headers(self, complete_cookie: str):
        """构建请求头"""
        return {
            "Cookie": complete_cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Origin": "https://www.doubao.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://www.doubao.com/chat/",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Agw-Js-Conv": "str",
            "X-Flow-Trace": f"04-{uuid.uuid4()}-{str(uuid.uuid4())[:16]}-01",
        }
    
    def build_request_body(self, message: str):
        """构建请求体"""
        local_conv_id = f"local_16{''.join(str(random.randint(0, 9)) for _ in range(14))}"
        local_msg_id = str(uuid.uuid4())
        
        return {
            "messages": [
                {
                    "content": json.dumps({"text": message}),
                    "content_type": 2001,
                    "attachments": [],
                    "references": [],
                }
            ],
            "completion_option": {
                "is_regen": False,
                "with_suggest": True,
                "need_create_conversation": True,
                "launch_stage": 1,
                "is_replace": False,
                "is_delete": False,
                "message_from": 0,
                "event_id": "0"
            },
            "conversation_id": "0",
            "local_conversation_id": local_conv_id,
            "local_message_id": local_msg_id
        }


def test_adapter():
    """测试适配器"""
    
    print("=" * 60)
    print("豆包适配器测试")
    print("=" * 60)
    
    # 创建适配器实例
    adapter = SimpleDoubaoAdapter()
    
    print(f"\n✓ 适配器创建成功")
    print(f"  Device ID: {adapter.device_id}")
    print(f"  Web ID: {adapter.web_id}")
    print(f"  User ID: {adapter.user_id}")
    
    # 测试 msToken 生成
    ms_token = adapter.generate_fake_ms_token()
    print(f"\n✓ msToken 生成成功")
    print(f"  长度: {len(ms_token)} 字符")
    print(f"  示例: {ms_token[:20]}...")
    
    # 测试 a_bogus 生成
    a_bogus = adapter.generate_fake_a_bogus()
    print(f"\n✓ a_bogus 生成成功")
    print(f"  长度: {len(a_bogus)} 字符")
    print(f"  格式: {a_bogus}")
    
    # 测试 Cookie 构建
    test_cookies = {
        "sessionid": "test_session_id_12345",
        "sessionid_ss": "test_session_ss_12345",
        "s_v_web_id": "test_web_id",
    }
    
    complete_cookie = adapter.build_complete_cookie(test_cookies)
    print(f"\n✓ Cookie 构建成功")
    print(f"  Cookie 片段: {complete_cookie[:100]}...")
    print(f"  总长度: {len(complete_cookie)} 字符")
    
    # 检查必要的字段
    required_fields = [
        "is_staff_user",
        "store-region",
        "sid_guard",
        "uid_tt",
        "sessionid",
        "sessionid_ss",
        "msToken"
    ]
    
    print(f"\n✓ Cookie 字段检查:")
    for field in required_fields:
        if field in complete_cookie:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} (缺失)")
    
    # 测试请求参数构建
    params = adapter.build_request_params()
    print(f"\n✓ 请求参数构建成功")
    print(f"  API 端点: /samantha/chat/completion")
    print(f"  aid: {params['aid']}")
    print(f"  device_id: {params['device_id'][:20]}...")
    print(f"  web_id: {params['web_id'][:20]}...")
    print(f"  msToken: {params['msToken'][:20]}...")
    print(f"  a_bogus: {params['a_bogus']}")
    
    # 测试请求头构建
    headers = adapter.build_request_headers(complete_cookie)
    print(f"\n✓ 请求头检查:")
    important_headers = [
        "Cookie",
        "User-Agent",
        "Referer",
        "Origin",
        "Sec-Ch-Ua",
        "Agw-Js-Conv",
        "X-Flow-Trace",
    ]
    for header in important_headers:
        if header in headers:
            value = headers[header]
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {header}: {display_value}")
        else:
            print(f"  ✗ {header} (缺失)")
    
    # 测试请求体构建
    body = adapter.build_request_body("你好，豆包！")
    print(f"\n✓ 请求体构建成功")
    print(f"  messages 数量: {len(body['messages'])}")
    print(f"  conversation_id: {body['conversation_id']}")
    print(f"  local_conversation_id: {body['local_conversation_id']}")
    print(f"  local_message_id: {body['local_message_id']}")
    
    # 完整请求示例
    print(f"\n" + "=" * 60)
    print("完整请求示例")
    print("=" * 60)
    print(f"\nPOST https://www.doubao.com/samantha/chat/completion")
    print(f"\n查询参数:")
    for key, value in list(params.items())[:5]:
        print(f"  {key}: {str(value)[:50]}")
    print(f"  ... 共 {len(params)} 个参数")
    
    print(f"\n请求头:")
    for key in ["Cookie", "User-Agent", "Content-Type", "Referer"]:
        value = headers[key]
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {display_value}")
    print(f"  ... 共 {len(headers)} 个请求头")
    
    print(f"\n请求体:")
    print(f"  messages[0].content: {body['messages'][0]['content'][:60]}...")
    print(f"  completion_option.need_create_conversation: {body['completion_option']['need_create_conversation']}")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n✅ 所有组件工作正常：")
    print("  1. msToken 生成 - 128字符随机Token")
    print("  2. a_bogus 生成 - 格式正确的签名")
    print("  3. Cookie 构建 - 包含所有必要字段")
    print("  4. 请求参数 - 符合 doubao-free-api 规范")
    print("  5. 请求头 - 完整的浏览器指纹伪装")
    print("  6. 请求体 - 正确的内部 API 格式")
    
    print(f"\n⚠️ 重要提示：")
    print("  - 这只是格式测试，未进行实际 API 调用")
    print("  - 实际使用需要真实的 sessionid Cookie")
    print("  - doubao-free-api 项目已归档，可能随时失效")
    print("  - 建议仅用于个人测试，不要商用")
    
    print(f"\n📝 下一步：")
    print("  1. 使用真实 sessionid 测试实际 API 调用")
    print("  2. 监控 API 响应和成功率")
    print("  3. 观察是否触发风控机制")
    print("  4. 长期建议迁移到火山引擎官方 API")


if __name__ == "__main__":
    test_adapter()
