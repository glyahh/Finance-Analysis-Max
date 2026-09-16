import math

import pytest

from finance_research.analytics import calculate_metrics
from finance_research.analytics.correlation import correlation
from finance_research.analytics.valuation import percentile_rank


def test_metrics_are_deterministic_and_capture_drawdown():
    result = calculate_metrics([100, 110, 105, 120], periods_per_year=3)
    assert result.observations == 4
    assert result.cumulative_return == pytest.approx(0.2)
    assert result.max_drawdown == pytest.approx(105 / 110 - 1)
    assert result.momentum == pytest.approx(0.2)
    assert result.trend_slope is not None


def test_insufficient_observations_return_none_not_fake_metrics():
    result = calculate_metrics([100])
    assert result.annualized_return is None
    assert result.annualized_volatility is None
    assert result.sharpe is None
    assert result.momentum is None


def test_invalid_prices_are_rejected():
    with pytest.raises(ValueError):
        calculate_metrics([100, 0])


def test_correlation_and_valuation_helpers():
    assert correlation([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
    assert percentile_rank([1, 2, 3, 4], 3) == pytest.approx(0.75)
    assert percentile_rank([], 3) is None

