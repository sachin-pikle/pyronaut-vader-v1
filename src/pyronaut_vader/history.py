from dataclasses import dataclass
from typing import Annotated

from micronaut.data.annotation import GeneratedValue, Id, MappedEntity, MappedProperty
from micronaut.data.jdbc.annotation import JdbcRepository
from micronaut.data.repository import CrudRepository
from micronaut.serde.annotation import Serdeable


@dataclass
@MappedEntity("sentiment_analysis")
@Serdeable
class SentimentAnalysisRecord:
    id: Annotated[int | None, Id, GeneratedValue]
    text: Annotated[str, MappedProperty(value="review_text", definition="CLOB")]
    label: str
    compound: float
    positive: float
    neutral: float
    negative: float


@JdbcRepository(dialect="ORACLE")
class SentimentAnalysisRepository(CrudRepository[SentimentAnalysisRecord, int]):
    pass
