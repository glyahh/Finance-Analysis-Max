from datetime import datetime, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.orchestrator import (
    CandidateInput,
    ResearchOrchestrator,
    ResearchRequest,
    ResearchStatus,
)


NOW = datetime(2026, 9, 16, tzinfo=timezone.utc)


def ev(subject, topic, value=1):
    return Evidence(
        evidence_type=EvidenceType.FACT,
        topic=topic,
        value=value,
        subject=subject,
        source=SourceMetadata(source="test", fetched_at=NOW),
    )


def test_orchestrator_asks_for_missing_forecast_horizon():
    result = ResearchOrchestrator().research(
        ResearchRequest(prompt="分析这个标的"),
        [],
        now=NOW,
    )
    assert result.status is ResearchStatus.NEEDS_INFORMATION
    assert result.plan.missing_fields == ("forecast_horizon",)


def test_orchestrator_runs_evidence_modules_forecast_counter_and_rank():
    candidates = [
        CandidateInput(
            instrument_id="000001",
            name="A",
            prices=[100, 101, 103, 102, 106, 110, 108, 115],
            evidence=(ev("000001", "market"), ev("000001", "earnings"), ev("000001", "outflow")),
        ),
    ]
    result = ResearchOrchestrator().research(
        ResearchRequest(prompt="研究未来3个月", minimum_evidence=3), candidates, now=NOW
    )
    assert result.status is ResearchStatus.READY
    assert result.reports[0].forecast.available is True
    assert result.reports[0].counter_evidence.found_counter_evidence is True
    assert result.ranking is not None
    assert result.ranking.ranked[0].candidate.instrument_id == "000001"

