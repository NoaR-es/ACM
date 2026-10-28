"""US-35.08 (contexto compacto) y US-35.09 (tokens ahorrados)."""

from __future__ import annotations

import json
import math
from collections.abc import Iterator

import pytest
from mcp import Client

from acm.app import build_engines
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.context import ESTIMATION_METHOD, ContextService, estimate_tokens
from acm.domain.errors import Forbidden, InvalidArgument, NotFound
from acm.domain.projects import ProjectService
from acm.inference.ports import EngineError, EngineHealth, GenerationRequest, GenerationResult
from acm.inference.router import EngineRouter
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN, add_member
from tests.fake_ollama import FakeOllama

P = "alpha"
LONG = "El sistema debe permitir gestionar proyectos con total trazabilidad y sin mezclar contextos. " * 30


class SpyGen:
    """Motor de generación de prueba: «resume» devolviendo la primera frase de la entrada."""

    provider = "ollama"

    def __init__(self, *, fail: bool = False, name: str = "ollama:spy"):
        self.name, self.fail = name, fail
        self.requests: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.requests.append(request)
        if self.fail:
            raise EngineError("respuesta vacía")
        return GenerationResult(request.messages[-1]["content"][:80] + " [resumen]", self.name, {}, 1.0)

    def health(self) -> EngineHealth:
        return EngineHealth(True)


def _seed(service: ProjectService, project: str = P) -> BacklogService:
    service.create(ADMIN, project, project)
    b = BacklogService(service)
    b.create_requirement(ADMIN, project, "Gestionar proyectos", LONG)
    b.create_requirement(ADMIN, project, "Aislar contextos", LONG)
    b.create_epic(ADMIN, project, "Proyectos", LONG, "Crear, abrir y configurar", ["REQ-001", "REQ-002"])
    b.create_feature(ADMIN, project, "EPIC-01", "Creación", LONG)
    b.create_story(
        ADMIN,
        project,
        "FEAT-01.01",
        "operador",
        "crear proyectos",
        "separar contextos",
        ["REQ-001", "REQ-002"],
        ["Un nombre vacío se rechaza", "Un duplicado no se crea"],
    )
    for i in range(6):
        b.create_story(
            ADMIN,
            project,
            "FEAT-01.01",
            "operador",
            f"historia hermana {i} " + "x" * 200,
            "valor",
            ["REQ-001"],
            ["criterio " + "y" * 200],
        )
    return b


def _context(service: ProjectService, *engines: object) -> ContextService:
    router = EngineRouter(service)
    for e in engines:
        router.registry.register(e)  # type: ignore[arg-type]
    return ContextService(service, BacklogService(service, router), router)


@pytest.fixture
def seeded(service: ProjectService) -> ProjectService:
    _seed(service)
    return service


# ---------------------------------------------------------------- US-35.08
def test_us3508_ca01_tamanos_entregado_y_completo(seeded: ProjectService) -> None:
    out = _context(seeded).compact(ADMIN, P, "US-01.01")
    assert out["delivered_tokens"] == math.ceil(len(json.dumps(out["sections"], ensure_ascii=False)) / 4)
    assert out["full_equivalent_tokens"] > out["delivered_tokens"] > 0
    assert out["saved_tokens"] == out["full_equivalent_tokens"] - out["delivered_tokens"]
    assert out["estimation_method"] == ESTIMATION_METHOD == "chars/4@v1"
    assert out["budget_tokens"] == 8000 and out["within_budget"]  # context.max_tokens del proyecto


def test_us3508_ca02_fragmentos_identifican_fuentes(seeded: ProjectService) -> None:
    gen = SpyGen()
    out = _context(seeded, gen).compact(ADMIN, P, "US-01.01", budget_tokens=600)
    assert out["summarized"] and out["summary_engine"] == "ollama:spy" and gen.requests
    by_name = {s["name"]: s for s in out["sections"]}
    assert by_name["requirements"]["sources"] == ["REQ-001", "REQ-002"]
    assert by_name["epic"]["sources"] == ["EPIC-01"]
    assert by_name["related_stories"]["sources"] == [f"US-01.0{i}" for i in range(2, 8)]
    summarized = [s for s in out["sections"] if s["summarized"]]
    assert summarized and all(s["sources"] and s["content"].endswith("[resumen]") for s in summarized)
    assert all(r.purpose == "context.compact" and r.project_id == P for r in gen.requests)


def test_us3508_ca03_sin_modelo_sin_resumir(seeded: ProjectService) -> None:
    out = _context(seeded).compact(ADMIN, P, "US-01.01", budget_tokens=600)
    assert not out["summarized"] and not out["within_budget"]
    assert out["not_summarized_reason"] == "no hay modelo local de generación configurado"
    assert not any(s["summarized"] for s in out["sections"])
    assert LONG.strip() in next(s for s in out["sections"] if s["name"] == "requirements")["content"]


def test_us3508_ca03_modelo_caido_entrega_sin_resumir(seeded: ProjectService) -> None:
    out = _context(seeded, SpyGen(fail=True)).compact(ADMIN, P, "US-01.01", budget_tokens=600)
    assert not out["summarized"] and out["not_summarized_reason"].startswith("no se pudo resumir: ENGINE_ERROR")
    assert not any(s["summarized"] for s in out["sections"])


