"""Flipkart scraper with robust page iteration and stop conditions."""
from __future__ import annotations

from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from src.config.settings import Settings
from src.extract.parser import parse_reviews_from_html
from src.utils.http import get_with_retry
from src.utils.logging import get_logger


class FlipkartScraper:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__, settings.log_level)

    @staticmethod
    def _page_url(url: str, page_number: int) -> str:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs["page"] = [str(page_number)]
        new_query = urlencode({k: v[0] for k, v in qs.items()})
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

    def scrape(self, url: str, max_pages: int = 200) -> list[dict]:
        all_rows: list[dict] = []
        empty_streak = 0
        for page in range(1, max_pages + 1):
            page_url = self._page_url(url, page)
            response = get_with_retry(page_url, self.settings)
            page_rows = parse_reviews_from_html(response.text, url, page)
            if not page_rows:
                empty_streak += 1
                if empty_streak >= 3:
                    self.logger.info("No reviews found repeatedly; stopping", extra={"count": empty_streak})
                    break
                continue
            empty_streak = 0
            all_rows.extend(page_rows)
            self.logger.info("Parsed review page", extra={"count": len(page_rows), "module": "extract"})
        if not all_rows:
            raise RuntimeError("No reviews parsed. Flipkart HTML structure may have changed.")
        return all_rows
