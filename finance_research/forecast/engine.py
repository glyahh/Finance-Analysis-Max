"""Transparent forecast baseline built from historical quantitative metrics.

This is intentionally a baseline, not a promise of returns. It exposes an
unavailable result when the supplied observations cannot support a range.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import sqrt
from typing import Sequence

from ..analytics import AnalyticsResult, calculate_metrics


class Trend(StrEnum):
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ForecastResult:
    horizon_periods: int
    available: bool
    trend: Trend
    expected_return_low: float | None = None
    expected_return_high: float | None = None
    downside_low: float | None = None
    downside_high: float | None = None
    reason: str | None = None


class ForecastEngine:
    def forecast(
        self,
        prices: Sequence[float],
        *,
        horizon_periods: int,
        periods_per_year: int = 252,
        context_adjustment: float = 0.0,
    ) -> ForecastResult:
        if horizon_periods <= 0:
            raise ValueError("horizon_periods must be positive")
        if periods_per_year <= 0:
            raise ValueError("periods_per_year must be positive")
        metrics = calculate_metrics(prices, periods_per_year=periods_per_year)
        if metrics.annualized_return is None or metrics.annualized_volatility is None:
            return ForecastResult(
                horizon_periods=horizon_periods,
                available=False,
                trend=Trend.UNAVAILABLE,
                reason="insufficient price observations for return and volatility estimates",
            )

        years = horizon_periods / periods_per_year
        central = metrics.annualized_return * years + context_adjustment
        dispersion = metrics.annualized_volatility * sqrt(years)
        low = central - dispersion
        high = central + dispersion
        downside_low = min(0.0, low)
        downside_high = min(0.0, central) if low < 0 else 0.0
        threshold = max(dispersion * 0.25, 1e-12)
        if central > threshold:
            trend = Trend.UP
        elif central < -threshold:
            trend = Trend.DOWN
        else:
            trend = Trend.SIDEWAYS
        return ForecastResult(
            horizon_periods=horizon_periods,
            available=True,
            trend=trend,
            expected_return_low=low,
            expected_return_high=high,
            downside_low=downside_low,
            downside_high=downside_high,
        )

