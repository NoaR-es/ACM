"""US-35.10, US-35.11, US-47.01 (interfaz de decisión, reglas, router) y US-22.01, US-22.03 (Ollama simulado)."""

from __future__ import annotations

import ast
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from mcp import Client

import acm
from acm.app import build_engines
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.errors import FailedPrecondition, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from acm.inference.ollama import OllamaClient, OllamaGenerationEngine
from acm.inference.ports import (
    Answer,
    DecisionEngine,
    DecisionRequest,
    DecisionResult,
    EngineError,
    EngineHealth,
    EngineUnavailable,
    GenerationEngine,
    GenerationRequest,
    Question,
)
from acm.inference.router import EngineRegistry, EngineRouter
from acm.inference.rules import RulesDecisionEngine
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN
from tests.fake_ollama import FakeOllama, free_port

P = "alpha"


class FakeJev:
    """Motor de decisión con el mismo contrato que tendrá el adaptador JEV (EPIC-50): cubre cualquier pregunta."""

    def __init__(self, *, fail: bool = False, calibrated: bool = True, name: str = "jev:test", provider: str = "jev"):
        self.name, self.provider, self.fail, self.calibrated = name, provider, fail, calibrated
        self.seen: list[DecisionRequest] = []

    def supports(self, request: DecisionRequest) -> bool:
        return True

    def decide(self, request: DecisionRequest) -> DecisionResult:
        self.seen.append(request)
        if self.fail:
            raise EngineUnavailable("Ollaya no responde")
        answers = {}
        for key, q in request.questions.items():
            opts = q.options()
            probs = {o: (0.9 if i == 0 else 0.1 / (len(opts) - 1)) for i, o in enumerate(opts)}
            value: str | float = probs["true"] if q.type == "noul" else (opts[0] if q.type == "choice" else 1.2)
            answers[key] = Answer(q.type, value, probs, 0.9, self.calibrated)
        return DecisionResult(answers, self.name, {"input_tokens": 10, "output_tokens": 1}, 1.0)

    def health(self) -> EngineHealth:
        return EngineHealth(not self.fail, "simulado")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def router(service: ProjectService) -> EngineRouter:
    service.create(ADMIN, P, "Alpha")
    return EngineRouter(service)


@pytest.fixture
def backlog(service: ProjectService, router: EngineRouter) -> BacklogService:
    b = BacklogService(service, router)
    b.create_requirement(ADMIN, P, "Gestionar proyectos")
    b.create_epic(ADMIN, P, "Proyectos", "Gestionar proyectos", "Crear y abrir", ["REQ-001"])
    b.create_feature(ADMIN, P, "EPIC-01", "Creación")
    b.create_story(
        ADMIN,
        P,
        "FEAT-01.01",
        "operador",
        "crear proyectos",
        "separar contextos",
        ["REQ-001"],
        ["Un nombre vacío se rechaza"],
    )
    b.create_story(ADMIN, P, "FEAT-01.01", "operador", "abrir proyectos", "trabajar", ["REQ-001"])
    return b


def _quality(state: dict, **questions: Question) -> DecisionRequest:
    return DecisionRequest(state=state, questions=questions, purpose="story.quality", project_id=P)


def _calls(data_dir: Path) -> list[dict]:
    conn = sqlite3.connect(data_dir / "acm.db")
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM inference_calls ORDER BY id")]
    conn.close()
    return rows


def _order(service: ProjectService, *providers: str) -> None:
    service.set_config(ADMIN, P, {"decision.engine_order": list(providers)})


ALL_QUESTIONS = {
    "readiness": {"type": "choice", "instructions": "¿lista?", "criteria": {"ready": "sí", "not_ready": "no"}},
    "has_acceptance_criteria": {"type": "noul", "instructions": "¿tiene CA?"},
    "completeness": {"type": "score", "instructions": "¿cuánto?", "criteria": ["0", "1", "2", "3", "4"]},
}


# ---------------------------------------------------------------- US-35.10
@pytest.mark.anyio
async def test_us3510_ca01_respuesta_tipada_con_probabilidades(
    service: ProjectService, backlog: BacklogService
) -> None:
    async with Client(build_mcp_server(service, lambda: ADMIN, engines=backlog.decisions)) as client:
        story = (await client.call_tool("acm_story_get", {"project_id": P, "story_id": "US-01.02"})).structured_content
        res = await client.call_tool(
            "acm_decide", {"project_id": P, "purpose": "story.quality", "questions": ALL_QUESTIONS, "state": story}
        )
    assert not res.is_error, res.content
    out = res.structured_content
    assert out["project_id"] == P
    answers = out["answers"]
    assert answers["readiness"]["type"] == "choice" and answers["readiness"]["value"] == "not_ready"
    assert answers["has_acceptance_criteria"] == {
        "type": "noul",
        "value": 0.0,
        "probabilities": {"true": 0.0, "false": 1.0},
        "confidence": 1.0,
        "calibrated": True,
    }
    assert answers["completeness"]["type"] == "score" and answers["completeness"]["value"] == 4.0  # 3/4 + 1
    for a in answers.values():
        assert abs(sum(a["probabilities"].values()) - 1.0) < 1e-9


