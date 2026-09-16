"""Macro context coverage module."""

from .base import ResearchModule


class MacroResearch(ResearchModule):
    module_id = "macro"
    required_topics = ("gdp", "cpi", "ppi", "pmi", "interest_rate", "liquidity", "fx", "employment")

