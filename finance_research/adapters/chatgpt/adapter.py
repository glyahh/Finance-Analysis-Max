"""ChatGPT-shaped adapter kept independent from ChatGPT product APIs."""

from __future__ import annotations

from typing import Any

from ...orchestrator import CandidateInput, ResearchOrchestrator, ResearchRequest
from ...output import render_result
from ..mcp_stdio.server import McpServer, _jsonable


class ChatGPTAdapter:
    """Translate a plain JSON request into the platform-independent research core."""

    def __init__(self, orchestrator: ResearchOrchestrator | None = None):
        self.orchestrator = orchestrator or ResearchOrchestrator()

    def respond(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt = request.get("prompt", "")
        candidates = request.get("candidates", [])
        if not isinstance(prompt, str) or not isinstance(candidates, list):
            return {"status": "error", "error": "prompt must be a string and candidates must be a list"}
        try:
            inputs = tuple(
                CandidateInput(
                    instrument_id=item["instrument_id"],
                    name=item["name"],
                    prices=item["prices"],
                    evidence=tuple(
                        McpServer._parse_evidence(item["instrument_id"], evidence)
                        for evidence in item["evidence"]
                    ),
                )
                for item in candidates
            )
            outcome = self.orchestrator.research(
                ResearchRequest(
                    prompt=prompt,
                    explicit_horizon_periods=request.get("horizon_periods"),
                    minimum_evidence=request.get("minimum_evidence", 3),
                ),
                inputs,
            )
        except (KeyError, TypeError, ValueError) as exc:
            return {"status": "error", "error": str(exc)}
        return {
            "status": outcome.status.value,
            "answer": render_result(outcome),
            "structured": _jsonable(outcome),
        }

