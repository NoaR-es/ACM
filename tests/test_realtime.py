"""EPIC-06 (Kanban), EPIC-21 (eventos y WebSocket) y EPIC-30 (API REST v1) contra ACM real por HTTP."""

from __future__ import annotations

import json
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import anyio
import httpx
import pytest
from mcp import Client, StdioServerParameters
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from acm.domain.backlog import BacklogService
from acm.domain.errors import FailedPrecondition, InvalidArgument
from tests.live import ADMIN, Acm, mcp

P = "alpha"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _seed(acm: Acm, project: str = P, stories: int = 2) -> BacklogService:
    acm.service.create(ADMIN, project, project.capitalize())
    b = BacklogService(acm.service)
    b.create_requirement(ADMIN, project, "Gestionar proyectos")
    b.create_epic(ADMIN, project, "Proyectos", "o", "s", ["REQ-001"])
    b.create_feature(ADMIN, project, "EPIC-01", "Creación")
    for i in range(stories):
        b.create_story(ADMIN, project, "FEAT-01.01", "operador", f"historia {i + 1}", "valor", ["REQ-001"], ["CA"])
    return b


def _ready_in_progress(b: BacklogService, project: str, story: str) -> None:
    b.mark_ready(ADMIN, project, story)
    b.set_status(ADMIN, project, story, "IN_PROGRESS")


def _http(acm: Acm, token: str | None) -> httpx.Client:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.Client(base_url=f"{acm.url}/api/v1", headers=headers, timeout=10)


@asynccontextmanager
async def ws(acm: Acm, token: str, after: int | None = None) -> AsyncIterator[tuple[ClientConnection, dict]]:
    async with connect(acm.url.replace("http", "ws") + "/api/v1/ws") as conn:
        await conn.send(json.dumps({"type": "auth", "token": token, "after": after}))
        ready = json.loads(await conn.recv())
        yield conn, ready


async def _events(
    conn: ClientConnection, n: int, *, types: tuple[str, ...] | None = None, timeout: float = 8
) -> list[dict[str, Any]]:
    """Los siguientes `n` eventos de dominio (opcionalmente solo de ciertos tipos), en orden de llegada."""
    out: list[dict[str, Any]] = []
    with anyio.fail_after(timeout):
        while len(out) < n:
            msg = json.loads(await conn.recv())
            if msg["type"] == "event" and (types is None or msg["event"]["type"] in types):
                out.append(msg["event"])
    return out


async def _silence(conn: ClientConnection, seconds: float = 1.0, *, types: tuple[str, ...] | None = None) -> list:
    """Eventos recibidos durante `seconds` (para comprobar que NO llega nada)."""
    got: list[dict[str, Any]] = []
    with anyio.move_on_after(seconds):
        while True:
            msg = json.loads(await conn.recv())
            if msg["type"] == "event" and (types is None or msg["event"]["type"] in types):
                got.append(msg["event"])
    return got


DOMAIN = (
    "project.created",
    "project.config_changed",
    "requirement.created",
    "epic.created",
    "epic.updated",
    "feature.created",
    "feature.split",
    "story.created",
    "story.updated",
    "story.status_changed",
    "member.changed",
    "principal.changed",
    "watchdog.run",
)


# ---------------------------------------------------------------- US-06.02 — cambiar el estado de una historia
def test_us0602_ca01_ca02_cambio_permitido_y_registrado(acm: Acm) -> None:
    b = _seed(acm)
    b.mark_ready(ADMIN, P, "US-01.01")
    story = b.set_status(ADMIN, P, "US-01.01", "IN_PROGRESS", "empiezo")
    assert story["status"] == "IN_PROGRESS"
    history = b.status_history(ADMIN, P, "US-01.01")["history"]
    assert [(h["from_status"], h["to_status"], h["changed_by"]) for h in history] == [
        ("PLANNED", "READY", ADMIN),
        ("READY", "IN_PROGRESS", ADMIN),
    ]
    assert history[1]["reason"] == "empiezo"


@pytest.mark.parametrize(
    ("path", "target", "message"),
    [
        ((), "READY", "gate"),
        ((), "DONE", "no permitida"),
        (("READY", "IN_PROGRESS"), "DONE", "no permitida"),
        (("READY", "IN_PROGRESS", "IMPLEMENTED", "TESTING"), "DONE", "no permitida"),
        (("READY",), "READY", "ya está"),
    ],
)
def test_us0602_ca03_transiciones_no_permitidas(acm: Acm, path: tuple[str, ...], target: str, message: str) -> None:
    b = _seed(acm)
    for status in path:
        (b.mark_ready(ADMIN, P, "US-01.01") if status == "READY" else b.set_status(ADMIN, P, "US-01.01", status))
    before = b.status_history(ADMIN, P, "US-01.01")["history"]
    with pytest.raises(FailedPrecondition, match=message):
        b.set_status(ADMIN, P, "US-01.01", target)
    assert b.status_history(ADMIN, P, "US-01.01")["history"] == before  # sin efectos
    with pytest.raises(InvalidArgument, match="status"):
        b.set_status(ADMIN, P, "US-01.01", "HECHO")


