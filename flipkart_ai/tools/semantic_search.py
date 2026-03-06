"""Semantic search over pgvector embeddings."""
from __future__ import annotations

import argparse

from src.config.settings import Settings
from src.embeddings.embedder import ReviewEmbedder
from src.embeddings.vector_store import semantic_search


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product_id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    settings = Settings()
    embedder = ReviewEmbedder(settings.model_name)
    query_vec = embedder.encode([args.query])[0]
    rows = semantic_search(settings.postgres_dsn, args.product_id, query_vec, args.top_k)
    for i, row in enumerate(rows, start=1):
        snippet = (row["cleaned_text"] or "")[:160]
        print(f"{i}. score={row['score']:.4f} rating={row['rating']} sentiment={row['sentiment_label']} id={row['review_id']}")
        print(f"   {snippet}")


if __name__ == "__main__":
    main()
