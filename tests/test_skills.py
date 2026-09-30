"""US-15.01, US-15.04..US-15.10 — catálogo de skills y extensión MCP Skills (SEP-2640)."""

from __future__ import annotations

import hashlib
import re
import shutil
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Literal

import anyio
import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from mcp.shared.subscriptions import ResourcesListChanged
from mcp_types import Request
from pydantic import TypeAdapter

from acm.domain.projects import ProjectService
from acm.mcp_server import SKILLS_EXTENSION, SkillsGetParams, SkillsListParams, build_mcp_server
from acm.skills_catalog import DEFAULT_ROOT, SkillCatalog
from tests.conftest import ADMIN

pytestmark = pytest.mark.anyio
ANY = TypeAdapter(dict[str, Any])
OFFICIAL = {"acm-discovery", "acm-invest", "acm-schema"}


class SkillsListRequest(Request[SkillsListParams, Literal["skills/list"]]):
    method: Literal["skills/list"] = "skills/list"
    params: SkillsListParams = SkillsListParams()


class SkillsGetRequest(Request[SkillsGetParams, Literal["skills/get"]]):
    method: Literal["skills/get"] = "skills/get"
    params: SkillsGetParams


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    target = tmp_path / "skills"
    shutil.copytree(DEFAULT_ROOT, target)
    return target


@pytest.fixture
async def client(service: ProjectService, skills_dir: Path) -> AsyncIterator[Client]:
    async with Client(build_mcp_server(service, lambda: ADMIN, SkillCatalog(skills_dir))) as c:
        yield c


def _write_skill(root: Path, folder: str, body: str = "Contenido.\n", **fm: str) -> None:
    fields = {
        "name": folder,
        "description": "Skill de prueba",
        "version": "1.0.0",
        "capabilities": "[x]",
        "dependencies": "[]",
    } | fm
    (root / folder).mkdir(parents=True, exist_ok=True)
    head = "\n".join(f"{k}: {v}" for k, v in fields.items() if v is not None)
    (root / folder / "SKILL.md").write_text(f"---\n{head}\n---\n\n{body}", encoding="utf-8")


async def _tool_names(client: Client) -> set[str]:
    return {t.name for t in (await client.list_tools()).tools}


