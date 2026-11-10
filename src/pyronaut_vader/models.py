from dataclasses import dataclass
from typing import Annotated

from jakarta.validation.constraints import NotBlank
from micronaut.serde.annotation import Serdeable


@Serdeable
@dataclass
class ReviewRequest:
    text: Annotated[str, NotBlank]


@Serdeable
@dataclass
class ReviewAnalysis:
    label: str
    compound: float
    positive: float
    neutral: float
    negative: float
