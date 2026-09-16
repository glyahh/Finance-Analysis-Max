import pytest

from finance_research.forecast import ForecastEngine, Trend


def test_forecast_returns_range_and_downside_without_guaranteeing_gain():
    result = ForecastEngine().forecast(
        [100, 101, 103, 102, 106, 110, 108, 115],
        horizon_periods=10,
        periods_per_year=252,
    )
    assert result.available is True
    assert result.trend in {Trend.UP, Trend.DOWN, Trend.SIDEWAYS}
    assert result.expected_return_low < result.expected_return_high
    assert result.downside_low <= result.downside_high <= 0


def test_forecast_is_unavailable_when_data_cannot_support_volatility():
    result = ForecastEngine().forecast([100, 101], horizon_periods=10)
    assert result.available is False
    assert result.trend is Trend.UNAVAILABLE
    assert result.expected_return_low is None


def test_forecast_rejects_invalid_horizon():
    with pytest.raises(ValueError):
        ForecastEngine().forecast([100, 101, 102], horizon_periods=0)