def test_us0602_done_solo_tras_verificar(acm: Acm) -> None:
    b = _seed(acm)
    b.mark_ready(ADMIN, P, "US-01.01")
    for status in ("IN_PROGRESS", "IMPLEMENTED", "TESTING", "VERIFIED", "DONE"):
        assert b.set_status(ADMIN, P, "US-01.01", status)["status"] == status


def test_us0602_ca04_el_tablero_refleja_el_estado(acm: Acm) -> None:
    b = _seed(acm)
    _ready_in_progress(b, P, "US-01.01")
    with _http(acm, acm.token(ADMIN)) as http:
        cards = http.get("/kanban").json()["cards"]
    assert {c["id"]: c["status"] for c in cards} == {"US-01.01": "IN_PROGRESS", "US-01.02": "PLANNED"}


# ---------------------------------------------------------------- US-06.01 — tablero (uno o varios proyectos)
def test_us0601_ca01_ca02_una_columna_por_historia_con_datos(acm: Acm) -> None:
    b = _seed(acm, stories=3)
    b.mark_ready(ADMIN, P, "US-01.02")
    with _http(acm, acm.token(ADMIN)) as http:
        board = http.get("/kanban", params={"projects": P}).json()
    assert board["columns"][:3] == ["PLANNED", "READY", "IN_PROGRESS"]
    ids = [c["id"] for c in board["cards"]]
    assert sorted(ids) == ["US-01.01", "US-01.02", "US-01.03"] and len(ids) == len(set(ids))
    for card in board["cards"]:
        assert card["status"] in board["columns"] and card["i_want"] and card["project_id"] == P


def test_us0601_ca03_solo_el_contexto_seleccionado_y_varios_a_la_vez(acm: Acm) -> None:
    _seed(acm, P)
    _seed(acm, "beta", stories=1)
    _seed(acm, "gamma", stories=1)
    with _http(acm, acm.token(ADMIN)) as http:
        one = http.get("/kanban", params={"projects": "beta"}).json()
        two = http.get("/kanban", params={"projects": "alpha,gamma"}).json()
        everything = http.get("/kanban").json()
    assert {c["project_id"] for c in one["cards"]} == {"beta"}
    assert {c["project_id"] for c in two["cards"]} == {"alpha", "gamma"} and two["projects"] == ["alpha", "gamma"]
    assert {c["project_id"] for c in everything["cards"]} == {"alpha", "beta", "gamma"}


def test_us0601_ca03_proyecto_ajeno_no_se_muestra(acm: Acm) -> None:
    _seed(acm, P)
    _seed(acm, "beta", stories=1)
    acm.identity.create_principal(ADMIN, "ana", "user")
    acm.identity.set_member(ADMIN, P, "ana", "member")
    with _http(acm, acm.token("ana")) as http:
        mine = http.get("/kanban").json()
        foreign = http.get("/kanban", params={"projects": "beta"})
    assert {c["project_id"] for c in mine["cards"]} == {P}
    assert foreign.status_code == 404 and foreign.json()["error"]["code"] == "NOT_FOUND"


def test_us0601_ca04_historia_inexistente_no_aparece(acm: Acm) -> None:
    _seed(acm, stories=1)
    with _http(acm, acm.token(ADMIN)) as http:
        cards = http.get("/kanban").json()["cards"]
        missing = http.get(f"/projects/{P}/stories/US-01.09")
    assert [c["id"] for c in cards] == ["US-01.01"] and missing.status_code == 404


# ---------------------------------------------------------------- US-21.01 — eventos de dominio
@pytest.mark.anyio
async def test_us2101_ca01_ca02_cambio_genera_evento_con_contexto(acm: Acm) -> None:
    b = _seed(acm)
    token = acm.token(ADMIN)
    async with ws(acm, token) as (conn, ready):
        assert ready["type"] == "ready" and ready["principal"] == ADMIN
        await anyio.to_thread.run_sync(b.mark_ready, ADMIN, P, "US-01.01")
        [event] = await _events(conn, 1, types=DOMAIN)
    assert event["type"] == "story.status_changed" and event["seq"] > ready["seq"]
    assert (event["project_id"], event["entity_type"], event["entity_id"], event["principal"]) == (
        P,
        "story",
        "US-01.01",
        ADMIN,
    )
    assert event["data"]["status"] == "READY" and event["data"]["from"] == "PLANNED" and event["ts"]


