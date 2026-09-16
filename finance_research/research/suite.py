"""Run the fixed first-version module set without turning each module into a service."""

from __future__ import annotations

from collections.abc import Iterable

from .base import ModuleResult, ResearchContext, ResearchModule
from .fund import FundResearch
from .fundamental import FundamentalResearch
from .macro import MacroResearch
from .market import MarketResearch
from .news_events import EventResearch, NewsResearch
from .policy import PolicyResearch
from .related_assets import RelatedAssetsResearch
from .sentiment import SentimentResearch


def default_modules() -> tuple[ResearchModule, ...]:
    return (
        MarketResearch(),
        MacroResearch(),
        PolicyResearch(),
        FundamentalResearch(),
        FundResearch(),
        NewsResearch(),
        EventResearch(),
        SentimentResearch(),
        RelatedAssetsResearch(),
    )


def run_modules(
    subject: str,
    evidence: Iterable,
    modules: Iterable[ResearchModule] | None = None,
) -> tuple[ModuleResult, ...]:
    context = ResearchContext(subject=subject, evidence=tuple(evidence))
    return tuple(module.run(context) for module in (modules or default_modules()))

