"""Frontera MCP: US-01.01 (errores explícitos) y US-01.06 (project_id en cada herramienta)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from mcp import Client

from acm.domain.projects import ProjectService
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN

pytestmark = pytest.mark.anyio

PROJECT_TOOLS = {"acm_project_open", "acm_project_config_get", "acm_project_config_set"}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(service: ProjectService) -> AsyncIterator[Client]:
    async with Client(build_mcp_server(service, principal=lambda: ADMIN)) as c:
        yield c


def _text(result) -> str:
    return result.content[0].text if result.content else ""


async def test_us0101_mcp_create_y_errores_explicitos(client: Client, data_dir: Path) -> None:
    ok = await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    assert not ok.is_error and ok.structured_content["project_id"] == "alpha"
    dup = await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    assert dup.is_error and "ALREADY_EXISTS" in _text(dup) and "alpha" in _text(dup)
    empty = await client.call_tool("acm_project_create", {"key": "beta", "name": "  "})
    assert empty.is_error and "INVALID_ARGUMENT: name" in _text(empty)
    assert not (data_dir / "projects" / "beta").exists()


async def test_us0106_ca01_herramientas_de_proyecto_exigen_project_id(client: Client) -> None:
    tools = {t.name: t for t in (await client.list_tools()).tools}
    assert PROJECT_TOOLS <= set(tools)
    for name in PROJECT_TOOLS:
        assert "project_id" in tools[name].input_schema.get("required", []), name
    missing = await client.call_tool("acm_project_open", {})
    assert missing.is_error and "project_id" in _text(missing)


async def test_us0106_ca02_respuestas_incluyen_project_id(client: Client) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    for name, args in [
        ("acm_project_open", {"project_id": "alpha"}),
        ("acm_project_config_get", {"project_id": "alpha"}),
        ("acm_project_config_set", {"project_id": "alpha", "changes": {"context.max_tokens": 1000}}),
    ]:
        result = await client.call_tool(name, args)
        assert not result.is_error, _text(result)
        assert result.structured_content["project_id"] == "alpha", name
    listed = await client.call_tool("acm_project_list", {})
    assert [p["project_id"] for p in listed.structured_content["result"]] == ["alpha"]


async def test_us0106_ca03_project_id_desconocido_error_explicito(client: Client, service: ProjectService) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    for name, args in [
        ("acm_project_open", {"project_id": "nope"}),
        ("acm_project_config_set", {"project_id": "nope", "changes": {"context.max_tokens": 1000}}),
    ]:
        result = await client.call_tool(name, args)
        assert result.is_error
        assert "NOT_FOUND" in _text(result) and "'nope'" in _text(result)
    bad = await client.call_tool("acm_project_open", {"project_id": "Con Mayúsculas"})
    assert bad.is_error and "INVALID_ARGUMENT: project_id" in _text(bad)
    assert [p["project_id"] for p in service.list_for(ADMIN)] == ["alpha"]
    cfg = {p["key"]: p["value"] for p in service.get_config(ADMIN, "alpha")["parameters"]}
    assert cfg["context.max_tokens"] == 8000  # ningún proyecto se modificó


async def test_us0106_ca04_instructions_explican_project_id(client: Client) -> None:
    text = client.instructions or ""
    assert "project_id" in text and "acm_project_list" in text
