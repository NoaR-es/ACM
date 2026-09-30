"""EPIC-13 — Watchdog: US-13.03 (salud), 13.05 (integridad), 13.06 (continuo), 13.07 (historias sin criterios),
13.10 (semáforo), 13.11 (bloqueo), 13.12 (auditoría completa), 13.13 (histórico); y US-35.11 CA-01."""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from mcp import Client

from acm.app import build_service, create_app
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.errors import DataIntegrityError, Forbidden, NotFound
from acm.domain.projects import ProjectService
from acm.domain.watchdog import WatchdogService
from acm.inference.router import EngineRouter
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN, add_member
from tests.fake_ollama import free_port
from tests.test_inference import FakeJev

P = "alpha"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _seed(service: ProjectService, project: str = P) -> BacklogService:
    service.create(ADMIN, project, project)
    b = BacklogService(service)
    b.create_requirement(ADMIN, project, "Gestionar proyectos")
    b.create_epic(ADMIN, project, "Proyectos", "o", "s", ["REQ-001"])
    b.create_feature(ADMIN, project, "EPIC-01", "Creación")
    b.create_story(
        ADMIN, project, "FEAT-01.01", "operador", "crear", "separar", ["REQ-001"], ["Nombre vacío rechazado"]
    )
    return b


def _watchdog(service: ProjectService, router: EngineRouter | None = None) -> WatchdogService:
    router = router or EngineRouter(service)
    return WatchdogService(service, BacklogService(service, router), router)


def _break_foreign_key(data_dir: Path, project: str = P) -> None:
    conn = sqlite3.connect(data_dir / "projects" / project / "project.db")
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("INSERT INTO story_requirements(story_id, requirement_id) VALUES ('US-01.01', 'REQ-999')")
    conn.commit()
    conn.close()


def _repair_foreign_key(data_dir: Path, project: str = P) -> None:
    conn = sqlite3.connect(data_dir / "projects" / project / "project.db")
    conn.execute("DELETE FROM story_requirements WHERE requirement_id = 'REQ-999'")
    conn.commit()
    conn.close()


def _corrupt_page_header(data_dir: Path, service: ProjectService, project: str = P) -> ProjectService:
    """Corrompe la cabecera de una página B-tree (determinista: SQLite no puede leer la base)."""
    b = BacklogService(service)
    for i in range(200):
        b.create_requirement(ADMIN, project, f"R{i}", "x" * 300)
    service.close()
    path = data_dir / "projects" / project / "project.db"
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    data = bytearray(path.read_bytes())
    data[4096 * 5 : 4096 * 5 + 8] = b"\xff" * 8
    path.write_bytes(bytes(data))
    fresh = ProjectService(data_dir)
    return fresh


