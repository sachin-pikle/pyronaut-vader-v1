from typing import Annotated

from jakarta.validation import Valid
from micronaut.http.annotation import Body, Controller, Get, Post
from micronaut.scheduling import TaskExecutors
from micronaut.scheduling.annotation import ExecuteOn
from micronaut.validation import Validated

from .history import SentimentAnalysisRecord
from .models import ReviewAnalysis, ReviewRequest
from .service import SentimentService


@Controller("/api/reviews")
@Validated
@ExecuteOn(TaskExecutors.BLOCKING)
class ReviewController:
    def __init__(self, sentiment_service: SentimentService):
        self.sentiment_service = sentiment_service

    @Post(
        value="/analyze",
        consumes="application/json",
        produces="application/json",
    )
    def analyze_review(
        self,
        request: Annotated[ReviewRequest, Body, Valid],
    ) -> ReviewAnalysis:
        return self.sentiment_service.analyze(request.text)

    @Get(value="/history", produces="application/json")
    def history(self) -> list[SentimentAnalysisRecord]:
        return self.sentiment_service.history()