def test_us2101_ca03_operacion_revertida_no_publica(acm: Acm) -> None:
    b = _seed(acm)
    before = acm.service.events.latest_seq()
    for bad in (
        lambda: acm.service.create(ADMIN, P, "duplicado"),
        lambda: b.create_story(ADMIN, P, "FEAT-01.01", "a", "b", "c", ["REQ-999"]),
        lambda: b.set_status(ADMIN, P, "US-01.01", "DONE"),
    ):
        with pytest.raises(Exception):  # noqa: B017 — cualquier rechazo del dominio
            bad()
    assert acm.service.events.after(before) == []


# ---------------------------------------------------------------- US-06.03 / US-21.02 — tiempo real
@pytest.mark.anyio
async def test_us0603_ca01_ca02_agente_cambia_y_los_clientes_lo_reciben(acm: Acm) -> None:
    b = _seed(acm)
    await anyio.to_thread.run_sync(b.mark_ready, ADMIN, P, "US-01.01")
    token = acm.token(ADMIN)
    async with ws(acm, token) as (ui_1, _), ws(acm, token) as (ui_2, _):
        async with mcp(acm, acm.token(ADMIN)) as agent:
            res = await agent.call_tool(
                "acm_story_set_status", {"project_id": P, "story_id": "US-01.01", "status": "IN_PROGRESS"}
            )
            assert not res.is_error, res.content
        for conn in (ui_1, ui_2):
            [event] = await _events(conn, 1, types=("story.status_changed",))
            assert event["entity_id"] == "US-01.01" and event["data"]["status"] == "IN_PROGRESS"


@pytest.mark.anyio
async def test_us0603_agente_por_stdio_en_otro_proceso(acm: Acm) -> None:
    b = _seed(acm)
    await anyio.to_thread.run_sync(b.mark_ready, ADMIN, P, "US-01.02")
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "acm", "mcp-stdio", "--data-dir", str(acm.data_dir)]
    )
    async with ws(acm, acm.token(ADMIN)) as (ui, _):
        async with Client(params) as agent:  # otro proceso, misma base: ADR-018
            res = await agent.call_tool(
                "acm_story_set_status", {"project_id": P, "story_id": "US-01.02", "status": "IN_PROGRESS"}
            )
            assert not res.is_error, res.content
        [event] = await _events(conn := ui, 1, types=("story.status_changed",))
    assert conn and event["entity_id"] == "US-01.02" and event["data"]["status"] == "IN_PROGRESS"


@pytest.mark.anyio
async def test_us0603_ca04_evento_duplicado_no_modifica_dos_veces(acm: Acm) -> None:
    b = _seed(acm)
    _ready_in_progress(b, P, "US-01.01")
    with _http(acm, acm.token(ADMIN)) as http:
        again = http.post(f"/projects/{P}/stories/US-01.01/status", json={"status": "IN_PROGRESS"})
    assert again.status_code == 409 and "ya está en IN_PROGRESS" in again.json()["error"]["message"]
    assert len(b.status_history(ADMIN, P, "US-01.01")["history"]) == 2
    seqs = [e["seq"] for e in acm.service.events.after(0)]
    assert seqs == sorted(set(seqs))  # cada evento tiene un seq único y creciente: el cliente descarta repetidos


@pytest.mark.anyio
async def test_us2102_ca01_ca02_solo_proyectos_autorizados(acm: Acm) -> None:
    alpha = _seed(acm, P)
    beta = _seed(acm, "beta", stories=1)
    acm.identity.create_principal(ADMIN, "ana", "user")
    acm.identity.set_member(ADMIN, P, "ana", "member")
    async with ws(acm, acm.token("ana")) as (conn, _):
        await anyio.to_thread.run_sync(beta.mark_ready, ADMIN, "beta", "US-01.01")
        await anyio.to_thread.run_sync(alpha.mark_ready, ADMIN, P, "US-01.01")
        received = await _silence(conn, 1.5)
    assert [(e["project_id"], e["entity_id"]) for e in received] == [(P, "US-01.01")]


