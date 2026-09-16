"""Single deterministic entry point for quantitative metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .returns import annualized_return, cumulative_return, validate_prices
from .risk import annualized_volatility, calmar_ratio, max_drawdown, sharpe_ratio
from .trend import linear_trend_slope, momentum


@dataclass(frozen=True, slots=True)
class AnalyticsResult:
    observations: int
    cumulative_return: float
    annualized_return: float | None
    annualized_volatility: float | None
    max_drawdown: float
    sharpe: float | None
    calmar: float | None
    momentum: float | None
    trend_slope: float | None


def calculate_metrics(
    prices: Sequence[float],
    *,
    periods_per_year: int = 252,
    risk_free_annual: float = 0.0,
) -> AnalyticsResult:
    validate_prices(prices)
    lookback = min(20, len(prices) - 1)
    return AnalyticsResult(
        observations=len(prices),
        cumulative_return=cumulative_return(prices),
        annualized_return=annualized_return(prices, periods_per_year),
        annualized_volatility=annualized_volatility(prices, periods_per_year),
        max_drawdown=max_drawdown(prices),
        sharpe=sharpe_ratio(
            prices,
            risk_free_annual=risk_free_annual,
            periods_per_year=periods_per_year,
        ),
        calmar=calmar_ratio(prices, periods_per_year),
        momentum=momentum(prices, lookback) if lookback > 0 else None,
        trend_slope=linear_trend_slope(prices),
    )

