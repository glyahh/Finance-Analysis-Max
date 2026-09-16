"""Pairwise correlation for aligned price series."""

from __future__ import annotations

import statistics
from typing import Sequence

from .returns import simple_returns


def correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    left_returns = simple_returns(left)
    right_returns = simple_returns(right)
    if len(left_returns) != len(right_returns) or len(left_returns) < 2:
        return None
    if statistics.stdev(left_returns) == 0 or statistics.stdev(right_returns) == 0:
        return None
    return statistics.correlation(left_returns, right_returns)

