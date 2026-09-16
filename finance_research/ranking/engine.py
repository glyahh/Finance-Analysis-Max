"""Deterministic ranking with a hard minimum-evidence gate."""

from __future__ import annotations

from dataclasses import dataclass

from ..analytics import AnalyticsResult
from ..forecast import ForecastResult


@dataclass(frozen=True, slots=True)
class RankingCriteria:
    upside_weight: float = 0.6
    downside_weight: float = 0.4

    def __post_init__(self) -> None:
        if self.upside_weight < 0 or self.downside_weight < 0:
            raise ValueError("ranking weights must not be negative")
        if self.upside_weight == 0 and self.downside_weight == 0:
            raise ValueError("at least one ranking weight must be positive")


@dataclass(frozen=True, slots=True)
class Candidate:
    instrument_id: str
    name: str
    metrics: AnalyticsResult
    forecast: ForecastResult
    evidence_count: int
    data_complete: bool
    data_time_valid: bool
    has_source: bool
    counter_evidence_checked: bool
    unresolved_major_conflict: bool

    def gate_failure_reasons(self, minimum_evidence: int) -> tuple[str, ...]:
        reasons: list[str] = []
        if self.evidence_count < minimum_evidence:
            reasons.append("insufficient_evidence")
        if not self.data_complete:
            reasons.append("incomplete_data")
        if not self.data_time_valid:
            reasons.append("invalid_or_future_timestamp")
        if not self.has_source:
            reasons.append("missing_source")
        if not self.counter_evidence_checked:
            reasons.append("counter_evidence_not_checked")
        if self.unresolved_major_conflict:
            reasons.append("unresolved_major_conflict")
        if not self.forecast.available:
            reasons.append("forecast_unavailable")
        return tuple(reasons)


@dataclass(frozen=True, slots=True)
class RankedCandidate:
    candidate: Candidate
    score: float


@dataclass(frozen=True, slots=True)
class RankingResult:
    ranked: tuple[RankedCandidate, ...]
    excluded: tuple[tuple[Candidate, tuple[str, ...]], ...]

    @property
    def has_recommendation(self) -> bool:
        return bool(self.ranked)


class RankEngine:
    def rank(
        self,
        candidates: tuple[Candidate, ...] | list[Candidate],
        *,
        criteria: RankingCriteria | None = None,
        minimum_evidence: int = 3,
        top_n: int = 5,
    ) -> RankingResult:
        if minimum_evidence < 0:
            raise ValueError("minimum_evidence must not be negative")
        if top_n <= 0:
            raise ValueError("top_n must be positive")
        criteria = criteria or RankingCriteria()
        eligible: list[RankedCandidate] = []
        excluded: list[tuple[Candidate, tuple[str, ...]]] = []
        for candidate in candidates:
            reasons = candidate.gate_failure_reasons(minimum_evidence)
            if reasons:
                excluded.append((candidate, reasons))
                continue
            forecast = candidate.forecast
            upside = forecast.expected_return_high or 0.0
            downside = abs(forecast.downside_low or 0.0)
            score = criteria.upside_weight * upside - criteria.downside_weight * downside
            eligible.append(RankedCandidate(candidate=candidate, score=score))
        eligible.sort(key=lambda item: (-item.score, item.candidate.instrument_id))
        return RankingResult(tuple(eligible[: min(top_n, 5)]), tuple(excluded))

