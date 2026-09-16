"""Common contract for deterministic research modules."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable

from ..core.models import Evidence, EvidenceType
from ..evidence.store import StoredEvidence


@dataclass(frozen=True, slots=True)
class ResearchContext:
    subject: str
    evidence: tuple[StoredEvidence, ...]


@dataclass(frozen=True, slots=True)
class ModuleResult:
    module: str
    subject: str
    evidence_ids: tuple[str, ...]
    observed_topics: tuple[str, ...]
    missing_topics: tuple[str, ...]
    fact_count: int
    opinion_count: int
    inference_count: int

    @property
    def evidence_count(self) -> int:
        return len(self.evidence_ids)


class ResearchModule(ABC):
    module_id = "base"
    required_topics: tuple[str, ...] = ()

    def run(self, context: ResearchContext) -> ModuleResult:
        relevant = tuple(
            item
            for item in context.evidence
            if item.evidence.subject in {context.subject, "*"}
        )
        module_items = tuple(item for item in relevant if item.evidence.topic.lower() in self.required_topics)
        topic_set = {item.evidence.topic.lower() for item in module_items}
        observed = tuple(topic for topic in self.required_topics if topic in topic_set)
        missing = tuple(topic for topic in self.required_topics if topic not in topic_set)
        return ModuleResult(
            module=self.module_id,
            subject=context.subject,
            evidence_ids=tuple(item.evidence_id for item in module_items),
            observed_topics=observed,
            missing_topics=missing,
            fact_count=sum(item.evidence.evidence_type is EvidenceType.FACT for item in module_items),
            opinion_count=sum(item.evidence.evidence_type is EvidenceType.OPINION for item in module_items),
            inference_count=sum(item.evidence.evidence_type is EvidenceType.INFERENCE for item in module_items),
        )
