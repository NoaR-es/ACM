"""EPIC-20: US-20.01 (roles), US-20.02 (autorizar), US-20.03 (tokens), US-20.04 (credenciales por principal),
US-20.05 (autenticar cada conexión MCP), US-20.08 (acceso por proyecto). ACM real por HTTP (uvicorn en un hilo)."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn
from mcp.shared.exceptions import MCPError

from acm.app import build_service, create_app
from acm.config import Settings
from acm.domain.audit import REDACTED
from acm.domain.errors import FailedPrecondition, Forbidden, InvalidArgument, NotFound, Unauthenticated
from acm.domain.identity import IdentityService
from acm.domain.projects import ProjectService
from tests.fake_ollama import free_port
from tests.live import ADMIN, Acm, mcp


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _post_mcp(acm: Acm, headers: dict[str, str]) -> httpx.Response:
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "acm_project_create", "arguments": {"key": "intruso", "name": "X"}},
    }
    async with httpx.AsyncClient() as http:
        return await http.post(
            f"{acm.url}/mcp/", json=body, headers={"Accept": "application/json, text/event-stream", **headers}
        )


def _agent(acm: Acm, principal: str = "agente-a", project: str | None = "alpha", role: str = "member") -> str:
    acm.identity.create_principal(ADMIN, principal, "agent")
    if project:
        acm.identity.set_member(ADMIN, project, principal, role)
    return acm.token(principal)


def _text(result) -> str:
    return result.content[0].text if result.content else ""


# ---------------------------------------------------------------- US-20.05 — autenticar cada conexión MCP
@pytest.mark.anyio
@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Basic YWRtaW46YWRtaW4="}, {"Authorization": "Bearer no-es-de-acm"}]
)
async def test_us2005_ca01_sin_token_401_sin_efectos(acm: Acm, headers: dict[str, str]) -> None:
    resp = await _post_mcp(acm, headers)
    assert resp.status_code == 401 and resp.headers["www-authenticate"] == 'Bearer realm="acm"'
    assert resp.json()["error"].startswith("UNAUTHENTICATED")
    assert acm.service.list_for(ADMIN) == []  # la herramienta no llegó a ejecutarse


@pytest.mark.anyio
async def test_us2005_ca02_token_desconocido_rechazado_y_auditado(acm: Acm) -> None:
    fake = "acm_" + "x" * 43
    resp = await _post_mcp(acm, {"Authorization": f"Bearer {fake}"})
    assert resp.status_code == 401 and "token desconocido" in resp.json()["error"]
    entry = acm.audit(operation="http:auth")[-1]
    assert entry["principal"] == "(anonymous)" and entry["status"] == "error"
    assert json.loads(entry["arguments_json"])["token_prefix"] == fake[:12]
    assert fake not in json.dumps(acm.audit())  # nunca se guarda el token completo


@pytest.mark.anyio
async def test_us2005_ca03_cada_peticion_con_su_identidad(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    tokens = {"agente-a": _agent(acm, "agente-a"), "agente-b": _agent(acm, "agente-b"), ADMIN: acm.token(ADMIN)}
    async with mcp(acm, tokens["agente-a"]) as a, mcp(acm, tokens["agente-b"]) as b, mcp(acm, tokens[ADMIN]) as adm:
        for _ in range(3):
            for who, client in (("agente-a", a), ("agente-b", b), (ADMIN, adm)):
                me = (await client.call_tool("acm_whoami", {})).structured_content
                assert me["id"] == who


# ---------------------------------------------------------------- US-20.03 — tokens
@pytest.mark.anyio
async def test_us2003_ca01_token_con_identidad_y_permisos(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    acm.service.create(ADMIN, "beta", "Beta")
    async with mcp(acm, _agent(acm)) as agent:
        me = (await agent.call_tool("acm_whoami", {})).structured_content
        assert (me["id"], me["kind"], me["role"]) == ("agente-a", "agent", "user")
        assert me["projects"] == [{"project_id": "alpha", "role": "member"}]
        ok = await agent.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "R"})
        foreign = await agent.call_tool("acm_requirement_create", {"project_id": "beta", "title": "R"})
        admin_only = await agent.call_tool("acm_project_create", {"key": "gamma", "name": "G"})
    assert not ok.is_error
    assert foreign.is_error and "NOT_FOUND" in _text(foreign)
    assert admin_only.is_error and "FORBIDDEN" in _text(admin_only)


@pytest.mark.anyio
async def test_us2003_ca02_revocado_deja_de_autorizar_al_instante(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    token = _agent(acm)
    token_id = acm.identity.list_tokens(ADMIN, "agente-a")["tokens"][0]["token_id"]
    async with mcp(acm, token) as agent:
        assert not (await agent.call_tool("acm_whoami", {})).is_error
        acm.identity.revoke_token(ADMIN, token_id)
        with pytest.raises(MCPError):  # la misma conexión recibe 401 en la siguiente petición
            await agent.call_tool("acm_whoami", {})
    resp = await _post_mcp(acm, {"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401 and f"{token_id} está revocado" in resp.json()["error"]


def test_us2003_ca03_token_no_se_muestra_completo(acm: Acm) -> None:
    created = acm.identity.create_token(ADMIN, ADMIN, "ci")
    secret = created["token"]
    assert secret.startswith("acm_") and len(secret) > 40 and created["prefix"] == secret[:12]
    listed = acm.identity.list_tokens(ADMIN)["tokens"][0]
    assert "token" not in listed and listed["prefix"] == secret[:12]
    raw = b"".join(p.read_bytes() for p in acm.data_dir.glob("acm.db*"))
    assert secret.encode() not in raw  # solo se guarda el hash


@pytest.mark.anyio
async def test_us2003_ca03_secreto_redactado_en_la_auditoria(acm: Acm) -> None:
    async with mcp(acm, acm.token(ADMIN)) as admin:
        await admin.call_tool("acm_principal_create", {"principal_id": "agente-z", "kind": "agent"})
        created = (
            await admin.call_tool("acm_token_create", {"principal_id": "agente-z", "name": "z"})
        ).structured_content
    entry = acm.audit(operation="acm_token_create")[-1]
    assert json.loads(entry["result_json"])["token"] == REDACTED
    assert created["token"] not in json.dumps(acm.audit())


@pytest.mark.anyio
async def test_us2003_ca04_uso_trazado(acm: Acm) -> None:
    token = acm.token(ADMIN)
    token_id = acm.identity.list_tokens(ADMIN)["tokens"][0]["token_id"]
    async with mcp(acm, token) as admin:
        await admin.call_tool("acm_project_create", {"key": "alpha", "name": "Alpha"})
        await admin.call_tool("acm_project_list", {})
    info = acm.identity.list_tokens(ADMIN)["tokens"][0]
    assert info["use_count"] >= 2 and info["last_used_at"]
    ops = {e["operation"]: e for e in acm.audit(token_id=token_id)}
    assert {"acm_project_create", "acm_project_list"} <= set(ops)


def test_us2003_solo_admin_crea_tokens_ajenos(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "bob", "user")
    acm.identity.create_principal(ADMIN, "eve", "user")
    with pytest.raises(Forbidden):
        acm.identity.create_token("bob", "eve", "robo")
    eve = acm.identity.create_token(ADMIN, "eve", "e")
    with pytest.raises(Forbidden):
        acm.identity.revoke_token("bob", eve["token_id"])
    assert acm.identity.revoke_token("eve", eve["token_id"])["active"] is False  # cada uno revoca los suyos


# ---------------------------------------------------------------- US-20.04 — credenciales independientes
def test_us2004_ca01_usuarios_y_agentes(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "ana", "user")
    acm.identity.create_principal(ADMIN, "bot-1", "agent")
    kinds = {p["id"]: p["kind"] for p in acm.identity.list_principals(ADMIN)["principals"]}
    assert kinds == {ADMIN: "user", "ana": "user", "bot-1": "agent"}
    with pytest.raises(InvalidArgument, match="kind"):
        acm.identity.create_principal(ADMIN, "raro", "robot")


def test_us2004_ca02_credenciales_por_principal(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "bot-1", "agent")
    acm.identity.create_principal(ADMIN, "bot-2", "agent")
    t1, t2 = acm.identity.create_token(ADMIN, "bot-1", "a"), acm.identity.create_token(ADMIN, "bot-2", "b")
    assert acm.identity.authenticate(t1["token"]) == ("bot-1", t1["token_id"])
    acm.identity.revoke_token(ADMIN, t1["token_id"])
    with pytest.raises(Unauthenticated):
        acm.identity.authenticate(t1["token"])
    assert acm.identity.authenticate(t2["token"])[0] == "bot-2"  # revocar a uno no afecta a otro


@pytest.mark.anyio
async def test_us2004_ca03_auditoria_distingue_principal(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    async with mcp(acm, _agent(acm, "bot-1")) as b1, mcp(acm, _agent(acm, "bot-2")) as b2:
        await b1.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "de bot-1"})
        await b2.call_tool("acm_requirement_create", {"project_id": "alpha", "title": "de bot-2"})
    who = [e["principal"] for e in acm.audit(operation="acm_requirement_create")]
    assert who == ["bot-1", "bot-2"]


# ---------------------------------------------------------------- US-20.01 — roles
def test_us2001_ca01_roles_definidos(acm: Acm) -> None:
    assert acm.identity.list_principals(ADMIN)["roles"] == {"global": ["admin", "user"], "project": ["owner", "member"]}


def test_us2001_ca02_asignar_rol_autorizado(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    acm.identity.create_principal(ADMIN, "ana", "user")
    assert acm.identity.set_global_role(ADMIN, "ana", "admin")["role"] == "admin"
    members = acm.identity.set_member(ADMIN, "alpha", "ana", "owner")["members"]
    assert {"principal_id": "ana", "role": "owner"} in [{k: m[k] for k in ("principal_id", "role")} for m in members]
    for call in (
        lambda: acm.identity.set_global_role(ADMIN, "ana", "root"),
        lambda: acm.identity.set_member(ADMIN, "alpha", "ana", "jefe"),
    ):
        with pytest.raises(InvalidArgument, match="role"):
            call()


def test_us2001_ca03_permisos_inmediatos(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    acm.identity.create_principal(ADMIN, "ana", "user")
    with pytest.raises(NotFound):
        acm.service.open("ana", "alpha")
    acm.identity.set_member(ADMIN, "alpha", "ana", "member")
    assert acm.service.open("ana", "alpha")["role"] == "member"
    acm.identity.remove_member(ADMIN, "alpha", "ana")
    with pytest.raises(NotFound):
        acm.service.open("ana", "alpha")
    with pytest.raises(Forbidden):
        acm.service.create("ana", "beta", "Beta")
    acm.identity.set_global_role(ADMIN, "ana", "admin")
    assert acm.service.create("ana", "beta", "Beta")["project_id"] == "beta"


@pytest.mark.anyio
async def test_us2001_ca04_cambios_auditados(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    async with mcp(acm, acm.token(ADMIN)) as admin:
        await admin.call_tool("acm_principal_create", {"principal_id": "ana", "kind": "user"})
        await admin.call_tool("acm_principal_set_role", {"principal_id": "ana", "role": "admin"})
        await admin.call_tool("acm_member_set", {"project_id": "alpha", "principal_id": "ana", "role": "owner"})
        await admin.call_tool("acm_member_remove", {"project_id": "alpha", "principal_id": "ana"})
    entries = {e["operation"]: json.loads(e["arguments_json"]) for e in acm.audit(principal=ADMIN)}
    assert entries["acm_principal_set_role"] == {"principal_id": "ana", "role": "admin"}
    assert entries["acm_member_set"] == {"project_id": "alpha", "principal_id": "ana", "role": "owner"}
    assert entries["acm_member_remove"] == {"project_id": "alpha", "principal_id": "ana"}


def test_us2001_nunca_sin_admin_ni_owner(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    with pytest.raises(FailedPrecondition, match="último admin"):
        acm.identity.set_global_role(ADMIN, ADMIN, "user")
    with pytest.raises(FailedPrecondition, match="sin owner"):
        acm.identity.remove_member(ADMIN, "alpha", ADMIN)
    with pytest.raises(FailedPrecondition, match="sin owner"):
        acm.identity.set_member(ADMIN, "alpha", ADMIN, "member")


# ---------------------------------------------------------------- US-20.02 — autorizar operaciones
@pytest.mark.anyio
async def test_us2002_ca01_ca02_ca03_permitida_se_ejecuta_denegada_sin_efectos(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    acm.identity.create_principal(ADMIN, "intruso", "user")
    async with mcp(acm, _agent(acm)) as member:
        allowed = await member.call_tool("acm_member_list", {"project_id": "alpha"})
        denied = await member.call_tool(
            "acm_member_set", {"project_id": "alpha", "principal_id": "intruso", "role": "owner"}
        )
        denied_admin = await member.call_tool("acm_principal_set_role", {"principal_id": "agente-a", "role": "admin"})
    assert not allowed.is_error
    assert denied.is_error and "FORBIDDEN" in _text(denied)
    assert denied_admin.is_error and "FORBIDDEN" in _text(denied_admin)
    members = {m["principal_id"]: m["role"] for m in acm.identity.list_members(ADMIN, "alpha")["members"]}
    assert members == {ADMIN: "owner", "agente-a": "member"}  # el rechazo no modificó nada
    assert acm.identity.get_principal(ADMIN, "agente-a")["role"] == "user"


@pytest.mark.anyio
async def test_us2002_ca04_intento_registrado(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    async with mcp(acm, _agent(acm)) as member:
        await member.call_tool("acm_principal_set_role", {"principal_id": "agente-a", "role": "admin"})
    entry = acm.audit(principal="agente-a", operation="acm_principal_set_role")[-1]
    assert entry["status"] == "error" and entry["error"].startswith("FORBIDDEN") and entry["token_id"]


def test_us2002_owner_gestiona_miembros_member_no(acm: Acm) -> None:
    acm.service.create(ADMIN, "alpha", "Alpha")
    for p in ("ana", "luis", "eva"):
        acm.identity.create_principal(ADMIN, p, "user")
    acm.identity.set_member(ADMIN, "alpha", "ana", "owner")
    acm.identity.set_member(ADMIN, "alpha", "luis", "member")
    acm.identity.set_member("ana", "alpha", "eva", "member")  # owner puede
    with pytest.raises(Forbidden):
        acm.identity.set_member("luis", "alpha", "eva", "owner")  # member no


# ---------------------------------------------------------------- US-20.08 — acceso por proyecto
@pytest.mark.anyio
async def test_us2008_ca01_ca02_solo_proyectos_propios(acm: Acm) -> None:
    for key in ("alpha", "beta"):
        acm.service.create(ADMIN, key, key)
    async with mcp(acm, _agent(acm, project="alpha")) as agent:
        listed = (await agent.call_tool("acm_project_list", {})).structured_content["result"]
        other = await agent.call_tool("acm_member_list", {"project_id": "beta"})
    assert [p["project_id"] for p in listed] == ["alpha"]
    assert other.is_error and "NOT_FOUND" in _text(other) and "'beta'" in _text(other)


@pytest.mark.anyio
async def test_us2008_ca03_admin_accede_a_todos(acm: Acm) -> None:
    for key in ("alpha", "beta"):
        acm.service.create(ADMIN, key, key)
    async with mcp(acm, acm.token(ADMIN)) as admin:
        listed = (await admin.call_tool("acm_project_list", {})).structured_content["result"]
    assert [p["project_id"] for p in listed] == ["alpha", "beta"]


# ---------------------------------------------------------------- CLI de arranque (ADR-017)
def _cli(data_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "acm", *args, "--data-dir", str(data_dir)], capture_output=True, text=True, timeout=60
    )


def test_cli_crea_principal_y_token_auditados(tmp_path: Path) -> None:
    data = tmp_path / "data"
    assert _cli(data, "principal", "create", "bot-cli", "--kind", "agent").returncode == 0
    out = _cli(data, "token", "create", "bot-cli", "--name", "local")
    assert out.returncode == 0, out.stderr
    token = json.loads(out.stdout)["token"]
    service = ProjectService(data)
    try:
        assert IdentityService(service).authenticate(token)[0] == "bot-cli"
        conn = sqlite3.connect(data / "acm.db")
        rows = conn.execute("SELECT operation, status, result_json FROM mcp_audit ORDER BY id").fetchall()
        conn.close()
    finally:
        service.close()
    assert [(r[0], r[1]) for r in rows] == [("cli:principal_create", "ok"), ("cli:token_create", "ok")]
    assert token not in rows[1][2] and json.loads(rows[1][2])["token"] == REDACTED
    bad = _cli(data, "token", "create", "no-existe", "--name", "x")
    assert bad.returncode == 2 and "NOT_FOUND" in bad.stderr


# ---------------------------------------------------------------- TD-002 — nombres de host permitidos
def _post_with_host(url: str, host: str, token: str) -> httpx.Response:
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    headers = {"Host": host, "Authorization": f"Bearer {token}", "Accept": "application/json, text/event-stream"}
    return httpx.post(f"{url}/mcp/", json=body, headers=headers, timeout=10)


def test_td002_host_permitido_por_configuracion(tmp_path: Path) -> None:
    port = free_port()
    settings = Settings.from_env(data_dir=tmp_path / "data", port=port)
    settings = Settings(**{**settings.__dict__, "allowed_hosts": ("acm.example.com",)})
    service = build_service(settings)
    token = IdentityService(service).create_token(ADMIN, ADMIN, "t")["token"]
    server = uvicorn.Server(uvicorn.Config(create_app(settings), host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        while not server.started:
            time.sleep(0.02)
        url = f"http://127.0.0.1:{port}"
        assert _post_with_host(url, "acm.example.com", token).status_code != 421
        assert _post_with_host(url, f"127.0.0.1:{port}", token).status_code != 421
        assert _post_with_host(url, "otro.example.com", token).status_code == 421
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        service.close()
