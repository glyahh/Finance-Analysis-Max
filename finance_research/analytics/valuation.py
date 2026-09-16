"""Generic valuation positioning helpers; no valuation data is fabricated here."""

from __future__ import annotations

from typing import Sequence


def percentile_rank(history: Sequence[float], current: float) -> float | None:
    """Return the fraction of historical values <= current, or None if empty."""

    if not history:
        return None
    return sum(float(value) <= float(current) for value in history) / len(history)

