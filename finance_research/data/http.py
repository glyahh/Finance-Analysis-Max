"""Small dependency-free HTTP JSON client with bounded timeout handling."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


class HttpClientError(RuntimeError):
    """A transport or response decoding error."""


@dataclass(frozen=True, slots=True)
class JsonResponse:
    payload: Any
    fetched_at: datetime
    from_cache: bool = False


class JsonClient(Protocol):
    def get_json(self, url: str, params: Mapping[str, Any] | None = None) -> JsonResponse:
        ...


def build_url(url: str, params: Mapping[str, Any] | None = None) -> str:
    if not params:
        return url
    split = urlsplit(url)
    query = urlencode([(key, value) for key, value in params.items() if value is not None])
    return urlunsplit((split.scheme, split.netloc, split.path, query, split.fragment))


class UrllibJsonClient:
    def __init__(self, timeout_seconds: float = 10.0, user_agent: str = "finance-research/0.1"):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def get_json(self, url: str, params: Mapping[str, Any] | None = None) -> JsonResponse:
        target = build_url(url, params)
        request = Request(
            target,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "identity",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
                payload = json.loads(body.decode("utf-8-sig"))
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise HttpClientError(f"GET {target} failed: {exc}") from exc
        return JsonResponse(payload=payload, fetched_at=datetime.now(timezone.utc))

