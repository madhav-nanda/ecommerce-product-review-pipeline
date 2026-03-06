# Flipkart AI Batch Review Pipeline

Production-grade, batch-only Bronze/Silver/Gold pipeline for **any Flipkart product review URL**.

## Architecture

1. **Extract (Batch):** requests + BeautifulSoup scraper with retry/backoff/throttle.
2. **Bronze:** immutable-ish raw records in MongoDB (`flipkart_reviews_bronze`) via idempotent upsert on deterministic `review_id`.
3. **Silver:** cleaned/normalized reviews in Parquet and Postgres (`flipkart_reviews_silver`).
4. **Gold ML Features:** sentiment + lexical/feature flags table (`gold_ml_features`).
5. **Gold Analytics:** daily trends, feature sentiment, top issues.
6. **Embeddings:** `all-MiniLM-L6-v2` embeddings in Postgres pgvector table (`gold_review_embeddings`).
7. **Semantic Search:** top-k vector similarity tool.

## Repository Tree

```text
flipkart_ai/
  README.md
  docker-compose.yml
  .env.example
  requirements.txt
  sql/
    init.sql
  src/
    config/settings.py
    orchestration/run_pipeline.py
    extract/flipkart_scraper.py
    extract/parser.py
    bronze/mongo_writer.py
    transform/cleaner.py
    transform/date_normalizer.py
    transform/location_normalizer.py
    transform/silver_writer.py
    quality/validators.py
    quality/dq_report.py
    features/feature_engineering.py
    features/sentiment.py
    features/gold_features_writer.py
    embeddings/embedder.py
    embeddings/vector_store.py
    analytics/aggregations.py
    analytics/gold_analytics_writer.py
    utils/logging.py
    utils/hashing.py
    utils/http.py
  tools/
    semantic_search.py
    backfill.py
  tests/
    test_hashing.py
    test_date_normalizer.py
    test_cleaner.py
    test_scraper_parser.py
```

## Setup

```bash
cd flipkart_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
```

## Run Pipeline

```bash
python -m src.orchestration.run_pipeline \
  --url "https://www.flipkart.com/apple-iphone-16-pro-max-natural-titanium-256-gb/product-reviews/itm05ad8e674782a?pid=MOBH4DQFRST2BQQ8&lid=LSTMOBH4DQFRST2BQQ8UII8UK&marketplace=FLIPKART" \
  --max_pages 200 \
  --mode full
```

Modes:
- `full`
- `extract_only`
- `transform_only`
- `embed_only`
- `analytics_only`

Optional incremental arg:
- `--since "2024-01-01"`

## Semantic Search

```bash
python tools/semantic_search.py --product_id MOBH4DQFRST2BQQ8 --query "camera quality in low light" --top_k 5
```

## Data Quality Report

Each run writes a JSON report under `data/reports/dq_<run_id>.json`:
- total row count
- invalid ratings
- empty cleaned text rows
- date parse success ratio

## Troubleshooting

- **403/429 blocking**: reduce `max_pages`, increase `REQUEST_SLEEP_SECONDS`, rerun later.
- **No parsed rows**: Flipkart may have changed HTML classes; update selectors in `src/extract/parser.py`.
- **Embedding download issues**: ensure internet access for first model download.

## Example Pipeline Output (illustrative)

```text
{"level":"INFO","message":"Parsed review page","count":10}
{"level":"INFO","message":"Parsed review page","count":10}
{"level":"INFO","message":"Pipeline finished","run_id":"...","product_id":"MOBH4DQFRST2BQQ8","count":185}
```

## Example Semantic Search Output (illustrative)

```text
1. score=0.8421 rating=5 sentiment=pos id=e8f...
   camera quality is excellent in daylight and low light...
2. score=0.8016 rating=4 sentiment=neu id=9bc...
   battery is good but camera shutter has minor delay...
```
