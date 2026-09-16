from finance_research.analytics import calculate_metrics
from finance_research.forecast import ForecastResult, Trend
from finance_research.ranking import Candidate, RankEngine, RankingCriteria


def candidate(instrument_id, expected_high, downside_low=-0.05, evidence_count=5, **kwargs):
    forecast = ForecastResult(
        horizon_periods=30,
        available=True,
        trend=Trend.UP,
        expected_return_low=expected_high - 0.05,
        expected_return_high=expected_high,
        downside_low=downside_low,
        downside_high=0,
    )
    return Candidate(
        instrument_id=instrument_id,
        name=instrument_id,
        metrics=calculate_metrics([100, 101, 102]),
        forecast=forecast,
        evidence_count=evidence_count,
        data_complete=kwargs.get("data_complete", True),
        data_time_valid=kwargs.get("data_time_valid", True),
        has_source=kwargs.get("has_source", True),
        counter_evidence_checked=kwargs.get("counter_evidence_checked", True),
        unresolved_major_conflict=kwargs.get("unresolved_major_conflict", False),
    )


def test_rank_engine_filters_gate_failures_and_limits_top_five():
    candidates = [candidate(f"id-{i}", expected_high=0.1 + i / 100) for i in range(7)]
    candidates.append(candidate("bad", 0.9, evidence_count=1))
    result = RankEngine().rank(candidates, minimum_evidence=3)
    assert len(result.ranked) == 5
    assert result.ranked[0].candidate.instrument_id == "id-6"
    assert any(item[0].instrument_id == "bad" for item in result.excluded)


def test_ranking_can_prioritize_downside_control():
    result = RankEngine().rank(
        [candidate("high", 0.3, -0.3), candidate("steady", 0.1, -0.02)],
        criteria=RankingCriteria(upside_weight=0.2, downside_weight=0.8),
    )
    assert result.ranked[0].candidate.instrument_id == "steady"


def test_no_eligible_candidate_means_no_recommendation():
    result = RankEngine().rank([candidate("bad", 0.2, data_complete=False)])
    assert result.has_recommendation is False

