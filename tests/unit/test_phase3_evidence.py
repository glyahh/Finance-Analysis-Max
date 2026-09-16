from datetime import datetime, timedelta, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.evidence import EvidenceEngine, FreshnessStatus


NOW = datetime(2026, 9, 16, tzinfo=timezone.utc)


def make_evidence(value, source, fetched_at):
    return Evidence(
        evidence_type=EvidenceType.FACT,
        topic="price",
        value=value,
        subject="000001",
        source=SourceMetadata(source=source, fetched_at=fetched_at),
    )


def test_freshness_is_explicit_and_future_data_is_not_usable():
    engine = EvidenceEngine(default_max_age=timedelta(days=1))
    fresh = engine.ingest(make_evidence(10, "source-a", NOW), now=NOW)
    future = engine.ingest(make_evidence(11, "source-b", NOW + timedelta(minutes=1)), now=NOW)
    assert fresh.freshness is FreshnessStatus.FRESH
    assert fresh.usable is True
    assert future.freshness is FreshnessStatus.FUTURE
    assert future.usable is False


def test_stale_evidence_is_marked_not_silently_dropped():
    engine = EvidenceEngine(default_max_age=timedelta(days=1))
    result = engine.ingest(
        make_evidence(10, "source-a", NOW - timedelta(days=2)),
        now=NOW,
    )
    assert result.freshness is FreshnessStatus.STALE
    assert result.usable is True


def test_conflicting_sources_are_preserved_and_linked():
    engine = EvidenceEngine()
    first = engine.ingest(make_evidence(10, "source-a", NOW), now=NOW)
    second = engine.ingest(make_evidence(11, "source-b", NOW), now=NOW)
    assert first.conflicts == ()
    assert len(second.conflicts) == 1
    conflict = second.conflicts[0]
    assert set(conflict.values) == {10, 11}
    assert set(conflict.evidence_ids) == {first.evidence_id, second.evidence_id}

