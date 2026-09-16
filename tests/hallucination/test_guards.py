from datetime import datetime, timedelta, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.evidence import EvidenceEngine, FreshnessStatus
from finance_research.ranking import RankEngine


def test_future_evidence_is_not_usable():
    now = datetime.now(timezone.utc)
    evidence = Evidence(
        evidence_type=EvidenceType.FACT,
        topic="price",
        value=123,
        subject="x",
        source=SourceMetadata(source="test", fetched_at=now + timedelta(days=1)),
    )
    assessment = EvidenceEngine().ingest(evidence, now=now)
    assert assessment.freshness is FreshnessStatus.FUTURE
    assert assessment.usable is False


def test_missing_candidate_evidence_cannot_become_recommendation():
    assert RankEngine().rank([]).has_recommendation is False

