"""
Run Doubao seedream image generation via a real Playwright session to avoid the direct API block.

Usage:
  1. `pip install playwright httpx`
  2. `playwright install chromium`
  3. Run `python scripts/test_doubao_playwright.py`
  4. Follow the prompt: log into Doubao, then press Enter to continue.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List

import httpx
from playwright.async_api import async_playwright

CHAT_URL = "https://www.doubao.com/chat/38410505787510530"
COMPLETION_URL = "https://www.doubao.com/samantha/chat/completion"


async def capture_session(login_url: str, headless: bool = False) -> Dict[str, Any]:
    """Open Playwright, let the user log in, then extract cookies/localStorage data."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(login_url)
        print("\nPlaywright browser is open. Log in to Doubao in the browser window.")
        await asyncio.get_event_loop().run_in_executor(
            None, input, "After signing in, press Enter to continue..."
        )
        cookies = await context.cookies()
        storage = await page.evaluate(
            """() => {
            const snapshot = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                snapshot[key] = localStorage.getItem(key);
            }
            return snapshot;
        }"""
        )
        user_agent = await page.evaluate("() => navigator.userAgent")
        await browser.close()
    return {"cookies": cookies, "storage": storage, "user_agent": user_agent}


def build_cookie_header(cookies: List[Dict[str, Any]]) -> str:
    """Construct Cookie header string limited to Doubao domains."""
    relevant = [
        f"{cookie['name']}={cookie['value']}"
        for cookie in cookies
        if "doubao.com" in cookie.get("domain", "")
    ]
    return "; ".join(relevant)


def build_payload() -> Dict[str, Any]:
    """Create payload for the seedream request."""
    return {
        "messages": [
            {
                "content": json.dumps(
                    {
                        "text": "Generate an imaginative illustration of a friendly turtle under a sunset.",
                        "model": "Seedream 4.5",
                        "template_type": "placeholder",
                        "use_creation": False,
                    }
                ),
                "content_type": 2009,
                "attachments": [],
            }
        ],
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
            "event_id": "0",
        },
        "evaluate_option": {"web_ab_params": ""},
        "section_id": str(uuid.uuid4().int % 10 ** 17),
        "conversation_id": "38410505787510530",
        "local_message_id": str(uuid.uuid4()),
        "stream": False,
    }


async def run_doubao_stream(session: Dict[str, Any]) -> List[str]:
    """Replay the Doubao SSE stream with the live cookies and storage data."""
    cookie_header = build_cookie_header(session["cookies"])
    ms_token = session["storage"].get("msToken")
    if not ms_token:
        raise RuntimeError("msToken was not found in localStorage after login.")

    headers = {
        "Cookie": cookie_header,
        "User-Agent": session["user_agent"],
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://www.doubao.com",
        "Referer": CHAT_URL,
        "last-event-id": "undefined",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "agw-js-conv": "str, str",
        "x-flow-trace": "04-0010429d8da86a8000025a5f230d4a1d-001cb63a9c8f8703-01",
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
        "msToken": ms_token,
        "a_bogus": "EX4VDzUwEp%2FbadMb8Cswelq5J9YlrBWyElTdWC257Kz1ah0T1Q1DTbazbNOPLCSJjYkkieZH4jSoGdjP884ZXUZkzmhkSqwjIt%2FIV06LMqqdaMisgrmTSLUFKwMYlRGLa%2F2cE9RR1sMwgEQlIHxolNVG75FERmYpbqeCdqTyaDCWpBgT9xADSWg%3D",
    }

    images: List[str] = []
    payload = build_payload()

    print("Sending completion request with live Playwright session...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST", COMPLETION_URL, headers=headers, json=payload, params=params, timeout=120.0
        ) as response:
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                body = await response.aread()
                raise RuntimeError(
                    f"Doubao responded with HTTP {response.status_code}: {body.decode(errors='ignore')}"
                )

            async for line in response.aiter_lines():
                if not line:
                    continue
                data_str = line[5:].strip() if line.startswith("data:") else line.strip()
                if not data_str or data_str == "[DONE]":
                    continue

                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event_type = data.get("event_type")
                event_data_str = data.get("event_data", "")

                if not event_data_str:
                    continue

                try:
                    event_data = json.loads(event_data_str)
                except json.JSONDecodeError:
                    print("Malformed event_data, skipping")
                    continue

                print(f"Received event {event_type} keys={list(event_data.keys())}")

                if event_type == 2005:
                    print("Doubao is still throttling this session. Try again later.")
                    break

                if event_type == 2001:
                    message = event_data.get("message", {})
                    content_type = message.get("content_type")
                    content = message.get("content", "")
                    if content_type == 2074:
                        try:
                            image_payload = json.loads(content)
                        except json.JSONDecodeError:
                            continue
                        creations = image_payload.get("creations", [])
                        for creation in creations:
                            if creation.get("type") != 1:
                                continue
                            image_info = creation.get("image", {})
                            image_url = (
                                image_info.get("image_ori_raw", {}).get("url")
                                or image_info.get("image_ori", {}).get("url")
                                or image_info.get("image_thumb", {}).get("url")
                            )
                            if image_url:
                                clean_url = image_url.split("?")[0]
                                if clean_url not in images:
                                    images.append(clean_url)
                                    print(f"Found image: {clean_url}")

                if event_type == 2003:
                    print("Stream ended.")
                    break

    return images


async def main() -> None:
    session = await capture_session(CHAT_URL, headless=False)
    images = await run_doubao_stream(session)
    print("\n" + "=" * 50)
    print(f"Collected {len(images)} image URLs:")
    for idx, url in enumerate(images, 1):
        print(f"{idx}. {url}")


if __name__ == "__main__":
    asyncio.run(main())
