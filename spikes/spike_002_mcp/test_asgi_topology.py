"""SPIKE-002 — Topología: un único proceso ASGI (uvicorn + Starlette) que sirve a la vez
  - el servidor MCP propio por Streamable HTTP en /mcp,
  - una API HTTP en /api/health,
  - un WebSocket en /ws que difunde eventos de dominio a los clientes conectados,
y comprueba que una operación hecha por un agente vía MCP llega como evento al WebSocket.

Ejecutar:  spikes/.venv/bin/python spikes/spike_002_mcp/test_asgi_topology.py
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import socket
import sys
from pathlib import Path
from typing import Any

import httpx
import uvicorn
import websockets
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from acm_mcp_proto import build_server  # noqa: E402

from mcp import Client  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: Any = "") -> None:
    RESULTS.append((name, bool(cond), str(detail)[:200]))


class EventBus:
    """Bus en memoria: difunde eventos a los WebSockets suscritos (sustituto mínimo de TECH-001/002)."""

    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()

    async def publish(self, event: dict[str, Any]) -> None:
        for ws in list(self.clients):
            with contextlib.suppress(Exception):
                await ws.send_json(event)


def build_app() -> tuple[Starlette, EventBus]:
    bus = EventBus()
    mcp_server = build_server()

    @mcp_server.tool()
    async def acm_move_story(story_id: str, to_status: str) -> dict[str, str]:
        """Mueve una historia de estado (demo del spike) y publica el evento de dominio."""
        event = {"type": "story.moved", "story_id": story_id, "to": to_status}
        await bus.publish(event)
        return event

    mcp_app = mcp_server.streamable_http_app(streamable_http_path="/")

    async def health(_request):
        return JSONResponse({"status": "ok"})

    async def ws_endpoint(ws: WebSocket):
        await ws.accept()
        bus.clients.add(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            bus.clients.discard(ws)

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        # El sub-app MCP montado no ejecuta su propio lifespan: el gestor de sesiones se arranca aquí.
        async with mcp_server.session_manager.run():
            yield

    app = Starlette(routes=[Route("/api/health", health), WebSocketRoute("/ws", ws_endpoint),
                            Mount("/mcp", app=mcp_app)], lifespan=lifespan)
    return app, bus


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def main() -> None:
    app, _bus = build_app()
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    task = asyncio.create_task(server.serve())
    for _ in range(100):
        if server.started:
            break
        await asyncio.sleep(0.05)
    base = f"http://127.0.0.1:{port}"
    try:
        async with httpx.AsyncClient() as http:
            r = await http.get(f"{base}/api/health")
            check("API HTTP /api/health responde en el mismo proceso", r.status_code == 200, r.text)
        async with websockets.connect(f"ws://127.0.0.1:{port}/ws") as ws:
            await asyncio.sleep(0.1)
            async with Client(f"{base}/mcp/") as client:
                check("cliente MCP por Streamable HTTP conecta y recibe instructions",
                      bool(client.instructions), (client.instructions or "")[:60])
                tools = sorted(t.name for t in (await client.list_tools()).tools)
                check("herramientas visibles por HTTP", "acm_move_story" in tools, tools)
                await client.call_tool("acm_move_story", {"story_id": "US-01.01", "to_status": "IN_PROGRESS"})
            msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            check("operación vía MCP llega como evento al WebSocket", msg.get("story_id") == "US-01.01"
                  and msg.get("to") == "IN_PROGRESS", msg)
    finally:
        server.should_exit = True
        await task


if __name__ == "__main__":
    asyncio.run(main())
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {('— ' + detail) if detail else ''}")
    failed = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} PASS")
    sys.exit(1 if failed or len(RESULTS) < 4 else 0)
