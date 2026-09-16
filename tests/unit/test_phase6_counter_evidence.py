from datetime import datetime, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.evidence.store import EvidenceStore
from finance_research.research.counter_evidence import CounterEvidenceEngine, Direction


def test_counter_evidence_search_finds_bear_case_for_bullish_judgment():
    evidence = Evidence(
        evidence_type=EvidenceType.FACT,
        topic="outflow",
        value="observed",
        subject="000001",
        source=SourceMetadata(source="test", fetched_at=datetime.now(timezone.utc)),
    )
    store = EvidenceStore()
    store.add(evidence)
    result = CounterEvidenceEngine().search("000001", Direction.BULLISH, store.all())
    assert result.found_counter_evidence is True
    assert result.evidence_ids
    assert "outflow" not in result.missing_topics


def test_counter_evidence_does_not_claim_missing_topics_were_checked():
    result = CounterEvidenceEngine().search("000001", Direction.BEARISH, ())
    assert result.found_counter_evidence is False
    assert result.searched_topics
    assert result.missing_topics == result.searched_topics