def test_us3510_ca02_motor_registrado(backlog: BacklogService, router: EngineRouter, data_dir: Path) -> None:
    story = backlog.get_story(ADMIN, P, "US-01.01")
    routed = router.decide(ADMIN, _quality(story, has_statement=Question("noul", "?")))
    assert routed.result.engine == "rules"
    row = next(c for c in _calls(data_dir) if c["id"] == routed.call_id)
    assert (row["engine"], row["status"], row["purpose"], row["project_id"], row["principal"]) == (
        "rules",
        "ok",
        "story.quality",
        P,
        ADMIN,
    )


def test_us3510_ca03_sin_motor_error_explicito(router: EngineRouter, data_dir: Path) -> None:
    request = DecisionRequest({"bug": "x"}, {"severity": Question("score", "?", ["baja", "alta"])}, "bug.severity", P)
    with pytest.raises(EngineUnavailable, match="ningún motor de .* cubre el propósito 'bug.severity'"):
        router.decide(ADMIN, request)
    assert _calls(data_dir)[-1]["status"] == "error"


def test_us3510_ca03_fallback_indicado(
    service: ProjectService, backlog: BacklogService, router: EngineRouter, data_dir: Path
) -> None:
    router.registry.register(FakeJev(fail=True))
    _order(service, "jev", "rules")
    story = backlog.get_story(ADMIN, P, "US-01.01")
    routed = router.decide(ADMIN, _quality(story, has_statement=Question("noul", "?")))
    assert routed.result.engine == "rules" and routed.result.fallback_from == "jev:test"
    assert _calls(data_dir)[-1]["fallback_from"] == "jev:test"


@pytest.mark.parametrize(
    "questions",
    [
        {},
        {"q": {"type": "maybe"}},
        {"q": {"type": "choice", "criteria": {"solo": "una"}}},
        {"q": {"type": "score", "criteria": ["uno"]}},
        {"q": {"type": "noul", "criteria": {"quizá": "x"}}},
    ],
)
def test_us3510_peticion_invalida_rechazada(questions: dict) -> None:
    with pytest.raises(InvalidArgument):
        DecisionRequest.from_json(P, "story.quality", {}, questions)


def test_us3510_proyecto_ajeno_rechazado(
    service: ProjectService, router: EngineRouter, backlog: BacklogService
) -> None:
    service.ensure_principal("intruso", "user")  # conocido, pero sin acceso a alpha
    story = backlog.get_story(ADMIN, P, "US-01.01")
    with pytest.raises(NotFound):
        router.decide("intruso", _quality(story, has_statement=Question("noul", "?")))


# ---------------------------------------------------------------- US-35.11
def test_us3511_ca01_gate_y_herramienta_usan_el_router(
    service: ProjectService, backlog: BacklogService, router: EngineRouter
) -> None:
    jev = FakeJev()
    router.registry.register(jev)
    _order(service, "jev", "rules")
    assert backlog.mark_ready(ADMIN, P, "US-01.01")["status"] == "READY"
    assert [r.purpose for r in jev.seen] == ["story.quality"]  # el gate READY decidió a través del router
    assert set(jev.seen[0].questions) == {
        "has_statement",
        "has_requirements",
        "has_acceptance_criteria",
        "technical_reason_ok",
    }


def test_us3511_ca02_reglas_sin_modelo(backlog: BacklogService, router: EngineRouter) -> None:
    assert [e.provider for e in router.registry.decision] == ["rules"] and not router.has_generation()
    with pytest.raises(FailedPrecondition, match="sin criterios de aceptación"):
        backlog.mark_ready(ADMIN, P, "US-01.02")
    assert backlog.mark_ready(ADMIN, P, "US-01.01")["status"] == "READY"


def test_us3511_ca03_conectar_jev_no_cambia_consumidores(
    service: ProjectService, backlog: BacklogService, router: EngineRouter
) -> None:
    request = DecisionRequest({"bug": "x"}, {"severity": Question("score", "?", ["baja", "alta"])}, "bug.severity", P)
    with pytest.raises(EngineUnavailable):
        router.decide(ADMIN, request)
    router.registry.register(FakeJev())  # conectar JEV = registrar el motor; ningún consumidor cambia
    routed = router.decide(ADMIN, request)
    assert routed.result.engine == "jev:test" and routed.result.answers["severity"].calibrated
    # orden por defecto rules → jev → ollama: lo que cubren las reglas lo siguen respondiendo las reglas
    assert backlog.mark_ready(ADMIN, P, "US-01.01")["status"] == "READY"


