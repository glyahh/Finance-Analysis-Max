---
name: finance-research
description: "Run evidence-first research for funds, stocks, ETFs, indices, sectors, and portfolios through the local Finance Analysis Max Python engine. Trigger on @finance-research, $finance-research, or clear requests for financial analysis, forecasting, screening, comparison, or recommendation."
---

# Finance Analysis Max

Use the local `finance-analysis-max-local` MCP server as the computation and data boundary. Do not replace tool results with model memory, invented values, or an implied successful lookup.

## Request workflow

1. Parse the requested instruments, asset type, horizon, risk tolerance, capital, holding period, objective, and ranking priorities.
2. Ask one concise question for missing information only when it would materially change the result, especially the forecast horizon or recommendation constraints.
3. Use the local MCP tools for structured work:
   - `search_instruments`: resolve candidates when its provider is available.
   - `get_instrument_info`: resolve identity and metadata.
   - `get_market_data`: obtain current normalized market data.
   - `get_history`: obtain historical normalized data.
   - `get_fund_holdings`: obtain fund holdings.
   - `get_financials`: obtain financial statements and fundamentals.
   - `get_capital_flow`: obtain capital-flow data.
   - `get_macro_data`: obtain macroeconomic data.
   - `search_news`: obtain dated news and event evidence.
   - `search_sentiment`: obtain sentiment and market-opinion evidence.
   - `calculate_metrics`: calculate deterministic return and risk metrics.
   - `forecast_instrument`: calculate the transparent baseline forecast range.
   - `research_instrument`: run evidence ingestion, research modules, counter-evidence, forecast, and ranking for supplied candidates.
4. When the local provider cannot supply a requested category, use Chat's available search capability for public evidence if available. Label every search result with source, URL, publication time, retrieval time, and whether it is fact, opinion, or inference.
5. Pass only evidence-backed prices and evidence into the local research tools. Never fabricate a candidate, price, holding, financial number, macro value, news event, or provider response.
6. Check both supporting and opposing evidence. Reject or qualify candidates when key data is missing, stale, contradictory, or below the evidence threshold.
7. Return the project report contract in this order:
   1. 研究结论摘要
   2. 关键驱动因素（利好、利空、最可能推翻当前判断的因素）
   3. 多维度分析
   4. 风险与重新评估条件
   5. 未来走势
   6. 购买优先级

## Evidence and output rules

- Distinguish facts, market opinions, and model inferences.
- Attach source and time to every key external fact and quantitative value.
- Do not promise returns or present a historical metric as a future guarantee.
- If a provider or search capability is unavailable, say so and preserve the data gap in the answer.
- Do not force five recommendations; output fewer or “暂无推荐” when the evidence gate is not met.
- Keep analysis and risk explanations before the final purchase-priority list.
- The Python engine performs deterministic parsing, validation, metrics, forecasting, caching, and ranking; Chat performs request understanding, evidence search when available, synthesis, and presentation.

## Invocation

- Primary local Chat invocation: `@finance-research`.
- The workflow must work without the REST service and without any public endpoint.
- The local MCP process is launched by the Codex client from this plugin's root; do not ask the user to start an HTTP server for ordinary Chat research.
