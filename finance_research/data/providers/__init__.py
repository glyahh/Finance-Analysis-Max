"""Provider interfaces; concrete sources are added in Phase 2."""

from .base import DataProvider, ProviderError
from .chain import ProviderChain
from .eastmoney import EastMoneyProvider

__all__ = ["DataProvider", "EastMoneyProvider", "ProviderChain", "ProviderError"]
