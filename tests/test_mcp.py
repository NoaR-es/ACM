"""Frontera MCP: US-01.01 (errores explícitos) y US-01.06 (project_id en cada herramienta)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from mcp import Client

from acm.domain.projects import ProjectService
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN, add_member

pytestmark = pytest.mark.anyio

PROJECT_TOOLS = {"acm_project_open", "acm_project_config_get", "acm_project_config_set"}
BACKLOG_TOOLS = {
    "acm_requirement_create",
    "acm_requirement_list",
    "acm_requirement_trace",
    "acm_epic_create",
    "acm_epic_link_requirements",
    "acm_epic_get",
    "acm_epic_list",
    "acm_epic_confirm_coverage",
    "acm_feature_create",
    "acm_feature_split",
    "acm_story_create",
    "acm_story_add_criteria",
    "acm_story_get",
    "acm_story_mark_ready",
    "acm_backlog_audit",
    "acm_decide",
    "acm_context_compact",
    "acm_member_set",
    "acm_member_remove",
    "acm_member_list",
    "acm_watchdog_run",
    "acm_watchdog_history",
    "acm_governance_status",
}
GLOBAL_TOOLS = {
    "acm_project_create",
    "acm_project_list",
    "acm_system_info",
    "acm_audit_list",
    "acm_skills_list",
    "acm_skill_get",
    "acm_skills_reload",
    "acm_engines_list",
    "acm_engines_refresh",
    "acm_savings_report",
    "acm_whoami",
    "acm_principal_create",
    "acm_principal_list",
    "acm_principal_set_role",
    "acm_token_create",
    "acm_token_list",
    "acm_token_revoke",
    "acm_health",
}


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


# ---------------------------------------------------------------- US-14.05..US-14.09
async def test_us1405_ca01_ca02_descubrir_herramientas(client: Client) -> None:
    tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == PROJECT_TOOLS | BACKLOG_TOOLS | GLOBAL_TOOLS
    for tool in tools.values():
        assert tool.description and tool.input_schema.get("type") == "object", tool.name


async def test_us1405_ca03_herramientas_de_proyecto_declaran_project_id(client: Client) -> None:
    tools = {t.name: t for t in (await client.list_tools()).tools}
    for name in PROJECT_TOOLS | BACKLOG_TOOLS:
        assert "project_id" in tools[name].input_schema.get("required", []), name


async def test_us1406_ca01_operacion_persiste(client: Client, service: ProjectService, data_dir: Path) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    req = await client.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "Persistir"})
    assert not req.is_error and req.structured_content["id"] == "REQ-001"
    # otra instancia del servidor sobre los mismos datos ve el cambio
    fresh = ProjectService(data_dir)
    try:
        async with Client(build_mcp_server(fresh, principal=lambda: ADMIN)) as other:
            listed = await other.call_tool("acm_requirement_list", {"project_id": "alpha"})
    finally:
        fresh.close()
    assert [r["title"] for r in listed.structured_content["requirements"]] == ["Persistir"]


async def test_us1406_ca02_operacion_rechazada_sin_efectos(client: Client) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    bad = await client.call_tool(
        "acm_epic_create",
        {"project_id": "alpha", "title": "E", "objective": "o", "scope": "s", "requirement_ids": ["REQ-999"]},
    )
    assert bad.is_error and "NOT_FOUND" in _text(bad) and "REQ-999" in _text(bad)
    epics = await client.call_tool("acm_epic_list", {"project_id": "alpha"})
    assert epics.structured_content["epics"] == []


async def test_us1407_varios_proyectos_misma_instancia(client: Client) -> None:
    for key in ("alpha", "beta"):
        await client.call_tool("acm_project_create", {"key": key, "name": key})
        await client.call_tool("acm_requirement_create", {"project_id": key, "title": f"R-{key}"})
    for key in ("alpha", "beta"):
        listed = await client.call_tool("acm_requirement_list", {"project_id": key})
        assert listed.structured_content["project_id"] == key
        assert [r["title"] for r in listed.structured_content["requirements"]] == [f"R-{key}"]


async def test_us1409_ca01_sin_project_id_no_reutiliza_el_anterior(client: Client) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    await client.call_tool("acm_project_open", {"project_id": "alpha"})
    missing = await client.call_tool("acm_requirement_create", {"title": "¿a qué proyecto?"})
    assert missing.is_error and "project_id" in _text(missing)
    listed = await client.call_tool("acm_requirement_list", {"project_id": "alpha"})
    assert listed.structured_content["requirements"] == []


async def test_us1409_ca02_proyecto_ajeno_rechazado_sin_efectos(
    client: Client, service: ProjectService, data_dir: Path
) -> None:
    await client.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
    await client.call_tool("acm_project_create", {"key": "beta", "name": "Beta"})
    add_member(data_dir, "alpha", "agente-a")
    async with Client(build_mcp_server(service, principal=lambda: "agente-a")) as agent:
        own = await agent.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "propio"})
        assert not own.is_error
        foreign = await agent.call_tool("acm_requirement_create", {"project_id": "beta", "title": "intrusión"})
        assert foreign.is_error and "NOT_FOUND" in _text(foreign) and "'beta'" in _text(foreign)
    listed = await client.call_tool("acm_requirement_list", {"project_id": "beta"})
    assert listed.structured_content["requirements"] == []
