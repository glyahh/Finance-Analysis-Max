"""Ordered provider fallback with bounded retries and explicit errors."""

from __future__ import annotations

from time import sleep

from ...core.models import DataRequest, ProviderResponse
from .base import DataProvider, ProviderError


class ProviderChain:
    def __init__(self, providers: list[DataProvider], retries: int = 1, backoff_seconds: float = 0.1):
        if not providers:
            raise ValueError("at least one provider is required")
        if retries < 0 or backoff_seconds < 0:
            raise ValueError("retries and backoff_seconds must not be negative")
        self.providers = providers
        self.retries = retries
        self.backoff_seconds = backoff_seconds

    def execute(self, request: DataRequest) -> ProviderResponse:
        failures: list[str] = []
        for provider in self.providers:
            if not provider.supports(request):
                continue
            for attempt in range(self.retries + 1):
                try:
                    return provider.execute(request)
                except (ProviderError, OSError, TimeoutError) as exc:
                    failures.append(f"{provider.provider_id}[{attempt + 1}]: {exc}")
                    if attempt < self.retries and self.backoff_seconds:
                        sleep(self.backoff_seconds * (attempt + 1))
        detail = "; ".join(failures) or "no provider supports request"
        raise ProviderError(f"all providers failed for {request.operation!r}: {detail}")

