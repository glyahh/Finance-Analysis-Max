from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from finance_research.core.models import DataRequest, ProviderResponse, SourceMetadata
from finance_research.data.cache import CachedJsonClient, FileCache
from finance_research.data.http import JsonResponse
from finance_research.data.normalization import normalize_klines, normalize_quote
from finance_research.data.providers import DataProvider, ProviderChain, ProviderError
from finance_research.data.providers.eastmoney import EastMoneyProvider


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def get_json(self, url, params=None):
        self.calls += 1
        return JsonResponse(self.payload, datetime.now(timezone.utc))


class FailingProvider(DataProvider):
    provider_id = "failing"

    def supports(self, request):
        return True

    def fetch(self, request):
        raise ProviderError("offline")


class WorkingProvider(DataProvider):
    provider_id = "working"

    def supports(self, request):
        return True

    def fetch(self, request):
        return ProviderResponse(
            provider=self.provider_id,
            request=request,
            records=({"ok": True},),
            source=SourceMetadata(source=self.provider_id, fetched_at=datetime.now(timezone.utc)),
        )


def test_eastmoney_payloads_normalize_without_fabricating_values():
    quote = normalize_quote({"data": {"f57": "000001", "f58": "平安银行", "f43": "10.5", "f169": "-"}})
    assert quote["price"] == 10.5
    assert quote["change_percent"] is None

    rows = normalize_klines({"data": {"klines": ["2026-01-01,10,11,12,9,100,1000,3,10,1,2"]}})
    assert rows[0]["close"] == 11
    assert rows[0]["turnover"] == 2


def test_file_cache_avoids_second_network_call(tmp_path: Path):
    client = FakeClient({"data": {"value": 1}})
    cached = CachedJsonClient(client, FileCache(tmp_path), timedelta(minutes=5))
    first = cached.get_json("https://example.test/data", {"id": "1"})
    second = cached.get_json("https://example.test/data", {"id": "1"})
    assert first.payload == second.payload
    assert second.from_cache is True
    assert client.calls == 1


def test_provider_chain_falls_back_in_order():
    response = ProviderChain([FailingProvider(), WorkingProvider()], retries=0).execute(
        DataRequest("get_market_data", subject="1.000001")
    )
    assert response.provider == "working"


def test_eastmoney_provider_keeps_source_provenance():
    client = FakeClient({"data": {"f57": "000001"}})
    response = EastMoneyProvider(client).execute(DataRequest("get_market_data", subject="1.000001"))
    assert response.source.source == "eastmoney"
    assert response.source.source_url.startswith("https://push2.eastmoney.com/")
    assert response.source.fetched_at.tzinfo is not None

