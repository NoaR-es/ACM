"""SPRINT-009 — conexión universal de agentes (US-14.12, US-14.13) con procesos reales.

Cada agente es un proceso `acm mcp-stdio` distinto, como lo arrancaría Claude Code, Cursor, Codex, Antigravity o
Hermes con la entrada estándar de su configuración. La interfaz local es un proceso `acm serve --local` real.
"""

from __future__ import annotations

import socket
import sys
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest
from mcp import Client, StdioServerParameters
from mcp_types import Implementation

from acm.config import Settings, default_data_dir
from acm.domain.access import AccessService
from acm.domain.backlog import BacklogService
from acm.domain.projects import ProjectService
from acm.local import is_local_request, port_in_use, start_local_ui, stop_local_ui
from acm.sessions import agent_principal
from tests.conftest import ADMIN
from tests.fake_ollama import free_port

HOST = socket.gethostname().split(".")[0].lower()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@asynccontextmanager
async def agent(data_dir: Path, client: str, **env: str) -> AsyncIterator[Client]:
    """Un agente real: proceso stdio con la entrada estándar de ACM, sin interfaz en segundo plano."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "acm", "mcp-stdio", "--data-dir", str(data_dir)],
        env={"ACM_UI": "0", **env},
    )
    async with Client(params, client_info=Implementation(name=client, version="1.0")) as c:
        yield c


def _data(result) -> dict:
    assert not result.is_error, result.content
    return result.structured_content


# ---------------------------------------------------------------- US-14.12 — una entrada estándar
def test_us1412_ca02_un_unico_estado_por_usuario(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("ACM_DATA_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert Settings.from_env().data_dir == default_data_dir() == tmp_path / ".acm"  # no depende de la carpeta actual
    monkeypatch.setenv("ACM_DATA_DIR", str(tmp_path / "otro"))
    assert Settings.from_env().data_dir == tmp_path / "otro"


def test_us1412_ca03_identidad_valida_y_distinta_por_cliente_y_equipo() -> None:
    from acm.domain.identity import PRINCIPAL_RE

    names = {agent_principal(c, "Mi Portátil") for c in ("claude-code", "Cursor", "codex_cli", "Antigravity", None)}
    assert len(names) == 5 and all(PRINCIPAL_RE.match(n) for n in names)
    assert agent_principal("Claude Code", "portatil") == "claude-code.portatil"
    assert agent_principal("claude-code", "pc-oficina") != agent_principal("claude-code", "portatil")
    assert PRINCIPAL_RE.match(agent_principal("x" * 200, "y" * 200))  # nunca excede el límite del identificador


@pytest.mark.anyio
async def test_us1412_ca03_cada_cliente_es_un_agente_con_su_nombre(data_dir: Path) -> None:
    async with (
        agent(data_dir, "claude-code") as a,
        agent(data_dir, "Cursor") as b,
        agent(data_dir, "codex", ACM_AGENT="Back End") as c,
    ):
        assert _data(await a.call_tool("acm_whoami", {}))["id"] == f"claude-code.{HOST}"
        assert _data(await b.call_tool("acm_whoami", {}))["id"] == f"cursor.{HOST}"
        who = _data(await c.call_tool("acm_whoami", {}))
        assert who["id"] == "back-end"  # ACM_AGENT fija el nombre
        assert who["kind"] == "agent" and who["role"] == "user"  # nunca admin: no gestiona accesos
    svc = ProjectService(data_dir)
    kinds = {p["id"]: p["kind"] for p in IdentityKinds.rows(svc)}
    assert kinds[f"claude-code.{HOST}"] == "agent" and kinds[ADMIN] == "user"
    svc.close()


class IdentityKinds:
    @staticmethod
    def rows(svc: ProjectService) -> list[dict]:
        with svc.global_db.read() as conn:
            return [dict(r) for r in conn.execute("SELECT id, role, kind FROM principals")]


@pytest.mark.anyio
async def test_us1412_ca01_flujo_completo_sin_pasos_previos(data_dir: Path) -> None:
    """Lo único que se hizo es lanzar el proceso: el agente crea, la persona aprueba y el otro agente entra."""
    async with agent(data_dir, "claude-code") as a:
        _data(await a.call_tool("acm_project_create", {"key": "reservas", "name": "Reservas"}))  # sin ser admin
        _data(await a.call_tool("acm_requirement_create", {"project_id": "reservas", "title": "Reservar mesa"}))
        async with agent(data_dir, "cursor") as b:
            directory = _data(await b.call_tool("acm_project_directory", {}))
            assert [(p["project_id"], p["your_role"]) for p in directory["projects"]] == [("reservas", None)]
            blocked = await b.call_tool("acm_requirement_list", {"project_id": "reservas"})
            assert blocked.is_error and "NOT_FOUND" in blocked.content[0].text
            joined = _data(
                await b.call_tool("acm_project_join", {"project_id": "reservas", "message": "ayudo en la UI"})
            )
            assert joined["status"] == "PENDING"
            svc = ProjectService(data_dir)  # la persona aprueba en la interfaz (aquí, el servicio que esta usa)
            AccessService(svc).decide(ADMIN, joined["request_id"], True)
            svc.close()
            listed = _data(await b.call_tool("acm_requirement_list", {"project_id": "reservas"}))
            assert [r["title"] for r in listed["requirements"]] == ["Reservar mesa"]


@pytest.mark.anyio
async def test_us1412_ca03_dos_sesiones_del_mismo_cliente_no_se_pisan(data_dir: Path) -> None:
    """Mismo cliente, mismo equipo: un solo principal, pero cada conexión es su propia sesión de trabajo."""
    svc = ProjectService(data_dir, local_mode=True)
    svc.ensure_principal(ADMIN, "admin")
    me = f"claude-code.{HOST}"
    svc.ensure_principal(me, "user", "agent")
    svc.create(ADMIN, "alpha", "Alpha")
    from acm.domain.identity import IdentityService

    IdentityService(svc).set_member(ADMIN, "alpha", me, "member")
    b = BacklogService(svc)
    b.create_requirement(ADMIN, "alpha", "Requisito")
    b.create_epic(ADMIN, "alpha", "Épica", "Objetivo", "Alcance", ["REQ-001"])
    b.create_feature(ADMIN, "alpha", "EPIC-01", "Feature")
    for i in (1, 2):
        b.create_story(ADMIN, "alpha", "FEAT-01.01", "operador", f"hacer {i}", "avanzar", ["REQ-001"], [f"CA {i}"])
    svc.close()
    async with agent(data_dir, "claude-code") as s1, agent(data_dir, "claude-code") as s2:
        assert _data(await s1.call_tool("acm_whoami", {}))["id"] == _data(await s2.call_tool("acm_whoami", {}))["id"]
        w1 = _data(await s1.call_tool("acm_next_work", {"project_id": "alpha"}))
        w2 = _data(await s2.call_tool("acm_next_work", {"project_id": "alpha"}))
        assert (w1["action"], w1["item"]) == ("refine", "US-01.01")
        assert (w2["action"], w2["item"]) == ("refine", "US-01.02")  # ACM no da lo mismo a las dos sesiones
        assert w2["others_working"][0]["agent"].startswith(f"{me}#")
        listed = _data(await s1.call_tool("acm_work_list", {"project_id": "alpha"}))
        assert len({c["agent"] for c in listed["claims"]}) == 2  # dos agentes distintos en el reparto
        denied = await s2.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "x"})
        assert not denied.is_error  # trabajar en el proyecto sigue permitido: solo se protegen las historias asignadas
        grab = await s2.call_tool(
            "acm_story_add_criteria", {"project_id": "alpha", "story_id": "US-01.01", "criteria": ["c"]}
        )
        assert grab.is_error and "asignada a" in grab.content[0].text


@pytest.mark.anyio
async def test_us1412_ca03_acm_principal_conserva_la_identidad_admin_unica(data_dir: Path) -> None:
    async with agent(data_dir, "claude-code", ACM_PRINCIPAL=ADMIN) as legacy:
        who = _data(await legacy.call_tool("acm_whoami", {}))
        assert who["id"] == ADMIN and who["role"] == "admin"


# ---------------------------------------------------------------- US-14.12 CA-04 — la interfaz local, sin token
def test_us1412_ca04_solo_peticiones_locales_con_la_cabecera_de_la_interfaz() -> None:
    assert is_local_request("127.0.0.1", "127.0.0.1:8765", "1")
    assert is_local_request("::1", "[::1]:8765", "1") and is_local_request("127.0.0.1", "localhost", "1")
    assert not is_local_request("127.0.0.1", "127.0.0.1:8765", None)  # sin la cabecera: una web ajena no puede
    assert not is_local_request("127.0.0.1", "127.0.0.1:8765", "0")
    assert not is_local_request("192.168.1.20", "127.0.0.1:8765", "1")  # otro equipo de la red
    assert not is_local_request("127.0.0.1", "evil.example.com", "1")  # DNS rebinding
    assert not is_local_request(None, "localhost:8765", "1")


@pytest.fixture
def daemon(tmp_path: Path) -> Iterator[Settings]:
    """La interfaz local como la arranca un agente: proceso aparte que sobrevive a quien lo lanzó."""
    settings = Settings.from_env(data_dir=tmp_path / "data", port=free_port())
    assert start_local_ui(settings) is True
    deadline = time.monotonic() + 20
    while not port_in_use("127.0.0.1", settings.port):
        assert time.monotonic() < deadline, "la interfaz local no arrancó"
        time.sleep(0.1)
    yield settings
    stop_local_ui(settings)


def test_us1412_ca04_interfaz_local_en_segundo_plano_sin_token(daemon: Settings) -> None:
    base = f"http://127.0.0.1:{daemon.port}"
    assert start_local_ui(daemon) is False  # ya hay una: no se lanza otra
    assert httpx.get(f"{base}/api/local-session").status_code == 404  # sin la cabecera de la interfaz
    session = httpx.get(f"{base}/api/local-session", headers={"X-ACM-Local": "1"})
    assert session.status_code == 200 and session.headers["cache-control"] == "no-store"
    token = session.json()["token"]
    me = httpx.get(f"{base}/api/v1/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["id"] == ADMIN and me["role"] == "admin" and me["kind"] == "user"
    assert httpx.get(f"{base}/api/v1/me").status_code == 401  # sin token, la API sigue cerrada
    assert httpx.get(f"{base}/api/v1/me", headers={"Host": "evil.example.com"}).status_code in (401, 421)
    evil = httpx.get(f"{base}/api/local-session", headers={"X-ACM-Local": "1", "Host": "evil.example.com"})
    assert evil.status_code == 404  # DNS rebinding: otro nombre de servidor no recibe el token


def test_us1412_ca04_la_interfaz_sobrevive_y_se_para_con_acm_stop(tmp_path: Path) -> None:
    settings = Settings.from_env(data_dir=tmp_path / "data", port=free_port())
    assert "No hay ninguna" in stop_local_ui(settings)
    start_local_ui(settings)
    deadline = time.monotonic() + 20
    while not port_in_use("127.0.0.1", settings.port):
        assert time.monotonic() < deadline
        time.sleep(0.1)
    assert "parada" in stop_local_ui(settings)
    deadline = time.monotonic() + 10
    while port_in_use("127.0.0.1", settings.port):
        assert time.monotonic() < deadline, "la interfaz no se paró"
        time.sleep(0.1)


def test_us1412_ca04_el_supervisor_trabaja_en_segundo_plano(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin que nadie lo pida, el proceso en segundo plano audita los proyectos y el supervisor deja su informe."""
    monkeypatch.setenv("ACM_WATCHDOG_INTERVAL_S", "1")
    data_dir = tmp_path / "data"
    svc = ProjectService(data_dir, local_mode=True)
    svc.ensure_principal(ADMIN, "admin")
    svc.create(ADMIN, "alpha", "Alpha")
    svc.close()
    settings = Settings.from_env(data_dir=data_dir, port=free_port())
    assert start_local_ui(settings) is True
    try:
        base = f"http://127.0.0.1:{settings.port}"
        deadline = time.monotonic() + 30
        token = None
        while token is None:
            assert time.monotonic() < deadline, "la interfaz local no arrancó"
            try:
                reply = httpx.get(f"{base}/api/local-session", headers={"X-ACM-Local": "1"})
                token = reply.json()["token"] if reply.status_code == 200 else None
            except httpx.TransportError:
                time.sleep(0.2)
        headers = {"Authorization": f"Bearer {token}"}
        run = None
        while run is None:
            assert time.monotonic() < deadline, "el supervisor no ejecutó ninguna ronda"
            history = httpx.get(f"{base}/api/v1/projects/alpha/governance", headers=headers).json()
            run = history.get("last_run")
            time.sleep(0.3)
        assert run["semaphore"] in ("GREEN", "YELLOW", "RED") and run["trigger"] == "scheduled"  # la ronda periódica
        assert history["integrity"]["integrity_status"] == "ok"
    finally:
        stop_local_ui(settings)
