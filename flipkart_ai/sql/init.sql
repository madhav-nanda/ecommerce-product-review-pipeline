CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_id TEXT PRIMARY KEY,
  start_time_utc TIMESTAMPTZ NOT NULL,
  end_time_utc TIMESTAMPTZ,
  url TEXT NOT NULL,
  product_id TEXT NOT NULL,
  mode TEXT NOT NULL,
  extracted_count INT DEFAULT 0,
  bronze_upserted_count INT DEFAULT 0,
  silver_loaded_count INT DEFAULT 0,
  embedded_count INT DEFAULT 0,
  status TEXT NOT NULL,
  message TEXT
);

CREATE TABLE IF NOT EXISTS flipkart_reviews_silver (
  review_id TEXT PRIMARY KEY,
  ingestion_run_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  product_slug TEXT,
  rating INT,
  title TEXT,
  review_text_raw TEXT,
  cleaned_text TEXT,
  reviewer_name TEXT,
  buyer_status TEXT,
  city TEXT,
  location_raw TEXT,
  date_text_raw TEXT,
  source_url TEXT,
  page_number INT,
  scrape_timestamp_utc TIMESTAMPTZ,
  processed_date_utc TIMESTAMPTZ,
  invalid_reason TEXT
);

CREATE TABLE IF NOT EXISTS gold_ml_features (
  review_id TEXT PRIMARY KEY,
  product_id TEXT NOT NULL,
  processed_date_utc TIMESTAMPTZ,
  rating INT,
  cleaned_text TEXT,
  review_length_chars INT,
  word_count INT,
  sentiment_score FLOAT,
  sentiment_label TEXT,
  mentions_camera BOOLEAN,
  mentions_battery BOOLEAN,
  mentions_display BOOLEAN,
  mentions_performance BOOLEAN,
  mentions_heat BOOLEAN,
  mentions_price BOOLEAN,
  mentions_delivery BOOLEAN
);

CREATE TABLE IF NOT EXISTS gold_daily_metrics (
  product_id TEXT,
  date DATE,
  review_count INT,
  avg_rating FLOAT,
  pos_count INT,
  neu_count INT,
  neg_count INT,
  PRIMARY KEY(product_id, date)
);

CREATE TABLE IF NOT EXISTS gold_feature_sentiment (
  product_id TEXT,
  feature TEXT,
  pos_count INT,
  neu_count INT,
  neg_count INT,
  PRIMARY KEY(product_id, feature)
);

CREATE TABLE IF NOT EXISTS gold_top_issues (
  product_id TEXT,
  issue TEXT,
  neg_mentions_count INT,
  example_review_ids TEXT,
  PRIMARY KEY(product_id, issue)
);

CREATE TABLE IF NOT EXISTS gold_review_embeddings (
  review_id TEXT PRIMARY KEY,
  product_id TEXT NOT NULL,
  cleaned_text TEXT,
  rating INT,
  sentiment_label TEXT,
  embedding vector(384)
);
