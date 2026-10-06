"""Sprints (EPIC-05): US-05.02..05.09 contra el dominio real y el servidor MCP (SQLite en un directorio temporal)."""

from __future__ import annotations

import sqlite3

import pytest
from mcp import Client

from acm.domain.backlog import BacklogService
from acm.domain.errors import FailedPrecondition, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN

P = "alpha"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def backlog(service: ProjectService) -> BacklogService:
    service.create(ADMIN, P, "Alpha")
    b = BacklogService(service)
    b.create_requirement(ADMIN, P, "Gestionar proyectos")
    b.create_epic(ADMIN, P, "Proyectos", "Gestionar", "Crear y abrir", ["REQ-001"])
    b.create_feature(ADMIN, P, "EPIC-01", "Creación")
    for i in range(1, 5):
        b.create_story(ADMIN, P, "FEAT-01.01", "operador", f"hacer {i}", "avanzar", ["REQ-001"], [f"CA {i}"])
    for sid in ("US-01.01", "US-01.02", "US-01.03"):
        b.mark_ready(ADMIN, P, sid)
    return b


@pytest.fixture
def sprints(backlog: BacklogService) -> SprintService:
    return SprintService(backlog)


def _new(sprints: SprintService, capacity: int | None = 3, name: str = "Sprint 1") -> dict:
    return sprints.create(ADMIN, P, name, "Entregar la creación de proyectos", "2026-10-01", "2026-10-14", capacity)


def _done(backlog: BacklogService, sid: str) -> None:
    for to in ("IN_PROGRESS", "IMPLEMENTED", "TESTING", "VERIFIED", "DONE"):
        backlog.set_status(ADMIN, P, sid, to)


# ---------------------------------------------------------------- US-05.02 crear un sprint
def test_us0502_ca01_identificador_y_objetivo(sprints: SprintService) -> None:
    s1, s2 = _new(sprints), _new(sprints, name="Sprint 2")
    assert (s1["id"], s2["id"]) == ("SPRINT-01", "SPRINT-02")
    assert s1["goal"] == "Entregar la creación de proyectos" and s1["status"] == "PLANNED"
    with pytest.raises(InvalidArgument) as err:
        sprints.create(ADMIN, P, "Sin objetivo", "  ", "2026-10-01", "2026-10-02")
    assert err.value.field == "goal"


def test_us0502_ca02_historias_vinculadas(sprints: SprintService, backlog: BacklogService) -> None:
    _new(sprints)
    sprint = sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01", "US-01.02"])
    assert sprint["story_ids"] == ["US-01.01", "US-01.02"] and sprint["warnings"] == []
    assert backlog.get_story(ADMIN, P, "US-01.01")["sprint_id"] == "SPRINT-01"
    assert backlog.get_story(ADMIN, P, "US-01.03")["sprint_id"] is None


def test_us0502_ca04_estados_definidos(sprints: SprintService) -> None:
    _new(sprints)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    assert sprints.start(ADMIN, P, "SPRINT-01")["status"] == "ACTIVE"
    with pytest.raises(FailedPrecondition, match="solo un sprint PLANNED"):
        sprints.start(ADMIN, P, "SPRINT-01")
    assert sprints.close(ADMIN, P, "SPRINT-01")["status"] == "CLOSED"
    _new(sprints, name="Sprint 2")
    assert sprints.cancel(ADMIN, P, "SPRINT-02")["status"] == "CANCELLED"
    with pytest.raises(FailedPrecondition, match="ya está CANCELLED"):
        sprints.cancel(ADMIN, P, "SPRINT-02")
    with pytest.raises(FailedPrecondition, match="solo un sprint ACTIVE"):
        sprints.close(ADMIN, P, "SPRINT-02")


def test_us0502_un_solo_sprint_activo(sprints: SprintService) -> None:
    for name, story in (("A", "US-01.01"), ("B", "US-01.02")):
        s = _new(sprints, name=name)
        sprints.add_stories(ADMIN, P, s["id"], [story])
    sprints.start(ADMIN, P, "SPRINT-01")
    with pytest.raises(FailedPrecondition, match="ya hay un sprint activo \\(SPRINT-01\\)"):
        sprints.start(ADMIN, P, "SPRINT-02")


# ---------------------------------------------------------------- US-05.03 cerrar un sprint
def _closing(sprints: SprintService, backlog: BacklogService) -> None:
    _new(sprints)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01", "US-01.02", "US-01.03"])
    sprints.start(ADMIN, P, "SPRINT-01")
    _done(backlog, "US-01.01")
    backlog.set_status(ADMIN, P, "US-01.02", "IN_PROGRESS")


def test_us0503_ca01_terminadas_y_no_terminadas(sprints: SprintService, backlog: BacklogService) -> None:
    _closing(sprints, backlog)
    summary = sprints.close(ADMIN, P, "SPRINT-01")["summary"]
    assert summary["done"] == ["US-01.01"] and summary["not_done"] == ["US-01.02", "US-01.03"]


