"""CLI orchestration entrypoint."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import uuid

from sqlalchemy import create_engine, text

from src.analytics.aggregations import daily_metrics, feature_sentiment, top_issues
from src.analytics.gold_analytics_writer import write_daily, write_feature_sentiment, write_top_issues
from src.bronze.mongo_writer import upsert_bronze
from src.config.settings import Settings
from src.embeddings.embedder import ReviewEmbedder
from src.embeddings.vector_store import ensure_vector_index, upsert_embeddings
from src.extract.flipkart_scraper import FlipkartScraper
from src.extract.parser import extract_product_metadata
from src.features.feature_engineering import build_feature_df
from src.features.gold_features_writer import write_gold_features
from src.quality.dq_report import write_dq_report
from src.quality.validators import validate_silver
from src.transform.silver_writer import build_silver_df, write_silver
from src.utils.logging import get_logger


def _init_run(engine, run_id: str, url: str, product_id: str, mode: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO pipeline_runs (run_id, start_time_utc, url, product_id, mode, status) VALUES (:run_id, :start, :url, :pid, :mode, :status)"
            ),
            {"run_id": run_id, "start": datetime.now(timezone.utc), "url": url, "pid": product_id, "mode": mode, "status": "RUNNING"},
        )


def _end_run(engine, run_id: str, status: str, metrics: dict, message: str = "") -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE pipeline_runs
                SET end_time_utc=:end_ts, status=:status, extracted_count=:extracted,
                    bronze_upserted_count=:bronze, silver_loaded_count=:silver,
                    embedded_count=:embedded, message=:message
                WHERE run_id=:run_id
                """
            ),
            {
                "end_ts": datetime.now(timezone.utc),
                "status": status,
                "extracted": metrics.get("extracted", 0),
                "bronze": metrics.get("bronze", 0),
                "silver": metrics.get("silver", 0),
                "embedded": metrics.get("embedded", 0),
                "message": message,
                "run_id": run_id,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--max_pages", type=int, default=200)
    parser.add_argument("--mode", choices=["full", "extract_only", "transform_only", "embed_only", "analytics_only"], default="full")
    parser.add_argument("--since", required=False)
    args = parser.parse_args()

    settings = Settings()
    logger = get_logger("pipeline", settings.log_level)
    run_id = str(uuid.uuid4())
    product_id, _ = extract_product_metadata(args.url)
    engine = create_engine(settings.postgres_dsn)
    metrics: dict[str, int] = {}

    _init_run(engine, run_id, args.url, product_id, args.mode)
    try:
        rows = []
        silver_df = None
        feature_df = None

        if args.mode in {"full", "extract_only"}:
            scraper = FlipkartScraper(settings)
            rows = scraper.scrape(args.url, max_pages=args.max_pages)
            metrics["extracted"] = len(rows)
            metrics["bronze"] = upsert_bronze(settings.mongo_uri, settings.mongo_db, rows, run_id)

        if args.mode in {"full", "transform_only"}:
            if not rows:
                scraper = FlipkartScraper(settings)
                rows = scraper.scrape(args.url, max_pages=args.max_pages)
            silver_df = build_silver_df(rows, run_id)
            dq = validate_silver(silver_df)
            write_dq_report(dq, run_id)
            metrics["silver"] = write_silver(silver_df, settings.postgres_dsn, product_id)
            feature_df = build_feature_df(silver_df[silver_df["invalid_reason"].isna()].copy())
            write_gold_features(feature_df, settings.postgres_dsn)

        if args.mode in {"full", "analytics_only"}:
            if feature_df is None:
                if silver_df is None:
                    scraper = FlipkartScraper(settings)
                    rows = scraper.scrape(args.url, max_pages=args.max_pages)
                    silver_df = build_silver_df(rows, run_id)
                feature_df = build_feature_df(silver_df[silver_df["invalid_reason"].isna()].copy())
            write_daily(daily_metrics(feature_df), settings.postgres_dsn)
            write_feature_sentiment(feature_sentiment(feature_df), settings.postgres_dsn)
            write_top_issues(top_issues(feature_df), settings.postgres_dsn)

        if args.mode in {"full", "embed_only"}:
            if feature_df is None:
                if silver_df is None:
                    scraper = FlipkartScraper(settings)
                    rows = scraper.scrape(args.url, max_pages=args.max_pages)
                    silver_df = build_silver_df(rows, run_id)
                feature_df = build_feature_df(silver_df[silver_df["invalid_reason"].isna()].copy())
            ensure_vector_index(settings.postgres_dsn)
            embedder = ReviewEmbedder(settings.model_name)
            emb = embedder.encode(feature_df["cleaned_text"].fillna("").tolist())
            metrics["embedded"] = upsert_embeddings(feature_df, emb, settings.postgres_dsn)

        _end_run(engine, run_id, "SUCCESS", metrics)
        logger.info("Pipeline finished", extra={"run_id": run_id, "product_id": product_id, "count": metrics.get("extracted", 0)})
    except Exception as exc:
        _end_run(engine, run_id, "FAILED", metrics, str(exc))
        logger.error(f"Pipeline failed: {exc}", extra={"run_id": run_id, "product_id": product_id})
        raise


if __name__ == "__main__":
    main()
