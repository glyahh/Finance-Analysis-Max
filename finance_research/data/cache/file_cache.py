"""Atomic JSON file cache for provider responses."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class CacheEntry:
    payload: Any
    stored_at: datetime


class FileCache:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.directory / f"{digest}.json"

    def get(self, key: str, max_age: timedelta) -> CacheEntry | None:
        path = self._path(key)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            stored_at = datetime.fromisoformat(record["stored_at"]).astimezone(timezone.utc)
            if datetime.now(timezone.utc) - stored_at > max_age:
                return None
            return CacheEntry(payload=record["payload"], stored_at=stored_at)
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

    def put(self, key: str, payload: Any) -> CacheEntry:
        stored_at = datetime.now(timezone.utc)
        path = self._path(key)
        record = {"stored_at": stored_at.isoformat(), "payload": payload}
        fd, temporary = tempfile.mkstemp(prefix=".cache-", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(record, handle, ensure_ascii=False, separators=(",", ":"))
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return CacheEntry(payload=payload, stored_at=stored_at)

