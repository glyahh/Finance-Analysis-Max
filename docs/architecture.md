# Architecture

The project is a modular monolith with layered boundaries:

`MCP / REST / ChatGPT adapters -> Orchestrator -> Evidence -> Research modules -> Forecast -> Ranking -> Renderer`

- `core/` contains provider-independent data contracts.
- `data/` contains timeout, cache, normalization, provenance, and fallback boundaries.
- `evidence/` distinguishes fact, opinion, and inference and preserves conflicts.
- `analytics/` and `forecast/` are deterministic and do not call an LLM.
- `research/` supplies market, macro, policy, fundamental, fund, news/event, sentiment, related-asset, and counter-evidence modules.
- `adapters/` are protocol boundaries; the research core does not depend on ChatGPT, Codex, or MCP.

The EastMoney live endpoint is wired through `EastMoneyProvider`; the current sandbox's TLS egress prevented live acceptance during this run, while offline provider/fallback behavior and MCP wiring are covered by tests.
