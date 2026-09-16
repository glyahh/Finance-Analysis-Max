import argparse

from .server import serve


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finance research REST and remote MCP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(args.host, args.port)

