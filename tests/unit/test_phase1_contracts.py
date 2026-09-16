from datetime import datetime, timezone
from decimal import Decimal

import pytest

from finance_research.core.models import (
    DataRequest,
    EvidenceType,
    Instrument,
    InstrumentType,
    ProviderResponse,
    SourceMetadata,
)
from finance_research.core.schemas import validate_provider_response
from finance_research.data.providers.base import DataProvider


class StubProvider(DataProvider):
    provider_id = "stub"

    def supports(self, request: DataRequest) -> bool:
        return request.operation == "instrument_info"

    def fetch(self, request: DataRequest) -> ProviderResponse:
        return ProviderResponse(
            provider=self.provider_id,
            request=request,
            records=({"price": Decimal("1.23")},),
            source=SourceMetadata(
                source="stub",
                fetched_at=datetime.now(timezone.utc),
            ),
        )


def test_domain_contracts_keep_instrument_and_evidence_types_explicit():
    instrument = Instrument("000001", "示例标的", InstrumentType.STOCK)
    assert instrument.instrument_type is InstrumentType.STOCK
    assert EvidenceType.FACT.value == "fact"


def test_provider_boundary_validates_and_returns_provenance():
    response = StubProvider().execute(DataRequest("instrument_info", subject="000001"))
    assert response.provider == "stub"
    assert response.source.fetched_at is not None


def test_provider_response_without_fetch_time_is_rejected():
    request = DataRequest("instrument_info")
    response = ProviderResponse(
        provider="stub",
        request=request,
        records=(),
        source=SourceMetadata(source="stub"),
    )
    with pytest.raises(ValueError, match="fetched_at"):
        validate_provider_response(response)

