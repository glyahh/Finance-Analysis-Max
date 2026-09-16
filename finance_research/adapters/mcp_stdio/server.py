"""Minimal dependency-free MCP stdio JSON-RPC server.

The server keeps the protocol adapter thin. It never fabricates data for tools
that need an external provider which has not been configured.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, TextIO

from ...analytics import calculate_metrics
from ...core.models import DataRequest, Evidence, EvidenceType, SourceMetadata
from ...data.cache import CachedJsonClient, FileCache
from ...data.http import UrllibJsonClient
from ...data.normalization import normalize_klines, normalize_quote
from ...data.providers import EastMoneyProvider, ProviderChain, ProviderError
from ...forecast import ForecastEngine
from ...orchestrator import CandidateInput, ResearchOrchestrator, ResearchRequest


UNAVAILABLE_DATA_TOOLS = {
    "search_instruments",
    "get_instrument_info",
    "get_fund_holdings",
    "get_financials",
    "get_capital_flow",
    "get_macro_data",
    "search_news",
    "search_sentiment",
}


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _text_result(payload: Any, *, is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(_jsonable(payload), ensure_ascii=False)}],
        "structuredContent": _jsonable(payload),
        "isError": is_error,
    }


TOOL_DEFINITIONS = [
    {
        "name": "calculate_metrics",
        "description": "Calculate deterministic historical risk and return metrics.",
        "inputSchema": {"type": "object", "required": ["prices"], "properties": {"prices": {"type": "array", "items": {"type": "number"}}, "periods_per_year": {"type": "integer"}}},
    },
    {
        "name": "forecast_instrument",
        "description": "Create a transparent baseline range from supplied historical prices.",
        "inputSchema": {"type": "object", "required": ["prices", "horizon_periods"], "properties": {"prices": {"type": "array", "items": {"type": "number"}}, "horizon_periods": {"type": "integer"}}},
    },
    {
        "name": "research_instrument",
        "description": "Run evidence-first research on supplied candidate data.",
        "inputSchema": {"type": "object", "required": ["instrument_id", "name", "prices", "evidence", "horizon_periods"], "properties": {"instrument_id": {"type": "string"}, "name": {"type": "string"}, "prices": {"type": "array", "items": {"type": "number"}}, "horizon_periods": {"type": "integer"}, "evidence": {"type": "array"}}},
    },
    {
        "name": "get_market_data",
        "description": "Fetch and normalize current market data through the configured provider chain.",
        "inputSchema": {"type": "object", "required": ["secid"], "properties": {"secid": {"type": "string"}}},
    },
    {
        "name": "get_history",
        "description": "Fetch and normalize historical market data through the configured provider chain.",
        "inputSchema": {"type": "object", "required": ["secid"], "properties": {"secid": {"type": "string"}, "beg": {"type": "string"}, "end": {"type": "string"}}},
    },
]
TOOL_DEFINITIONS.extend(
    {
        "name": name,
        "description": "External data operation; requires a configured provider.",
        "inputSchema": {"type": "object"},
    }
    for name in sorted(UNAVAILABLE_DATA_TOOLS)
)


class McpServer:
    protocol_version = "2025-06-18"

    def __init__(self, provider_chain: ProviderChain | None = None):
        self.orchestrator = ResearchOrchestrator()
        if provider_chain is None:
            client = CachedJsonClient(
                UrllibJsonClient(timeout_seconds=10),
                FileCache(Path(".finance-research-cache")),
                timedelta(minutes=5),
            )
            provider_chain = ProviderChain([EastMoneyProvider(client)], retries=1)
        self.provider_chain = provider_chain

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any] | None:
        request_id = request.get("id")
        method = request.get("method")
        if request.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return _error(request_id, -32600, "invalid JSON-RPC request")
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "finance-research", "version": "0.1.0"},
                },
            }
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOL_DEFINITIONS}}
        if method == "tools/call":
            params = request.get("params") or {}
            return self._call_tool(request_id, params.get("name"), params.get("arguments") or {})
        return _error(request_id, -32601, f"method not found: {method}")

    def _call_tool(self, request_id: Any, name: str | None, arguments: dict[str, Any]) -> dict[str, Any]:
        if not name:
            return _error(request_id, -32602, "tool name is required")
        try:
            if name in UNAVAILABLE_DATA_TOOLS:
                return {"jsonrpc": "2.0", "id": request_id, "result": _text_result({"status": "unavailable", "reason": "no external provider configured"}, is_error=True)}
            if name in {"get_market_data", "get_history"}:
                payload = self._provider_data(name, arguments)
                return {"jsonrpc": "2.0", "id": request_id, "result": _text_result(payload)}
            if name == "calculate_metrics":
                payload = calculate_metrics(arguments["prices"], periods_per_year=arguments.get("periods_per_year", 252))
            elif name == "forecast_instrument":
                payload = ForecastEngine().forecast(arguments["prices"], horizon_periods=arguments["horizon_periods"])
            elif name == "research_instrument":
                payload = self._research(arguments)
            else:
                return _error(request_id, -32602, f"unknown tool: {name}")
            return {"jsonrpc": "2.0", "id": request_id, "result": _text_result(payload)}
        except (KeyError, TypeError, ValueError, ProviderError) as exc:
            return _error(request_id, -32602, str(exc))

    def _provider_data(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        subject = arguments.get("secid") or arguments.get("subject")
        if not subject:
            raise ValueError("secid or subject is required")
        request = DataRequest(
            operation=name,
            subject=subject,
            parameters={key: value for key, value in arguments.items() if key not in {"secid", "subject"}},
        )
        response = self.provider_chain.execute(request)
        raw = response.records[0]
        normalized = normalize_quote(raw) if name == "get_market_data" else normalize_klines(raw)
        return {
            "provider": response.provider,
            "source": response.source.source,
            "source_url": response.source.source_url,
            "fetched_at": response.source.fetched_at,
            "normalized": normalized,
        }

    def _research(self, arguments: dict[str, Any]) -> Any:
        evidence = tuple(self._parse_evidence(arguments["instrument_id"], item) for item in arguments["evidence"])
        outcome = self.orchestrator.research(
            ResearchRequest(
                prompt=f"研究未来{arguments['horizon_periods']}个交易周期",
                explicit_horizon_periods=arguments["horizon_periods"],
            ),
            [CandidateInput(arguments["instrument_id"], arguments["name"], arguments["prices"], evidence)],
        )
        return outcome

    @staticmethod
    def _parse_evidence(subject: str, item: dict[str, Any]) -> Evidence:
        fetched_at = datetime.fromisoformat(item["fetched_at"]) if item.get("fetched_at") else None
        published_at = datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None
        return Evidence(
            evidence_type=EvidenceType(item.get("type", "fact")),
            topic=item["topic"],
            value=item.get("value"),
            subject=item.get("subject", subject),
            source=SourceMetadata(
                source=item["source"],
                source_url=item.get("source_url"),
                fetched_at=fetched_at,
                published_at=published_at,
            ),
        )


def serve_stdio(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
    """Read MCP Content-Length frames; accept JSON lines for local smoke tests."""

    server = McpServer()
    while True:
        first = stdin.readline()
        if not first:
            break
        first = first.strip()
        if not first:
            continue
        if first.lower().startswith("content-length:"):
            length = int(first.split(":", 1)[1].strip())
            while stdin.readline().strip():
                pass
            raw = stdin.read(length)
        else:
            raw = first
        response = server.dispatch(json.loads(raw))
        if response is not None:
            encoded = json.dumps(response, ensure_ascii=False).encode("utf-8")
            stdout.write(f"Content-Length: {len(encoded)}\r\n\r\n")
            stdout.write(encoded.decode("utf-8"))
            stdout.flush()
