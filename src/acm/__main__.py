"""CLI de ACM.

acm serve [--host H] [--port P] [--data-dir D]   # proceso ASGI: /api y /mcp (Streamable HTTP)
acm mcp-stdio [--data-dir D]                     # servidor MCP por stdio para agentes locales
"""

from __future__ import annotations

import argparse
import sys

from acm.config import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acm", description="Agile Context Manager")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="sirve /api y /mcp por HTTP")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    serve.add_argument("--data-dir")
    stdio = sub.add_parser("mcp-stdio", help="servidor MCP por stdio")
    stdio.add_argument("--data-dir")
    args = parser.parse_args(argv)

    if args.command == "serve":
        import uvicorn

        from acm.app import create_app

        settings = Settings.from_env(host=args.host, port=args.port, data_dir=args.data_dir)
        uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
        return 0

    from acm.app import build_service
    from acm.mcp_server import build_mcp_server

    settings = Settings.from_env(data_dir=args.data_dir)
    service = build_service(settings)
    try:
        build_mcp_server(service, principal=lambda: settings.principal).run()  # transporte stdio
    finally:
        service.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
