"""SPIKE-002 — Aislamiento multi-proyecto: ¿puede el servidor recordar el "proyecto seleccionado" por sesión?

Compara dos diseños sobre Streamable HTTP con la versión de protocolo que negocia el SDK:
  D1 "selección con estado": acm_select_project guarda el proyecto asociado a la sesión (ctx.session)
     y acm_whoami lo lee en una llamada posterior.
  D2 "proyecto explícito": cada herramienta recibe project_id y el servidor lo valida contra una lista
     de proyectos permitidos (en producto: token con alcance por proyecto, EPIC-20).

Ejecutar:  spikes/.venv/bin/python spikes/spike_002_mcp/test_session_isolation.py
"""
from __future__ import annotations

import asyncio
import socket
import sys
import weakref
from pathlib import Path
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount

from mcp import Client
from mcp.server.mcpserver import Context, MCPServer

RESULTS: list[tuple[str, bool, str]] = []
INFO: list[str] = []


def check(name: str, cond: bool, detail: Any = "") -> None:
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def build() -> MCPServer:
    server = MCPServer(name="acm-isolation-spike")
    selected: "weakref.WeakKeyDictionary[Any, str]" = weakref.WeakKeyDictionary()
    session_ids: list[int] = []
    allowed = {"alice": {"P-A"}, "bob": {"P-B"}}  # sustituto del alcance de token (EPIC-20)
    backlog = {"P-A": ["US-A1", "US-A2"], "P-B": ["US-B1"]}

    @server.tool()
    def acm_select_project(project_id: str, ctx: Context) -> str:
        """D1: guarda el proyecto en el estado de la sesión."""
        session_ids.append(id(ctx.session))
        try:
            selected[ctx.session] = project_id
        except TypeError:
            return "session-not-weakrefable"
        return "ok"

    @server.tool()
    def acm_whoami(ctx: Context) -> str:
        """D1: lee el proyecto seleccionado en una llamada anterior."""
        session_ids.append(id(ctx.session))
        return selected.get(ctx.session, "NONE")

    @server.tool()
    def acm_backlog(principal: str, project_id: str) -> list[str]:
        """D2: proyecto explícito en cada llamada, validado contra el alcance del principal."""
        if project_id not in allowed.get(principal, set()):
            raise PermissionError(f"{principal} no tiene acceso a {project_id}")
        return backlog[project_id]

    server._spike_session_ids = session_ids  # type: ignore[attr-defined]
    return server


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def text_of(res: Any) -> str:
    return res.content[0].text if res.content else ""


async def main() -> None:
    server = build()
    app = Starlette(routes=[Mount("/mcp", app=server.streamable_http_app(streamable_http_path="/"))],
                    lifespan=lambda _a: server.session_manager.run())
    port = free_port()
    uv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    task = asyncio.create_task(uv.serve())
    while not uv.started:
        await asyncio.sleep(0.05)
    url = f"http://127.0.0.1:{port}/mcp/"
    try:
        async with Client(url) as c1:
            INFO.append(f"versión negociada por HTTP: {getattr(c1.session, 'protocol_version', '?')}")
            r = await c1.call_tool("acm_select_project", {"project_id": "P-A"})
            w = await c1.call_tool("acm_whoami", {})
            INFO.append(f"D1 select → {text_of(r)!r}; whoami en la llamada siguiente → {text_of(w)!r}")
            ids = server._spike_session_ids  # type: ignore[attr-defined]
            INFO.append(f"D1 ids de ctx.session en 2 llamadas consecutivas del mismo cliente: distintos={len(set(ids)) > 1}")
            d1_retains = text_of(w) == "P-A"
            check("D1 (selección con estado) NO es fiable sobre HTTP con este protocolo "
                  "(el servidor no conserva la selección entre llamadas)", not d1_retains, text_of(w))
        async with Client(url) as a, Client(url) as b:
            ra = await a.call_tool("acm_backlog", {"principal": "alice", "project_id": "P-A"})
            rb = await b.call_tool("acm_backlog", {"principal": "bob", "project_id": "P-B"})
            check("D2: cada cliente obtiene solo el backlog de su proyecto",
                  "US-A1" in text_of(ra) and "US-B1" in text_of(rb) and "US-B1" not in text_of(ra), (text_of(ra), text_of(rb)))
            cross = await a.call_tool("acm_backlog", {"principal": "alice", "project_id": "P-B"})
            check("D2: acceso cruzado a otro proyecto rechazado con error", cross.is_error, text_of(cross))
    finally:
        uv.should_exit = True
        await task


if __name__ == "__main__":
    asyncio.run(main())
    for line in INFO:
        print(f"INFO  {line}")
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {('— ' + detail) if detail else ''}")
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} PASS")
    sys.exit(1 if failed or len(RESULTS) < 3 else 0)
