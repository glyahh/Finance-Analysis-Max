"""Active search for evidence that could invalidate an initial judgment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from ..evidence.store import StoredEvidence


class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


DEFAULT_OPPOSING_TOPICS = {
    Direction.BULLISH: (
        "negative_news",
        "outflow",
        "overvaluation",
        "earnings_decline",
        "fundamental_deterioration",
        "regulatory_event",
        "downside_risk",
    ),
    Direction.BEARISH: (
        "positive_news",
        "inflow",
        "undervaluation",
        "earnings_growth",
        "fundamental_improvement",
        "supportive_policy",
        "upside_catalyst",
    ),
    Direction.NEUTRAL: (),
}


@dataclass(frozen=True, slots=True)
class CounterEvidenceResult:
    subject: str
    initial_direction: Direction
    searched_topics: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    missing_topics: tuple[str, ...]

    @property
    def found_counter_evidence(self) -> bool:
        return bool(self.evidence_ids)


class CounterEvidenceEngine:
    def __init__(self, opposing_topics: dict[Direction, tuple[str, ...]] | None = None):
        self.opposing_topics = opposing_topics or DEFAULT_OPPOSING_TOPICS

    def search(
        self,
        subject: str,
        initial_direction: Direction,
        evidence: Iterable[StoredEvidence],
    ) -> CounterEvidenceResult:
        topics = tuple(self.opposing_topics.get(initial_direction, ()))
        relevant = tuple(
            item
            for item in evidence
            if item.evidence.subject in {subject, "*"}
            and item.evidence.topic.lower() in topics
        )
        found_topics = {item.evidence.topic.lower() for item in relevant}
        return CounterEvidenceResult(
            subject=subject,
            initial_direction=initial_direction,
            searched_topics=topics,
            evidence_ids=tuple(item.evidence_id for item in relevant),
            missing_topics=tuple(topic for topic in topics if topic not in found_topics),
        )

