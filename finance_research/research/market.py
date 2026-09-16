"""Market context coverage module."""

from .base import ResearchModule


class MarketResearch(ResearchModule):
    module_id = "market"
    required_topics = ("market", "benchmark", "volatility", "risk_appetite")

