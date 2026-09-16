"""Cache decorator for JSON clients; transport remains independently replaceable."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import Any, Mapping

from ..http import HttpClientError, JsonClient, JsonResponse
from .file_cache import FileCache


class CachedJsonClient:
    def __init__(self, client: JsonClient, cache: FileCache, max_age: timedelta):
        if max_age.total_seconds() < 0:
            raise ValueError("max_age must not be negative")
        self.client = client
        self.cache = cache
        self.max_age = max_age

    @staticmethod
    def _key(url: str, params: Mapping[str, Any] | None) -> str:
        return json.dumps({"url": url, "params": params or {}}, sort_keys=True, default=str)

    def get_json(self, url: str, params: Mapping[str, Any] | None = None) -> JsonResponse:
        key = self._key(url, params)
        cached = self.cache.get(key, self.max_age)
        if cached is not None:
            return JsonResponse(payload=cached.payload, fetched_at=cached.stored_at, from_cache=True)
        try:
            response = self.client.get_json(url, params)
        except HttpClientError:
            raise
        self.cache.put(key, response.payload)
        return response