def test_us3508_historia_y_criterios_siempre_literales(seeded: ProjectService) -> None:
    out = _context(seeded, SpyGen()).compact(ADMIN, P, "US-01.01", budget_tokens=64)
    by_name = {s["name"]: s for s in out["sections"]}
    assert by_name["story"]["content"].startswith("US-01.01 [PLANNED] (user_story) Como operador, quiero crear")
    assert (
        by_name["acceptance_criteria"]["content"] == "CA-01: Un nombre vacío se rechaza\nCA-02: Un duplicado no se crea"
    )
    assert not by_name["story"]["summarized"] and not by_name["acceptance_criteria"]["summarized"]


@pytest.mark.parametrize("budget", [0, 63, 200_001, "mucho", True])
def test_us3508_presupuesto_invalido(seeded: ProjectService, budget: object) -> None:
    with pytest.raises(InvalidArgument, match="budget_tokens"):
        _context(seeded).compact(ADMIN, P, "US-01.01", budget_tokens=budget)


def test_us3508_proyecto_ajeno_rechazado(seeded: ProjectService, data_dir) -> None:
    _seed(seeded, "beta")
    add_member(data_dir, "beta", "agente-b")
    with pytest.raises(NotFound):
        _context(seeded).compact("agente-b", P, "US-01.01")


@pytest.fixture
def ollama() -> Iterator[FakeOllama]:
    with FakeOllama() as fake:
        yield fake


def test_us3508_resumen_con_ollama_simulado(seeded: ProjectService, ollama: FakeOllama) -> None:
    ollama.state.reply = "Requisitos REQ-001 y REQ-002: gestionar y aislar proyectos."
    router = build_engines(
        seeded, Settings(data_dir=seeded.data_dir, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    )
    out = ContextService(seeded, BacklogService(seeded, router), router).compact(
        ADMIN, P, "US-01.01", budget_tokens=600
    )
    assert out["summarized"] and out["summary_engine"] == "ollama:qwen2.5:0.5b"
    chats = [r for r in ollama.state.requests if r["path"] == "/api/chat"]
    assert chats and all(c["body"]["model"] == "qwen2.5:0.5b" for c in chats)
    assert out["delivered_tokens"] < estimate_tokens(
        ContextService(seeded, BacklogService(seeded), EngineRouter(seeded))._gather(ADMIN, P, "US-01.01")[0]
    )


# ---------------------------------------------------------------- US-35.09
def _deliveries(service: ProjectService) -> list[dict]:
    with service.global_db.read() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM context_deliveries ORDER BY id")]


def test_us3509_ca01_cada_entrega_registrada(seeded: ProjectService) -> None:
    ctx = _context(seeded)
    a = ctx.compact(ADMIN, P, "US-01.01")
    b = ctx.compact(ADMIN, P, "US-01.02")
    rows = _deliveries(seeded)
    assert [r["id"] for r in rows] == [a["delivery_id"], b["delivery_id"]]
    assert (rows[0]["delivered_tokens"], rows[0]["full_tokens"]) == (a["delivered_tokens"], a["full_equivalent_tokens"])
    assert rows[1]["story_id"] == "US-01.02" and rows[1]["principal"] == ADMIN


def test_us3509_ca02_agregado_por_agente_y_proyecto(seeded: ProjectService, data_dir) -> None:
    _seed(seeded, "beta")
    add_member(data_dir, P, "agente-a")
    ctx = _context(seeded)
    ctx.compact(ADMIN, P, "US-01.01")
    ctx.compact(ADMIN, "beta", "US-01.01")
    ctx.compact("agente-a", P, "US-01.01")
    ctx.compact("agente-a", P, "US-01.02")
    report = ctx.savings_report(ADMIN)
    keys = [(g["principal"], g["project_id"], g["deliveries"]) for g in report["groups"]]
    assert keys == [("agente-a", P, 2), (ADMIN, P, 1), (ADMIN, "beta", 1)]
    assert report["totals"]["deliveries"] == 4
    assert report["totals"]["saved"] == sum(g["saved"] for g in report["groups"])
    only_a = ctx.savings_report(ADMIN, filter_principal="agente-a")
    assert [g["principal"] for g in only_a["groups"]] == ["agente-a"]
    only_beta = ctx.savings_report(ADMIN, project_id="beta")
    assert [g["project_id"] for g in only_beta["groups"]] == ["beta"]


def test_us3509_ca03_metodo_indicado(seeded: ProjectService) -> None:
    ctx = _context(seeded)
    ctx.compact(ADMIN, P, "US-01.01")
    report = ctx.savings_report(ADMIN)
    assert report["methods"] == ["chars/4@v1"] and report["groups"][0]["method"] == "chars/4@v1"


def test_us3509_solo_admin(seeded: ProjectService) -> None:
    seeded.ensure_principal("bob", "user")
    with pytest.raises(Forbidden):
        _context(seeded).savings_report("bob")


@pytest.mark.anyio
async def test_us3508_us3509_por_mcp(seeded: ProjectService) -> None:
    async with Client(build_mcp_server(seeded, lambda: ADMIN)) as client:
        ctx = await client.call_tool("acm_context_compact", {"project_id": P, "story_id": "US-01.01"})
        report = await client.call_tool("acm_savings_report", {"project_id": P})
    assert not ctx.is_error and ctx.structured_content["project_id"] == P
    assert report.structured_content["totals"]["deliveries"] == 1


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
