"""One-process research flow composed from the independent deterministic layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from ..analytics import calculate_metrics
from ..core.models import Evidence
from ..evidence import EvidenceAssessment, EvidenceEngine, FreshnessStatus
from ..forecast import ForecastEngine, ForecastResult, Trend
from ..ranking import Candidate, RankEngine, RankedCandidate, RankingCriteria, RankingResult
from ..research import ModuleResult, run_modules
from ..research.counter_evidence import CounterEvidenceEngine, CounterEvidenceResult, Direction
from .plan import ResearchPlan, make_plan


class ResearchStatus(StrEnum):
    READY = "ready"
    NEEDS_INFORMATION = "needs_information"


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    prompt: str
    explicit_horizon_periods: int | None = None
    minimum_evidence: int = 3
    ranking_criteria: RankingCriteria = RankingCriteria()


@dataclass(frozen=True, slots=True)
class CandidateInput:
    instrument_id: str
    name: str
    prices: Sequence[float]
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True, slots=True)
class CandidateReport:
    instrument_id: str
    name: str
    evidence: tuple[Evidence, ...]
    assessments: tuple[EvidenceAssessment, ...]
    modules: tuple[ModuleResult, ...]
    forecast: ForecastResult
    counter_evidence: CounterEvidenceResult


@dataclass(frozen=True, slots=True)
class ResearchOutcome:
    status: ResearchStatus
    plan: ResearchPlan
    reports: tuple[CandidateReport, ...] = ()
    ranking: RankingResult | None = None


class ResearchOrchestrator:
    def __init__(
        self,
        *,
        evidence_engine: EvidenceEngine | None = None,
        forecast_engine: ForecastEngine | None = None,
        counter_engine: CounterEvidenceEngine | None = None,
        rank_engine: RankEngine | None = None,
    ):
        self.evidence_engine = evidence_engine or EvidenceEngine()
        self.forecast_engine = forecast_engine or ForecastEngine()
        self.counter_engine = counter_engine or CounterEvidenceEngine()
        self.rank_engine = rank_engine or RankEngine()

    def research(
        self,
        request: ResearchRequest,
        candidates: Sequence[CandidateInput],
        *,
        now: datetime | None = None,
    ) -> ResearchOutcome:
        plan = make_plan(request.prompt, request.explicit_horizon_periods)
        if plan.missing_fields:
            return ResearchOutcome(status=ResearchStatus.NEEDS_INFORMATION, plan=plan)
        if request.minimum_evidence < 0:
            raise ValueError("minimum_evidence must not be negative")
        now = now or datetime.now(timezone.utc)
        reports: list[CandidateReport] = []
        rank_inputs: list[Candidate] = []
        for candidate_input in candidates:
            assessments = tuple(
                self.evidence_engine.ingest(evidence, now=now) for evidence in candidate_input.evidence
            )
            stored = self.evidence_engine.store.all()
            candidate_stored = tuple(
                item for item in stored if item.evidence.subject in {candidate_input.instrument_id, "*"}
            )
            modules = run_modules(candidate_input.instrument_id, candidate_stored)
            forecast = self.forecast_engine.forecast(
                candidate_input.prices,
                horizon_periods=plan.horizon_periods or 1,
            )
            direction = {
                Trend.UP: Direction.BULLISH,
                Trend.DOWN: Direction.BEARISH,
            }.get(forecast.trend, Direction.NEUTRAL)
            counter = self.counter_engine.search(candidate_input.instrument_id, direction, candidate_stored)
            conflicts = tuple(conflict for assessment in assessments for conflict in assessment.conflicts)
            rank_inputs.append(
                Candidate(
                    instrument_id=candidate_input.instrument_id,
                    name=candidate_input.name,
                    metrics=calculate_metrics(candidate_input.prices),
                    forecast=forecast,
                    evidence_count=len(assessments),
                    data_complete=bool(candidate_input.prices) and bool(candidate_input.evidence),
                    data_time_valid=all(
                        item.freshness in {FreshnessStatus.FRESH, FreshnessStatus.STALE}
                        for item in assessments
                    ),
                    has_source=all(item.source.source.strip() for item in candidate_input.evidence),
                    counter_evidence_checked=True,
                    unresolved_major_conflict=bool(conflicts),
                )
            )
            reports.append(
                CandidateReport(
                    instrument_id=candidate_input.instrument_id,
                    name=candidate_input.name,
                    evidence=tuple(candidate_input.evidence),
                    assessments=assessments,
                    modules=modules,
                    forecast=forecast,
                    counter_evidence=counter,
                )
            )
        ranking = self.rank_engine.rank(
            rank_inputs,
            criteria=request.ranking_criteria,
            minimum_evidence=request.minimum_evidence,
        )
        return ResearchOutcome(
            status=ResearchStatus.READY,
            plan=plan,
            reports=tuple(reports),
            ranking=ranking,
        )