def _skill_text(name: str) -> str:
    return (DEFAULT_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- US-15.01
def test_us1501_ca01_id_y_version() -> None:
    catalog = SkillCatalog()
    for skill in catalog.skills.values():
        assert skill.frontmatter["name"] == skill.name
        assert re.match(r"^\d+\.\d+\.\d+$", skill.frontmatter["version"])


def test_us1501_ca02_ca03_capacidades_y_dependencias() -> None:
    catalog = SkillCatalog()
    for skill in catalog.skills.values():
        assert isinstance(skill.frontmatter["capabilities"], list) and skill.frontmatter["capabilities"]
        assert all(dep in catalog.skills for dep in skill.frontmatter["dependencies"])
    assert catalog.skills["acm-invest"].frontmatter["dependencies"] == ["acm-schema"]


@pytest.mark.parametrize(
    ("name", "fm", "reason"),
    [
        ("sin-version", {"version": None}, "version"),
        ("version-mala", {"version": "1.0"}, "version"),
        ("sin-capacidades", {"capabilities": "[]"}, "capabilities"),
        ("nombre-distinto", {"name": "otro"}, "name"),
        ("dep-rota", {"dependencies": "[no-existe]"}, "dependencias"),
    ],
)
def test_us1501_ca04_skill_invalida_no_se_activa(tmp_path: Path, name: str, fm: dict, reason: str) -> None:
    _write_skill(tmp_path, "valida")
    _write_skill(tmp_path, name, **fm)
    catalog = SkillCatalog(tmp_path)
    assert set(catalog.skills) == {"valida"}
    assert reason in catalog.rejected[name]


def test_us1501_ca04_rechazo_en_cascada(tmp_path: Path) -> None:
    _write_skill(tmp_path, "base", version="x")
    _write_skill(tmp_path, "hija", dependencies="[base]")
    catalog = SkillCatalog(tmp_path)
    assert catalog.skills == {} and set(catalog.rejected) == {"base", "hija"}


# ---------------------------------------------------------------- US-15.04
async def test_us1504_ca01_instructions_piden_cargar_skills(client: Client) -> None:
    text = client.instructions or ""
    assert "skills/list" in text and "acm_skills_list" in text and "acm-schema" in text


async def test_us1504_ca02_capacidades_declaradas(client: Client) -> None:
    caps = client.server_capabilities
    assert caps.resources is not None
    assert caps.extensions[SKILLS_EXTENSION] == {"directoryRead": False}


async def test_us1504_ca03_skills_list(client: Client) -> None:
    listed = await client.session.send_request(SkillsListRequest(), ANY)
    assert listed["resultType"] == "complete"
    assert {s["frontmatter"]["name"] for s in listed["skills"]} == OFFICIAL
    for s in listed["skills"]:
        assert s["uri"] == f"skill://acm/{s['frontmatter']['name']}/SKILL.md" and s["frontmatter"]["description"]
        assert all(r["digest"].startswith("sha256:") and r["size"] > 0 for r in s["resources"])


# ---------------------------------------------------------------- US-15.05
async def test_us1505_ca01_leer_cada_archivo_y_verificar_digest(client: Client) -> None:
    listed = await client.session.send_request(SkillsListRequest(), ANY)
    for s in listed["skills"]:
        for r in s["resources"]:
            text = (await client.read_resource(r["uri"])).contents[0].text
            assert "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest() == r["digest"], r["uri"]


async def test_us1505_ca02_skills_get_y_error(client: Client) -> None:
    got = await client.session.send_request(
        SkillsGetRequest(params=SkillsGetParams(uri="skill://acm/acm-invest/SKILL.md")), ANY
    )
    assert got["skill"]["frontmatter"]["name"] == "acm-invest"
    with pytest.raises(MCPError) as err:
        await client.session.send_request(SkillsGetRequest(params=SkillsGetParams(uri="skill://acm/x/SKILL.md")), ANY)
    assert err.value.code == -32602


async def test_us1505_ca03_herramientas_de_respaldo(client: Client) -> None:
    listed = await client.call_tool("acm_skills_list", {})
    assert {s["frontmatter"]["name"] for s in listed.structured_content["result"]} == OFFICIAL
    got = await client.call_tool("acm_skill_get", {"name": "acm-schema"})
    assert got.structured_content["files"]["skill://acm/acm-schema/SKILL.md"] == _skill_text("acm-schema")
    missing = await client.call_tool("acm_skill_get", {"name": "no-existe"})
    assert missing.is_error and "NOT_FOUND" in missing.content[0].text


# ---------------------------------------------------------------- US-15.06
def test_us1506_ca01_version_en_frontmatter() -> None:
    assert all(s.frontmatter.get("version") for s in SkillCatalog().skills.values())


def test_us1506_ca02_digest_cambia_solo_si_cambia_el_contenido(skills_dir: Path) -> None:
    catalog = SkillCatalog(skills_dir)
    before = catalog.skills["acm-invest"].files[0].digest
    assert catalog.reload() is False and catalog.skills["acm-invest"].files[0].digest == before
    path = skills_dir / "acm-invest" / "SKILL.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nNueva línea.\n", encoding="utf-8")
    assert catalog.reload() is True and catalog.skills["acm-invest"].files[0].digest != before
    assert (
        catalog.skills["acm-schema"].files[0].digest == SkillCatalog(DEFAULT_ROOT).skills["acm-schema"].files[0].digest
    )


async def test_us1506_ca03_notificacion_al_cambiar_catalogo(client: Client, skills_dir: Path) -> None:
    async with client.listen(resources_list_changed=True) as sub:
        _write_skill(skills_dir, "acm-nueva")
        result = await client.call_tool("acm_skills_reload", {})
        assert result.structured_content["changed"] is True
        with anyio.fail_after(5):
            event = await sub.__anext__()
        assert isinstance(event, ResourcesListChanged)
    unchanged = await client.call_tool("acm_skills_reload", {})
    assert unchanged.structured_content["changed"] is False


async def test_us1506_recargar_requiere_admin(service: ProjectService, skills_dir: Path) -> None:
    service.ensure_principal("bob", "user")
    async with Client(build_mcp_server(service, lambda: "bob", SkillCatalog(skills_dir))) as bob:
        result = await bob.call_tool("acm_skills_reload", {})
    assert result.is_error and "FORBIDDEN" in result.content[0].text


