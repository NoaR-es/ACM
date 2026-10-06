"""API REST v1 de escritura (SPRINT-008): la parte servidor de US-31.09..31.12 y de los sprints (US-05.05 CA-06).

ACM real por HTTP con tokens reales. Cada escritura se valida en el dominio, se audita como `rest:*` y emite su evento.
"""

from __future__ import annotations

import httpx
import pytest

from tests.live import ADMIN, Acm

P = "alpha"


def _client(acm: Acm, principal: str = ADMIN) -> httpx.Client:
    return httpx.Client(base_url=f"{acm.url}/api/v1", headers={"Authorization": f"Bearer {acm.token(principal)}"})


def _ok(resp: httpx.Response, status: int = 200) -> dict:
    assert resp.status_code == status, resp.text
    return resp.json()


def _backlog(c: httpx.Client) -> None:
    _ok(c.post("/projects", json={"key": P, "name": "Alpha", "description": "d"}), 201)
    _ok(c.post(f"/projects/{P}/requirements", json={"title": "Gestionar proyectos"}), 201)
    _ok(
        c.post(
            f"/projects/{P}/epics", json={"title": "E", "objective": "o", "scope": "s", "requirement_ids": ["REQ-001"]}
        ),
        201,
    )
    _ok(c.post(f"/projects/{P}/features", json={"epic_id": "EPIC-01", "title": "F"}), 201)
    for i in (1, 2):
        _ok(
            c.post(
                f"/projects/{P}/stories",
                json={
                    "feature_id": "FEAT-01.01",
                    "as_a": "a",
                    "i_want": f"b{i}",
                    "so_that": "c",
                    "requirement_ids": ["REQ-001"],
                    "acceptance_criteria": [f"CA {i}"],
                },
            ),
            201,
        )


# ---------------------------------------------------------------- US-31.09 proyectos y configuración
def test_us3109_ca01_crear_proyecto_y_errores(acm: Acm) -> None:
    with _client(acm) as c:
        created = _ok(c.post("/projects", json={"key": P, "name": "Alpha", "description": "Plataforma"}), 201)
        assert created["project_id"] == P and created["description"] == "Plataforma"
        dup = c.post("/projects", json={"key": P, "name": "Otra"})
        bad = c.post("/projects", json={"key": "Con Espacios", "name": "X"})
    assert dup.status_code == 409 and dup.json()["error"]["code"] == "ALREADY_EXISTS"
    assert bad.status_code == 400 and bad.json()["error"]["field"] == "key"
    assert acm.audit(operation="rest:project_create", status="ok")[0]["principal"] == ADMIN


def test_us3109_ca02_configuracion_valida_todo_antes_de_guardar(acm: Acm) -> None:
    with _client(acm) as c:
        _ok(c.post("/projects", json={"key": P, "name": "Alpha"}), 201)
        mixed = c.patch(f"/projects/{P}/config", json={"changes": {"context.max_tokens": 5000, "supervisor.mode": "x"}})
        assert mixed.status_code == 400 and mixed.json()["error"]["field"] == "supervisor.mode"
        params = {p["key"]: p["value"] for p in _ok(c.get(f"/projects/{P}/config"))["parameters"]}
        assert params["context.max_tokens"] == 8000  # nada guardado
        _ok(c.patch(f"/projects/{P}/config", json={"changes": {"decision.engine_order": ["jev", "rules"]}}))
        params = {p["key"]: p["value"] for p in _ok(c.get(f"/projects/{P}/config"))["parameters"]}
    assert params["decision.engine_order"] == ["jev", "rules"]


def test_us3109_ca03_solo_owner_o_admin_configuran(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "bea", "user")
    with _client(acm) as admin:
        _ok(admin.post("/projects", json={"key": P, "name": "Alpha"}), 201)
        _ok(admin.put(f"/projects/{P}/members/bea", json={"role": "member"}))
    with _client(acm, "bea") as bea:
        assert _ok(bea.get(f"/projects/{P}/config"))["parameters"]
        denied = bea.patch(f"/projects/{P}/config", json={"changes": {"context.max_tokens": 1000}})
    assert denied.status_code == 403 and denied.json()["error"]["code"] == "FORBIDDEN"


