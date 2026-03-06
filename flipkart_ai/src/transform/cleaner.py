"""Text cleaning utilities."""
import re


def clean_review_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"READ MORE", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()
