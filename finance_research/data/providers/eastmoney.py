"""EastMoney public quote/history provider.

The provider returns source payloads plus provenance. It does not turn missing
fields into zeroes and does not make analytical claims.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..http import HttpClientError, JsonClient
from ...core.models import DataRequest, ProviderResponse, SourceMetadata
from .base import DataProvider, ProviderError


class EastMoneyProvider(DataProvider):
    provider_id = "eastmoney"
    _quote_url = "https://push2.eastmoney.com/api/qt/stock/get"
    _history_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

    def __init__(self, client: JsonClient):
        self.client = client

    def supports(self, request: DataRequest) -> bool:
        return request.operation in {"get_market_data", "get_history"}

    def fetch(self, request: DataRequest) -> ProviderResponse:
        secid = request.parameters.get("secid") or request.subject
        if not secid:
            raise ProviderError("EastMoney requires parameters.secid or subject")
        if request.operation == "get_market_data":
            url = self._quote_url
            params = {"secid": secid, "fields": "f43,f57,f58,f169,f170"}
        else:
            url = self._history_url
            params = {
                "secid": secid,
                "klt": request.parameters.get("klt", 101),
                "fqt": request.parameters.get("fqt", 1),
                "beg": request.parameters.get("beg", "0"),
                "end": request.parameters.get("end", "20500101"),
                "fields1": "f1,f2,f3",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60",
            }
        try:
            response = self.client.get_json(url, params)
        except HttpClientError as exc:
            raise ProviderError(str(exc)) from exc
        return ProviderResponse(
            provider=self.provider_id,
            request=request,
            records=(response.payload,),
            source=SourceMetadata(
                source=self.provider_id,
                source_url=url,
                fetched_at=response.fetched_at,
                raw_reference=f"cache_hit={response.from_cache}",
            ),
        )