# ---------------------------------------------------------------- US-31.10 construir el backlog
def test_us3110_ca01_crear_todo_el_backlog(acm: Acm) -> None:
    with _client(acm) as c:
        _backlog(c)
        backlog = _ok(c.get(f"/projects/{P}/backlog"))
    assert [r["id"] for r in backlog["requirements"]] == ["REQ-001"]
    assert backlog["epics"][0]["features"][0]["story_ids"] == ["US-01.01", "US-01.02"]
    assert backlog["stories"][0]["acceptance_criteria"] == [{"code": "CA-01", "text": "CA 1"}]
    ops = {a["operation"] for a in acm.audit(status="ok")}
    assert {"rest:requirement_create", "rest:epic_create", "rest:feature_create", "rest:story_create"} <= ops


def test_us3110_ca02_anadir_criterios(acm: Acm) -> None:
    with _client(acm) as c:
        _backlog(c)
        story = _ok(c.post(f"/projects/{P}/stories/US-01.01/criteria", json={"criteria": ["Otro", "Y otro"]}))
    assert [x["code"] for x in story["acceptance_criteria"]] == ["CA-01", "CA-02", "CA-03"]


def test_us3110_ca03_enlazar_confirmar_y_dividir(acm: Acm) -> None:
    with _client(acm) as c:
        _backlog(c)
        _ok(c.post(f"/projects/{P}/requirements", json={"title": "Otro requisito"}), 201)
        epic = _ok(c.post(f"/projects/{P}/epics/EPIC-01/requirements", json={"requirement_ids": ["REQ-002"]}))
        assert epic["requirement_ids"] == ["REQ-001", "REQ-002"]
        assert _ok(c.post(f"/projects/{P}/epics/EPIC-01/confirm-coverage"))["coverage_confirmed_by"] == ADMIN
        parts = [{"title": "F1", "story_ids": ["US-01.01"]}, {"title": "F2", "story_ids": ["US-01.02"]}]
        split = _ok(c.post(f"/projects/{P}/features/FEAT-01.01/split", json={"parts": parts}))
    assert split["split_into"] == ["FEAT-01.02", "FEAT-01.03"]


def test_us3110_ca04_error_con_campo(acm: Acm) -> None:
    with _client(acm) as c:
        _backlog(c)
        resp = c.post(
            f"/projects/{P}/stories",
            json={
                "feature_id": "FEAT-01.01",
                "as_a": "a",
                "i_want": "  ",
                "so_that": "c",
                "requirement_ids": ["REQ-001"],
            },
        )
        missing = c.post(f"/projects/{P}/stories", json={"as_a": "a"})
    assert resp.status_code == 400 and resp.json()["error"]["field"] == "i_want"
    assert missing.status_code == 400 and missing.json()["error"]["code"] == "INVALID_ARGUMENT"


# ---------------------------------------------------------------- US-31.11 acceso
def test_us3111_ca01_ca02_principales_roles_y_miembros(acm: Acm) -> None:
    with _client(acm) as c:
        _ok(c.post("/projects", json={"key": P, "name": "Alpha"}), 201)
        bot = _ok(c.post("/principals", json={"principal_id": "bot-ci", "kind": "agent"}), 201)
        assert bot["id"] == "bot-ci" and bot["kind"] == "agent"
        assert _ok(c.put("/principals/bot-ci/role", json={"role": "admin"}))["role"] == "admin"
        _ok(c.put(f"/projects/{P}/members/bot-ci", json={"role": "member"}))
        assert _ok(c.put(f"/projects/{P}/members/bot-ci", json={"role": "owner"}))
        roles = {m["principal_id"]: m["role"] for m in _ok(c.get(f"/projects/{P}/members"))["members"]}
        assert roles["bot-ci"] == "owner"
        _ok(c.delete(f"/projects/{P}/members/bot-ci"))
        assert "bot-ci" not in {m["principal_id"] for m in _ok(c.get(f"/projects/{P}/members"))["members"]}


