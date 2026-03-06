"""Gold feature engineering."""
import pandas as pd

from src.features.sentiment import VaderSentiment

FEATURE_KEYWORDS = {
    "mentions_camera": ["camera"],
    "mentions_battery": ["battery", "charging"],
    "mentions_display": ["display", "screen"],
    "mentions_performance": ["performance", "lag", "speed"],
    "mentions_heat": ["heating", "heat"],
    "mentions_price": ["price", "cost", "value"],
    "mentions_delivery": ["delivery", "packaging"],
}


def build_feature_df(silver_df: pd.DataFrame) -> pd.DataFrame:
    df = silver_df.copy()
    analyzer = VaderSentiment()
    sentiments = df["cleaned_text"].fillna("").map(analyzer.score)
    df["sentiment_score"] = sentiments.map(lambda x: x[0])
    df["sentiment_label"] = sentiments.map(lambda x: x[1])
    df["review_length_chars"] = df["cleaned_text"].fillna("").str.len()
    df["word_count"] = df["cleaned_text"].fillna("").str.split().str.len()
    for flag, words in FEATURE_KEYWORDS.items():
        df[flag] = df["cleaned_text"].fillna("").map(lambda t: any(w in t for w in words))
    cols = [
        "review_id", "product_id", "processed_date_utc", "rating", "cleaned_text", "review_length_chars",
        "word_count", "sentiment_score", "sentiment_label", *FEATURE_KEYWORDS.keys()
    ]
    return df[cols]
