"""Silver transformation and persistence."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.transform.cleaner import clean_review_text
from src.transform.date_normalizer import parse_relative_date
from src.transform.location_normalizer import parse_location


def build_silver_df(rows: list[dict], run_id: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ingestion_run_id"] = run_id
    df["cleaned_text"] = df["review_text_raw"].fillna("").map(clean_review_text)
    parsed_dates = [parse_relative_date(d, s) for d, s in zip(df["date_text_raw"], df["scrape_timestamp_utc"])]
    df["processed_date_utc"] = parsed_dates
    loc = df["location_raw"].fillna("").map(parse_location)
    df["buyer_status"] = loc.map(lambda x: x[0])
    df["city"] = loc.map(lambda x: x[1])
    df["invalid_reason"] = None
    df.loc[~df["rating"].between(1, 5, inclusive="both"), "invalid_reason"] = "invalid_rating"
    df.loc[df["cleaned_text"].str.len() == 0, "invalid_reason"] = "empty_cleaned_text"
    return df


def write_silver(df: pd.DataFrame, postgres_dsn: str, product_id: str) -> int:
    if df.empty:
        return 0
    day_part = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = Path("data/silver") / product_id / day_part
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_dir / "part-000.parquet", index=False)

    engine = create_engine(postgres_dsn)
    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.execute(
                text(
                    """
                    INSERT INTO flipkart_reviews_silver (
                        review_id, ingestion_run_id, product_id, product_slug, rating, title,
                        review_text_raw, cleaned_text, reviewer_name, buyer_status, city,
                        location_raw, date_text_raw, source_url, page_number, scrape_timestamp_utc,
                        processed_date_utc, invalid_reason
                    ) VALUES (
                        :review_id, :ingestion_run_id, :product_id, :product_slug, :rating, :title,
                        :review_text_raw, :cleaned_text, :reviewer_name, :buyer_status, :city,
                        :location_raw, :date_text_raw, :source_url, :page_number, :scrape_timestamp_utc,
                        :processed_date_utc, :invalid_reason
                    )
                    ON CONFLICT (review_id) DO UPDATE SET
                        ingestion_run_id = EXCLUDED.ingestion_run_id,
                        cleaned_text = EXCLUDED.cleaned_text,
                        processed_date_utc = EXCLUDED.processed_date_utc,
                        invalid_reason = EXCLUDED.invalid_reason
                    """
                ),
                row,
            )
    return len(df)
