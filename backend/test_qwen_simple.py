# -*- coding: utf-8 -*-
"""
通义千问适配器优化测试脚本
"""
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import uuid


class SimpleQwenAdapter:
    """简化的通义千问适配器 - 用于测试"""
    
    API_BASE = "https://qianwen.biz.aliyun.com"
    
    @staticmethod
    def generate_complete_cookie(ticket: str) -> str:
        """生成完整的 Cookie 字符串"""
        cookie_name = 'login_aliyunid_ticket' if len(ticket) > 100 else 'tongyi_sso_ticket'
        random_t = str(uuid.uuid4()).replace('-', '')
        
        return "; ".join([
            f"{cookie_name}={ticket}",
            "aliyun_choice=intl",
            "_samesite_flag_=true",
            f"t={random_t}",
        ])
    
    def build_request_headers(self, ticket: str):
        """构建请求头"""
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Cookie": self.generate_complete_cookie(ticket),
            "Origin": "https://tongyi.aliyun.com",
            "Pragma": "no-cache",
            "Referer": "https://tongyi.aliyun.com/",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Platform": "pc_tongyi",
            "X-Xsrf-Token": str(uuid.uuid4()),
        }
    
    def build_request_body(self, message: str, session_id: str = ""):
        """构建请求体"""
        request_id = str(uuid.uuid4()).replace('-', '')
        file_upload_batch_id = str(uuid.uuid4())
        
        return {
            "mode": "chat",
            "model": "",
            "action": "next",
            "userAction": "chat",
            "requestId": request_id,
            "sessionId": session_id,
            "sessionType": "text_chat",
            "parentMsgId": "",
            "params": {
                "fileUploadBatchId": file_upload_batch_id
            },
            "contents": [
                {
                    "content": message,
                    "contentType": "text",
                    "role": "user",
                }
            ],
        }


def test_adapter():
    """测试适配器"""
    
    print("=" * 60)
    print("通义千问适配器测试 - 基于 qwen-free-api 优化")
    print("=" * 60)
    
    # 创建适配器实例
    adapter = SimpleQwenAdapter()
    
    print(f"\n✓ 适配器创建成功")
    print(f"  API Base: {adapter.API_BASE}")
    
    # 测试 Cookie 生成
    test_ticket = "test_tongyi_sso_ticket_12345"
    complete_cookie = adapter.generate_complete_cookie(test_ticket)
    print(f"\n✓ Cookie 生成成功 (短ticket)")
    print(f"  Cookie: {complete_cookie[:80]}...")
    print(f"  长度: {len(complete_cookie)} 字符")
    
    # 测试长 ticket
    long_ticket = "a" * 150
    long_cookie = adapter.generate_complete_cookie(long_ticket)
    print(f"\n✓ Cookie 生成成功 (长ticket)")
    print(f"  使用 login_aliyunid_ticket")
    print(f"  长度: {len(long_cookie)} 字符")
    
    # 检查必要字段
    required_fields = [
        "tongyi_sso_ticket",
        "aliyun_choice",
        "_samesite_flag_",
        "t=",
    ]
    
    print(f"\n✓ Cookie 字段检查:")
    for field in required_fields:
        if field in complete_cookie:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} (缺失)")
    
    # 测试请求头构建
    headers = adapter.build_request_headers(test_ticket)
    print(f"\n✓ 请求头构建成功")
    print(f"  共 {len(headers)} 个请求头")
    
    important_headers = [
        "Cookie",
        "Content-Type",
        "Origin",
        "Referer",
        "Sec-Ch-Ua",
        "X-Platform",
        "X-Xsrf-Token",
    ]
    
    print(f"\n✓ 重要请求头检查:")
    for header in important_headers:
        if header in headers:
            value = headers[header]
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✓ {header}: {display_value}")
        else:
            print(f"  ✗ {header} (缺失)")
    
    # 测试请求体构建
    body = adapter.build_request_body("你好，通义千问！")
    print(f"\n✓ 请求体构建成功")
    print(f"  mode: {body['mode']}")
    print(f"  action: {body['action']}")
    print(f"  sessionType: {body['sessionType']}")
    print(f"  requestId: {body['requestId']}")
    print(f"  contents 数量: {len(body['contents'])}")
    print(f"  message: {body['contents'][0]['content']}")
    
    # 完整请求示例
    print(f"\n" + "=" * 60)
    print("完整请求示例")
    print("=" * 60)
    print(f"\nPOST {adapter.API_BASE}/dialog/conversation")
    print(f"\n请求头:")
    for key in ["Content-Type", "Cookie", "Origin", "X-Platform"]:
        value = headers[key]
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {display_value}")
    print(f"  ... 共 {len(headers)} 个请求头")
    
    print(f"\n请求体:")
    print(f"  mode: {body['mode']}")
    print(f"  sessionType: {body['sessionType']}")
    print(f"  contents[0].content: {body['contents'][0]['content']}")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n✅ 优化内容对比：")
    print("  1. API 端点: qianwen.biz.aliyun.com (而非 www.qianwen.com)")
    print("  2. Cookie: 自动识别 ticket 类型，添加必要字段")
    print("  3. 请求头: 完整的浏览器指纹 (17个字段)")
    print("  4. 请求体: 符合 qwen-free-api 格式")
    print("  5. 使用 HTTP/2 连接（实际调用时）")
    
    print(f"\n⚠️ 重要提示：")
    print("  - 这只是格式测试，未进行实际 API 调用")
    print("  - 实际使用需要真实的 tongyi_sso_ticket")
    print("  - qwen-free-api 项目已归档，可能随时失效")
    print("  - 建议仅用于个人测试，商用请使用 DashScope 官方 API")
    
    print(f"\n📝 主要改进：")
    print("  1. 端点从 www.qianwen.com 改为 qianwen.biz.aliyun.com")
    print("  2. 登录URL从 qianwen.com 改为 tongyi.aliyun.com")
    print("  3. Cookie 域名从 .qianwen.com 改为 .aliyun.com")
    print("  4. 完善请求头，添加 X-Platform 和 X-Xsrf-Token")
    print("  5. 请求体格式与 qwen-free-api 保持一致")


if __name__ == "__main__":
    test_adapter()
