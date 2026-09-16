"""Fund and holdings evidence coverage module."""

from .base import ResearchModule


class FundResearch(ResearchModule):
    module_id = "fund"
    required_topics = ("fund_type", "nav", "holdings", "fund_manager", "fund_size", "sector_exposure")

