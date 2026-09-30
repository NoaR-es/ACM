"""US-14.10 y US-14.11 — auditoría de invocaciones MCP."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from mcp import Client

from acm.domain.audit import RESULT_MAX_CHARS
from acm.domain.projects import ProjectService
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def admin(service: ProjectService) -> AsyncIterator[Client]:
    async with Client(build_mcp_server(service, principal=lambda: ADMIN)) as c:
        yield c


async def _entries(client: Client, **filters) -> list[dict]:
    result = await client.call_tool("acm_audit_list", filters)
    assert not result.is_error, result.content
    return result.structured_content["entries"]


async def test_us1410_ca01_admin_lista_invocaciones(admin: Client) -> None:
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    await admin.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "R"})
    entries = await _entries(admin, limit=10)
    assert [e["operation"] for e in entries[:2]] == ["acm_requirement_create", "acm_project_create"]
    assert entries[0]["principal"] == ADMIN and entries[0]["project_id"] == "alpha" and entries[0]["ts"]


async def test_us1410_ca02_filtros(admin: Client, service: ProjectService) -> None:
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    await admin.call_tool("acm_project_create", {"key": "beta", "name": "Beta"})
    await admin.call_tool("acm_requirement_create", {"project_id": "beta", "title": "R"})
    service.ensure_principal("bob", "user")
    async with Client(build_mcp_server(service, principal=lambda: "bob")) as bob:
        await bob.call_tool("acm_project_list", {})
    assert {e["operation"] for e in await _entries(admin, operation="acm_project_create")} == {"acm_project_create"}
    assert [e["principal"] for e in await _entries(admin, principal_id="bob")] == ["bob"]
    by_project = await _entries(admin, project_id="beta")
    assert [e["operation"] for e in by_project] == ["acm_requirement_create"]
    assert await _entries(admin, operation="no-existe") == []


async def test_us1410_ca03_no_admin_rechazado(service: ProjectService) -> None:
    service.ensure_principal("bob", "user")
    async with Client(build_mcp_server(service, principal=lambda: "bob")) as bob:
        result = await bob.call_tool("acm_audit_list", {})
    assert result.is_error and "FORBIDDEN" in result.content[0].text


async def test_us1411_ca01_ca03_argumentos_y_duracion(admin: Client) -> None:
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha", "description": "d"})
    entry = (await _entries(admin, operation="acm_project_create"))[0]
    assert entry["arguments"] == {"key": "alpha", "name": "Alpha", "description": "d"}
    assert isinstance(entry["duration_ms"], float) and entry["duration_ms"] >= 0
    assert '"project_id": "alpha"' in entry["result_json"] and entry["status"] == "ok"


async def test_us1411_ca02_resultado_truncado(admin: Client) -> None:
    for i in range(40):
        await admin.call_tool("acm_project_create", {"key": f"proyecto-{i:02d}", "name": "N" * 100})
    await admin.call_tool("acm_project_list", {})
    entry = (await _entries(admin, operation="acm_project_list"))[0]
    assert entry["result_truncated"] is True and len(entry["result_json"]) == RESULT_MAX_CHARS
    small = (await _entries(admin, operation="acm_project_create"))[0]
    assert small["result_truncated"] is False


async def test_us1411_ca04_estado_y_error(admin: Client) -> None:
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    ok, err = sorted(await _entries(admin, operation="acm_project_create"), key=lambda e: e["id"])
    assert ok["status"] == "ok" and ok["error"] == ""
    assert err["status"] == "error" and err["error"].startswith("ALREADY_EXISTS") and err["result_json"] == ""


async def test_us1411_ca05_intentos_no_autorizados(admin: Client, service: ProjectService) -> None:
    await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    async with Client(build_mcp_server(service, principal=lambda: "fantasma")) as ghost:
        await ghost.call_tool("acm_project_list", {})
        await ghost.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "intrusión"})
    entries = await _entries(admin, principal_id="fantasma")
    assert {e["operation"] for e in entries} == {"acm_project_list", "acm_requirement_create"}
    assert all(e["status"] == "error" and e["error"].startswith("FORBIDDEN") for e in entries)
