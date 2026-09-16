"""Related-asset and dependency coverage module."""

from .base import ResearchModule


class RelatedAssetsResearch(ResearchModule):
    module_id = "related_assets"
    required_topics = ("related_asset", "upstream", "downstream", "commodity", "overseas_asset")

