"""Leakage-safe walk-forward evaluation for the forecast baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .engine import ForecastEngine, ForecastResult, Trend


@dataclass(frozen=True, slots=True)
class BacktestPoint:
    origin_index: int
    forecast: ForecastResult
    realized_return: float


@dataclass(frozen=True, slots=True)
class WalkForwardResult:
    points: tuple[BacktestPoint, ...]
    mean_absolute_error: float | None
    directional_accuracy: float | None


class WalkForwardEvaluator:
    def __init__(self, forecast_engine: ForecastEngine | None = None):
        self.forecast_engine = forecast_engine or ForecastEngine()

    def evaluate(
        self,
        prices: Sequence[float],
        *,
        horizon_periods: int,
        minimum_history: int = 30,
        periods_per_year: int = 252,
    ) -> WalkForwardResult:
        if horizon_periods <= 0 or minimum_history <= 1:
            raise ValueError("horizon_periods must be positive and minimum_history must exceed one")
        points: list[BacktestPoint] = []
        for origin in range(minimum_history, len(prices) - horizon_periods + 1):
            history = prices[:origin]
            forecast = self.forecast_engine.forecast(
                history,
                horizon_periods=horizon_periods,
                periods_per_year=periods_per_year,
            )
            realized = float(prices[origin + horizon_periods - 1]) / float(prices[origin - 1]) - 1.0
            points.append(BacktestPoint(origin, forecast, realized))

        usable = [
            point
            for point in points
            if point.forecast.available
            and point.forecast.expected_return_low is not None
            and point.forecast.expected_return_high is not None
        ]
        if not usable:
            return WalkForwardResult(tuple(points), None, None)
        errors = [
            abs((point.forecast.expected_return_low + point.forecast.expected_return_high) / 2 - point.realized_return)
            for point in usable
        ]
        directional = [
            (point.forecast.trend is Trend.UP and point.realized_return > 0)
            or (point.forecast.trend is Trend.DOWN and point.realized_return < 0)
            or (point.forecast.trend is Trend.SIDEWAYS and abs(point.realized_return) < 1e-12)
            for point in usable
        ]
        return WalkForwardResult(tuple(points), sum(errors) / len(errors), sum(directional) / len(directional))