# ---------------------------------------------------------------- US-13.05 / US-13.11
def test_us1305_ca01_detecta_relaciones_rotas(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    _break_foreign_key(data_dir)
    run = _watchdog(service).run(ADMIN, P)
    assert run["integrity"] == "corrupt" and run["semaphore"] == "RED"
    fk = [f for f in run["findings"] if f["code"] == "SQLITE_FOREIGN_KEY"]
    assert fk and fk[0]["severity"] == "CRITICAL" and fk[0]["target"].startswith("story_requirements#")


def test_us1305_ca01_detecta_base_danada(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    fresh = _corrupt_page_header(data_dir, service)
    try:
        run = _watchdog(fresh).run(ADMIN, P)
        assert run["integrity"] == "corrupt"
        assert {f["code"] for f in run["findings"]} & {"DB_UNREADABLE", "SQLITE_INTEGRITY"}
        assert all(f["source"] == "integrity" for f in run["findings"])  # no se evalúa nada sobre la base dañada
    finally:
        fresh.close()


def test_us1305_ca02_us1311_ca01_ca03_escrituras_bloqueadas_sin_efectos(
    service: ProjectService, data_dir: Path
) -> None:
    b = _seed(service)
    _break_foreign_key(data_dir)
    _watchdog(service).run(ADMIN, P)
    for write in (
        lambda: b.create_requirement(ADMIN, P, "nuevo"),
        lambda: b.add_criteria(ADMIN, P, "US-01.01", ["otro"]),
        lambda: service.set_config(ADMIN, P, {"context.max_tokens": 1000}),
    ):
        with pytest.raises(DataIntegrityError):
            write()
    assert [r["id"] for r in b.list_requirements(ADMIN, P)["requirements"]] == ["REQ-001"]  # lecturas sí; sin efectos
    assert len(b.get_story(ADMIN, P, "US-01.01")["acceptance_criteria"]) == 1


def test_us1311_ca02_bloqueo_explicado(service: ProjectService, data_dir: Path) -> None:
    b = _seed(service)
    _break_foreign_key(data_dir)
    _watchdog(service).run(ADMIN, P)
    with pytest.raises(DataIntegrityError, match="cuarentena.*SQLITE_FOREIGN_KEY.*acm_watchdog_run"):
        b.create_requirement(ADMIN, P, "nuevo")


def test_us1305_ca03_reparada_se_levanta_la_cuarentena(service: ProjectService, data_dir: Path) -> None:
    b = _seed(service)
    wd = _watchdog(service)
    _break_foreign_key(data_dir)
    wd.run(ADMIN, P)
    _repair_foreign_key(data_dir)
    run = wd.run(ADMIN, P)
    assert run["integrity"] == "ok" and run["semaphore"] == "GREEN"
    assert b.create_requirement(ADMIN, P, "ya se puede")["id"] == "REQ-002"


# ---------------------------------------------------------------- US-13.07 / US-35.11 CA-01
def test_us1307_ca01_historia_sin_criterios_detectada(service: ProjectService) -> None:
    b = _seed(service)
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir", "trabajar", ["REQ-001"])
    run = _watchdog(service).run(ADMIN, P)
    missing = [f for f in run["findings"] if f["code"] == "STORY_WITHOUT_CRITERIA"]
    assert [(f["target"], f["severity"]) for f in missing] == [("US-01.02", "WARNING")]
    assert run["semaphore"] == "AMBER"


def test_us1307_ca02_evaluada_por_el_motor_de_decision(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    run = _watchdog(service).run(ADMIN, P)
    assert run["engines"] == ["rules"]
    conn = sqlite3.connect(data_dir / "acm.db")
    purposes = [r[0] for r in conn.execute("SELECT purpose FROM inference_calls WHERE project_id = ?", (P,))]
    conn.close()
    assert purposes == ["story.quality"]


def test_us1307_ca03_historia_completa_sin_hallazgos(service: ProjectService) -> None:
    _seed(service)
    run = _watchdog(service).run(ADMIN, P)
    assert run["findings"] == [] and run["semaphore"] == "GREEN"


def test_us1307_motor_no_calibrado_pide_revision(service: ProjectService) -> None:
    b = _seed(service)
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir", "trabajar", ["REQ-001"])
    router = EngineRouter(service)

    class Pessimist(FakeJev):
        def decide(self, request):  # type: ignore[no-untyped-def]
            result = super().decide(request)
            for a in result.answers.values():
                object.__setattr__(a, "value", 0.1)
            return result

    router.registry.register(Pessimist(calibrated=False, name="ollama:llm", provider="ollama"))
    service.set_config(ADMIN, P, {"decision.engine_order": ["ollama", "rules"]})
    run = _watchdog(service, router).run(ADMIN, P)
    story = [f for f in run["findings"] if f["source"] == "decision"]
    assert story and all(f["severity"] == "REVIEW" and f["engine"] == "ollama:llm" for f in story)
    assert run["counts"]["warning"] == 0 and run["semaphore"] == "AMBER"


def test_us3511_ca01_watchdog_consume_la_interfaz(service: ProjectService) -> None:
    _seed(service)
    router = EngineRouter(service)
    spy = FakeJev()
    router.registry.register(spy)
    service.set_config(ADMIN, P, {"decision.engine_order": ["jev", "rules"]})
    run = _watchdog(service, router).run(ADMIN, P)
    assert [r.purpose for r in spy.seen] == ["story.quality"] and run["engines"] == ["jev:test"]


# ---------------------------------------------------------------- US-13.10 — semáforo
def test_us1310_ca01_reglas_del_semaforo(service: ProjectService, data_dir: Path) -> None:
    b = _seed(service)
    wd = _watchdog(service)
    assert wd.run(ADMIN, P)["semaphore"] == "GREEN"
    b.create_requirement(ADMIN, P, "huérfano")
    info = wd.run(ADMIN, P)
    assert info["semaphore"] == "GREEN" and info["counts"]["info"] == 1  # INFO no cambia el color
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir", "trabajar", ["REQ-001"])
    assert wd.run(ADMIN, P)["semaphore"] == "AMBER"
    _break_foreign_key(data_dir)
    assert wd.run(ADMIN, P)["semaphore"] == "RED"


def test_us1310_ca02_ca03_indicadores_del_proyecto(service: ProjectService) -> None:
    _seed(service)
    wd = _watchdog(service)
    before = wd.status(ADMIN, P)
    assert before["semaphore"] == "UNKNOWN" and before["last_run"] is None and before["writable"]
    run = wd.run(ADMIN, P)
    after = wd.status(ADMIN, P)
    assert after["semaphore"] == "GREEN" and after["last_run"]["id"] == run["run_id"]
    assert after["integrity"]["integrity_status"] == "ok"
    assert set(after["last_run"]) >= {"critical", "warning", "review", "info", "ts"}


# ---------------------------------------------------------------- US-13.12 / US-13.13
@pytest.mark.anyio
async def test_us1312_ca01_ca02_ca03_auditoria_completa_por_mcp(service: ProjectService) -> None:
    b = _seed(service)
    b.create_requirement(ADMIN, P, "huérfano")
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir", "trabajar", ["REQ-001"])
    async with Client(build_mcp_server(service, lambda: ADMIN)) as client:
        res = await client.call_tool("acm_watchdog_run", {"project_id": P})
    assert not res.is_error, res.content
    run = res.structured_content
    assert run["project_id"] == P and run["trigger"] == "manual"
    assert {f["source"] for f in run["findings"]} == {"decision", "structure"} and run["integrity"] == "ok"
    for f in run["findings"]:
        assert set(f) >= {"code", "severity", "target", "message", "source"}


def test_us1313_ca01_ca02_ca03_historico(service: ProjectService) -> None:
    b = _seed(service)
    wd = _watchdog(service)
    first = wd.run(ADMIN, P)
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir", "trabajar", ["REQ-001"])
    second = wd.run(ADMIN, P)
    runs = wd.history(ADMIN, P)["runs"]
    assert [r["id"] for r in runs] == [second["run_id"], first["run_id"]]  # más recientes primero
    assert [r["semaphore"] for r in runs] == ["AMBER", "GREEN"]
    assert runs[0]["findings"] == second["findings"] and runs[1]["findings"] == []
    assert [r["id"] for r in wd.history(ADMIN, P, limit=1)["runs"]] == [second["run_id"]]


def test_us1313_ca04_historico_aislado_por_proyecto(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    _seed(service, "beta")
    wd = _watchdog(service)
    wd.run(ADMIN, P)
    add_member(data_dir, "beta", "agente-b")
    with pytest.raises(NotFound):
        wd.history("agente-b", P)
    with pytest.raises(NotFound):
        wd.run("agente-b", P)
    assert wd.history("agente-b", "beta")["runs"] == []


# ---------------------------------------------------------------- US-13.06 — continuo
def test_us1306_ca01_se_ejecuta_periodicamente(tmp_path: Path) -> None:
    port = free_port()
    settings = Settings.from_env(data_dir=tmp_path / "data", port=port)
    settings = Settings(**{**settings.__dict__, "watchdog_interval_s": 0.3})
    service = build_service(settings)
    _seed(service)
    _seed(service, "beta")
    server = uvicorn.Server(uvicorn.Config(create_app(settings), host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 15
        while True:
            with service.global_db.read() as conn:
                rows = conn.execute("SELECT project_id, trigger, principal FROM watchdog_runs").fetchall()
            if {r[0] for r in rows} == {P, "beta"}:
                break
            assert time.monotonic() < deadline, "el Watchdog periódico no se ejecutó"
            time.sleep(0.1)
        assert {(r[1], r[2]) for r in rows} == {("scheduled", settings.principal)}
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        service.close()


def test_us1306_ca02_fallo_en_un_proyecto_no_detiene_a_los_demas(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    _seed(service, "beta")
    _break_foreign_key(data_dir, P)
    summary = {s["project_id"]: s for s in _watchdog(service).run_all(ADMIN)}
    assert summary[P]["semaphore"] == "RED" and summary["beta"]["semaphore"] == "GREEN"


def test_us1306_ca03_intervalo_configurable_y_solo_admin(service: ProjectService, monkeypatch) -> None:
    monkeypatch.setenv("ACM_WATCHDOG_INTERVAL_S", "0")
    assert Settings.from_env(data_dir="x").watchdog_interval_s == 0
    monkeypatch.setenv("ACM_WATCHDOG_INTERVAL_S", "120")
    assert Settings.from_env(data_dir="x").watchdog_interval_s == 120
    service.ensure_principal("bob", "user")
    with pytest.raises(Forbidden):
        _watchdog(service).run_all("bob")


# ---------------------------------------------------------------- US-13.03 — salud global
def test_us1303_ca01_ca02_componentes_con_estado(service: ProjectService) -> None:
    _seed(service)
    health = _watchdog(service).health(ADMIN, build_mcp_server(service, lambda: ADMIN).acm_catalog)
    names = {c["name"]: c for c in health["components"]}
    assert {"sqlite:global", f"sqlite:project:{P}", "skills", "inference:rules"} <= set(names)
    assert all(c["status"] in ("ok", "degraded", "error") and c["kind"] for c in health["components"])
    assert names["sqlite:global"]["status"] == "ok" and names["inference:rules"]["status"] == "ok"


def test_us1303_ca03_componente_degradado_identificado(service: ProjectService, data_dir: Path) -> None:
    _seed(service)
    _seed(service, "beta")
    router = EngineRouter(service)
    from acm.inference.ollama import OllamaClient, OllamaGenerationEngine

    router.registry.register(OllamaGenerationEngine(OllamaClient(f"http://127.0.0.1:{free_port()}"), "m"))
    wd = _watchdog(service, router)
    _break_foreign_key(data_dir, "beta")
    wd.run(ADMIN, "beta")
    health = {c["name"]: c for c in wd.health(ADMIN)["components"]}
    assert health[f"sqlite:project:{P}"]["status"] == "degraded"  # nunca auditado
    assert health["sqlite:project:beta"]["status"] == "error"  # en cuarentena
    assert (
        health["inference:ollama:m"]["status"] == "error" and "no accesible" in health["inference:ollama:m"]["detail"]
    )
    assert wd.health(ADMIN)["status"] == "degraded"
    router.registry.close()


def test_us1303_ca04_informacion_actualizada(service: ProjectService) -> None:
    _seed(service)
    wd = _watchdog(service)
    first = wd.health(ADMIN)
    wd.run(ADMIN, P)
    second = wd.health(ADMIN)
    assert second["checked_at"] > first["checked_at"]
    status = lambda h: {c["name"]: c["status"] for c in h["components"]}[f"sqlite:project:{P}"]  # noqa: E731
    assert (status(first), status(second)) == ("degraded", "ok")


@pytest.mark.anyio
async def test_us1303_solo_admin(service: ProjectService) -> None:
    service.ensure_principal("bob", "user")
    async with Client(build_mcp_server(service, lambda: "bob")) as bob:
        res = await bob.call_tool("acm_health", {})
    assert res.is_error and "FORBIDDEN" in res.content[0].text
