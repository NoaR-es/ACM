"""ACM real por HTTP para los tests: uvicorn en un hilo, con acceso directo a los datos (fixture `acm`)."""

from __future__ import annotations

import threading
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
import pytest
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from acm.app import build_service, create_app
from acm.config import Settings
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from tests.fake_ollama import free_port

ADMIN = "local-admin"


@dataclass
class Acm:
    url: str
    data_dir: Path
    service: ProjectService  # acceso directo a los datos para preparar escenarios y comprobar efectos
    identity: IdentityService

    def token(self, principal: str, name: str = "t") -> str:
        return self.identity.create_token(ADMIN, principal, name)["token"]

    def audit(self, **where: str) -> list[dict]:
        clause = " AND ".join(f"{k} = ?" for k in where) or "1"
        with self.service.global_db.read() as conn:
            return [
                dict(r)
                for r in conn.execute(f"SELECT * FROM mcp_audit WHERE {clause} ORDER BY id", tuple(where.values()))
            ]


@pytest.fixture
def acm(tmp_path: Path) -> Iterator[Acm]:
    port = free_port()
    settings = Settings.from_env(data_dir=tmp_path / "data", port=port)
    service = build_service(settings)
    identity = IdentityService(service)
    server = uvicorn.Server(uvicorn.Config(create_app(settings), host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started:
        assert time.monotonic() < deadline, "ACM no arrancó"
        time.sleep(0.02)
    try:
        yield Acm(f"http://127.0.0.1:{port}", settings.data_dir, service, identity)
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        service.close()


@asynccontextmanager
async def mcp(acm: Acm, token: str | None) -> AsyncIterator[Client]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers) as http:
        async with Client(streamable_http_client(f"{acm.url}/mcp/", http_client=http)) as client:
            yield client
