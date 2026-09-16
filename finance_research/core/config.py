"""Configuration kept independent from provider and adapter implementations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    cache_dir: Path = Path(".finance-research-cache")
    provider_timeout_seconds: float = 10.0
    provider_retry_count: int = 2

    def __post_init__(self) -> None:
        if self.provider_timeout_seconds <= 0:
            raise ValueError("provider_timeout_seconds must be positive")
        if self.provider_retry_count < 0:
            raise ValueError("provider_retry_count must not be negative")

