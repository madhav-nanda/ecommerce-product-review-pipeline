"""PGVector storage and semantic search helpers."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text


def ensure_vector_index(postgres_dsn: str) -> None:
    engine = create_engine(postgres_dsn)
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_gold_review_embeddings_ivfflat ON gold_review_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"))


def upsert_embeddings(df: pd.DataFrame, embeddings: list[list[float]], postgres_dsn: str) -> int:
    if df.empty:
        return 0
    engine = create_engine(postgres_dsn)
    with engine.begin() as conn:
        for row, emb in zip(df.to_dict(orient="records"), embeddings):
            payload = {
                "review_id": row["review_id"],
                "product_id": row["product_id"],
                "cleaned_text": row["cleaned_text"],
                "rating": row["rating"],
                "sentiment_label": row["sentiment_label"],
                "embedding": emb,
            }
            conn.execute(
                text(
                    """
                    INSERT INTO gold_review_embeddings (review_id, product_id, cleaned_text, rating, sentiment_label, embedding)
                    VALUES (:review_id, :product_id, :cleaned_text, :rating, :sentiment_label, :embedding)
                    ON CONFLICT (review_id) DO NOTHING
                    """
                ),
                payload,
            )
    return len(df)


def semantic_search(postgres_dsn: str, product_id: str, query_embedding: list[float], top_k: int) -> list[dict]:
    engine = create_engine(postgres_dsn)
    sql = text(
        """
        SELECT review_id, cleaned_text, rating, sentiment_label,
               1 - (embedding <=> :query_embedding) AS score
        FROM gold_review_embeddings
        WHERE product_id = :product_id
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, {"query_embedding": query_embedding, "product_id": product_id, "top_k": top_k}).mappings().all()
    return [dict(r) for r in rows]
