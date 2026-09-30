"""ADR-014 con FastAPI: un proceso ASGI real (uvicorn) sirve /api y /mcp; y el modo stdio del CLI."""

from __future__ import annotations

import asyncio
import socket
import sys
from pathlib import Path

import httpx
import pytest
import uvicorn
from mcp import Client, StdioServerParameters

from acm.app import create_app
from acm.config import Settings

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def test_fastapi_sirve_api_y_mcp_en_un_proceso(tmp_path: Path) -> None:
    port = _free_port()
    settings = Settings.from_env(data_dir=tmp_path / "data", port=port)
    server = uvicorn.Server(uvicorn.Config(create_app(settings), host="127.0.0.1", port=port, log_level="warning"))
    task = asyncio.create_task(server.serve())
    try:
        for _ in range(200):
            if server.started:
                break
            await asyncio.sleep(0.05)
        async with httpx.AsyncClient() as http:
            health = (await http.get(f"http://127.0.0.1:{port}/api/health")).json()
        assert health["status"] == "ok" and health["sqlite"]["foreign_keys"] is True
        async with Client(f"http://127.0.0.1:{port}/mcp/") as client:
            assert "project_id" in (client.instructions or "")
            created = await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
            assert not created.is_error, created.content
            opened = await client.call_tool("acm_project_open", {"project_id": "alpha"})
            assert opened.structured_content["project_id"] == "alpha"
    finally:
        server.should_exit = True
        await task


async def test_modo_stdio_del_cli(tmp_path: Path) -> None:
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "acm", "mcp-stdio", "--data-dir", str(tmp_path / "data")]
    )
    async with Client(params) as client:
        created = await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
        assert not created.is_error, created.content
        listed = await client.call_tool("acm_project_list", {})
        assert [p["project_id"] for p in listed.structured_content["result"]] == ["alpha"]
