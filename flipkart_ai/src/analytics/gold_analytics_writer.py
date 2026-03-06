"""Writers for gold analytics tables."""
import pandas as pd
from sqlalchemy import create_engine, text


def _upsert(df: pd.DataFrame, table: str, key_cols: list[str], postgres_dsn: str) -> int:
    if df.empty:
        return 0
    engine = create_engine(postgres_dsn)
    cols = df.columns.tolist()
    inserts = ", ".join(cols)
    values = ", ".join(f":{c}" for c in cols)
    non_key = [c for c in cols if c not in key_cols]
    updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in non_key)
    conflict = ", ".join(key_cols)
    sql = text(
        f"INSERT INTO {table} ({inserts}) VALUES ({values}) ON CONFLICT ({conflict}) DO UPDATE SET {updates}"
    )
    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.execute(sql, row)
    return len(df)


def write_daily(df: pd.DataFrame, postgres_dsn: str) -> int:
    return _upsert(df, "gold_daily_metrics", ["product_id", "date"], postgres_dsn)


def write_feature_sentiment(df: pd.DataFrame, postgres_dsn: str) -> int:
    return _upsert(df, "gold_feature_sentiment", ["product_id", "feature"], postgres_dsn)


def write_top_issues(df: pd.DataFrame, postgres_dsn: str) -> int:
    return _upsert(df, "gold_top_issues", ["product_id", "issue"], postgres_dsn)
