"""Persist gold ML feature table."""
import pandas as pd
from sqlalchemy import create_engine, text


def write_gold_features(df: pd.DataFrame, postgres_dsn: str) -> int:
    if df.empty:
        return 0
    engine = create_engine(postgres_dsn)
    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.execute(
                text(
                    """
                    INSERT INTO gold_ml_features (
                      review_id, product_id, processed_date_utc, rating, cleaned_text,
                      review_length_chars, word_count, sentiment_score, sentiment_label,
                      mentions_camera, mentions_battery, mentions_display,
                      mentions_performance, mentions_heat, mentions_price, mentions_delivery
                    ) VALUES (
                      :review_id, :product_id, :processed_date_utc, :rating, :cleaned_text,
                      :review_length_chars, :word_count, :sentiment_score, :sentiment_label,
                      :mentions_camera, :mentions_battery, :mentions_display,
                      :mentions_performance, :mentions_heat, :mentions_price, :mentions_delivery
                    )
                    ON CONFLICT (review_id) DO UPDATE SET
                      sentiment_score = EXCLUDED.sentiment_score,
                      sentiment_label = EXCLUDED.sentiment_label,
                      review_length_chars = EXCLUDED.review_length_chars,
                      word_count = EXCLUDED.word_count
                    """
                ),
                row,
            )
    return len(df)
