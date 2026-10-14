"""CLI de ACM.

acm serve [--host H] [--port P] [--data-dir D] [--local]  # proceso ASGI: /api y /mcp (Streamable HTTP)
acm mcp-stdio [--data-dir D]                     # servidor MCP por stdio para agentes locales (ADR-023)
acm stop [--data-dir D]                          # para la interfaz local que arrancó un agente
acm principal create ID --kind user|agent [--role admin|user] [--data-dir D]
acm token create PRINCIPAL --name N [--data-dir D]  # imprime el token UNA vez (ADR-017)

Los comandos `principal` y `token` actúan como ACM_PRINCIPAL (admin local): quien accede a los datos del servidor
ya los controla. Quedan auditados como `cli:*`.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace

from acm.config import Settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acm", description="Agile Context Manager")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="sirve la interfaz web, /api y /mcp por HTTP")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    serve.add_argument("--data-dir")
    serve.add_argument("--local", action="store_true", help="modo local: la interfaz de este equipo entra sin token")
    sub.add_parser("stop", help="para la interfaz local que arrancó un agente").add_argument("--data-dir")
    stdio = sub.add_parser("mcp-stdio", help="servidor MCP por stdio")
    stdio.add_argument("--data-dir")
    principal = sub.add_parser("principal", help="gestiona principales (admin local)")
    principal_sub = principal.add_subparsers(dest="action", required=True)
    p_create = principal_sub.add_parser("create", help="da de alta un usuario o agente")
    p_create.add_argument("principal_id")
    p_create.add_argument("--kind", required=True, choices=["user", "agent"])
    p_create.add_argument("--role", default="user", choices=["admin", "user"])
    p_create.add_argument("--data-dir")
    token = sub.add_parser("token", help="gestiona tokens de acceso (admin local)")
    token_sub = token.add_subparsers(dest="action", required=True)
    t_create = token_sub.add_parser("create", help="crea un token y lo imprime una sola vez")
    t_create.add_argument("principal_id")
    t_create.add_argument("--name", required=True)
    t_create.add_argument("--data-dir")
    args = parser.parse_args(argv)

    if args.command in ("principal", "token"):
        return _admin_command(args)

    if args.command == "stop":
        from acm.local import stop_local_ui

        print(stop_local_ui(Settings.from_env(data_dir=args.data_dir)))
        return 0

    if args.command == "serve":
        import uvicorn

        from acm.app import create_app

        settings = Settings.from_env(host=args.host, port=args.port, data_dir=args.data_dir)
        if args.local:
            settings = replace(settings, local_mode=True)
        uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
        return 0

    return _run_stdio(Settings.from_env(data_dir=args.data_dir))


def _run_stdio(settings: Settings) -> int:
    """Servidor MCP por stdio. Con `ACM_PRINCIPAL` explícito, una única identidad admin (comportamiento anterior).
    Sin él, modo local (ADR-023): cada agente es un principal propio, no admin, que se deduce de su cliente y de este
    equipo (o de `ACM_AGENT`), y la interfaz y el supervisor corren en un proceso aparte que sobrevive a los agentes."""
    from acm.app import build_engines, build_service
    from acm.local import local_principal, start_local_ui
    from acm.mcp_server import build_mcp_server

    legacy = "ACM_PRINCIPAL" in os.environ
    if not legacy:
        settings = replace(settings, local_mode=True)
    service = build_service(settings)
    engines = build_engines(service, settings)
    who = (lambda: settings.principal) if legacy else local_principal(service, settings)
    if not legacy and settings.ui:
        start_local_ui(settings)
    try:
        build_mcp_server(service, principal=who, engines=engines, stdio=True).run()  # stdio
    finally:
        engines.registry.close()
        service.close()
    return 0


def _admin_command(args: argparse.Namespace) -> int:
    import json
    import time

    from acm.app import build_service
    from acm.domain.audit import AuditService
    from acm.domain.errors import AcmError
    from acm.domain.identity import IdentityService

    settings = Settings.from_env(data_dir=args.data_dir)
    service = build_service(settings)
    identity, audit = IdentityService(service), AuditService(service)
    if args.command == "principal":
        operation, arguments = (
            "cli:principal_create",
            {"principal_id": args.principal_id, "kind": args.kind, "role": args.role},
        )
        run = lambda: identity.create_principal(settings.principal, args.principal_id, args.kind, args.role)  # noqa: E731
    else:
        operation, arguments = "cli:token_create", {"principal_id": args.principal_id, "name": args.name}
        run = lambda: identity.create_token(settings.principal, args.principal_id, args.name)  # noqa: E731
    start = time.perf_counter()
    try:
        try:
            result = run()
        except AcmError as exc:
            audit.record(
                principal=settings.principal,
                operation=operation,
                arguments=arguments,
                status="error",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(exc),
            )
            print(str(exc), file=sys.stderr)
            return 2
        audit.record(
            principal=settings.principal,
            operation=operation,
            arguments=arguments,
            status="ok",
            duration_ms=(time.perf_counter() - start) * 1000,
            result=result,
        )  # el secreto se redacta
    finally:
        service.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
