"""Deterministic VADER sentiment scoring."""
from __future__ import annotations

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


class VaderSentiment:
    def __init__(self) -> None:
        try:
            self.analyzer = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download("vader_lexicon")
            self.analyzer = SentimentIntensityAnalyzer()

    def score(self, text: str) -> tuple[float, str]:
        compound = self.analyzer.polarity_scores(text or "")["compound"]
        if compound >= 0.05:
            label = "pos"
        elif compound <= -0.05:
            label = "neg"
        else:
            label = "neu"
        return float(compound), label