def test_us3511_gate_rechaza_motor_no_calibrado(
    service: ProjectService, backlog: BacklogService, router: EngineRouter
) -> None:
    router.registry.register(FakeJev(calibrated=False, name="ollama:llm", provider="ollama"))
    _order(service, "ollama", "rules")
    with pytest.raises(FailedPrecondition, match="no calibradas.*revisión humana"):
        backlog.mark_ready(ADMIN, P, "US-01.01")
    assert backlog.get_story(ADMIN, P, "US-01.01")["status"] == "PLANNED"


def test_us3511_gate_detecta_cambio_durante_la_decision(
    service: ProjectService, backlog: BacklogService, router: EngineRouter
) -> None:
    class Racing(FakeJev):
        def decide(self, request: DecisionRequest) -> DecisionResult:
            backlog.add_criteria(ADMIN, P, "US-01.01", ["Criterio añadido en paralelo"])
            return super().decide(request)

    router.registry.register(Racing())
    _order(service, "jev", "rules")
    with pytest.raises(FailedPrecondition, match="cambió mientras se validaba"):
        backlog.mark_ready(ADMIN, P, "US-01.01")


# ---------------------------------------------------------------- US-47.01
CONSUMERS = ("domain/backlog.py", "domain/context.py", "mcp_server.py")


def test_us4701_ca01_consumidores_no_dependen_de_implementacion() -> None:
    root = Path(acm.__file__).parent
    for rel in CONSUMERS:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        assert not imported & {"acm.inference.rules", "acm.inference.ollama"}, rel


def test_us4701_ca02_interfaz_abstracta(service: ProjectService) -> None:
    assert isinstance(RulesDecisionEngine(), DecisionEngine)
    assert isinstance(OllamaGenerationEngine(OllamaClient("http://127.0.0.1:1"), "m"), GenerationEngine)
    assert isinstance(FakeJev(), DecisionEngine)
    registry = EngineRegistry(service)
    with pytest.raises(InvalidArgument, match="no implementa"):
        registry.register(type("Nada", (), {"name": "x", "provider": "y"})())  # type: ignore[arg-type]
    registry.register(RulesDecisionEngine())
    with pytest.raises(InvalidArgument, match="ya hay un motor"):
        registry.register(RulesDecisionEngine())


@pytest.mark.anyio
async def test_us4701_ca03_implementacion_actual_sigue_funcionando(service: ProjectService) -> None:
    async with Client(build_mcp_server(service, lambda: ADMIN)) as client:
        await client.call_tool("acm_project_create", {"key": P, "name": "Alpha"})
        await client.call_tool("acm_requirement_create", {"project_id": P, "title": "R"})
        await client.call_tool("acm_epic_create", {"project_id": P, "title": "E", "objective": "o", "scope": "s"})
        await client.call_tool("acm_feature_create", {"project_id": P, "epic_id": "EPIC-01", "title": "F"})
        await client.call_tool(
            "acm_story_create",
            {
                "project_id": P,
                "feature_id": "FEAT-01.01",
                "as_a": "a",
                "i_want": "b",
                "so_that": "c",
                "requirement_ids": ["REQ-001"],
                "acceptance_criteria": ["x"],
            },
        )
        ready = await client.call_tool("acm_story_mark_ready", {"project_id": P, "story_id": "US-01.01"})
        engines = (await client.call_tool("acm_engines_list", {})).structured_content
    assert not ready.is_error and ready.structured_content["status"] == "READY"
    assert [e["name"] for e in engines["engines"] if e["registered"]] == ["rules"]
    assert "readiness" in engines["rules"]["story.quality"]


# ---------------------------------------------------------------- US-22.01 / US-22.03 (Ollama simulado)
@pytest.fixture
def ollama() -> Iterator[FakeOllama]:
    with FakeOllama() as fake:
        yield fake


def _ollama_router(service: ProjectService, url: str, model: str = "qwen2.5:0.5b") -> EngineRouter:
    return build_engines(service, Settings(data_dir=service.data_dir, ollama_url=url, ollama_model=model))


def test_us2201_ca01_consulta_el_runtime_configurado(service: ProjectService, ollama: FakeOllama) -> None:
    router = _ollama_router(service, ollama.url)
    rows = {r["name"]: r for r in router.registry.refresh()}
    assert ollama.state.requests[-1] == {"path": "/api/tags"}
    assert rows["ollama:qwen2.5:0.5b"]["endpoint"] == ollama.url and rows["ollama:qwen2.5:0.5b"]["status"] == "ok"


