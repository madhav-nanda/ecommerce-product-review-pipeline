"""Gold analytics aggregations."""
import pandas as pd


def daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["date"] = pd.to_datetime(tmp["processed_date_utc"]).dt.date
    agg = tmp.groupby(["product_id", "date"]).agg(
        review_count=("review_id", "count"),
        avg_rating=("rating", "mean"),
        pos_count=("sentiment_label", lambda s: int((s == "pos").sum())),
        neu_count=("sentiment_label", lambda s: int((s == "neu").sum())),
        neg_count=("sentiment_label", lambda s: int((s == "neg").sum())),
    ).reset_index()
    return agg


def feature_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    feature_cols = [c for c in df.columns if c.startswith("mentions_")]
    for feature in feature_cols:
        sub = df[df[feature]]
        if sub.empty:
            continue
        rows.append({
            "product_id": sub["product_id"].iloc[0],
            "feature": feature.replace("mentions_", ""),
            "pos_count": int((sub["sentiment_label"] == "pos").sum()),
            "neu_count": int((sub["sentiment_label"] == "neu").sum()),
            "neg_count": int((sub["sentiment_label"] == "neg").sum()),
        })
    return pd.DataFrame(rows)


def top_issues(df: pd.DataFrame) -> pd.DataFrame:
    issue_map = {
        "heating": "mentions_heat",
        "battery": "mentions_battery",
        "delivery": "mentions_delivery",
        "price": "mentions_price",
    }
    rows = []
    for issue, col in issue_map.items():
        sub = df[(df[col]) & (df["sentiment_label"] == "neg")]
        rows.append(
            {
                "product_id": df["product_id"].iloc[0],
                "issue": issue,
                "neg_mentions_count": int(len(sub)),
                "example_review_ids": ",".join(sub["review_id"].head(5).tolist()),
            }
        )
    return pd.DataFrame(rows)
