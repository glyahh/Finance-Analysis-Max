from datetime import datetime, timezone

from finance_research.core.models import Evidence, EvidenceType, SourceMetadata
from finance_research.orchestrator import CandidateInput, ResearchOrchestrator, ResearchRequest
from finance_research.output import render_result


def test_renderer_has_six_sections_and_purchase_priority_is_last():
    now = datetime(2026, 9, 16, tzinfo=timezone.utc)
    evidence = tuple(
        Evidence(
            evidence_type=EvidenceType.FACT,
            topic=topic,
            value="observed",
            subject="000001",
            source=SourceMetadata(source="test", fetched_at=now),
        )
        for topic in ("inflow", "outflow", "earnings")
    )
    outcome = ResearchOrchestrator().research(
        ResearchRequest(prompt="研究未来3个月", minimum_evidence=3),
        [CandidateInput("000001", "示例标的", [100, 101, 103, 102, 106, 110], evidence)],
        now=now,
    )
    rendered = render_result(outcome)
    assert sum(line.startswith("## ") and not line.startswith("### ") for line in rendered.splitlines()) == 6
    assert rendered.index("## 6. 购买优先级") > rendered.index("## 5. 未来走势")
    assert "来源：test" in rendered
    assert "置信度" not in rendered
    assert rendered.rstrip().endswith("1. 示例标的")