@pytest.mark.anyio
async def test_us2102_actividad_solo_para_admin(acm: Acm) -> None:
    _seed(acm, P)
    acm.identity.create_principal(ADMIN, "ana", "user")
    acm.identity.set_member(ADMIN, P, "ana", "member")
    async with ws(acm, acm.token("ana")) as (ana, _), ws(acm, acm.token(ADMIN)) as (admin, _):
        async with mcp(acm, acm.token(ADMIN)) as agent:
            await agent.call_tool("acm_backlog_audit", {"project_id": P})
        [activity] = await _events(admin, 1, types=("activity",))
        assert activity["entity_id"] == "acm_backlog_audit" and activity["data"]["status"] == "ok"
        assert await _silence(ana, 1.0, types=("activity",)) == []


@pytest.mark.anyio
async def test_us2102_ca03_desconexion_libera_la_suscripcion(acm: Acm) -> None:
    token = acm.token(ADMIN)
    with _http(acm, token) as http:
        async with ws(acm, token):
            assert (await anyio.to_thread.run_sync(lambda: http.get("/meta").json()))["active_subscriptions"] == 1
        with anyio.fail_after(5):
            while (await anyio.to_thread.run_sync(lambda: http.get("/meta").json()))["active_subscriptions"] != 0:
                await anyio.sleep(0.1)


@pytest.mark.anyio
@pytest.mark.parametrize("hello", [{"type": "auth", "token": "acm_falso"}, {"type": "hola"}, {"type": "auth"}])
async def test_us2102_ws_exige_autenticacion(acm: Acm, hello: dict) -> None:
    async with connect(acm.url.replace("http", "ws") + "/api/v1/ws") as conn:
        await conn.send(json.dumps(hello))
        msg = json.loads(await conn.recv())
        assert msg["type"] == "error" and "UNAUTHENTICATED" in msg["error"]
        with pytest.raises(ConnectionClosed) as closed:
            await conn.recv()
    assert closed.value.rcvd.code == 4401


# ---------------------------------------------------------------- US-21.03 — reanudar tras reconexión
@pytest.mark.anyio
async def test_us2103_ca01_ca02_ca03_ca04_reanuda_sin_perder_ni_duplicar(acm: Acm) -> None:
    b = _seed(acm, stories=3)
    token = acm.token(ADMIN)
    async with ws(acm, token) as (_conn, ready):
        last_seen = ready["seq"]
    # Desconectado: ocurren cambios que el cliente no ve.
    for sid in ("US-01.01", "US-01.02", "US-01.03"):
        b.mark_ready(ADMIN, P, sid)
    b.set_status(ADMIN, P, "US-01.02", "IN_PROGRESS")
    async with ws(acm, token, after=last_seen) as (conn, ready):
        assert ready["seq"] == last_seen
        missed = await _events(conn, 4, types=DOMAIN)
    assert [e["seq"] for e in missed] == sorted({e["seq"] for e in missed}) and missed[0]["seq"] > last_seen
    # Estado final reconstruido con los eventos = estado del servidor.
    state = {c["id"]: c["status"] for c in _http(acm, token).get("/kanban").json()["cards"]}
    replayed = {"US-01.01": "PLANNED", "US-01.02": "PLANNED", "US-01.03": "PLANNED"}
    for e in missed:
        replayed[e["entity_id"]] = e["data"]["status"]
    assert replayed == state


@pytest.mark.anyio
async def test_us2103_resync_si_los_eventos_ya_no_estan(acm: Acm) -> None:
    b = _seed(acm, stories=3)
    for sid in ("US-01.01", "US-01.02", "US-01.03"):
        b.mark_ready(ADMIN, P, sid)
    acm.service.events.prune(keep=1)
    async with connect(acm.url.replace("http", "ws") + "/api/v1/ws") as conn:
        await conn.send(json.dumps({"type": "auth", "token": acm.token(ADMIN), "after": 1}))
        first = json.loads(await conn.recv())
    assert first["type"] == "resync"


def test_us2103_eventos_por_rest(acm: Acm) -> None:
    b = _seed(acm)
    seq = acm.service.events.latest_seq()
    b.mark_ready(ADMIN, P, "US-01.01")
    with _http(acm, acm.token(ADMIN)) as http:
        events = http.get("/events", params={"after": seq}).json()["events"]
    assert [(e["type"], e["entity_id"]) for e in events] == [("story.status_changed", "US-01.01")]


