from jakarta.inject import Singleton
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .models import ReviewAnalysis


@Singleton
class SentimentService:
    def __init__(self):
        self._analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> ReviewAnalysis:
        scores = self._analyzer.polarity_scores(text)
        compound = float(scores["compound"])

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return ReviewAnalysis(
            label=label,
            compound=compound,
            positive=float(scores["pos"]),
            neutral=float(scores["neu"]),
            negative=float(scores["neg"]),
        )
