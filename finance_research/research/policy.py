"""Policy evidence coverage module."""

from .base import ResearchModule


class PolicyResearch(ResearchModule):
    module_id = "policy"
    required_topics = ("fiscal_policy", "monetary_policy", "industry_policy", "regulation")