def test_us0503_ca02_trasladar_no_terminadas(sprints: SprintService, backlog: BacklogService) -> None:
    _closing(sprints, backlog)
    _new(sprints, name="Sprint 2")
    closed = sprints.close(ADMIN, P, "SPRINT-01", carry_over_to="SPRINT-02")
    assert closed["summary"]["carried_over_to"] == "SPRINT-02"
    assert sprints.get(ADMIN, P, "SPRINT-02")["story_ids"] == ["US-01.02", "US-01.03"]
    assert backlog.get_story(ADMIN, P, "US-01.02")["sprint_id"] == "SPRINT-02"
    assert backlog.get_story(ADMIN, P, "US-01.01")["sprint_id"] is None  # la terminada no se traslada


def test_us0503_ca02_sin_destino_vuelven_al_backlog(sprints: SprintService, backlog: BacklogService) -> None:
    _closing(sprints, backlog)
    sprints.close(ADMIN, P, "SPRINT-01")
    assert all(backlog.get_story(ADMIN, P, s)["sprint_id"] is None for s in ("US-01.02", "US-01.03"))
    _new(sprints, name="Sprint 2")
    sprints.add_stories(ADMIN, P, "SPRINT-02", ["US-01.02"])
    sprints.start(ADMIN, P, "SPRINT-02")
    with pytest.raises(FailedPrecondition, match="solo se traslada a un PLANNED"):
        sprints.close(ADMIN, P, "SPRINT-02", carry_over_to="SPRINT-01")  # SPRINT-01 ya está cerrado


def test_us0503_ca03_resumen_del_sprint(sprints: SprintService, backlog: BacklogService) -> None:
    _closing(sprints, backlog)
    summary = sprints.close(ADMIN, P, "SPRINT-01")["summary"]
    assert summary["completion_pct"] == 33 and summary["stories"] == 3
    assert summary["text"].startswith("SPRINT-01 «Sprint 1»: 1 de 3 historias terminadas (33 %)")
    assert "vuelven al backlog" in summary["text"]


def test_us0503_ca04_historial_conservado(sprints: SprintService, backlog: BacklogService) -> None:
    _closing(sprints, backlog)
    closed = sprints.close(ADMIN, P, "SPRINT-01")
    assert closed["story_ids"] == []
    assert {h["story_id"]: h["outcome"] for h in closed["history"]} == {
        "US-01.01": "done",
        "US-01.02": "returned",
        "US-01.03": "returned",
    }
    with pytest.raises(FailedPrecondition, match="su historial no se modifica"):
        sprints.remove_story(ADMIN, P, "SPRINT-01", "US-01.01")


# ---------------------------------------------------------------- US-05.04 objetivo, fechas y capacidad
def test_us0504_ca01_objetivo_fechas_y_capacidad(sprints: SprintService) -> None:
    s = _new(sprints, capacity=5)
    assert (s["start_date"], s["end_date"], s["capacity"]) == ("2026-10-01", "2026-10-14", 5)
    assert _new(sprints, capacity=None, name="Sin capacidad")["capacity"] is None


@pytest.mark.parametrize(
    ("start", "end", "field"),
    [
        ("2026-13-01", "2026-12-01", "start_date"),
        ("2026-10-02", "ayer", "end_date"),
        ("2026-10-02", "2026-10-01", "end_date"),
    ],
)
def test_us0504_ca02_fechas_invalidas(sprints: SprintService, start: str, end: str, field: str) -> None:
    with pytest.raises(InvalidArgument) as err:
        sprints.create(ADMIN, P, "S", "Objetivo", start, end)
    assert err.value.field == field


@pytest.mark.parametrize("capacity", [0, -1, 1001, "3", True])
def test_us0504_ca03_capacidad_fuera_de_rango(sprints: SprintService, capacity: object) -> None:
    with pytest.raises(InvalidArgument) as err:
        sprints.create(ADMIN, P, "S", "Objetivo", "2026-10-01", "2026-10-02", capacity)
    assert err.value.field == "capacity"


# ---------------------------------------------------------------- US-05.05 asignar historias
def test_us0505_ca01_ca05_asignar_y_retirar(sprints: SprintService) -> None:
    _new(sprints)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01", "US-01.02"])
    after = sprints.remove_story(ADMIN, P, "SPRINT-01", "US-01.02")
    assert after["story_ids"] == ["US-01.01"] and after["history"][0]["outcome"] == "removed"
    assert sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.02"])["story_ids"] == ["US-01.01", "US-01.02"]
    with pytest.raises(NotFound):
        sprints.remove_story(ADMIN, P, "SPRINT-01", "US-01.04")


def test_us0505_ca02_una_historia_un_sprint_abierto(sprints: SprintService) -> None:
    _new(sprints)
    _new(sprints, name="Sprint 2")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    with pytest.raises(FailedPrecondition, match="US-01.01 ya está en SPRINT-01"):
        sprints.add_stories(ADMIN, P, "SPRINT-02", ["US-01.02", "US-01.01"])
    assert sprints.get(ADMIN, P, "SPRINT-02")["story_ids"] == []  # atómico: no se añadió ninguna


