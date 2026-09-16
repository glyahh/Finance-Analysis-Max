"""Validation helpers for the phase-one contracts."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import DataRequest, Instrument, ProviderResponse


def ensure_utc(value: datetime) -> datetime:
    """Return an aware UTC datetime and reject ambiguous naive timestamps."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must include timezone information")
    return value.astimezone(timezone.utc)


def validate_instrument(instrument: Instrument) -> Instrument:
    if not instrument.instrument_id.strip():
        raise ValueError("instrument_id must not be empty")
    if not instrument.name.strip():
        raise ValueError("name must not be empty")
    return instrument


def validate_request(request: DataRequest) -> DataRequest:
    if not request.operation.strip():
        raise ValueError("operation must not be empty")
    if request.start and request.end and ensure_utc(request.start) > ensure_utc(request.end):
        raise ValueError("request start must not be after end")
    return request


def validate_provider_response(response: ProviderResponse) -> ProviderResponse:
    if not response.provider.strip():
        raise ValueError("provider must not be empty")
    validate_request(response.request)
    if response.source.fetched_at is None:
        raise ValueError("provider response requires fetched_at provenance")
    ensure_utc(response.source.fetched_at)
    return response

