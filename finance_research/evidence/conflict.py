"""Conflict detection that preserves all source claims for later resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from ..core.models import Evidence


@dataclass(frozen=True, slots=True)
class EvidenceConflict:
    subject: str
    topic: str
    evidence_ids: tuple[str, ...]
    values: tuple[Any, ...]


def _stable_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def detect_conflicts(
    evidence_items: Iterable[tuple[str, Evidence]],
) -> tuple[EvidenceConflict, ...]:
    grouped: dict[tuple[str, str], list[tuple[str, Evidence]]] = {}
    for evidence_id, evidence in evidence_items:
        grouped.setdefault((evidence.subject, evidence.topic), []).append((evidence_id, evidence))

    conflicts: list[EvidenceConflict] = []
    for (subject, topic), items in grouped.items():
        values: dict[str, Any] = {}
        ids: dict[str, list[str]] = {}
        for evidence_id, evidence in items:
            key = _stable_value(evidence.value)
            values.setdefault(key, evidence.value)
            ids.setdefault(key, []).append(evidence_id)
        if len(values) > 1:
            ordered_keys = sorted(values)
            conflicts.append(
                EvidenceConflict(
                    subject=subject,
                    topic=topic,
                    evidence_ids=tuple(item_id for key in ordered_keys for item_id in ids[key]),
                    values=tuple(values[key] for key in ordered_keys),
                )
            )
    return tuple(conflicts)

