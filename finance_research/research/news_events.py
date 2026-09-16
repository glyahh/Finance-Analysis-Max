"""News and event evidence coverage modules."""

from .base import ResearchModule


class NewsResearch(ResearchModule):
    module_id = "news"
    required_topics = ("news", "company_event", "industry_event", "policy_event")


class EventResearch(ResearchModule):
    module_id = "events"
    required_topics = ("event", "geopolitics", "earnings_event", "regulatory_event", "shock")

