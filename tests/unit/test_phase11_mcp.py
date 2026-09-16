import json
from datetime import datetime, timezone

from finance_research.adapters.mcp_stdio.server import McpServer
from finance_research.data.http import JsonResponse
from finance_research.data.providers import EastMoneyProvider, ProviderChain


class FakeClient:
    def get_json(self, url, params=None):
        return JsonResponse(
            {"data": {"f57": "000001", "f58": "示例", "f43": "10.5", "f169": "1.2", "f170": "0.1"}},
            datetime.now(timezone.utc),
        )


def test_mcp_initialize_and_tools_list():
    server = McpServer()
    initialized = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert initialized["result"]["serverInfo"]["name"] == "finance-research"
    tools = server.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {tool["name"] for tool in tools["result"]["tools"]}
    assert {"calculate_metrics", "forecast_instrument", "research_instrument"} <= names


def test_mcp_calculate_metrics_returns_structured_content():
    server = McpServer()
    response = server.dispatch(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "calculate_metrics", "arguments": {"prices": [100, 101, 103]}},
        }
    )
    assert response["result"]["structuredContent"]["observations"] == 3
    assert response["result"]["isError"] is False


def test_mcp_does_not_fake_unconfigured_external_data():
    server = McpServer()
    response = server.dispatch(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "search_instruments", "arguments": {"query": "000001"}},
        }
    )
    assert response["result"]["isError"] is True
    assert response["result"]["structuredContent"]["status"] == "unavailable"


def test_mcp_wires_market_data_through_injected_provider_chain():
    server = McpServer(ProviderChain([EastMoneyProvider(FakeClient())], retries=0))
    response = server.dispatch(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "get_market_data", "arguments": {"secid": "1.000001"}},
        }
    )
    assert response["result"]["structuredContent"]["normalized"]["price"] == "10.5"
    assert response["result"]["structuredContent"]["source"] == "eastmoney"
