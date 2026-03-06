"""Date normalization from relative strings."""
from __future__ import annotations

from datetime import datetime, timedelta
import re


def parse_relative_date(date_text_raw: str, scrape_timestamp_utc: str) -> datetime | None:
    if not date_text_raw:
        return None
    ref = datetime.fromisoformat(scrape_timestamp_utc.replace("Z", "+00:00"))
    text = date_text_raw.strip().lower()

    m = re.match(r"(\d+)\s+day", text)
    if m:
        return ref - timedelta(days=int(m.group(1)))
    m = re.match(r"(\d+)\s+month", text)
    if m:
        return ref - timedelta(days=30 * int(m.group(1)))
    m = re.match(r"(\d+)\s+year", text)
    if m:
        return ref - timedelta(days=365 * int(m.group(1)))

    for fmt in ["%d %b, %Y", "%d %B %Y", "%b, %Y"]:
        try:
            return datetime.strptime(date_text_raw.strip(), fmt)
        except ValueError:
            continue
    return None
