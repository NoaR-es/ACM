"""SPRINT-009 — reparto de trabajo entre agentes: US-14.16 (pedir trabajo) y US-14.17 (asignación con caducidad)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from mcp import Client

from acm.domain.backlog import BacklogService
from acm.domain.errors import FailedPrecondition, Forbidden
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
from acm.domain.work import WorkService
from acm.mcp_server import build_mcp_server
from acm.sessions import current_session
from tests.conftest import ADMIN

P = "alpha"
A, B = "claude-code.portatil", "cursor.portatil"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def local(data_dir: Path) -> Iterator[ProjectService]:
    svc = ProjectService(data_dir, local_mode=True)
    svc.ensure_principal(ADMIN, "admin")
    for agent in (A, B):
        svc.ensure_principal(agent, "user", "agent")
    svc.create(ADMIN, P, "Alpha")
    identity = IdentityService(svc)
    for agent in (A, B):
        identity.set_member(ADMIN, P, agent, "member")
    yield svc
    svc.close()


@pytest.fixture
def backlog(local: ProjectService) -> BacklogService:
    b = BacklogService(local)
    b.create_requirement(ADMIN, P, "Requisito")
    b.create_epic(ADMIN, P, "Épica", "Objetivo", "Alcance", ["REQ-001"])
    b.create_feature(ADMIN, P, "EPIC-01", "Feature")
    return b


def _stories(backlog: BacklogService, n: int, ready: int = 0) -> None:
    for i in range(1, n + 1):
        backlog.create_story(ADMIN, P, "FEAT-01.01", "operador", f"hacer {i}", "avanzar", ["REQ-001"], [f"CA {i}"])
    for i in range(1, ready + 1):
        backlog.mark_ready(ADMIN, P, f"US-01.{i:02d}")


@pytest.fixture
def work(backlog: BacklogService) -> WorkService:
    return WorkService(backlog)


def _active_sprint(backlog: BacklogService, stories: list[str]) -> None:
    sprints = SprintService(backlog)
    sprints.create(ADMIN, P, "Sprint 1", "Entregar", "2026-10-01", "2026-10-14", None)
    sprints.add_stories(ADMIN, P, "SPRINT-01", stories)
    sprints.start(ADMIN, P, "SPRINT-01")


def _expire(local: ProjectService, item: str) -> None:
    past = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    with local.project_db(P).write() as conn:
        conn.execute("UPDATE work_claims SET expires_at = ? WHERE item = ?", (past, item))


# ---------------------------------------------------------------- US-14.16 — pedir el siguiente trabajo
def test_us1416_ca01_responde_lo_que_toca_segun_el_estado(work: WorkService, backlog: BacklogService) -> None:
    assert work.next_work(A, P)["action"] == "build_backlog"  # proyecto vacío
    work.release(A, P, "backlog")
    _stories(backlog, 3)
    refine = work.next_work(A, P)
    assert refine["action"] == "refine" and refine["item"] == "US-01.01" and refine["story"]["status"] == "PLANNED"
    assert "acm_story_mark_ready" in " ".join(refine["steps"]) and "PLANNED" in refine["reason"]
    backlog.mark_ready(A, P, "US-01.01")  # lo hace el agente: ya no hay que refinarla
    plan = work.next_work(A, P)
    assert plan["action"] == "plan_sprint" and "READY" in plan["reason"]
    _active_sprint(backlog, ["US-01.01"])
    implement = work.next_work(A, P)
    assert implement["action"] == "implement" and implement["item"] == "US-01.01" and "SPRINT-01" in implement["reason"]


def test_us1416_ca01_avanza_con_el_estado_de_la_historia(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 1, ready=1)
    _active_sprint(backlog, ["US-01.01"])
    assert work.next_work(A, P)["action"] == "implement"
    backlog.set_status(A, P, "US-01.01", "IN_PROGRESS")
    backlog.set_status(A, P, "US-01.01", "IMPLEMENTED")
    verify = work.next_work(A, P)
    assert verify["action"] == "verify" and verify["item"] == "US-01.01"
    for to in ("TESTING", "VERIFIED"):
        backlog.set_status(A, P, "US-01.01", to)
    closing = work.next_work(A, P)
    assert closing["action"] == "close_sprint" and closing["sprint_id"] == "SPRINT-01"
    SprintService(backlog).close(A, P, "SPRINT-01")
    assert work.next_work(A, P)["action"] == "idle"  # nada READY, nada PLANNED: no queda trabajo


def test_us1416_ca01_sprint_planificado_sin_iniciar(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 1, ready=1)
    sprints = SprintService(backlog)
    sprints.create(ADMIN, P, "Sprint 1", "Entregar", "2026-10-01", "2026-10-14", None)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    start = work.next_work(A, P)
    assert start["action"] == "start_sprint" and start["sprint_id"] == "SPRINT-01"


def test_us1416_ca02_dos_agentes_nunca_reciben_lo_mismo(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 3, ready=3)
    _active_sprint(backlog, ["US-01.01", "US-01.02", "US-01.03"])
    first, second, third = work.next_work(A, P), work.next_work(B, P), work.next_work(B, P)
    assert first["item"] == "US-01.01" and first["claim"]["ttl_minutes"] == 30
    assert second["item"] == "US-01.02" and not second["continuing"]
    assert third["item"] == "US-01.02" and third["continuing"]  # pedir otra vez sin terminar: sigue con lo suyo
    assert [o["item"] for o in second["others_working"]] == ["US-01.01"]
    assert second["others_working"][0]["agent"] == A
    assert work.next_work(A, P)["item"] == "US-01.01"


def test_us1416_ca02_sin_trabajo_libre_espera(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 1, ready=1)
    _active_sprint(backlog, ["US-01.01"])
    assert work.next_work(A, P)["item"] == "US-01.01"
    idle = work.next_work(B, P)
    assert idle["action"] == "idle" and "otros agentes" in idle["reason"] and idle["others_working"][0]["agent"] == A
    assert work.next_work(B, P, claim=False)["action"] == "idle"


def test_us1416_ca02_consultar_sin_asignar(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 2, ready=2)
    peek = work.next_work(A, P, claim=False)
    assert peek["claim"] is None and peek["action"] == "plan_sprint"
    assert work.claims(A, P)["claims"] == []  # mirar no asigna nada


def test_us1416_ca03_historia_asignada_a_otro_no_se_cambia(
    local: ProjectService, work: WorkService, backlog: BacklogService
) -> None:
    _stories(backlog, 2, ready=2)
    _active_sprint(backlog, ["US-01.01", "US-01.02"])
    assert work.next_work(A, P)["item"] == "US-01.01"
    with pytest.raises(FailedPrecondition, match=f"asignada a {A}"):
        backlog.set_status(B, P, "US-01.01", "IN_PROGRESS")
    with pytest.raises(FailedPrecondition, match="acm_next_work"):
        backlog.add_criteria(B, P, "US-01.01", ["otro criterio"])
    backlog.set_status(A, P, "US-01.01", "IN_PROGRESS")  # el dueño sí
    backlog.set_status(ADMIN, P, "US-01.01", "BLOCKED")  # una persona siempre puede, p. ej. desde el Kanban
    backlog.set_status(B, P, "US-01.02", "IN_PROGRESS")  # y lo que no está asignado, cualquiera


def test_us1416_acceso_de_solo_lectura_no_recibe_trabajo(local: ProjectService, work: WorkService) -> None:
    local.ensure_principal("lector", "user", "agent")
    IdentityService(local).set_member(ADMIN, P, "lector", "viewer")
    with pytest.raises(Forbidden, match="solo lectura"):
        work.next_work("lector", P)


# ---------------------------------------------------------------- US-14.17 — caducidad, liberación y visibilidad
def test_us1417_ca01_la_asignacion_se_renueva_al_tocar_la_historia(
    local: ProjectService, work: WorkService, backlog: BacklogService
) -> None:
    _stories(backlog, 1, ready=1)
    _active_sprint(backlog, ["US-01.01"])
    work.next_work(A, P)
    _expire(local, "US-01.01")
    backlog.set_status(A, P, "US-01.01", "IN_PROGRESS")  # caducada pero sigue siendo suya: se renueva al trabajarla
    [claim] = work.claims(A, P)["claims"]
    assert claim["item"] == "US-01.01" and claim["agent"] == A
    assert datetime.fromisoformat(claim["expires_at"]) > datetime.now(UTC) + timedelta(minutes=29)


def test_us1417_ca01_caducada_queda_libre_para_otro(
    local: ProjectService, work: WorkService, backlog: BacklogService
) -> None:
    _stories(backlog, 1, ready=1)
    _active_sprint(backlog, ["US-01.01"])
    work.next_work(A, P)
    assert work.next_work(B, P)["action"] == "idle"
    _expire(local, "US-01.01")  # A desapareció
    assert work.claims(B, P)["claims"] == []
    taken = work.next_work(B, P)
    assert taken["item"] == "US-01.01" and not taken["continuing"]
    backlog.set_status(B, P, "US-01.01", "IN_PROGRESS")  # ya es de B: A no lo puede mover
    with pytest.raises(FailedPrecondition, match=f"asignada a {B}"):
        backlog.set_status(A, P, "US-01.01", "BLOCKED")


def test_us1417_ca01_plazo_configurable(local: ProjectService, work: WorkService, backlog: BacklogService) -> None:
    local.set_config(ADMIN, P, {"work.claim_ttl_minutes": 5})
    _stories(backlog, 1)
    assert work.next_work(A, P)["claim"]["ttl_minutes"] == 5
    with pytest.raises(Exception, match="entre 1 y 1440"):
        local.set_config(ADMIN, P, {"work.claim_ttl_minutes": 0})


def test_us1417_ca02_liberar_el_trabajo(local: ProjectService, work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 2, ready=2)
    _active_sprint(backlog, ["US-01.01", "US-01.02"])
    work.next_work(A, P)
    with pytest.raises(Forbidden, match="solo él o una persona"):
        work.release(B, P, "US-01.01")
    assert work.release(A, P, "US-01.01")["released"] is True
    assert work.next_work(B, P)["item"] == "US-01.01"  # liberado: otro lo recibe
    assert work.release(ADMIN, P, "US-01.01")["was"] == B  # una persona puede liberar cualquiera
    events = [e["type"] for e in local.events.after(0, 200) if e["entity_type"] == "work"]
    assert events == ["work.claimed", "work.released", "work.claimed", "work.released"]


def test_us1417_ca02_pedir_otra_cosa_libera_lo_que_ya_no_corresponde(
    work: WorkService, backlog: BacklogService
) -> None:
    _stories(backlog, 1)
    assert work.next_work(A, P)["item"] == "US-01.01"  # refinar
    backlog.mark_ready(A, P, "US-01.01")  # el agente la deja READY: ya no hay que refinarla
    nxt = work.next_work(A, P)
    assert nxt["action"] == "plan_sprint" and [c["item"] for c in work.claims(A, P)["claims"]] == ["sprint-planning"]


def test_us1417_ca03_mismo_cliente_en_dos_sesiones_no_se_pisa(work: WorkService, backlog: BacklogService) -> None:
    """Dos sesiones del mismo principal (mismo cliente en el mismo equipo) reparten el trabajo como dos agentes."""
    _stories(backlog, 2, ready=2)
    _active_sprint(backlog, ["US-01.01", "US-01.02"])
    current_session.set("aaaa")
    first = work.next_work(A, P)
    current_session.set("bbbb")
    second = work.next_work(A, P)
    assert first["item"] == "US-01.01" and second["item"] == "US-01.02"
    assert second["others_working"][0]["agent"] == f"{A}#aaaa"
    with pytest.raises(FailedPrecondition, match=f"{A}#aaaa"):
        backlog.set_status(A, P, "US-01.01", "IN_PROGRESS")  # misma identidad, otra sesión: no es suyo
    current_session.set("aaaa")
    backlog.set_status(A, P, "US-01.01", "IN_PROGRESS")
    assert {c["agent"] for c in work.claims(A, P)["claims"]} == {f"{A}#aaaa", f"{A}#bbbb"}
    current_session.set("")


def test_us1417_ca03_se_ve_quien_trabaja_en_que(work: WorkService, backlog: BacklogService) -> None:
    _stories(backlog, 2, ready=2)
    _active_sprint(backlog, ["US-01.01", "US-01.02"])
    work.next_work(A, P)
    work.next_work(B, P)
    claims = {c["item"]: c["agent"] for c in work.claims(ADMIN, P)["claims"]}
    assert claims == {"US-01.01": A, "US-01.02": B}


# ---------------------------------------------------------------- por MCP
@pytest.mark.anyio
async def test_us1416_flujo_del_agente_por_mcp(local: ProjectService, backlog: BacklogService) -> None:
    _stories(backlog, 1, ready=1)
    _active_sprint(backlog, ["US-01.01"])
    async with Client(build_mcp_server(local, lambda: A)) as agent:
        work = (await agent.call_tool("acm_next_work", {"project_id": P})).structured_content
        assert work["action"] == "implement" and work["item"] == "US-01.01" and work["steps"]
        listed = (await agent.call_tool("acm_work_list", {"project_id": P})).structured_content
        assert listed["claims"][0]["agent"] == A
        released = (await agent.call_tool("acm_work_release", {"project_id": P, "item": "US-01.01"})).structured_content
        assert released["released"] is True
        missing = await agent.call_tool("acm_work_release", {"project_id": P, "item": "US-01.01"})
        assert missing.is_error and "NOT_FOUND" in missing.content[0].text
