"""
Playwright WebSocket utilities exported under the `pw_service` namespace.
"""
from typing import Any, Awaitable, Callable, Dict

from app.services.oauth.playwright_service import (
    capture_screenshot as _capture_screenshot,
    navigate_to as _navigate_to,
    click_element as _click_element,
    input_text as _input_text,
    execute_script as _execute_script,
    get_current_url as _get_current_url,
    start_screenshot_stream as _start_screenshot_stream,
    stop_screenshot_stream as _stop_screenshot_stream,
    playwright_service,
)

async def capture_screenshot(platform: str, user_id: int = 1) -> Any:
    return await _capture_screenshot(platform, user_id=user_id)

async def navigate_to(platform: str, url: str, user_id: int = 1) -> bool:
    return await _navigate_to(platform, url, user_id=user_id)

async def click_element(platform: str, selector: str, user_id: int = 1) -> bool:
    return await _click_element(platform, selector, user_id=user_id)

async def input_text(platform: str, selector: str, text: str, user_id: int = 1) -> bool:
    return await _input_text(platform, selector, text, user_id=user_id)

async def execute_script(platform: str, script: str, user_id: int = 1) -> Any:
    return await _execute_script(platform, script, user_id=user_id)

async def get_current_url(platform: str, user_id: int = 1) -> str:
    return await _get_current_url(platform, user_id=user_id)

async def start_screenshot_stream(
    platform: str,
    callback: Callable[[str], Awaitable[None]],
    interval_ms: int = 2000,
    user_id: int = 1,
) -> None:
    await _start_screenshot_stream(platform, callback, interval_ms=interval_ms, user_id=user_id)

async def stop_screenshot_stream(platform: str, user_id: int = 1) -> None:
    await _stop_screenshot_stream(platform, user_id=user_id)

async def authorize_platform(
    platform_meta: Dict[str, Any],
    on_progress: Callable[[str, Dict[str, Any]], Awaitable[None]],
) -> Dict[str, Any]:
    return await playwright_service.authorize_platform(platform_meta, on_progress)

__all__ = [
    "capture_screenshot",
    "navigate_to",
    "click_element",
    "input_text",
    "execute_script",
    "get_current_url",
    "start_screenshot_stream",
    "stop_screenshot_stream",
    "authorize_platform",
]
