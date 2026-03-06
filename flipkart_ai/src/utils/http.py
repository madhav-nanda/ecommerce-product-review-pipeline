"""HTTP client utility with retries, backoff and throttling."""
import time
from typing import Optional

import requests

from src.config.settings import Settings


def get_with_retry(url: str, settings: Settings, params: Optional[dict] = None) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    delay = settings.request_sleep_seconds
    for attempt in range(1, settings.max_retries + 1):
        resp = requests.get(url, headers=headers, params=params, timeout=settings.request_timeout_seconds)
        if resp.status_code == 200:
            time.sleep(settings.request_sleep_seconds)
            return resp
        if resp.status_code in {403, 429} and attempt == settings.max_retries:
            raise RuntimeError(f"Blocked by source: status={resp.status_code}")
        time.sleep(delay)
        delay *= settings.backoff_factor
    raise RuntimeError("Request failed after max retries")
