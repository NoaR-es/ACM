"""Supervisor ágil autónomo (SPRINT-008): US-13.14, US-13.15, US-04.10, US-04.14, US-04.15 y US-43.08.

ACM usa sus propios motores —JEV (Ollaya simulado) y Ollama (simulado)— dentro de cada ejecución del Watchdog para
revisar historias, sprints y Kanban, informar y aplicar solo cambios seguros. Dominio y SQLite reales.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from acm.app import build_engines
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.projects import ProjectService
from acm.domain.sprints import SprintService
from acm.domain.supervisor import SAFE_ACTIONS, SUPERVISOR
from acm.domain.watchdog import WatchdogService
from acm.inference.router import EngineRouter
from tests.conftest import ADMIN
from tests.fake_ollama import FakeOllama
from tests.fake_ollaya import FakeOllaya

P = "alpha"
NO = {"type": "noul", "noul": 0.04}  # JEV muy seguro de «no»
YES = {"type": "noul", "noul": 0.97}
SMALL = {
    "type": "choice",
    "choice": "small",
    "confidence": 0.95,
    "probabilities": {"small": 0.95, "medium": 0.04, "large": 0.01},
}
LARGE = {
    "type": "choice",
    "choice": "large",
    "confidence": 0.92,
    "probabilities": {"small": 0.02, "medium": 0.06, "large": 0.92},
}


@pytest.fixture
def ollaya() -> Iterator[FakeOllaya]:
    with FakeOllaya() as fake:
        fake.state.answers = {"invest": YES, "criteria_verifiable": YES, "size": SMALL}
        yield fake


@pytest.fixture
def ollama() -> Iterator[FakeOllama]:
    with FakeOllama() as fake:
        yield fake


def _setup(service: ProjectService, **settings: str) -> tuple[WatchdogService, BacklogService, SprintService]:
    service.create(ADMIN, P, "Alpha")
    router: EngineRouter = build_engines(service, Settings(data_dir=service.data_dir, **settings))  # type: ignore[arg-type]
    backlog = BacklogService(service, router)
    backlog.create_requirement(ADMIN, P, "Gestionar proyectos", "Alta y apertura de proyectos")
    backlog.create_epic(ADMIN, P, "Proyectos", "Gestionar", "Crear y abrir", ["REQ-001"])
    backlog.create_feature(ADMIN, P, "EPIC-01", "Creación")
    for i in range(1, 4):
        backlog.create_story(ADMIN, P, "FEAT-01.01", "operador", f"hacer {i}", "avanzar", ["REQ-001"], [f"CA {i}"])
    return WatchdogService(service, backlog, router), backlog, SprintService(backlog)


def _jev(ollaya: FakeOllaya) -> dict[str, str]:
    return {"jev_url": ollaya.url, "jev_model": "laya"}


def _ollama(ollama: FakeOllama) -> dict[str, str]:
    return {"ollama_url": ollama.url, "ollama_model": "qwen2.5:0.5b"}


def _codes(run: dict, target: str | None = None) -> set[str]:
    return {f["code"] for f in run["findings"] if target is None or f["target"] == target}


def _action(run: dict, type_: str, target: str) -> dict:
    return next(a for a in run["actions"] if a["type"] == type_ and a["target"] == target)


def _age(data_dir: Path, story_id: str, iso: str = "2026-01-01T00:00:00+00:00") -> None:
    conn = sqlite3.connect(data_dir / "projects" / P / "project.db")
    conn.execute("UPDATE stories SET updated_at = ? WHERE id = ?", (iso, story_id))
    conn.commit()
    conn.close()


def _decides(ollaya: FakeOllaya) -> int:
    return sum(r["path"] == "/api/decide" for r in ollaya.state.requests)


# ---------------------------------------------------------------- US-13.14 supervisar e informar
def test_us1314_ca01_revisa_historias_sprints_y_kanban(
    service: ProjectService, ollaya: FakeOllaya, data_dir: Path
) -> None:
    watchdog, backlog, sprints = _setup(service, **_jev(ollaya))
    service.set_config(ADMIN, P, {"kanban.wip_limit": 1, "supervisor.mode": "propose"})
    for sid in ("US-01.01", "US-01.02"):
        backlog.mark_ready(ADMIN, P, sid)
        backlog.set_status(ADMIN, P, sid, "IN_PROGRESS")
    sprints.create(ADMIN, P, "S1", "Objetivo", "2026-01-01", "2026-01-10", capacity=1)
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    sprints.start(ADMIN, P, "SPRINT-01")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.03"])  # ahora supera su capacidad y hay una sin refinar
    _age(data_dir, "US-01.01")
    run = watchdog.run(ADMIN, P)
    assert {
        "SPRINT_OVERDUE",
        "SPRINT_OVERLOADED",
        "SPRINT_STORY_NOT_READY",
        "WIP_EXCEEDED",
        "STORY_STALE",
        "WORK_OUTSIDE_SPRINT",
    } <= _codes(run)
    assert _codes(run, "US-01.02") >= {"WORK_OUTSIDE_SPRINT"} and _codes(run, "US-01.01") >= {"STORY_STALE"}
    assert run["summary"]["active_sprint"]["id"] == "SPRINT-01"
    assert _decides(ollaya) >= 3  # una revisión JEV por historia viva
    scheduled = watchdog.run_all(ADMIN)  # la ejecución periódica incluye al supervisor
    assert watchdog.history(ADMIN, P, 1)["runs"][0]["summary"]["active_sprint"]["id"] == "SPRINT-01"
    assert scheduled[0]["project_id"] == P


def test_us1314_ca02_juicio_delegado_con_motor_y_calibracion(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    ollaya.state.by_state_id = {"US-01.02": {"invest": NO}}
    watchdog, _, _ = _setup(service, **_jev(ollaya))
    finding = next(f for f in watchdog.run(ADMIN, P)["findings"] if f["code"] == "STORY_NOT_INVEST")
    assert (finding["target"], finding["severity"], finding["engine"]) == ("US-01.02", "WARNING", "jev:laya")
    assert finding["confidence"] == pytest.approx(0.96)
    # Con un motor no calibrado (Ollama) el mismo juicio solo pide revisión (ADR-015).
    service2 = ProjectService(service.data_dir / "otra")
    service2.ensure_principal(ADMIN, "admin")
    ollama.state.decisions = {"invest": "false"}
    watchdog2, _, _ = _setup(service2, **_ollama(ollama))
    f2 = next(f for f in watchdog2.run(ADMIN, P)["findings"] if f["code"] == "STORY_NOT_INVEST")
    assert f2["severity"] == "REVIEW" and f2["engine"] == "ollama-decide:qwen2.5:0.5b" and f2["confidence"] is None
    service2.close()


def test_us1314_ca03_no_repite_revisiones_sin_cambios(service: ProjectService, ollaya: FakeOllaya) -> None:
    watchdog, backlog, _ = _setup(service, **_jev(ollaya))
    service.set_config(ADMIN, P, {"supervisor.mode": "propose"})
    watchdog.run(ADMIN, P)
    first = _decides(ollaya)
    watchdog.run(ADMIN, P)
    assert _decides(ollaya) == first  # nada cambió: se reutiliza la revisión
    backlog.add_criteria(ADMIN, P, "US-01.03", ["Otro criterio"])
    watchdog.run(ADMIN, P)
    assert _decides(ollaya) == first + 1  # solo se revisa de nuevo la historia que cambió


def test_us1314_ca04_informe_con_modelo_local(service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama) -> None:
    ollama.state.reply = "## Hecho\nNada todavía.\n## Pendiente\nUS-01.01, US-01.02, US-01.03."
    watchdog, _, _ = _setup(service, **_jev(ollaya), **_ollama(ollama))
    run = watchdog.run(ADMIN, P)
    assert run["report_engine"] == "ollama:qwen2.5:0.5b" and run["report"].startswith("## Hecho\nNada todavía.")
    sent = ollama.state.requests[-1]["body"]
    assert "no inventes nada" in sent["messages"][0]["content"] and '"pending"' in sent["messages"][1]["content"]
    assert "**Pendiente:**" in run["report"]  # el informe sin modelo se conserva debajo, como respaldo verificable
    assert "ollama:qwen2.5:0.5b" in run["engines"]


def test_us1314_ca04_informe_sin_modelo(service: ProjectService) -> None:
    watchdog, _, _ = _setup(service)
    run = watchdog.run(ADMIN, P)
    assert run["report_engine"] == "" and "**Hecho:** 0 historias terminadas" in run["report"]
    assert "**Pendiente:** 3 historias por empezar (US-01.01, US-01.02, US-01.03)" in run["report"]
    assert "Sin motor de decisión con modelo" in run["report"] and run["summary"]["notes"]
    stored = watchdog.history(ADMIN, P, 1)["runs"][0]
    assert stored["report"] == run["report"] and stored["summary"]["pending"] == ["US-01.01", "US-01.02", "US-01.03"]


# ---------------------------------------------------------------- US-13.15 autonomía segura
def test_us1315_ca01_solo_acciones_seguras(service: ProjectService, ollaya: FakeOllaya, data_dir: Path) -> None:
    ollaya.state.by_state_id = {"US-01.02": {"size": LARGE}}
    watchdog, backlog, sprints = _setup(service, **_jev(ollaya))
    backlog.mark_ready(ADMIN, P, "US-01.03")
    backlog.set_status(ADMIN, P, "US-01.03", "IN_PROGRESS")
    sprints.create(ADMIN, P, "S1", "Objetivo", "2026-01-01", "2026-01-02")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.03"])
    sprints.start(ADMIN, P, "SPRINT-01")
    _age(data_dir, "US-01.03")
    run = watchdog.run(ADMIN, P)
    for type_, target in (
        ("story.split", "US-01.02"),
        ("sprint.close", "SPRINT-01"),
        ("story.review_stale", "US-01.03"),
    ):
        action = _action(run, type_, target)
        assert not action["applied"] and type_ not in SAFE_ACTIONS
    assert sprints.get(ADMIN, P, "SPRINT-01")["status"] == "ACTIVE"
    assert backlog.get_story(ADMIN, P, "US-01.03")["status"] == "IN_PROGRESS"
    assert set(SAFE_ACTIONS) == {"story.mark_ready", "story.back_to_planned", "sprint.remove_story"}
    assert not any(a.get("to") in ("DONE", "CANCELLED", "DEPRECATED") for a in run["actions"])


def test_us1315_ca02_calibrado_y_umbral(service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama) -> None:
    ollaya.state.by_state_id = {"US-01.02": {"size": {**SMALL, "confidence": 0.7}}}
    watchdog, backlog, _ = _setup(service, **_jev(ollaya))
    run = watchdog.run(ADMIN, P)
    applied = _action(run, "story.mark_ready", "US-01.01")
    low = _action(run, "story.mark_ready", "US-01.02")
    assert applied["applied"] and applied["engine"] == "jev:laya" and applied["confidence"] == pytest.approx(0.95)
    assert not low["applied"] and not low["safe"] and low["confidence"] == pytest.approx(0.7)  # bajo el 85 %
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "READY"
    assert backlog.get_story(ADMIN, P, "US-01.02")["status"] == "PLANNED"
    # Ollama (no calibrado) nunca aplica: solo propone.
    service2 = ProjectService(service.data_dir / "otra")
    service2.ensure_principal(ADMIN, "admin")
    watchdog2, backlog2, _ = _setup(service2, **_ollama(ollama))
    run2 = watchdog2.run(ADMIN, P)
    assert not _action(run2, "story.mark_ready", "US-01.01")["applied"]
    assert backlog2.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"
    service2.close()


def test_us1315_ca03_auditada_como_supervisor_y_reversible(
    service: ProjectService, ollaya: FakeOllaya, data_dir: Path
) -> None:
    watchdog, backlog, _ = _setup(service, **_jev(ollaya))
    watchdog.run(ADMIN, P)
    history = backlog.status_history(ADMIN, P, "US-01.01")["history"]
    assert history[-1]["changed_by"] == SUPERVISOR and history[-1]["to_status"] == "READY"
    conn = sqlite3.connect(data_dir / "acm.db")
    row = conn.execute(
        "SELECT principal, status, arguments_json FROM mcp_audit WHERE operation = 'supervisor:story.mark_ready' "
        "ORDER BY id LIMIT 1"
    ).fetchone()
    kind = conn.execute("SELECT kind FROM principals WHERE id = ?", (SUPERVISOR,)).fetchone()[0]
    conn.close()
    assert row[0] == SUPERVISOR and row[1] == "ok" and "jev:laya" in row[2] and "confianza 0.95" in row[2]
    assert kind == "agent"
    # Deshacer: una persona devuelve la historia a PLANNED.
    assert backlog.set_status(ADMIN, P, "US-01.01", "PLANNED", "deshacer supervisor")["status"] == "PLANNED"


def test_us1315_ca04_modos_apagado_proponer_aplicar(service: ProjectService, ollaya: FakeOllaya) -> None:
    watchdog, backlog, _ = _setup(service, **_jev(ollaya))
    service.set_config(ADMIN, P, {"supervisor.mode": "off"})
    off = watchdog.run(ADMIN, P)
    assert off["actions"] == [] and off["report"] == "" and _decides(ollaya) == 0
    service.set_config(ADMIN, P, {"supervisor.mode": "propose"})
    proposed = watchdog.run(ADMIN, P)
    assert proposed["actions"] and not any(a["applied"] for a in proposed["actions"])
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"
    service.set_config(ADMIN, P, {"supervisor.mode": "apply_safe"})
    applied = watchdog.run(ADMIN, P)
    assert _action(applied, "story.mark_ready", "US-01.01")["applied"]


def test_us1315_devuelve_a_planned_y_saca_canceladas(service: ProjectService, ollaya: FakeOllaya) -> None:
    watchdog, backlog, sprints = _setup(service, **_jev(ollaya))
    service.set_config(ADMIN, P, {"supervisor.mode": "propose"})
    backlog.mark_ready(ADMIN, P, "US-01.01")
    backlog.mark_ready(ADMIN, P, "US-01.02")
    sprints.create(ADMIN, P, "S1", "Objetivo", "2030-01-01", "2030-01-10")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.02", "US-01.03"])
    backlog.set_status(ADMIN, P, "US-01.03", "CANCELLED")
    ollaya.state.answers = {"invest": YES, "criteria_verifiable": NO, "size": SMALL}
    service.set_config(ADMIN, P, {"supervisor.mode": "apply_safe"})
    run = watchdog.run(ADMIN, P)
    assert _action(run, "story.back_to_planned", "US-01.01")["applied"]
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"
    # US-01.02 está en un sprint: no se devuelve a PLANNED por su cuenta.
    assert not any(a["type"] == "story.back_to_planned" and a["target"] == "US-01.02" for a in run["actions"])
    assert _action(run, "sprint.remove_story", "US-01.03")["applied"]
    assert sprints.get(ADMIN, P, "SPRINT-01")["story_ids"] == ["US-01.02"]


# ---------------------------------------------------------------- US-04.10 / US-04.14 / US-04.15
def test_us0410_ca01_historia_grande_o_no_testeable(service: ProjectService, ollaya: FakeOllaya) -> None:
    ollaya.state.by_state_id = {"US-01.01": {"size": LARGE}, "US-01.02": {"criteria_verifiable": NO}}
    watchdog, _, _ = _setup(service, **_jev(ollaya))
    run = watchdog.run(ADMIN, P)
    assert "STORY_TOO_LARGE" in _codes(run, "US-01.01") and "CRITERIA_NOT_VERIFIABLE" in _codes(run, "US-01.02")
    assert _action(run, "story.split", "US-01.01")["reason"] == "dividirla en historias más pequeñas"


def test_us0414_ca01_evalua_invest(service: ProjectService, ollaya: FakeOllaya) -> None:
    ollaya.state.by_state_id = {"US-01.03": {"invest": NO}}
    watchdog, _, _ = _setup(service, **_jev(ollaya))
    run = watchdog.run(ADMIN, P)
    assert _codes(run, "US-01.03") == {"STORY_NOT_INVEST"} and _codes(run, "US-01.01") == set()
    sent = next(
        r["body"]
        for r in ollaya.state.requests
        if r["path"] == "/api/decide" and r["body"]["state"]["id"] == "US-01.03"
    )
    assert "INVEST" in sent["questions"]["invest"]["instructions"]
    assert sent["state"]["criterios"] == ["CA-01: CA 3"] and sent["state"]["requisitos"][0].startswith("REQ-001")


def test_us0415_ca01_criterios_vagos(service: ProjectService, ollaya: FakeOllaya) -> None:
    ollaya.state.answers = {"invest": YES, "criteria_verifiable": NO, "size": SMALL}
    watchdog, _, _ = _setup(service, **_jev(ollaya))
    run = watchdog.run(ADMIN, P)
    vague = [f for f in run["findings"] if f["code"] == "CRITERIA_NOT_VERIFIABLE"]
    assert {f["target"] for f in vague} == {"US-01.01", "US-01.02", "US-01.03"}
    assert all(f["severity"] == "WARNING" and f["engine"] == "jev:laya" for f in vague)


# ---------------------------------------------------------------- US-43.08 riesgo del sprint
def test_us4308_ca01_prediccion_de_riesgo(service: ProjectService, ollaya: FakeOllaya) -> None:
    ollaya.state.answers |= {
        "risk": {
            "type": "score",
            "score": 1.9,
            "confidence": 0.8,
            "legend": {"0": "bajo", "1": "medio", "2": "alto"},
            "probabilities": {"0": 0.05, "1": 0.15, "2": 0.8},
        }
    }
    watchdog, backlog, sprints = _setup(service, **_jev(ollaya))
    service.set_config(ADMIN, P, {"supervisor.mode": "propose"})
    backlog.mark_ready(ADMIN, P, "US-01.01")
    sprints.create(ADMIN, P, "S1", "Entregar altas", "2026-01-01", "2030-01-01")
    sprints.add_stories(ADMIN, P, "SPRINT-01", ["US-01.01"])
    sprints.start(ADMIN, P, "SPRINT-01")
    run = watchdog.run(ADMIN, P)
    risk = next(f for f in run["findings"] if f["code"] == "SPRINT_AT_RISK")
    assert (risk["target"], risk["severity"], risk["engine"]) == ("SPRINT-01", "WARNING", "jev:laya")
    assert run["summary"]["active_sprint"]["risk"] == "alto" and run["summary"]["active_sprint"]["risk_calibrated"]
    sent = next(
        r["body"] for r in ollaya.state.requests if r["path"] == "/api/decide" and "risk" in r["body"]["questions"]
    )
    assert sent["state"]["objetivo"] == "Entregar altas" and sent["state"]["historias_por_estado"] == {"READY": 1}


def test_us1315_ca01_accion_desconocida_nunca_figura_como_aplicada(service: ProjectService) -> None:
    watchdog, _, _ = _setup(service)
    action = {"type": "story.delete", "target": "US-01.01", "reason": "x", "engine": "rules", "confidence": 1.0}
    watchdog.supervisor._apply(P, action)
    assert action["applied"] is False and "fuera de la lista de acciones seguras" in action["error"]