def test_us3111_ca03_ca04_token_una_vez_y_revocacion_inmediata(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "bea", "user")
    with _client(acm) as c:
        created = _ok(c.post("/tokens", json={"principal_id": "bea", "name": "portátil"}), 201)
        secret = created["token"]
        assert secret.startswith("acm_") and all("token" not in t for t in _ok(c.get("/tokens"))["tokens"])
        with httpx.Client(base_url=f"{acm.url}/api/v1", headers={"Authorization": f"Bearer {secret}"}) as bea:
            assert _ok(bea.get("/me"))["id"] == "bea"
            _ok(c.delete(f"/tokens/{created['token_id']}"))
            assert bea.get("/me").status_code == 401
    audited = acm.audit(operation="rest:token_create")[0]
    assert secret not in audited["result_json"] and secret not in audited["arguments_json"]


# ---------------------------------------------------------------- US-31.12 motores
def test_us3112_ca02_refrescar_motores_solo_admin(acm: Acm) -> None:
    acm.identity.create_principal(ADMIN, "bea", "user")
    with _client(acm) as c:
        engines = _ok(c.post("/engines/refresh"))["engines"]
    assert {e["name"]: e["status"] for e in engines}["rules"] == "ok"
    with _client(acm, "bea") as bea:
        assert bea.post("/engines/refresh").status_code == 403


# ---------------------------------------------------------------- sprints por REST y Kanban de un sprint
def test_us0505_ca06_sprints_y_kanban_del_sprint(acm: Acm) -> None:
    with _client(acm) as c:
        _backlog(c)
        body = {"name": "S1", "goal": "Objetivo", "start_date": "2026-10-01", "end_date": "2026-10-14", "capacity": 1}
        assert _ok(c.post(f"/projects/{P}/sprints", json=body), 201)["id"] == "SPRINT-01"
        added = _ok(c.post(f"/projects/{P}/sprints/SPRINT-01/stories", json={"story_ids": ["US-01.01"]}))
        assert added["story_ids"] == ["US-01.01"] and added["warnings"] == [
            "US-01.01 no está READY: refínala antes de empezar"
        ]
        board = _ok(c.get("/kanban", params={"projects": P, "sprint": "SPRINT-01"}))
        assert [card["id"] for card in board["cards"]] == ["US-01.01"] and board["cards"][0]["sprint_id"] == "SPRINT-01"
        _ok(c.post("/projects", json={"key": "beta", "name": "Beta"}), 201)
        both = c.get("/kanban", params={"sprint": "SPRINT-01"})  # dos proyectos accesibles: sprint ambiguo
        assert both.status_code == 400 and both.json()["error"]["field"] == "sprint"
        _ok(c.post(f"/projects/{P}/sprints/SPRINT-01/stories", json={"story_ids": ["US-01.02"]}))
        over = c.post(f"/projects/{P}/sprints/SPRINT-01/start", json={})
        assert over.status_code == 409 and "sobrecargado" in over.json()["error"]["message"]
        _ok(c.delete(f"/projects/{P}/sprints/SPRINT-01/stories/US-01.02"))
        assert _ok(c.post(f"/projects/{P}/sprints/SPRINT-01/start", json={}))["status"] == "ACTIVE"
        closed = _ok(c.post(f"/projects/{P}/sprints/SPRINT-01/close", json={}))
        assert closed["status"] == "CLOSED" and closed["summary"]["not_done"] == ["US-01.01"]
        assert _ok(c.get(f"/projects/{P}/sprints"))["sprints"][0]["status"] == "CLOSED"


def test_escrituras_rest_emiten_actividad(acm: Acm) -> None:
    before = acm.service.events.latest_seq()
    with _client(acm) as c:
        _ok(c.post("/projects", json={"key": P, "name": "Alpha"}), 201)
        c.post("/projects", json={"key": P, "name": "Alpha"})
    ops = [
        (e["entity_id"], e["data"]["status"]) for e in acm.service.events.after(before, 50) if e["type"] == "activity"
    ]
    assert ops == [("rest:project_create", "ok"), ("rest:project_create", "error")]


@pytest.mark.parametrize("path", ["/projects/nope/requirements", "/projects/nope/sprints"])
def test_escritura_en_proyecto_ajeno_no_lo_revela(acm: Acm, path: str) -> None:
    with _client(acm) as c:
        body = (
            {"title": "x"}
            if "requirements" in path
            else {"name": "s", "goal": "g", "start_date": "2026-10-01", "end_date": "2026-10-02"}
        )
        resp = c.post(path, json=body)
    assert resp.status_code == 404 and resp.json()["error"]["code"] == "NOT_FOUND"
