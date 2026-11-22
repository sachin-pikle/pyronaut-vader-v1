from jakarta.inject import Singleton
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .history import SentimentAnalysisRecord, SentimentAnalysisRepository
from .models import ReviewAnalysis


@Singleton
class SentimentService:
    def __init__(self, history_repository: SentimentAnalysisRepository):
        self._analyzer = SentimentIntensityAnalyzer()
        self._history_repository = history_repository

    def analyze(self, text: str) -> ReviewAnalysis:
        scores = self._analyzer.polarity_scores(text)
        compound = float(scores["compound"])

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        analysis = ReviewAnalysis(
            label=label,
            compound=compound,
            positive=float(scores["pos"]),
            neutral=float(scores["neu"]),
            negative=float(scores["neg"]),
        )

        self._history_repository.save(
            SentimentAnalysisRecord(
                id=None,
                text=text,
                label=analysis.label,
                compound=analysis.compound,
                positive=analysis.positive,
                neutral=analysis.neutral,
                negative=analysis.negative,
            )
        )

        return analysis

    def history(self) -> list[SentimentAnalysisRecord]:
        return self._history_repository.findAll()
