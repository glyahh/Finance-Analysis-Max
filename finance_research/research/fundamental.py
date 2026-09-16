"""Company fundamental evidence coverage module."""

from .base import ResearchModule


class FundamentalResearch(ResearchModule):
    module_id = "fundamental"
    required_topics = ("financials", "revenue", "earnings", "cash_flow", "valuation", "competition")

