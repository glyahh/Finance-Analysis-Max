"""Dependency-free REST and remote MCP HTTP adapter."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from ..mcp_stdio.server import McpServer, TOOL_DEFINITIONS


MAX_BODY_BYTES = 2 * 1024 * 1024


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def create_server(host: str = "127.0.0.1", port: int = 8000, mcp: McpServer | None = None) -> ThreadingHTTPServer:
    protocol = mcp or McpServer()

    class Handler(BaseHTTPRequestHandler):
        server_version = "finance-research/0.1"

        def _send_json(self, status: int, payload: Any) -> None:
            body = _json_bytes(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/healthz":
                self._send_json(200, {"status": "ok", "service": "finance-research"})
            elif path in {"/v1/tools", "/mcp/tools"}:
                self._send_json(200, {"tools": TOOL_DEFINITIONS})
            else:
                self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            length = self.headers.get("Content-Length")
            try:
                size = int(length or "0")
            except ValueError:
                self._send_json(400, {"error": "invalid_content_length"})
                return
            if size < 0 or size > MAX_BODY_BYTES:
                self._send_json(413, {"error": "request_too_large"})
                return
            try:
                request = json.loads(self.rfile.read(size).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": f"invalid_json: {exc}"})
                return
            path = urlparse(self.path).path
            if path == "/mcp":
                response = protocol.dispatch(request)
                if response is None:
                    self.send_response(204)
                    self.end_headers()
                else:
                    self._send_json(200, response)
                return
            if path.startswith("/v1/tools/"):
                name = path.removeprefix("/v1/tools/")
                response = protocol.dispatch(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id", 1),
                        "method": "tools/call",
                        "params": {"name": name, "arguments": request.get("arguments", request)},
                    }
                )
                self._send_json(200, response)
                return
            self._send_json(404, {"error": "not_found"})

        def log_message(self, format: str, *args: Any) -> None:
            return

    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host, port)
    try:
        server.serve_forever()
    finally:
        server.server_close()