# ---------------------------------------------------------------- US-30.01..03 — API REST v1
ENDPOINTS = {
    ("get", "/me"),
    ("get", "/meta"),
    ("get", "/projects"),
    ("get", "/projects/{project_id}"),
    ("get", "/projects/{project_id}/backlog"),
    ("get", "/projects/{project_id}/stories/{story_id}"),
    ("post", "/projects/{project_id}/stories/{story_id}/status"),
    ("post", "/projects/{project_id}/stories/{story_id}/ready"),
    ("get", "/projects/{project_id}/requirements/{requirement_id}/trace"),
    ("get", "/projects/{project_id}/context/{story_id}"),
    ("get", "/projects/{project_id}/members"),
    ("get", "/projects/{project_id}/config"),
    ("get", "/projects/{project_id}/governance"),
    ("post", "/projects/{project_id}/watchdog"),
    ("get", "/kanban"),
    ("get", "/activity"),
    ("get", "/events"),
    ("get", "/health"),
    ("get", "/engines"),
    ("get", "/savings"),
    ("get", "/skills"),
    ("get", "/skills/{name}"),
    ("get", "/principals"),
    ("get", "/tokens"),
}


def test_us3001_ca01_us3002_contrato_documentado(acm: Acm) -> None:
    with _http(acm, acm.token(ADMIN)) as http:
        spec = http.get("/openapi.json").json()
    documented = {(m, path) for path, ops in spec["paths"].items() for m in ops}
    assert documented == ENDPOINTS
    status_op = spec["paths"]["/projects/{project_id}/stories/{story_id}/status"]["post"]
    assert "requestBody" in status_op and "200" in status_op["responses"]
    for path, ops in spec["paths"].items():
        for op in ops.values():
            assert {"400", "401", "403", "404", "409"} <= set(op["responses"]), path


def test_us3001_ca02_ca04_entradas_invalidas_formato_consistente(acm: Acm) -> None:
    _seed(acm)
    with _http(acm, acm.token(ADMIN)) as http:
        responses = [
            http.post(f"/projects/{P}/stories/US-01.01/status", json={"status": "HECHO"}),
            http.post(f"/projects/{P}/stories/US-01.01/status", json={"estado": "READY"}),
            http.post(f"/projects/{P}/stories/US-01.01/status", content=b"{no es json"),
            http.get("/projects/NoValido"),
            http.post(f"/projects/{P}/stories/US-01.01/status", json={"status": "DONE"}),
        ]
    assert [r.status_code for r in responses] == [400, 400, 400, 400, 409]
    for r in responses:
        body = r.json()
        assert set(body) == {"error"} and set(body["error"]) == {"code", "message", "field"}


def test_us3001_ca03_autorizacion_aplicada(acm: Acm) -> None:
    _seed(acm)
    acm.identity.create_principal(ADMIN, "ana", "user")
    with _http(acm, None) as anon, _http(acm, acm.token("ana")) as ana:
        assert anon.get("/projects").status_code == 401
        assert ana.get("/health").status_code == 403
        assert ana.get(f"/projects/{P}/backlog").status_code == 404
        assert ana.post(f"/projects/{P}/stories/US-01.01/ready").status_code == 404
    assert acm.service.list_for(ADMIN)[0]["project_id"] == P


def test_us3003_ca01_ca02_ca03_version_en_la_ruta(acm: Acm) -> None:
    with _http(acm, acm.token(ADMIN)) as http:
        meta = http.get("/meta").json()
        spec = http.get("/openapi.json").json()
    assert meta["acm_version"] == spec["info"]["version"]
    assert httpx.get(f"{acm.url}/api/health").status_code == 200  # ruta pública previa, sin versionar (política)
    assert httpx.get(f"{acm.url}/api/v2/projects").status_code == 404


def test_us3001_lectura_completa_del_proyecto(acm: Acm) -> None:
    b = _seed(acm)
    b.mark_ready(ADMIN, P, "US-01.01")
    with _http(acm, acm.token(ADMIN)) as http:
        backlog = http.get(f"/projects/{P}/backlog").json()
        story = http.get(f"/projects/{P}/stories/US-01.01").json()
        portfolio = http.get("/projects").json()["projects"][0]
        skills = http.get("/skills").json()
        schema_doc = http.get("/skills/acm-schema").json()
    assert [r["id"] for r in backlog["requirements"]] == ["REQ-001"] and len(backlog["stories"]) == 2
    assert backlog["epics"][0]["features"][0]["story_ids"] == ["US-01.01", "US-01.02"]
    assert story["acceptance_criteria"][0]["text"] == "CA" and story["allowed_transitions"] == [
        "IN_PROGRESS",
        "PLANNED",
        "CANCELLED",
    ]
    assert [h["to_status"] for h in story["history"]] == ["READY"]
    assert portfolio["stories_by_status"]["READY"] == 1 and portfolio["governance"]["semaphore"] == "UNKNOWN"
    assert {s["frontmatter"]["name"] for s in skills["skills"]} >= {"acm-schema"}
    assert schema_doc["files"]["SKILL.md"].startswith("---")