# ---------------------------------------------------------------- US-15.07
def test_us1507_ca01_skills_oficiales_versionadas_con_el_codigo() -> None:
    import acm

    assert DEFAULT_ROOT == Path(acm.__file__).parent / "skills"
    catalog = SkillCatalog()
    assert set(catalog.skills) == OFFICIAL and catalog.rejected == {}


async def test_us1507_ca02_skill_retirada_desaparece(client: Client, skills_dir: Path) -> None:
    uri = "skill://acm/acm-discovery/SKILL.md"
    assert (await client.read_resource(uri)).contents[0].text
    shutil.rmtree(skills_dir / "acm-discovery")
    await client.call_tool("acm_skills_reload", {})
    listed = await client.session.send_request(SkillsListRequest(), ANY)
    assert "acm-discovery" not in {s["frontmatter"]["name"] for s in listed["skills"]}
    with pytest.raises(MCPError):
        await client.read_resource(uri)


async def test_us1507_ca03_descargas_auditadas(client: Client) -> None:
    await client.session.send_request(SkillsListRequest(), ANY)
    await client.read_resource("skill://acm/acm-schema/SKILL.md")
    await client.session.send_request(
        SkillsGetRequest(params=SkillsGetParams(uri="skill://acm/acm-schema/SKILL.md")), ANY
    )
    await client.call_tool("acm_skill_get", {"name": "acm-schema"})
    entries = (await client.call_tool("acm_audit_list", {"limit": 20})).structured_content["entries"]
    ops = [e["operation"] for e in entries]
    assert {"skills/list", "resources/read", "skills/get", "acm_skill_get"} <= set(ops)
    read = next(e for e in entries if e["operation"] == "resources/read")
    assert read["arguments"] == {"uri": "skill://acm/acm-schema/SKILL.md"} and read["principal"] == ADMIN


# ---------------------------------------------------------------- US-15.08..10
TOOL_RE = re.compile(r"\bacm_[a-z_]+\b")


def test_us1508_ca01_acm_schema_valida() -> None:
    skill = SkillCatalog().skills["acm-schema"]
    assert skill.frontmatter["dependencies"] == []


async def test_us1508_ca02_ca03_documenta_exactamente_las_herramientas(client: Client) -> None:
    documented = set(TOOL_RE.findall(_skill_text("acm-schema")))
    assert documented == await _tool_names(client)


def test_us1508_ca04_modelo_y_flujo() -> None:
    text = _skill_text("acm-schema")
    for word in (
        "Requisito",
        "Épica",
        "Feature",
        "Historia",
        "Criterio de aceptación",
        "Flujo recomendado",
        "project_id",
    ):
        assert word in text, word


def test_us1509_ca01_acm_invest_valida() -> None:
    assert SkillCatalog().skills["acm-invest"].frontmatter["dependencies"] == ["acm-schema"]


def test_us1509_ca02_ca03_invest_y_criterios_binarios() -> None:
    text = _skill_text("acm-invest")
    for letter in (
        "I — Independiente",
        "N — Negociable",
        "V — Valiosa",
        "E — Estimable",
        "S — Pequeña",
        "T — Testeable",
    ):
        assert letter in text, letter
    assert "PASS/FAIL" in text and "binarios" in text


async def test_us1509_us1510_ca04_solo_herramientas_existentes(client: Client) -> None:
    tools = await _tool_names(client)
    for name in ("acm-invest", "acm-discovery"):
        mentioned = set(TOOL_RE.findall(_skill_text(name)))
        assert mentioned and mentioned <= tools, (name, mentioned - tools)


def test_us1510_ca01_acm_discovery_valida() -> None:
    assert SkillCatalog().skills["acm-discovery"].frontmatter["dependencies"] == ["acm-schema"]


def test_us1510_ca02_ca03_preguntas_y_registro() -> None:
    text = _skill_text("acm-discovery")
    for topic in (
        "Visión",
        "Actores",
        "Alcance",
        "Restricciones",
        "Dependencias ocultas",
        "Riesgos",
        "Conflictos",
        "acm_requirement_create",
        "acm_epic_create",
        "acm_requirement_trace",
        "No inventes",
    ):
        assert topic in text, topic
