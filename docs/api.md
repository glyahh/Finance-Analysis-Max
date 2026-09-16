# API and tool list

## Deterministic tools

- `calculate_metrics`
- `forecast_instrument`
- `research_instrument`

## Provider-facing responsibilities

- `search_instruments`
- `get_instrument_info`
- `get_market_data`
- `get_history`
- `get_fund_holdings`
- `get_financials`
- `get_capital_flow`
- `get_macro_data`
- `search_news`
- `search_sentiment`

`get_market_data` and `get_history` are wired to the EastMoney Provider chain and return normalized records with provenance. The remaining provider-facing names return an explicit unavailable state until their corresponding provider is wired. This is preferable to returning fabricated financial data.
