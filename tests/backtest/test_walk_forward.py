from finance_research.forecast import WalkForwardEvaluator


def test_walk_forward_uses_only_prefix_history_and_reports_error_metrics():
    prices = [100 + index * 0.5 for index in range(45)]
    result = WalkForwardEvaluator().evaluate(prices, horizon_periods=3, minimum_history=10)
    assert result.points
    assert result.points[0].origin_index == 10
    assert result.mean_absolute_error is not None
    assert result.directional_accuracy is not None


def test_walk_forward_returns_no_fake_accuracy_without_usable_points():
    result = WalkForwardEvaluator().evaluate([100, 101, 102], horizon_periods=2, minimum_history=2)
    assert result.mean_absolute_error is None
    assert result.directional_accuracy is None

