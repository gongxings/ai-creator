"""
临时测试豆包图片生成 - 使用用户提供的curl信息
"""
import asyncio
import httpx
import json
import uuid
import re

async def test_doubao_image():
    # 从curl中提取的完整Cookie
    cookies = {
        "i18next": "zh",
        "s_v_web_id": "verify_mlb4q9tv_mxSPv0i4_o7Ax_41Ga_8cIo_hvMcGZd0o4kg",
        "passport_csrf_token": "f28e3fca407e5f3f6e06edc70d9abd20",
        "passport_csrf_token_default": "f28e3fca407e5f3f6e06edc70d9abd20",
        "odin_tt": "d9801661723aeaa4c06785e96b760d00b13ab48857f1364c31e5491f574b5aa96b0c56a9cef8f8af6669ae018f223f6a8da48f202ed6fd0038d69ee53aa9e4e1",
        "n_mh": "qYda4-0WJvO1DEPc-KFvRHGbPI8IGJvmKre0HqTGIeA",
        "sid_guard": "d2da92c1a72c8667b8dce3a04f0c44a4|1770397128|2592000|Sun,+08-Mar-2026+16:58:48+GMT",
        "uid_tt": "d81450d504ea0cd1d1ee8bfbc3e2e460",
        "uid_tt_ss": "d81450d504ea0cd1d1ee8bfbc3e2e460",
        "sid_tt": "d2da92c1a72c8667b8dce3a04f0c44a4",
        "sessionid": "d2da92c1a72c8667b8dce3a04f0c44a4",
        "sessionid_ss": "d2da92c1a72c8667b8dce3a04f0c44a4",
        "session_tlb_tag": "sttt|15|0tqSwacshme43OOgTwxEpP_________1rNRzxO0q8OaZQBXAYbVW7DEGNpnn0VbyGVH_v5C4UZ0%3D",
        "is_staff_user": "false",
        "sid_ucp_v1": "1.0.0-KDVjZmEzZWViYTI3OGJjNTdhNmYyZjEwZGI0MzcyYmE3MzhjNjcxZGEKHwjLtdCKwcwVEMi7mMwGGMKxHiAMMKSshLIGOAdA9AcaAmhsIiBkMmRhOTJjMWE3MmM4NjY3YjhkY2UzYTA0ZjBjNDRhNA",
        "ssid_ucp_v1": "1.0.0-KDVjZmEzZWViYTI3OGJjNTdhNmYyZjEwZGI0MzcyYmE3MzhjNjcxZGEKHwjLtdCKwcwVEMi7mMwGGMKxHiAMMKSshLIGOAdA9AcaAmhsIiBkMmRhOTJjMWE3MmM4NjY3YjhkY2UzYTA0ZjBjNDRhNA",
        "gd_random": "eyJtYXRjaCI6ZmFsc2UsInBlcmNlbnQiOjAuODQ4MDkxOTAyMzUzNTExMX0=.wswEm5fIuHQ7eQ45mJVU/UNy+jxh6eF6xTK+fDgqXGY=",
        "ttwid": "1%7Cr7bpEwXogIBm3yVPRhk_itXFct2gOEVk4B0nHIA86gg%7C1770479514%7Cc512747bd8e7cde5dc0464f11140038eec170ed5703139000d4b4d4e3ba3b1dc",
        "passport_fe_beating_status": "true",
        "flow_ssr_sidebar_expand": "1"
    }

    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        "Cookie": cookie_str,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://www.doubao.com",
        "Referer": "https://www.doubao.com/chat/38410505787510530",
        "last-event-id": "undefined",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "agw-js-conv": "str, str",
        "x-flow-trace": "04-0010429d8da86a8000025a5f230d4a1d-001cb63a9c8f8703-01"
    }

    payload = {
        "messages": [{
            "content": json.dumps({
                "text": "帮我生成图片：比基尼美女沙滩",
                "model": "Seedream 4.5",
                "template_type": "placeholder",
                "use_creation": False
            }),
            "content_type": 2009,
            "attachments": []
        }],
        "completion_option": {
            "is_regen": False,
            "with_suggest": False,
            "need_create_conversation": False,
            "launch_stage": 1,
            "is_replace": False,
            "is_delete": False,
            "is_ai_playground": False,
            "message_from": 0,
            "action_bar_skill_id": 3,
            "use_auto_cot": False,
            "resend_for_regen": False,
            "enable_commerce_credit": False,
            "event_id": "0"
        },
        "evaluate_option": {
            "web_ab_params": ""
        },
        "section_id": str(uuid.uuid4().int % 10**17),
        "conversation_id": "38410505787510530",
        "local_message_id": str(uuid.uuid4()),
        "stream": False
    }

    params = {
        "aid": "497858",
        "device_id": "7603797591654303251",
        "device_platform": "web",
        "fp": "verify_mlb4q9tv_mxSPv0i4_o7Ax_41Ga_8cIo_hvMcGZd0o4kg",
        "language": "zh",
        "pc_version": "3.5.1",
        "pkg_type": "release_version",
        "real_aid": "497858",
        "region": "",
        "samantha_web": "1",
        "sys_region": "",
        "tea_uuid": "7603797621974681123",
        "use-olympus-account": "1",
        "version_code": "20800",
        "web_id": "7603797621974681123",
        "web_tab_id": str(uuid.uuid4()),
        "msToken": "ZY8kIt-mbW2QcfWAsmHmi9nt5AQBn4ck84bE0lXo2mFr-cdB7-kuE0vv5QfGzEiTlW4BvaUOoiTHdKiweqLbtMjgKFL7OKMDWwG32CQecJ36GbLIZY3zLrscgnC5glk1dhr00LLDqcB30LBzFvuGnQ24DJX9hJk%3D",
        "a_bogus": "EX4VDzUwEp%2FbadMb8Cswelq5J9YlrBWyElTdWC257Kz1ah0T1Q1DTbazbNOPLCSJjYkkieZH4jSoGdjP884ZXUZkzmhkSqwjIt%2FIV06LMqqdaMisgrmTSLUFKwMYlRGLa%2F2cE9RR1sMwgEQlIHxolNVG75FERmYpbqeCdqTyaDCWpBgT9xADSWg%3D"
    }

    print("Testing Doubao image generation with stream response...")
    print(f"Conversation ID: {payload['conversation_id']}")

    images = []
    text_content = ""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://www.doubao.com/samantha/chat/completion",
                headers=headers,
                json=payload,
                params=params,
                timeout=120.0,
            ) as response:
                print(f"\nResponse status: {response.status_code}")

                if response.status_code != 200:
                    body = await response.aread()
                    print(f"ERROR: HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}")
                    return

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                    else:
                        data_str = line.strip()
                    if not data_str or data_str == "[DONE]":
                        continue

                    try:
                        data = json.loads(data_str)
                        event_type = data.get("event_type")
                        event_data_str = data.get("event_data", "")

                        # 解析event_data
                        if event_data_str:
                            try:
                                event_data = json.loads(event_data_str)
                            except:
                                print(f"[DEBUG] Failed to parse event_data: {event_data_str[:100]}...")
                                continue
                        else:
                            continue

                        print(f"[DEBUG] event_type={event_type}, event_data keys={list(event_data.keys())}")

                        # event_type 2001 = 消息事件
                        if event_type == 2001:
                            message = event_data.get("message", {})
                            message_content = message.get("content", "")
                            content_type = message.get("content_type")

                            print(f"[DEBUG] message content_type={content_type}, content={message_content[:50]}...")

                            # 解析message content（也是JSON）
                            try:
                                msg_obj = json.loads(message_content)
                                text_parts = msg_obj.get("text", "")
                                text_content += text_parts

                                print(f"[DEBUG] msg_obj keys={list(msg_obj.keys())}")

                                # event_type 2074 = 图片生成结果
                                if content_type == 2074:
                                    # 图片数据在message_content中
                                    try:
                                        image_data = json.loads(message_content)
                                        print(f"[DEBUG] image_data keys={list(image_data.keys())}")
                                        creations = image_data.get("creations", [])

                                        for creation in creations:
                                            if creation.get("type") == 1:  # 图片类型
                                                image_info = creation.get("image", {})
                                                print(f"[DEBUG] image_info keys={list(image_info.keys())}")
                                                # 优先使用image_ori_raw（无水印）
                                                image_url = (
                                                    image_info.get("image_ori_raw", {})
                                                    .get("url") or
                                                    image_info.get("image_ori", {})
                                                    .get("url") or
                                                    image_info.get("image_thumb", {})
                                                    .get("url")
                                                )
                                                if image_url:
                                                    # 清理URL参数
                                                    clean_url = image_url.split("?")[0]
                                                    if clean_url not in images:
                                                        images.append(clean_url)
                                                        print(f"\n✅ Found image: {clean_url[:80]}...")
                                    except json.JSONDecodeError as e:
                                        print(f"[DEBUG] Failed to parse image data: {e}")
                            except json.JSONDecodeError:
                                pass

                        # event_type 2003 = 流结束
                        if event_type == 2003:
                            print("\nStream finished")
                            break

                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n" + "="*50)
    print(f"生成完成！共获取 {len(images)} 张图片")
    print(f"="*50)
    for i, img in enumerate(images, 1):
        print(f"{i}. {img}")

if __name__ == "__main__":
    asyncio.run(test_doubao_image())
