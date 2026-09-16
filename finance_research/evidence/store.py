"""In-memory evidence store with deterministic ids and no source loss."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from ..core.models import Evidence
from .conflict import EvidenceConflict, detect_conflicts


@dataclass(frozen=True, slots=True)
class StoredEvidence:
    evidence_id: str
    evidence: Evidence


class EvidenceStore:
    def __init__(self):
        self._items: dict[str, Evidence] = {}

    @staticmethod
    def _id(evidence: Evidence) -> str:
        material = {
            "type": evidence.evidence_type.value,
            "topic": evidence.topic,
            "value": evidence.value,
            "subject": evidence.subject,
            "source": evidence.source.source,
            "source_url": evidence.source.source_url,
            "published_at": evidence.source.published_at.isoformat()
            if evidence.source.published_at
            else None,
            "fetched_at": evidence.source.fetched_at.isoformat()
            if evidence.source.fetched_at
            else None,
        }
        return hashlib.sha256(
            json.dumps(material, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

    def add(self, evidence: Evidence) -> str:
        evidence_id = self._id(evidence)
        self._items[evidence_id] = evidence
        return evidence_id

    def get(self, evidence_id: str) -> Evidence | None:
        return self._items.get(evidence_id)

    def all(self) -> tuple[StoredEvidence, ...]:
        return tuple(StoredEvidence(key, value) for key, value in self._items.items())

    def conflicts(self) -> tuple[EvidenceConflict, ...]:
        return detect_conflicts(self._items.items())

