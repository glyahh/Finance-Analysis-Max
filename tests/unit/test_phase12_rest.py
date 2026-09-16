import json
import threading
from urllib.request import Request, urlopen

from finance_research.adapters.rest.server import create_server


def request_json(url, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, method=method, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urlopen(request, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_rest_health_tools_and_remote_mcp():
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        status, health = request_json(base + "/healthz")
        assert status == 200 and health["status"] == "ok"
        status, tools = request_json(base + "/v1/tools")
        assert status == 200 and any(tool["name"] == "calculate_metrics" for tool in tools["tools"])
        status, response = request_json(
            base + "/mcp",
            method="POST",
            payload={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        )
        assert status == 200 and response["result"]["serverInfo"]["name"] == "finance-research"
    finally:
        server.shutdown()
        server.server_close()

