"""Deterministic review identifier helpers."""
import hashlib


def deterministic_review_id(product_id: str, reviewer_name: str, title: str, review_text: str, date_text_raw: str) -> str:
    raw = "||".join(
        [product_id.strip(), reviewer_name.strip(), title.strip(), review_text.strip(), date_text_raw.strip()]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
