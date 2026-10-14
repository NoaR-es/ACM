"""SPRINT-009 — unirse a proyectos con aprobación de una persona: US-14.14 (agente) y US-14.15 (operador)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from mcp import Client

from acm.domain.access import AccessService
from acm.domain.backlog import BacklogService
from acm.domain.errors import FailedPrecondition, Forbidden, InvalidArgument, NotFound
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN

P = "alpha"
BOT = "claude-code.portatil"
OTHER = "cursor.portatil"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def local(data_dir: Path) -> Iterator[ProjectService]:
    """ACM en modo local (ADR-023): los agentes ven el directorio y crean sus proyectos."""
    svc = ProjectService(data_dir, local_mode=True)
    svc.ensure_principal(ADMIN, "admin")
    svc.ensure_principal(BOT, "user", "agent")
    svc.ensure_principal(OTHER, "user", "agent")
    svc.create(ADMIN, P, "Alpha")
    BacklogService(svc).create_requirement(ADMIN, P, "Requisito de origen")
    yield svc
    svc.close()


@pytest.fixture
def access(local: ProjectService) -> AccessService:
    return AccessService(local)


# ---------------------------------------------------------------- US-14.14 — el agente elige proyecto
def test_us1414_ca01_directorio_con_rol_y_peticiones(local: ProjectService, access: AccessService) -> None:
    local.create(BOT, "beta", "Beta")  # el agente es owner de beta
    access.request_join(BOT, P, "read")
    listing = {p["project_id"]: p for p in access.directory(BOT)["projects"]}
    assert listing["beta"]["your_role"] == "owner" and listing["beta"]["join_request"] is None
    assert listing[P]["your_role"] is None  # existe, pero no es miembro
    assert listing[P]["join_request"]["status"] == "PENDING" and listing[P]["join_request"]["access"] == "read"
    # otro agente ve los mismos proyectos con su propia situación
    other = {p["project_id"]: p for p in access.directory(OTHER)["projects"]}
    assert set(other) == {P, "beta"} and other[P]["join_request"] is None


def test_us1414_ca01_fuera_del_modo_local_solo_ve_los_suyos(data_dir: Path) -> None:
    svc = ProjectService(data_dir)  # servidor con tokens: no se enumeran proyectos ajenos
    svc.ensure_principal(ADMIN, "admin")
    svc.ensure_principal(BOT, "user", "agent")
    svc.create(ADMIN, P, "Alpha")
    assert AccessService(svc).directory(BOT)["projects"] == []
    with pytest.raises(Forbidden):  # y crear proyectos sigue siendo cosa de un admin
        svc.create(BOT, "beta", "Beta")
    svc.close()


def test_us1414_ca02_crear_proyecto_nuevo_sin_aprobacion(local: ProjectService) -> None:
    created = local.create(BOT, "beta", "Beta")
    assert created["project_id"] == "beta"
    assert local.open(BOT, "beta")["role"] == "owner"
    assert [m["principal_id"] for m in IdentityService(local).list_members(BOT, "beta")["members"]] == [BOT]
    with pytest.raises(NotFound):  # y no abre la puerta a los proyectos de los demás
        local.open(BOT, P)


def test_us1414_ca03_pedir_unirse_deja_pendiente_y_sin_acceso(local: ProjectService, access: AccessService) -> None:
    first = access.request_join(BOT, P, "write", "quiero implementar US-01.01")
    assert first["status"] == "PENDING" and first["access"] == "write" and first["message"].startswith("quiero")
    again = access.request_join(BOT, P, "write")  # repetir no duplica la petición
    assert again["request_id"] == first["request_id"]
    assert len(access.list_requests(ADMIN)["requests"]) == 1
    for call in (local.open, BacklogService(local).list_requirements):  # hasta que se apruebe, no existe para él
        with pytest.raises(NotFound):
            call(BOT, P)


def test_us1414_ca03_entradas_invalidas(access: AccessService) -> None:
    with pytest.raises(InvalidArgument):
        access.request_join(BOT, P, "todo")
    with pytest.raises(InvalidArgument):
        access.request_join(BOT, P, "write", "x" * 501)
    with pytest.raises(NotFound):
        access.request_join(BOT, "no-existe", "write")


def test_us1414_ca04_consultar_el_estado_de_la_peticion(local: ProjectService, access: AccessService) -> None:
    assert access.join_status(BOT, P)["status"] == "NONE"
    pending = access.request_join(BOT, P)
    assert access.join_status(BOT, P)["status"] == "PENDING" and "persona" in access.join_status(BOT, P)["next"]
    access.decide(ADMIN, pending["request_id"], True)
    assert access.join_status(BOT, P) == {"project_id": P, "status": "MEMBER", "role": "member"}
    assert access.request_join(BOT, P)["status"] == "MEMBER"  # pedir estando dentro no crea nada


# ---------------------------------------------------------------- US-14.15 — la persona decide
def test_us1415_ca01_las_peticiones_pendientes_llegan_en_tiempo_real(
    local: ProjectService, access: AccessService
) -> None:
    before = local.events.latest_seq()
    request = access.request_join(BOT, P, "read")
    [event] = [e for e in local.events.after(before, 50) if e["type"] == "join.requested"]
    assert event["project_id"] == P and event["data"] == {"principal_id": BOT, "access": "read"}
    [pending] = access.list_requests(ADMIN)["requests"]
    assert pending["request_id"] == request["request_id"] and pending["kind"] == "agent"
    assert pending["project_name"] == "Alpha" and access.list_requests(ADMIN)["can_decide"] is True


def test_us1415_ca02_aprobar_con_escritura_o_solo_lectura(local: ProjectService, access: AccessService) -> None:
    backlog = BacklogService(local)
    write = access.request_join(BOT, P, "write")["request_id"]
    read = access.request_join(OTHER, P, "write")["request_id"]
    approved = access.decide(ADMIN, write, True)
    assert approved["status"] == "APPROVED" and approved["granted_role"] == "member" and approved["decided_by"] == ADMIN
    access.decide(ADMIN, read, True, "viewer")  # la persona rebaja a solo lectura lo que el agente pidió
    backlog.create_requirement(BOT, P, "lo añade un miembro")
    assert backlog.list_requirements(OTHER, P)["requirements"]  # el viewer lee…
    with pytest.raises(Forbidden):
        backlog.create_requirement(OTHER, P, "…pero no escribe")
    types = [e["type"] for e in local.events.after(0, 200)]
    assert types.count("join.decided") == 2 and "member.changed" in types


def test_us1415_ca02_rol_invalido_y_peticion_ya_decidida(local: ProjectService, access: AccessService) -> None:
    rid = access.request_join(BOT, P)["request_id"]
    with pytest.raises(InvalidArgument):
        access.decide(ADMIN, rid, True, "owner")  # un agente nunca entra como owner
    access.decide(ADMIN, rid, True)
    with pytest.raises(FailedPrecondition):
        access.decide(ADMIN, rid, False)
    with pytest.raises(NotFound):
        access.decide(ADMIN, 999, True)


def test_us1415_ca03_rechazar_y_el_agente_lo_sabe(local: ProjectService, access: AccessService) -> None:
    rid = access.request_join(BOT, P)["request_id"]
    rejected = access.decide(ADMIN, rid, False)
    assert rejected["status"] == "REJECTED" and rejected["granted_role"] is None
    status = access.join_status(BOT, P)
    assert status["status"] == "REJECTED" and "rechazada" in status["next"]
    with pytest.raises(NotFound):
        local.open(BOT, P)
    assert access.request_join(BOT, P)["status"] == "PENDING"  # puede volver a pedirlo: nueva petición


def test_us1415_ca04_retirar_a_un_agente_en_cualquier_momento(local: ProjectService, access: AccessService) -> None:
    identity = IdentityService(local)
    access.decide(ADMIN, access.request_join(BOT, P)["request_id"], True)
    assert local.open(BOT, P)["role"] == "member"
    identity.remove_member(ADMIN, P, BOT)
    with pytest.raises(NotFound):
        local.open(BOT, P)
    status = access.join_status(BOT, P)  # no debe creer que aún tiene acceso por una aprobación antigua
    assert status["status"] == "REMOVED" and "retiró" in status["next"]
    listing = {p["project_id"]: p for p in access.directory(BOT)["projects"]}
    assert listing[P]["your_role"] is None and listing[P]["join_request"]["status"] == "REMOVED"
    assert access.request_join(BOT, P)["status"] == "PENDING"  # puede pedirlo de nuevo


def test_us1415_solo_una_persona_decide_y_solo_la_de_su_proyecto(local: ProjectService, access: AccessService) -> None:
    identity = IdentityService(local)
    rid = access.request_join(BOT, P)["request_id"]
    with pytest.raises(NotFound):  # un agente no ve ni las peticiones de los demás
        access.decide(OTHER, rid, True)
    # ni siquiera siendo owner del proyecto: dar acceso es cosa de personas
    local.ensure_principal("agente-owner", "user", "agent")
    identity.set_member(ADMIN, P, "agente-owner", "owner")
    with pytest.raises(Forbidden, match="persona"):
        access.decide("agente-owner", rid, True)
    with pytest.raises(Forbidden, match="persona"):
        identity.set_member("agente-owner", P, OTHER, "member")
    with pytest.raises(Forbidden, match="persona"):
        identity.remove_member("agente-owner", P, "agente-owner")
    # un owner que es persona sí puede, pero solo en su proyecto
    local.ensure_principal("ana", "user", "user")
    identity.set_member(ADMIN, P, "ana", "owner")
    local.create(ADMIN, "beta", "Beta")
    other = access.request_join(OTHER, "beta")["request_id"]
    assert [r["project_id"] for r in access.list_requests("ana")["requests"]] == [P]
    with pytest.raises(NotFound):
        access.decide("ana", other, True)
    assert access.decide("ana", rid, True)["status"] == "APPROVED"


# ---------------------------------------------------------------- por MCP, como lo usa el agente
@pytest.mark.anyio
async def test_us1414_flujo_del_agente_por_mcp(local: ProjectService) -> None:
    server = build_mcp_server(local, lambda: BOT)
    async with Client(server) as agent:
        directory = (await agent.call_tool("acm_project_directory", {})).structured_content
        assert [p["project_id"] for p in directory["projects"]] == [P] and "acm_project_join" in directory["how_to"]
        joined = (
            await agent.call_tool("acm_project_join", {"project_id": P, "access_level": "write"})
        ).structured_content
        assert joined["status"] == "PENDING" and "persona" in joined["next"]
        blocked = await agent.call_tool("acm_requirement_list", {"project_id": P})
        assert blocked.is_error and "NOT_FOUND" in blocked.content[0].text
        AccessService(local).decide(ADMIN, joined["request_id"], True)  # la persona aprueba en la interfaz
        status = (await agent.call_tool("acm_project_join_status", {"project_id": P})).structured_content
        assert status["status"] == "MEMBER"
        assert not (await agent.call_tool("acm_requirement_list", {"project_id": P})).is_error
        denied = await agent.call_tool("acm_member_set", {"project_id": P, "principal_id": OTHER, "role": "member"})
        assert denied.is_error and "FORBIDDEN" in denied.content[0].text  # un agente no da acceso a otro
