"""Evidence engine facade used by later research modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..core.models import Evidence
from .conflict import EvidenceConflict
from .freshness import FreshnessStatus, classify_freshness
from .store import EvidenceStore


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    evidence_id: str
    freshness: FreshnessStatus
    conflicts: tuple[EvidenceConflict, ...]
    usable: bool


class EvidenceEngine:
    def __init__(
        self,
        store: EvidenceStore | None = None,
        *,
        default_max_age: timedelta = timedelta(days=7),
    ):
        if default_max_age.total_seconds() < 0:
            raise ValueError("default_max_age must not be negative")
        self.store = store or EvidenceStore()
        self.default_max_age = default_max_age

    def ingest(
        self,
        evidence: Evidence,
        *,
        now: datetime | None = None,
        max_age: timedelta | None = None,
    ) -> EvidenceAssessment:
        if evidence.source.source.strip() == "":
            raise ValueError("evidence requires a source")
        now = now or datetime.now(timezone.utc)
        evidence_id = self.store.add(evidence)
        freshness = classify_freshness(
            evidence,
            now=now,
            max_age=max_age if max_age is not None else self.default_max_age,
        )
        conflicts = tuple(
            conflict
            for conflict in self.store.conflicts()
            if evidence_id in conflict.evidence_ids
        )
        return EvidenceAssessment(
            evidence_id=evidence_id,
            freshness=freshness,
            conflicts=conflicts,
            usable=freshness is not FreshnessStatus.FUTURE,
        )

