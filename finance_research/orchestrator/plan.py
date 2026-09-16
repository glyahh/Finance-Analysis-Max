"""Small request planner; it asks only for information that changes forecast output."""

from __future__ import annotations

import re
from dataclasses import dataclass


_HORIZON_RE = re.compile(r"(?:未来|将来|next|for)\s*(\d+)\s*个?\s*(天|日|周|月|年|day|days|week|weeks|month|months|year|years)", re.I)


@dataclass(frozen=True, slots=True)
class ResearchPlan:
    horizon_periods: int | None
    missing_fields: tuple[str, ...]


def horizon_to_periods(amount: int, unit: str) -> int:
    unit = unit.lower()
    multipliers = {
        "天": 1,
        "日": 1,
        "周": 5,
        "月": 21,
        "年": 252,
        "day": 1,
        "days": 1,
        "week": 5,
        "weeks": 5,
        "month": 21,
        "months": 21,
        "year": 252,
        "years": 252,
    }
    return amount * multipliers[unit]


def make_plan(prompt: str, explicit_horizon_periods: int | None = None) -> ResearchPlan:
    horizon = explicit_horizon_periods
    if horizon is None:
        match = _HORIZON_RE.search(prompt)
        if match:
            horizon = horizon_to_periods(int(match.group(1)), match.group(2))
    missing = () if horizon and horizon > 0 else ("forecast_horizon",)
    return ResearchPlan(horizon_periods=horizon, missing_fields=missing)
