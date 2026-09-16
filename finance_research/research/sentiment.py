"""Sentiment and market-opinion coverage module."""

from .base import ResearchModule


class SentimentResearch(ResearchModule):
    module_id = "sentiment"
    required_topics = ("sentiment", "social", "investor_opinion", "market_reputation")

