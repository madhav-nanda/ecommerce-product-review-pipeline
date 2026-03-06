"""Data quality checks for silver dataframe."""
import pandas as pd


def validate_silver(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0, "invalid_rating": 0, "empty_cleaned_text": 0, "date_parse_success": 0.0}
    invalid_rating = int((~df["rating"].between(1, 5, inclusive="both")).sum())
    empty_cleaned = int((df["cleaned_text"].fillna("").str.len() == 0).sum())
    date_parse_success = float(df["processed_date_utc"].notna().mean())
    return {
        "total": int(len(df)),
        "invalid_rating": invalid_rating,
        "empty_cleaned_text": empty_cleaned,
        "date_parse_success": round(date_parse_success, 4),
    }
