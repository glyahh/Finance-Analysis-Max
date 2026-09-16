# Configuration and local run

No third-party runtime dependency is required.

## Tests

```powershell
python -m pytest -q
```

## stdio MCP

```powershell
python -m finance_research.adapters.mcp_stdio
```

Register the command in a local MCP client with transport `stdio`, working directory set to this project, and command `python -m finance_research.adapters.mcp_stdio`.

## REST and Remote MCP

```powershell
python -m finance_research.adapters.rest --host 127.0.0.1 --port 8000
```

- `GET /healthz`
- `GET /v1/tools`
- `POST /v1/tools/{tool_name}`
- `POST /mcp`

External data tools return an explicit unavailable result until a provider is configured; they never invent records.

