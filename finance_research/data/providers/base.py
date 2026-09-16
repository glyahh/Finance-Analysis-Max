"""Provider boundary for all external financial data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...core.models import DataRequest, ProviderResponse
from ...core.schemas import validate_request, validate_provider_response


class ProviderError(RuntimeError):
    """A provider-specific failure that the data layer can handle or fallback from."""


class DataProvider(ABC):
    """Common interface implemented by EastMoney, finshare, and backups.

    Retry, timeout, freshness, caching, and fallback policies belong above this
    boundary; a provider only fetches data and reports provenance.
    """

    provider_id: str

    @abstractmethod
    def supports(self, request: DataRequest) -> bool:
        """Return whether this provider can service the request."""

    @abstractmethod
    def fetch(self, request: DataRequest) -> ProviderResponse:
        """Fetch raw records and provenance without inventing missing values."""

    def execute(self, request: DataRequest) -> ProviderResponse:
        """Validate the request and the provider's response at the boundary."""

        validate_request(request)
        if not self.supports(request):
            raise ProviderError(
                f"provider {self.provider_id!r} does not support {request.operation!r}"
            )
        response = self.fetch(request)
        return validate_provider_response(response)

