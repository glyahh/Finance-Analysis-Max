from datetime import datetime, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.orchestrator import CandidateInput, ResearchOrchestrator, ResearchRequest
from finance_research.output import render_result


def test_output_contract_keeps_priority_as_final_section():
    now = datetime.now(timezone.utc)
    evidence = tuple(
        Evidence(EvidenceType.FACT, topic, "observed", "x", SourceMetadata("test", fetched_at=now))
        for topic in ("market", "earnings", "outflow")
    )
    outcome = ResearchOrchestrator().research(
        ResearchRequest("研究未来1个月", minimum_evidence=3),
        [CandidateInput("x", "X", [100, 101, 102, 103, 104], evidence)],
        now=now,
    )
    rendered = render_result(outcome)
    assert rendered.rfind("## 6. 购买优先级") > rendered.rfind("## 5. 未来走势")
    assert "模型置信度" not in rendered

