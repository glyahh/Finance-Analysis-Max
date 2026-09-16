"""Normalize EastMoney quote and kline payloads without filling missing values."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


def _decimal(value: Any) -> Decimal | None:
    if value in (None, "", "-", "--"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def normalize_quote(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = payload.get("data") or {}
    return {
        "code": data.get("f57"),
        "name": data.get("f58"),
        "price": _decimal(data.get("f43")),
        "change_percent": _decimal(data.get("f169")),
        "change_amount": _decimal(data.get("f170")),
    }


def normalize_klines(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") or {}
    records: list[dict[str, Any]] = []
    for row in data.get("klines") or []:
        fields = str(row).split(",")
        if len(fields) < 11:
            continue
        records.append(
            {
                "date": fields[0],
                "open": _decimal(fields[1]),
                "close": _decimal(fields[2]),
                "high": _decimal(fields[3]),
                "low": _decimal(fields[4]),
                "volume": _decimal(fields[5]),
                "amount": _decimal(fields[6]),
                "amplitude": _decimal(fields[7]),
                "change_percent": _decimal(fields[8]),
                "change_amount": _decimal(fields[9]),
                "turnover": _decimal(fields[10]),
            }
        )
    return records

