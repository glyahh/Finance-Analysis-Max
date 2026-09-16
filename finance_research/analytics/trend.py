"""Momentum and trend features."""

from __future__ import annotations

from typing import Sequence

from .returns import validate_prices


def momentum(prices: Sequence[float], lookback: int) -> float | None:
    validate_prices(prices)
    if lookback <= 0 or len(prices) <= lookback:
        return None
    return float(prices[-1]) / float(prices[-1 - lookback]) - 1.0


def linear_trend_slope(prices: Sequence[float]) -> float | None:
    validate_prices(prices)
    if len(prices) < 2:
        return None
    x_values = range(len(prices))
    x_mean = (len(prices) - 1) / 2
    y_mean = sum(float(value) for value in prices) / len(prices)
    numerator = sum((x - x_mean) * (float(y) - y_mean) for x, y in zip(x_values, prices))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    return numerator / denominator

