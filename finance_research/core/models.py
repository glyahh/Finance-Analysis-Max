"""Stable domain models shared by all layers.

The first phase deliberately uses standard-library dataclasses so the core
contracts do not depend on an adapter, provider, or LLM framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Mapping


class InstrumentType(StrEnum):
    FUND = "fund"
    ETF = "etf"
    STOCK = "stock"
    INDEX = "index"
    INDUSTRY = "industry"
    SECTOR = "sector"
    PORTFOLIO = "portfolio"
    OTHER = "other"


class EvidenceType(StrEnum):
    FACT = "fact"
    OPINION = "opinion"
    INFERENCE = "inference"


@dataclass(frozen=True, slots=True)
class Instrument:
    """A researchable financial object identified by a provider-independent id."""

    instrument_id: str
    name: str
    instrument_type: InstrumentType
    market: str | None = None
    currency: str | None = None
    provider_symbols: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    """Provenance fields required before external data can enter the engine."""

    source: str
    source_url: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    raw_reference: str | None = None


@dataclass(frozen=True, slots=True)
class DataPoint:
    """A normalized time-series value with its source metadata."""

    timestamp: datetime
    value: Decimal
    metric: str
    subject: str
    source: SourceMetadata
    unit: str | None = None


@dataclass(frozen=True, slots=True)
class Evidence:
    """Evidence contract used by research and rendering layers."""

    evidence_type: EvidenceType
    topic: str
    value: Any
    subject: str
    source: SourceMetadata
    freshness: str | None = None


@dataclass(frozen=True, slots=True)
class DataRequest:
    """Provider-neutral request envelope.

    Providers may interpret ``parameters`` according to ``operation``, but
    the envelope keeps the orchestrator independent of any single source.
    """

    operation: str
    subject: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """Raw provider response before normalization and quality checks."""

    provider: str
    request: DataRequest
    records: tuple[Mapping[str, Any], ...]
    source: SourceMetadata

