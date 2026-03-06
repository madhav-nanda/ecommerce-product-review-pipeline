"""HTML parser for Flipkart reviews pages."""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None

from src.utils.hashing import deterministic_review_id


def extract_product_metadata(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    product_slug = parsed.path.strip("/").split("/")[0]
    product_id = parse_qs(parsed.query).get("pid", ["unknown"])[0]
    return product_id, product_slug


def _regex_parse(html: str, source_url: str, page_number: int) -> list[dict[str, Any]]:
    product_id, product_slug = extract_product_metadata(source_url)
    scrape_ts = datetime.now(timezone.utc).isoformat()
    cards = re.findall(r'<div class="_27M-vq">(.*?)</div>\s*</div>?', html, flags=re.S)
    results: list[dict[str, Any]] = []
    for card in cards:
        def _grab(pattern: str) -> str:
            m = re.search(pattern, card, flags=re.S)
            return re.sub("<.*?>", "", m.group(1)).strip() if m else ""
        rating_txt = _grab(r'<div class="_3LWZlK">(.*?)</div>')
        title_val = _grab(r'<p class="_2-N8zT">(.*?)</p>')
        text_val = _grab(r'<div class="t-ZTKy"><div>(.*?)</div>')
        reviewer_val = _grab(r'<p class="_2sc7ZR _2V5EHH">(.*?)</p>') or "unknown"
        meta = re.findall(r'<p class="_2sc7ZR">(.*?)</p>', card, flags=re.S)
        location_raw = meta[0].strip() if len(meta) > 0 else ""
        date_text_raw = meta[1].strip() if len(meta) > 1 else ""
        review_id = deterministic_review_id(product_id, reviewer_val, title_val, text_val, date_text_raw)
        results.append({"review_id": review_id, "product_id": product_id, "product_slug": product_slug, "rating": int(rating_txt) if rating_txt.isdigit() else None, "title": title_val, "review_text_raw": text_val, "reviewer_name": reviewer_val, "location_raw": location_raw, "date_text_raw": date_text_raw, "source_url": source_url, "page_number": page_number, "scrape_timestamp_utc": scrape_ts})
    return results


def parse_reviews_from_html(html: str, source_url: str, page_number: int) -> list[dict[str, Any]]:
    if BeautifulSoup is None:
        return _regex_parse(html, source_url, page_number)
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div._27M-vq") or soup.select("div.col.EPCmJX")
    product_id, product_slug = extract_product_metadata(source_url)
    results: list[dict[str, Any]] = []
    scrape_ts = datetime.now(timezone.utc).isoformat()

    for card in cards:
        rating = card.select_one("div._3LWZlK")
        title = card.select_one("p._2-N8zT")
        text = card.select_one("div.t-ZTKy div") or card.select_one("div.ZmyHeo")
        reviewer = card.select_one("p._2sc7ZR._2V5EHH")
        meta = card.select("p._2sc7ZR")
        rating_val = int(rating.text.strip()) if rating and rating.text.strip().isdigit() else None
        title_val = title.text.strip() if title else ""
        text_val = text.get_text(" ", strip=True) if text else ""
        reviewer_val = reviewer.text.strip() if reviewer else "unknown"
        location_raw = meta[1].text.strip() if len(meta) > 1 else ""
        date_text_raw = meta[2].text.strip() if len(meta) > 2 else ""
        review_id = deterministic_review_id(product_id, reviewer_val, title_val, text_val, date_text_raw)
        results.append({"review_id": review_id, "product_id": product_id, "product_slug": product_slug, "rating": rating_val, "title": title_val, "review_text_raw": text_val, "reviewer_name": reviewer_val, "location_raw": location_raw, "date_text_raw": date_text_raw, "source_url": source_url, "page_number": page_number, "scrape_timestamp_utc": scrape_ts})
    return results
