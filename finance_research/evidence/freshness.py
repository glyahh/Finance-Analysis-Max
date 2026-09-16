"""Explicit freshness classification; no silent date assumptions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import StrEnum

from ..core.models import Evidence


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"
    FUTURE = "future"


def classify_freshness(
    evidence: Evidence,
    *,
    now: datetime,
    max_age: timedelta,
) -> FreshnessStatus:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must include timezone information")
    fetched_at = evidence.source.fetched_at
    if fetched_at is None or fetched_at.tzinfo is None or fetched_at.utcoffset() is None:
        return FreshnessStatus.UNKNOWN
    fetched_at = fetched_at.astimezone(timezone.utc)
    now = now.astimezone(timezone.utc)
    if fetched_at > now:
        return FreshnessStatus.FUTURE
    return FreshnessStatus.FRESH if now - fetched_at <= max_age else FreshnessStatus.STALE