def test_us0505_ca03_terminales_rechazadas(sprints: SprintService, backlog: BacklogService) -> None:
    backlog.set_status(ADMIN, P, "US-01.03", "CANCELLED")
    _new(sprints)
    with pytest.raises(FailedPrecondition, match="US-01.03 está CANCELLED"):
        sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.03"])


def test_us0505_ca04_aviso_si_no_esta_ready(sprints: SprintService) -> None:
    _new(sprints)
    sprint = sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.04"])
    assert sprint["warnings"] == ["US-01.04 no está READY: refínala antes de empezar"]


# ---------------------------------------------------------------- US-05.06 métricas históricas
def test_us0506_ca01_ca02_metricas_conservadas(sprints: SprintService, backlog: BacklogService, data_dir) -> None:
    _closing(sprints, backlog)
    sprints.close(ADMIN, P, "SPRINT-01")
    backlog.set_status(ADMIN, P, "US-01.02", "IMPLEMENTED")  # cambios posteriores no alteran el cierre
    listed = sprints.list(ADMIN, P)["sprints"][0]
    assert listed["summary"]["stories_by_status"] == {"DONE": 1, "IN_PROGRESS": 1, "READY": 1}
    conn = sqlite3.connect(data_dir / "projects" / P / "project.db")
    stored = conn.execute("SELECT status, closed_by FROM sprints WHERE id = 'SPRINT-01'").fetchone()
    conn.close()
    assert stored == ("CLOSED", ADMIN)


# ---------------------------------------------------------------- US-05.07 / US-05.08 capacidad y carga
def test_us0507_us0508_capacidad_y_carga(sprints: SprintService) -> None:
    _new(sprints, capacity=2)
    sprint = sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01", "US-01.02"])
    assert (sprint["capacity"], sprint["load"], sprint["overloaded"]) == (2, 2, False)
    sprint = sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.03"])
    assert (sprint["load"], sprint["overloaded"]) == (3, True)
    assert sprint["warnings"] == ["SPRINT-01 supera su capacidad: 3 historias de 2"]
    assert sprint["stories_by_status"] == {"READY": 3}


# ---------------------------------------------------------------- US-05.09 sobrecarga antes de iniciar
def test_us0509_ca01_ca02_sobrecarga_detectada_antes_de_iniciar(sprints: SprintService) -> None:
    _new(sprints, capacity=1)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01", "US-01.02"])
    with pytest.raises(FailedPrecondition, match="sobrecargado: 2 historias para una capacidad de 1"):
        sprints.start(ADMIN, P, "SPRINT-01")
    assert sprints.get(ADMIN, P, "SPRINT-01")["status"] == "PLANNED"
    assert sprints.start(ADMIN, P, "SPRINT-01", force=True)["status"] == "ACTIVE"


def test_us0509_sprint_vacio_no_se_inicia(sprints: SprintService) -> None:
    _new(sprints)
    with pytest.raises(FailedPrecondition, match="no tiene historias"):
        sprints.start(ADMIN, P, "SPRINT-01")


# ---------------------------------------------------------------- por MCP y con eventos
@pytest.mark.anyio
async def test_us0502_sprints_por_mcp_con_eventos(service: ProjectService, backlog: BacklogService) -> None:
    before = service.events.latest_seq()
    async with Client(build_mcp_server(service, lambda: ADMIN)) as client:
        created = await client.call_tool(
            "acm_sprint_create",
            {"project_id": P, "name": "S1", "goal": "Objetivo", "start_date": "2026-10-01", "end_date": "2026-10-10"},
        )
        await client.call_tool(
            "acm_sprint_add_stories", {"project_id": P, "sprint_id": "SPRINT-01", "story_ids": ["US-01.01"]}
        )
        started = await client.call_tool("acm_sprint_start", {"project_id": P, "sprint_id": "SPRINT-01"})
        listed = await client.call_tool("acm_sprint_list", {"project_id": P})
    assert created.structured_content["id"] == "SPRINT-01" and started.structured_content["status"] == "ACTIVE"
    assert listed.structured_content["sprints"][0]["story_ids"] == ["US-01.01"]
    types = [e["type"] for e in service.events.after(before, 50) if e["entity_type"] == "sprint"]
    assert types == ["sprint.created", "sprint.updated", "sprint.started"]


@pytest.mark.anyio
async def test_us0502_cancelar_por_mcp(
    service: ProjectService, backlog: BacklogService, sprints: SprintService
) -> None:
    sprints.create(ADMIN, P, "S1", "Objetivo", "2026-10-01", "2026-10-10")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    async with Client(build_mcp_server(service, lambda: ADMIN)) as client:
        cancelled = await client.call_tool("acm_sprint_cancel", {"project_id": P, "sprint_id": "SPRINT-01"})
        again = await client.call_tool("acm_sprint_cancel", {"project_id": P, "sprint_id": "SPRINT-01"})
    assert cancelled.structured_content["status"] == "CANCELLED"
    assert again.is_error and "FAILED_PRECONDITION" in again.content[0].text
    assert backlog.get_story(ADMIN, P, "US-01.01")["sprint_id"] is None
