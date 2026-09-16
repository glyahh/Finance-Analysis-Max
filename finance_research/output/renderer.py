"""Fixed six-section renderer with provenance attached to factual lines."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..core.models import Evidence, EvidenceType
from ..orchestrator.engine import ResearchOutcome, ResearchStatus


POSITIVE_TOPICS = {"inflow", "earnings_growth", "positive_news", "supportive_policy", "upside_catalyst"}
NEGATIVE_TOPICS = {"outflow", "earnings_decline", "negative_news", "regulatory_event", "downside_risk", "overvaluation"}


def _date(value: datetime | None) -> str:
    return value.isoformat() if value else "未提供"


def _evidence_line(evidence: Evidence) -> str:
    return (
        f"- {evidence.topic}: {evidence.value} "
        f"（来源：{evidence.source.source}；时间：{_date(evidence.source.published_at or evidence.source.fetched_at)}；"
        f"类型：{evidence.evidence_type.value}）"
    )


def _topic_lines(evidence: Iterable[Evidence], topics: set[str], empty: str) -> list[str]:
    lines = [_evidence_line(item) for item in evidence if item.topic.lower() in topics]
    return lines or [f"- {empty}"]


def _percent(value: float | None) -> str:
    return "无法确认" if value is None else f"{value * 100:.1f}%"


def render_result(outcome: ResearchOutcome) -> str:
    reports_by_id = {report.instrument_id: report for report in outcome.reports}
    ranked = outcome.ranking.ranked if outcome.ranking else ()
    lines = [
        "## 1. 研究结论摘要",
    ]
    if outcome.status is ResearchStatus.NEEDS_INFORMATION:
        lines.append(f"缺少必要条件：{', '.join(outcome.plan.missing_fields)}。请补充后再研究。")
    elif not ranked:
        lines.append("当前没有达到最低证据门槛的可推荐对象。")
    else:
        lines.append(f"已完成 {len(outcome.reports)} 个候选的证据研究、预测和门槛筛选，最终保留 {len(ranked)} 个对象。")

    all_evidence = tuple(item for report in outcome.reports for item in report.evidence)
    lines.extend(
        [
            "",
            "## 2. 关键驱动因素",
            "### 利好因素",
            *_topic_lines(all_evidence, POSITIVE_TOPICS, "暂无可核验利好证据。"),
            "### 利空因素",
            *_topic_lines(all_evidence, NEGATIVE_TOPICS, "暂无可核验利空证据。"),
            "### 最可能推翻当前判断的因素",
        ]
    )
    if outcome.reports:
        for report in outcome.reports:
            missing = report.counter_evidence.missing_topics
            lines.append(f"- {report.name}：需继续验证 {', '.join(missing) if missing else '已发现的反向证据变化'}。")
    else:
        lines.append("- 尚未形成判断，无法定义推翻条件。")

    lines.extend(["", "## 3. 多维度分析"])
    for report in outcome.reports:
        lines.append(f"### {report.name}")
        for module in report.modules:
            observed = ", ".join(module.observed_topics) or "无"
            missing = ", ".join(module.missing_topics) or "无"
            lines.append(f"- {module.module}：已观察 {observed}；缺失 {missing}。")
    if not outcome.reports:
        lines.append("- 暂无可分析对象。")

    lines.extend(["", "## 4. 风险与重新评估条件"])
    for report in outcome.reports:
        timestamps = [_date(item.source.published_at or item.source.fetched_at) for item in report.evidence]
        latest = max(timestamps) if timestamps else "未提供"
        lines.append(
            f"- {report.name}：当前预测下行区间 { _percent(report.forecast.downside_low) } ～ "
            f"{ _percent(report.forecast.downside_high) }；数据时间覆盖至 {latest}；"
            "若核心数据、政策、资金流或反向证据发生明显变化，应重新研究。"
        )
    if not outcome.reports:
        lines.append("- 尚未生成风险判断。")

    lines.extend(["", "## 5. 未来走势"])
    for item in ranked:
        report = reports_by_id[item.candidate.instrument_id]
        forecast = report.forecast
        lines.extend(
            [
                f"### {report.name}",
                f"预测周期：{forecast.horizon_periods} 个交易周期",
                f"预期涨跌幅：{_percent(forecast.expected_return_low)} ～ {_percent(forecast.expected_return_high)}",
                f"潜在下行风险：{_percent(forecast.downside_low)} ～ {_percent(forecast.downside_high)}",
                f"趋势：{forecast.trend.value}",
            ]
        )
    if not ranked:
        lines.append("暂无可输出的合格候选。")

    lines.extend(["", "## 6. 购买优先级", ""])
    if ranked:
        lines.extend(f"{index}. {item.candidate.name}" for index, item in enumerate(ranked, 1))
    else:
        lines.append("暂无推荐")
    return "\n".join(lines)

