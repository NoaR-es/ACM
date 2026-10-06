"""Segundo cerebro completo (SPRINT-008): JEV vía Ollaya (US-50.01..04) y Ollama como motor de decisión (US-22.04).

Motores reales de ACM (`JevDecisionEngine`, `OllamaDecisionEngine`) contra servidores HTTP simulados que reproducen
el contrato documentado de Ollaya y Ollama. La verificación contra runtimes reales queda en SPIKE-005/006 (IMP-004).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from mcp import Client

from acm.app import build_engines
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.context import ContextService
from acm.domain.errors import FailedPrecondition, InvalidArgument
from acm.domain.projects import ProjectService
from acm.inference.jev import JevDecisionEngine, OllayaClient
from acm.inference.ollama import DECISION_PROMPT_VERSION, OllamaClient, OllamaDecisionEngine
from acm.inference.ports import DecisionEngine, DecisionRequest, EngineError, EngineUnavailable
from acm.inference.router import EngineRouter
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN
from tests.fake_ollama import FakeOllama, free_port
from tests.fake_ollaya import FakeOllaya

P = "alpha"
QUESTIONS = {
    "department": {
        "type": "choice",
        "instructions": "¿Qué equipo debe atenderlo?",
        "criteria": {"billing": "Pagos y facturas", "technical": "Errores", "account": "Cuenta"},
    },
    "urgency": {"type": "score", "instructions": "¿Cuánta urgencia?", "criteria": ["baja", "media", "alta"]},
    "refund": {"type": "noul", "instructions": "¿Pide un reembolso?"},
}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def ollaya() -> Iterator[FakeOllaya]:
    with FakeOllaya() as fake:
        yield fake


@pytest.fixture
def ollama() -> Iterator[FakeOllama]:
    with FakeOllama() as fake:
        yield fake


def _router(service: ProjectService, **settings: str | None) -> EngineRouter:
    if P not in [p["project_id"] for p in service.list_for(ADMIN)]:
        service.create(ADMIN, P, "Alpha")
    return build_engines(service, Settings(data_dir=service.data_dir, **settings))  # type: ignore[arg-type]


def _jev(ollaya: FakeOllaya, **extra: str | None) -> dict[str, str | None]:
    return {"jev_url": ollaya.url, "jev_model": "laya", **extra}


def _ollama(ollama: FakeOllama) -> dict[str, str]:
    return {"ollama_url": ollama.url, "ollama_model": "qwen2.5:0.5b"}


def _request(purpose: str = "ticket.triage", questions: dict | None = None) -> DecisionRequest:
    return DecisionRequest.from_json(P, purpose, "Me cobraron dos veces este mes.", questions or QUESTIONS)


def _calls(data_dir: Path) -> list[dict]:
    conn = sqlite3.connect(data_dir / "acm.db")
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM inference_calls ORDER BY id")]
    conn.close()
    return rows


def _status(router: EngineRouter) -> dict[str, dict]:
    return {r["name"]: r for r in router.registry.refresh()}


# ---------------------------------------------------------------- US-50.01 conectar un servidor JEV
def test_us5001_ca01_registra_jev_y_comprueba_salud(service: ProjectService, ollaya: FakeOllaya) -> None:
    router = _router(service, **_jev(ollaya))
    engine = next(e for e in router.registry.decision if e.provider == "jev")
    assert isinstance(engine, DecisionEngine) and engine.name == "jev:laya"
    row = _status(router)["jev:laya"]
    assert (row["kind"], row["provider"], row["status"], row["endpoint"]) == ("decision", "jev", "ok", ollaya.url)
    assert row["models"] == ["decider:latest", "laya:latest"]  # `laya` = `laya:latest`, como en Ollama


def test_us5001_ca02_envia_la_clave_del_servidor(service: ProjectService, ollaya: FakeOllaya) -> None:
    ollaya.state.api_key = "s3cr3t"
    assert _status(_router(service, **_jev(ollaya, jev_api_key="s3cr3t")))["jev:laya"]["status"] == "ok"
    assert ollaya.state.requests[-1]["auth"] == "Bearer s3cr3t"
    row = _status(_router(service, **_jev(ollaya, jev_api_key="otra")))["jev:laya"]
    assert row["status"] == "error" and "401" in row["detail"]


def test_us5001_ca03_servidor_caido_o_sin_modelo_no_afecta_a_los_demas(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    caido = _status(_router(service, jev_url=f"http://127.0.0.1:{free_port()}", jev_model="laya", **_ollama(ollama)))
    assert caido["jev:laya"]["status"] == "error" and "no accesible" in caido["jev:laya"]["detail"]
    assert caido["ollama-decide:qwen2.5:0.5b"]["status"] == "ok" and caido["rules"]["status"] == "ok"
    sin_modelo = _status(_router(service, jev_url=ollaya.url, jev_model="kev"))["jev:kev"]
    assert sin_modelo["status"] == "error" and "no está instalado" in sin_modelo["detail"]


def test_us5001_ca04_configuracion_incompleta(service: ProjectService, ollaya: FakeOllaya) -> None:
    with pytest.raises(InvalidArgument, match="ACM_JEV_MODEL necesita ACM_JEV_URL"):
        build_engines(service, Settings(data_dir=service.data_dir, jev_model="laya"))
    # Solo la URL: los modelos se descubren y se eligen después en ACM (US-50.09); decidir sin modelo es un error claro.
    router = _router(service, jev_url=ollaya.url)
    row = _status(router)["jev:-"]
    assert row["status"] == "error" and "ningún modelo por defecto" in row["detail"]
    with pytest.raises(EngineUnavailable, match="no hay modelo de Ollaya para este propósito"):
        router.decide(ADMIN, _request())


# ---------------------------------------------------------------- US-50.02 el agente pide una evaluación JEV
@pytest.mark.anyio
async def test_us5002_ca01_acm_decide_responde_jev_calibrado(service: ProjectService, ollaya: FakeOllaya) -> None:
    router = _router(service, **_jev(ollaya))
    async with Client(build_mcp_server(service, lambda: ADMIN, engines=router)) as client:
        res = await client.call_tool(
            "acm_decide",
            {"project_id": P, "purpose": "ticket.triage", "questions": QUESTIONS, "state": "Me cobraron dos veces."},
        )
    assert not res.is_error, res.content
    out = res.structured_content
    assert out["engine"] == "jev:laya" and out["fallback_from"] is None
    assert all(a["calibrated"] for a in out["answers"].values())
    dept = out["answers"]["department"]
    assert dept["value"] == "billing" and dept["confidence"] == 0.78 and dept["probabilities"]["billing"] == 0.85
    sent = ollaya.state.requests[-1]["body"]
    assert sent["model"] == "laya" and sent["state"] == "Me cobraron dos veces." and sent["keep_alive"] == "10m"
    assert sent["questions"]["department"]["criteria"] == QUESTIONS["department"]["criteria"]
    assert "criteria" not in sent["questions"]["refund"]  # noul sin criterios: no se inventan


def test_us5002_ca02_traduccion_al_contrato_de_acm(service: ProjectService, ollaya: FakeOllaya) -> None:
    result = _router(service, **_jev(ollaya)).decide(ADMIN, _request()).result
    urgency, refund = result.answers["urgency"], result.answers["refund"]
    assert urgency.value == pytest.approx(2.1982)  # Ollaya 0..n-1 → ACM 1..n (como las reglas)
    assert urgency.probabilities == {"baja": 0.2, "media": 0.6, "alta": 0.2}  # por nivel, no por índice
    assert refund.value == pytest.approx(0.9127)
    assert refund.probabilities == pytest.approx({"true": 0.9127, "false": 0.0873})
    assert result.usage == {"input_tokens": 118, "output_tokens": 0}


@pytest.mark.parametrize("mode", ["invalid", "missing_answer", "bad_choice"])
def test_us5002_ca03_respuesta_invalida_es_engine_error(
    service: ProjectService, ollaya: FakeOllaya, data_dir: Path, mode: str
) -> None:
    ollaya.state.mode = mode
    with pytest.raises(EngineUnavailable, match="jev:laya → ENGINE_ERROR"):
        _router(service, **_jev(ollaya)).decide(ADMIN, _request())
    assert _calls(data_dir)[-1]["status"] == "error"


@pytest.mark.parametrize("mode", ["queue_full", "load_failed"])
def test_us5002_ca03_servidor_ocupado_es_no_disponible(service: ProjectService, ollaya: FakeOllaya, mode: str) -> None:
    ollaya.state.mode = mode
    engine = JevDecisionEngine(OllayaClient(ollaya.url), "laya")
    with pytest.raises(EngineUnavailable, match="QUEUE_FULL|MODEL_LOAD_FAILED"):
        engine.decide(_request())
    ollaya.state.mode = "invalid"
    with pytest.raises(EngineError, match="422 INVALID_REQUEST"):
        engine.decide(_request())
    engine.close()


# ---------------------------------------------------------------- US-50.03 generativo → Ollama, decisional → JEV
def test_us5003_ca01_decision_a_jev_y_resumen_a_ollama(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_jev(ollaya), **_ollama(ollama))
    assert router.decide(ADMIN, _request()).result.engine == "jev:laya"
    backlog = BacklogService(service, router)
    backlog.create_requirement(ADMIN, P, "Gestionar proyectos", "x" * 3000)
    backlog.create_epic(ADMIN, P, "Proyectos", "Objetivo", "Alcance", ["REQ-001"])
    backlog.create_feature(ADMIN, P, "EPIC-01", "Creación")
    backlog.create_story(ADMIN, P, "FEAT-01.01", "operador", "crear", "separar", ["REQ-001"], ["CA"])
    ctx = ContextService(service, backlog, router).compact(ADMIN, P, "US-01.01", 128)
    assert ctx["summarized"] and ctx["summary_engine"] == "ollama:qwen2.5:0.5b"
    assert [r["path"] for r in ollaya.state.requests].count("/api/decide") == 1
    assert "format" not in ollama.state.requests[-1]["body"]  # el resumen no es una decisión


def test_us5003_ca02_sin_jev_decide_ollama_sin_calibrar(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, jev_url=f"http://127.0.0.1:{free_port()}", jev_model="laya", **_ollama(ollama))
    result = router.decide(ADMIN, _request()).result
    assert result.engine == "ollama-decide:qwen2.5:0.5b" and result.fallback_from == "jev:laya"
    assert not any(a.calibrated for a in result.answers.values())


def test_us5003_ca03_orden_por_proyecto_sin_reiniciar(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_jev(ollaya), **_ollama(ollama))
    service.set_config(ADMIN, P, {"decision.engine_order": ["ollama", "jev"]})
    assert router.decide(ADMIN, _request()).result.engine == "ollama-decide:qwen2.5:0.5b"
    service.set_config(ADMIN, P, {"decision.engine_order": ["rules"]})
    with pytest.raises(EngineUnavailable, match="ningún motor"):
        router.decide(ADMIN, _request())


# ---------------------------------------------------------------- US-50.04 qué motor produjo cada decisión
@pytest.mark.anyio
async def test_us5004_ca01_ca02_cada_decision_registra_su_motor(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama, data_dir: Path
) -> None:
    router = _router(service, **_jev(ollaya), **_ollama(ollama))
    async with Client(build_mcp_server(service, lambda: ADMIN, engines=router)) as client:
        args = {"project_id": P, "purpose": "ticket.triage", "questions": QUESTIONS, "state": "texto"}
        first = (await client.call_tool("acm_decide", args)).structured_content
        service.set_config(ADMIN, P, {"decision.engine_order": ["ollama"]})
        second = (await client.call_tool("acm_decide", args)).structured_content
    calls = {c["id"]: c for c in _calls(data_dir)}
    for out, engine in ((first, "jev:laya"), (second, "ollama-decide:qwen2.5:0.5b")):
        row = calls[out["call_id"]]
        assert out["engine"] == engine
        assert (row["kind"], row["purpose"], row["project_id"], row["engine"], row["status"]) == (
            "decision",
            "ticket.triage",
            P,
            engine,
            "ok",
        )
    assert calls[first["call_id"]]["input_tokens"] == 118


# ---------------------------------------------------------------- US-22.04 conectar una instancia Ollama
def test_us2204_ca01_registra_generacion_y_decision(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, **_ollama(ollama))
    rows = _status(router)
    assert rows["ollama:qwen2.5:0.5b"]["kind"] == "generation"
    assert rows["ollama-decide:qwen2.5:0.5b"]["kind"] == "decision"
    assert all(rows[n]["status"] == "ok" for n in ("ollama:qwen2.5:0.5b", "ollama-decide:qwen2.5:0.5b"))


def test_us2204_ca02_solo_elige_entre_las_opciones(service: ProjectService, ollama: FakeOllama) -> None:
    ollama.state.decisions = {"department": "account", "urgency": "alta", "refund": "false"}
    engine = OllamaDecisionEngine(OllamaClient(ollama.url), "qwen2.5:0.5b")
    result = engine.decide(_request())
    body = ollama.state.requests[-1]["body"]
    props = body["format"]["properties"]
    assert props["department"]["enum"] == ["billing", "technical", "account"]
    assert props["urgency"]["enum"] == ["baja", "media", "alta"] and props["refund"]["enum"] == ["true", "false"]
    assert body["format"]["required"] == ["department", "urgency", "refund"]
    assert body["messages"][0]["role"] == "system" and DECISION_PROMPT_VERSION == "ollama-decide@v1"
    a = result.answers
    assert (a["department"].value, a["urgency"].value, a["refund"].value) == ("account", 3.0, 0.0)
    assert all(not x.calibrated and x.probabilities is None for x in a.values())
    engine.close()


def test_us2204_ca03_el_gate_no_acepta_a_ollama(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, **_ollama(ollama))
    backlog = BacklogService(service, router)
    backlog.create_requirement(ADMIN, P, "R")
    backlog.create_epic(ADMIN, P, "E", "o", "s", ["REQ-001"])
    backlog.create_feature(ADMIN, P, "EPIC-01", "F")
    backlog.create_story(ADMIN, P, "FEAT-01.01", "a", "b", "c", ["REQ-001"], ["CA"])
    service.set_config(ADMIN, P, {"decision.engine_order": ["ollama"]})
    with pytest.raises(FailedPrecondition, match="no calibrad"):
        backlog.mark_ready(ADMIN, P, "US-01.01")
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"


def test_us2204_ca04_respuesta_fuera_de_opciones_es_error(service: ProjectService, ollama: FakeOllama) -> None:
    ollama.state.decisions = {"department": "marketing"}
    with pytest.raises(EngineUnavailable, match="ENGINE_ERROR.*no es una opción"):
        _router(service, **_ollama(ollama)).decide(ADMIN, _request())
