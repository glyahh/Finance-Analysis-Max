"""Return calculations with explicit insufficient-data behavior."""

from __future__ import annotations

from math import isfinite
from typing import Sequence


def validate_prices(prices: Sequence[float]) -> None:
    if not prices:
        raise ValueError("prices must not be empty")
    if any(not isfinite(float(price)) or float(price) <= 0 for price in prices):
        raise ValueError("prices must be finite and positive")


def simple_returns(prices: Sequence[float]) -> tuple[float, ...]:
    validate_prices(prices)
    return tuple(float(current) / float(previous) - 1.0 for previous, current in zip(prices, prices[1:]))


def cumulative_return(prices: Sequence[float]) -> float:
    validate_prices(prices)
    return float(prices[-1]) / float(prices[0]) - 1.0


def annualized_return(prices: Sequence[float], periods_per_year: int = 252) -> float | None:
    validate_prices(prices)
    if len(prices) < 2 or periods_per_year <= 0:
        return None
    periods = len(prices) - 1
    return (float(prices[-1]) / float(prices[0])) ** (periods_per_year / periods) - 1.0