def test_us2201_ca02_modelos_detectados_identificados(service: ProjectService, ollama: FakeOllama) -> None:
    router = _ollama_router(service, ollama.url)
    row = next(r for r in router.registry.refresh() if r["provider"] == "ollama")
    assert row["models"] == ["llama3.2:1b", "qwen2.5:0.5b"] and row["checked_at"]


def test_us2201_ca03_runtime_inaccesible_estado_error(service: ProjectService) -> None:
    router = _ollama_router(service, f"http://127.0.0.1:{free_port()}")
    row = next(r for r in router.registry.refresh() if r["provider"] == "ollama")
    assert row["status"] == "error" and "no accesible" in row["detail"] and row["models"] == []


def test_us2201_ca04_no_afirma_modelo_no_detectado(service: ProjectService, ollama: FakeOllama) -> None:
    router = _ollama_router(service, ollama.url, model="inventado:7b")
    row = next(r for r in router.registry.refresh() if r["provider"] == "ollama")
    assert row["status"] == "error" and "no está instalado" in row["detail"]
    assert "inventado:7b" not in row["models"]


def test_us2201_configuracion_incompleta_rechazada(service: ProjectService) -> None:
    with pytest.raises(InvalidArgument, match="deben configurarse juntos"):
        build_engines(service, Settings(data_dir=service.data_dir, ollama_url="http://127.0.0.1:1"))


def _gen(max_tokens: int = 50) -> GenerationRequest:
    return GenerationRequest([{"role": "user", "content": "Resume REQ-001"}], "context.compact", P, max_tokens)


def test_us2203_ca01_peticion_llega_al_modelo_configurado(service: ProjectService, ollama: FakeOllama) -> None:
    service.create(ADMIN, P, "Alpha")
    result = _ollama_router(service, ollama.url).generate(ADMIN, _gen(33)).result
    body = ollama.state.requests[-1]["body"]
    assert body["model"] == "qwen2.5:0.5b" and body["stream"] is False and body["options"] == {"num_predict": 33}
    assert body["messages"] == [{"role": "user", "content": "Resume REQ-001"}]
    assert result.text == ollama.state.reply and result.engine == "ollama:qwen2.5:0.5b"


def test_us2203_ca02_respuesta_vinculada_a_la_ejecucion(
    service: ProjectService, ollama: FakeOllama, data_dir: Path
) -> None:
    service.create(ADMIN, P, "Alpha")
    routed = _ollama_router(service, ollama.url).generate(ADMIN, _gen())
    row = next(c for c in _calls(data_dir) if c["id"] == routed.call_id)
    assert (row["kind"], row["engine"], row["status"], row["input_tokens"], row["output_tokens"]) == (
        "generation",
        "ollama:qwen2.5:0.5b",
        "ok",
        42,
        7,
    )


@pytest.mark.parametrize("url_kind", ["caido", "error500"])
def test_us2203_ca03_fallo_del_modelo_estado_error(
    service: ProjectService, ollama: FakeOllama, data_dir: Path, url_kind: str
) -> None:
    service.create(ADMIN, P, "Alpha")
    ollama.state.mode = "error500"
    url = ollama.url if url_kind == "error500" else f"http://127.0.0.1:{free_port()}"
    with pytest.raises(EngineUnavailable):
        _ollama_router(service, url).generate(ADMIN, _gen())
    assert _calls(data_dir)[-1]["status"] == "error"


@pytest.mark.parametrize("mode", ["empty", "not_done", "not_json"])
def test_us2203_ca04_sin_respuesta_valida_no_hay_exito(
    service: ProjectService, ollama: FakeOllama, data_dir: Path, mode: str
) -> None:
    service.create(ADMIN, P, "Alpha")
    ollama.state.mode = mode
    with pytest.raises(EngineError):
        _ollama_router(service, ollama.url).generate(ADMIN, _gen())
    assert _calls(data_dir)[-1]["status"] == "error"


@pytest.mark.anyio
async def test_engines_refresh_solo_admin(service: ProjectService) -> None:
    service.ensure_principal("bob", "user")
    async with Client(build_mcp_server(service, lambda: "bob")) as bob:
        res = await bob.call_tool("acm_engines_refresh", {})
    assert res.is_error and "FORBIDDEN" in res.content[0].text


def test_us2201_cierre_libera_el_cliente_http(service: ProjectService) -> None:
    router = _ollama_router(service, "http://127.0.0.1:1")
    engine = router.registry.generation[0]
    router.registry.close()
    assert engine.client._http.is_closed  # type: ignore[attr-defined]
