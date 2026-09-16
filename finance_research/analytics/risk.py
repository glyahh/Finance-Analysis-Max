"""Risk metrics calculated only from supplied historical observations."""

from __future__ import annotations

import statistics
from typing import Sequence

from .returns import simple_returns, validate_prices


def annualized_volatility(prices: Sequence[float], periods_per_year: int = 252) -> float | None:
    returns = simple_returns(prices)
    if len(returns) < 2 or periods_per_year <= 0:
        return None
    return statistics.stdev(returns) * periods_per_year**0.5


def max_drawdown(prices: Sequence[float]) -> float:
    validate_prices(prices)
    peak = float(prices[0])
    worst = 0.0
    for value in prices:
        price = float(value)
        peak = max(peak, price)
        worst = min(worst, price / peak - 1.0)
    return worst


def sharpe_ratio(
    prices: Sequence[float],
    *,
    risk_free_annual: float = 0.0,
    periods_per_year: int = 252,
) -> float | None:
    volatility = annualized_volatility(prices, periods_per_year)
    if volatility in (None, 0):
        return None
    from .returns import annualized_return

    return (annualized_return(prices, periods_per_year) - risk_free_annual) / volatility


def calmar_ratio(prices: Sequence[float], periods_per_year: int = 252) -> float | None:
    drawdown = max_drawdown(prices)
    if drawdown == 0:
        return None
    from .returns import annualized_return

    return annualized_return(prices, periods_per_year) / abs(drawdown)

