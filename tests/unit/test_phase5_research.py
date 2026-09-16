from datetime import datetime, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.evidence.store import EvidenceStore
from finance_research.research import default_modules, run_modules


def evidence(topic, value="observed", subject="000001", kind=EvidenceType.FACT):
    return Evidence(
        evidence_type=kind,
        topic=topic,
        value=value,
        subject=subject,
        source=SourceMetadata(source="test", fetched_at=datetime.now(timezone.utc)),
    )


def test_research_suite_reports_coverage_without_inventing_missing_topics():
    store = EvidenceStore()
    store.add(evidence("market"))
    store.add(evidence("earnings", kind=EvidenceType.OPINION))
    results = run_modules("000001", store.all())
    assert len(results) == 9
    market = next(result for result in results if result.module == "market")
    assert market.observed_topics == ("market",)
    assert "macro" not in market.observed_topics
    assert "benchmark" in market.missing_topics
    assert market.fact_count == 1
    assert market.opinion_count == 0


def test_research_context_is_subject_scoped():
    store = EvidenceStore()
    store.add(evidence("market", subject="other"))
    results = run_modules("000001", store.all(), modules=default_modules()[:1])
    assert results[0].evidence_count == 0
    assert results[0].missing_topics == default_modules()[0].required_topics
