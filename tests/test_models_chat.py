"""Catálogo y selección de modelos (US-50.09, US-50.10, US-22.06, US-22.07) y conversación con el modelo local con
agente interno (US-22.10, US-22.11). Motores reales contra Ollama y Ollaya simulados; SQLite real.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from mcp import Client

from acm.app import build_engines
from acm.config import Settings
from acm.domain.backlog import BacklogService
from acm.domain.chat import HISTORY_MAX, MAX_TOOL_ROUNDS, TOOL_NAMES, ChatService
from acm.domain.errors import FailedPrecondition, Forbidden, InvalidArgument, NotFound
from acm.domain.models import ModelService
from acm.domain.projects import ProjectService
from acm.inference.ports import DecisionRequest, EngineError, EngineUnavailable
from acm.inference.router import EngineRouter
from acm.mcp_server import build_mcp_server
from tests.conftest import ADMIN
from tests.fake_ollama import FakeOllama
from tests.fake_ollaya import FakeOllaya

P = "alpha"
Q = {"ok": {"type": "noul", "instructions": "¿Está bien?"}}


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


def _router(service: ProjectService, **settings: str) -> EngineRouter:
    service.create(ADMIN, P, "Alpha")
    service.ensure_principal("bea", "user")
    return build_engines(service, Settings(data_dir=service.data_dir, **settings))  # type: ignore[arg-type]


def _both(ollaya: FakeOllaya, ollama: FakeOllama, **extra: str) -> dict[str, str]:
    return {"jev_url": ollaya.url, "ollama_url": ollama.url, **extra}


def _decide(router: EngineRouter, purpose: str, model: str | None = None) -> str:
    request = DecisionRequest.from_json(P, purpose, "texto", Q, model)
    return router.decide(ADMIN, request).result.engine


def _seed(service: ProjectService, router: EngineRouter) -> BacklogService:
    b = BacklogService(service, router)
    b.create_requirement(ADMIN, P, "Gestionar proyectos")
    b.create_epic(ADMIN, P, "Proyectos", "Gestionar", "Crear", ["REQ-001"])
    b.create_feature(ADMIN, P, "EPIC-01", "Creación")
    b.create_story(
        ADMIN, P, "FEAT-01.01", "operador", "crear proyectos", "separar", ["REQ-001"], ["Nombre vacío rechazado"]
    )
    return b


# ---------------------------------------------------------------- US-50.09 ver y elegir modelos
def test_us5009_ca01_muestra_modelos_detectados(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    cat = ModelService(service, _router(service, **_both(ollaya, ollama))).catalog(ADMIN)
    assert [m["name"] for m in cat["jev"]["available"]] == ["decider:latest", "laya:latest"]
    assert [m["name"] for m in cat["ollama"]["available"]] == ["llama3.2:1b", "qwen2.5:0.5b"]
    assert cat["ollama"]["available"][0]["details"]["parameter_size"] == "494M"
    assert cat["ollama"]["selected"] is None and cat["jev"]["default_model"] is None  # nada elegido: nada inventado


def test_us5009_ca02_elegir_uno_de_ollama_y_varios_de_ollaya(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_both(ollaya, ollama))
    cat = ModelService(service, router).select(
        ADMIN,
        ollama_model="llama3.2:1b",
        jev_default_model="laya",
        jev_models_by_purpose={"agile.sprint_review": "decider", "ticket.triage": "decider:latest"},
    )
    assert cat["ollama"]["selected"] == "llama3.2:1b" and cat["jev"]["default_model"] == "laya"
    by_name = {m["name"]: m for m in cat["jev"]["available"]}
    assert by_name["decider:latest"]["purposes"] == ["agile.sprint_review", "ticket.triage"]
    assert by_name["laya:latest"]["default"] and not by_name["decider:latest"]["default"]
    with pytest.raises(InvalidArgument, match="no está instalado") as err:
        ModelService(service, router).select(ADMIN, ollama_model="gpt-5")
    assert err.value.field == "ollama_model"
    with pytest.raises(InvalidArgument, match="no está instalado"):
        ModelService(service, router).select(ADMIN, jev_default_model="laya", jev_models_by_purpose={"x": "kev"})
    assert ModelService(service, router).catalog(ADMIN)["jev"]["models_by_purpose"]["ticket.triage"] == "decider:latest"


def test_us5009_ca03_se_aplica_sin_reiniciar_y_prevalece_sobre_el_arranque(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_both(ollaya, ollama, jev_model="laya", ollama_model="qwen2.5:0.5b"))
    assert _decide(router, "ticket.triage") == "jev:laya"
    ModelService(service, router).select(ADMIN, jev_default_model="decider", ollama_model="llama3.2:1b")
    assert _decide(router, "ticket.triage") == "jev:decider"  # mismo proceso, sin reiniciar
    other = build_engines(service, Settings(data_dir=service.data_dir, **_both(ollaya, ollama, jev_model="laya")))
    assert _decide(other, "ticket.triage") == "jev:decider"  # otro proceso: manda lo elegido en ACM
    service.set_config(ADMIN, P, {"decision.engine_order": ["ollama"]})
    assert _decide(router, "ticket.triage") == "ollama-decide:llama3.2:1b"
    assert ModelService(service, router).catalog(ADMIN)["ollama"]["source"] == "acm"


def test_us5009_ca04_notas_del_operador_y_solo_admin(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_both(ollaya, ollama))
    notes = {"decider:latest": "Sí/no rápidos sobre calidad", "laya:latest": "Clasificación general (enrutador)"}
    cat = ModelService(service, router).select(ADMIN, jev_model_notes=notes)
    assert {m["name"]: m["note"] for m in cat["jev"]["available"]} == notes
    with pytest.raises(Forbidden):
        ModelService(service, router).select("bea", ollama_model="llama3.2:1b")
    with pytest.raises(FailedPrecondition, match="JEV no está configurado"):
        ModelService(service, build_engines(service, Settings(data_dir=service.data_dir))).select(
            ADMIN, jev_default_model="laya"
        )


# ---------------------------------------------------------------- US-22.06 / US-22.07 modelo según la tarea
def test_us2206_us2207_modelo_segun_el_proposito(service: ProjectService, ollaya: FakeOllaya) -> None:
    router = _router(service, jev_url=ollaya.url, jev_model="laya")
    ModelService(service, router).select(ADMIN, jev_models_by_purpose={"agile.story_review": "decider"})
    assert _decide(router, "agile.story_review") == "jev:decider"  # el asignado a esa tarea
    assert _decide(router, "cualquier.otra") == "jev:laya"  # el de por defecto
    sent = [r["body"]["model"] for r in ollaya.state.requests if r["path"] == "/api/decide"]
    assert sent == ["decider", "laya"]


# ---------------------------------------------------------------- US-50.10 el agente conoce los modelos
@pytest.mark.anyio
async def test_us5010_ca01_ca02_catalogo_para_agentes(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_both(ollaya, ollama))
    ModelService(service, router).select(ADMIN, jev_default_model="laya", jev_model_notes={"laya:latest": "General"})
    async with Client(build_mcp_server(service, lambda: "bea", engines=router)) as agent:
        cat = (await agent.call_tool("acm_models_list", {})).structured_content
        denied = await agent.call_tool("acm_models_select", {"ollama_model": "llama3.2:1b"})
    laya = cat["jev"]["available"][1]
    assert (laya["name"], laya["default"], laya["purposes"], laya["note"]) == ("laya:latest", True, [], "General")
    # Guía de uso de cada modelo (fuente: README de Ollaya): qué es y para qué sirve.
    assert "Enrutador" in laya["guide"]["summary"] and "CPU" in laya["guide"]["best_for"]
    assert "Decodificadores Qwen3.5" in cat["jev"]["available"][0]["guide"]["summary"]
    assert "winnow:e4b" in cat["jev"]["guide"]["choosing"][0] and "ollaya-dev/ollaya" in cat["jev"]["guide"]["source"]
    assert "acm_decide" in cat["usage"]["jev"] and "acm_chat" in cat["usage"]["ollama"]
    assert set(cat["purposes"]) >= {"agile.story_review", "agile.sprint_review", "agent.chat"}
    assert denied.is_error and "FORBIDDEN" in denied.content[0].text


@pytest.mark.anyio
async def test_us5010_ca03_modelo_concreto_y_caida_indicada(
    service: ProjectService, ollaya: FakeOllaya, ollama: FakeOllama
) -> None:
    router = _router(service, **_both(ollaya, ollama, jev_model="laya", ollama_model="qwen2.5:0.5b"))
    _decide(router, "x")  # registra un propósito de agente
    async with Client(build_mcp_server(service, lambda: ADMIN, engines=router)) as agent:
        args = {"project_id": P, "purpose": "ticket.triage", "questions": Q, "state": "texto"}
        chosen = (await agent.call_tool("acm_decide", args | {"model": "decider"})).structured_content
        missing = (await agent.call_tool("acm_decide", args | {"model": "kev"})).structured_content
        cat = (await agent.call_tool("acm_models_list", {})).structured_content
    assert chosen["engine"] == "jev:decider" and chosen["fallback_from"] is None
    assert missing["engine"] == "ollama-decide:qwen2.5:0.5b" and missing["fallback_from"] == "jev:laya"
    assert "ticket.triage" in cat["seen_purposes"] and "x" in cat["seen_purposes"]


# ---------------------------------------------------------------- US-22.10 hilo conservado
def test_us2210_ca01_ca02_hilo_con_contexto(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    chat = ChatService(service, BacklogService(service, router), router)
    ollama.state.reply = "Hola, ¿en qué te ayudo?"
    first = chat.send(ADMIN, P, "Hola")
    assert (first["thread_id"], first["reply"], first["model"], first["context_messages"]) == (
        "TH-001",
        "Hola, ¿en qué te ayudo?",
        "qwen2.5:0.5b",
        0,
    )
    ollama.state.reply = "Seguimos."
    second = chat.send(ADMIN, P, "¿Qué te dije?", first["thread_id"])
    sent = ollama.state.requests[-1]["body"]["messages"]
    assert [m["role"] for m in sent] == ["system", "user", "assistant", "user"]
    assert sent[1]["content"] == "Hola" and sent[2]["content"] == "Hola, ¿en qué te ayudo?"
    assert second["context_messages"] == 2 and second["thread_id"] == "TH-001"


def test_us2210_ca03_hilo_privado(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    from tests.conftest import add_member

    add_member(service.data_dir, P, "bea", "member")
    chat = ChatService(service, BacklogService(service, router), router)
    mine = chat.send("bea", P, "Mi hilo")["thread_id"]
    admin = chat.send(ADMIN, P, "Hilo del admin")["thread_id"]
    assert [t["id"] for t in chat.threads("bea", P)["threads"]] == [mine]
    assert {t["id"] for t in chat.threads(ADMIN, P)["threads"]} == {mine, admin}  # un admin ve todos
    with pytest.raises(NotFound):
        chat.get("bea", P, admin)
    with pytest.raises(NotFound):
        chat.send("bea", P, "intruso", admin)


def test_us2210_ca04_mensajes_conservados(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    chat = ChatService(service, BacklogService(service, router), router)
    tid = chat.send(ADMIN, P, "Uno", title="Revisión")["thread_id"]
    thread = chat.get(ADMIN, P, tid)
    assert thread["title"] == "Revisión" and [m["role"] for m in thread["messages"]] == ["user", "assistant"]
    assert thread["messages"][0]["principal"] == ADMIN and thread["messages"][1]["model"] == "qwen2.5:0.5b"
    for i in range(HISTORY_MAX):
        chat.send(ADMIN, P, f"m{i}", tid)
    sent = ollama.state.requests[-1]["body"]["messages"]
    assert len(sent) == 1 + HISTORY_MAX + 1  # system + últimos HISTORY_MAX + el nuevo: el hilo no crece sin límite


def test_us2210_ca05_sin_modelo_error_explicito(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service)
    chat = ChatService(service, BacklogService(service, router), router)
    with pytest.raises(EngineUnavailable, match="no hay un Ollama configurado"):
        chat.send(ADMIN, P, "Hola")
    router2 = build_engines(service, Settings(data_dir=service.data_dir, ollama_url=ollama.url))
    with pytest.raises(EngineUnavailable, match="no hay modelo de Ollama seleccionado"):
        ChatService(service, BacklogService(service, router2), router2).send(ADMIN, P, "Hola")
    assert chat.threads(ADMIN, P)["threads"] == []  # un fallo no deja hilos a medias


# ---------------------------------------------------------------- US-22.11 agente interno con herramientas
def test_us2211_ca01_ca02_consulta_el_proyecto_con_herramientas(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    _seed(service, router)
    ollama.state.script = [
        {"tool_calls": [{"function": {"name": "backlog_overview", "arguments": {}}}]},
        {"tool_calls": [{"function": {"name": "get_story", "arguments": '{"story_id": "US-01.01"}'}}]},
        {"content": "US-01.01 (crear proyectos) está PLANNED y tiene 1 criterio."},
    ]
    out = ChatService(service, BacklogService(service, router), router).send(ADMIN, P, "¿Cómo va US-01.01?")
    assert out["reply"].startswith("US-01.01 (crear proyectos)")
    assert [(c["name"], c["ok"]) for c in out["tool_calls"]] == [("backlog_overview", True), ("get_story", True)]
    first = ollama.state.requests[-3]["body"]
    assert {t["function"]["name"] for t in first["tools"]} == TOOL_NAMES
    assert "No inventes datos" in first["messages"][0]["content"] and "US-NN.MM" in first["messages"][0]["content"]
    last = ollama.state.requests[-1]["body"]["messages"]
    tool_msgs = [m for m in last if m["role"] == "tool"]
    assert [m["tool_name"] for m in tool_msgs] == ["backlog_overview", "get_story"]
    assert json.loads(tool_msgs[1]["content"])["acceptance_criteria"] == [
        {"code": "CA-01", "text": "Nombre vacío rechazado"}
    ]
    assert not TOOL_NAMES & {"set_status", "create_story", "add_criteria", "mark_ready"}  # nunca escritura


def test_us2211_ca02_permisos_de_quien_pregunta(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    service.create(ADMIN, "beta", "Beta")
    from tests.conftest import add_member

    add_member(service.data_dir, P, "bea", "member")
    ollama.state.script = [
        {"tool_calls": [{"function": {"name": "get_story", "arguments": {"story_id": "US-09.09"}}}]},
        {"content": "No existe."},
    ]
    out = ChatService(service, BacklogService(service, router), router).send("bea", P, "¿Y US-09.09?")
    assert out["tool_calls"] == [{"name": "get_story", "arguments": {"story_id": "US-09.09"}, "ok": False}]
    tool = next(m for m in ollama.state.requests[-1]["body"]["messages"] if m["role"] == "tool")
    assert "NOT_FOUND" in tool["content"]
    with pytest.raises(NotFound):  # bea no ve el proyecto beta: ni siquiera puede abrir un hilo allí
        ChatService(service, BacklogService(service, router), router).send("bea", "beta", "hola")


def test_us2211_ca03_herramientas_en_el_hilo(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    _seed(service, router)
    ollama.state.script = [
        {"tool_calls": [{"function": {"name": "list_sprints", "arguments": {}}}]},
        {"content": "No hay sprints."},
    ]
    chat = ChatService(service, BacklogService(service, router), router)
    tid = chat.send(ADMIN, P, "¿Sprints?")["thread_id"]
    roles = [(m["role"], m["tool_name"]) for m in chat.get(ADMIN, P, tid)["messages"]]
    assert roles == [("user", ""), ("assistant", ""), ("tool", "list_sprints"), ("assistant", "")]
    assert chat.get(ADMIN, P, tid)["messages"][1]["tool_calls"][0]["function"]["name"] == "list_sprints"


def test_us2211_ca04_rondas_limitadas(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    call = {"tool_calls": [{"function": {"name": "backlog_overview", "arguments": {}}}]}
    ollama.state.script = [call] * (MAX_TOOL_ROUNDS + 3)
    ollama.state.reply = "Respuesta final sin herramientas."
    out = ChatService(service, BacklogService(service, router), router).send(ADMIN, P, "bucle")
    assert len(out["tool_calls"]) == MAX_TOOL_ROUNDS and out["reply"] == "Respuesta final sin herramientas."
    assert "tools" not in ollama.state.requests[-1]["body"]  # la última ronda no ofrece herramientas


@pytest.mark.anyio
async def test_us2210_por_mcp(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    async with Client(build_mcp_server(service, lambda: ADMIN, engines=router)) as agent:
        first = (await agent.call_tool("acm_chat", {"project_id": P, "message": "Hola"})).structured_content
        await agent.call_tool("acm_chat", {"project_id": P, "message": "Sigue", "thread_id": first["thread_id"]})
        threads = (await agent.call_tool("acm_chat_threads", {"project_id": P})).structured_content
        thread = (
            await agent.call_tool("acm_chat_get", {"project_id": P, "thread_id": first["thread_id"]})
        ).structured_content
    assert threads["threads"][0]["messages"] == 4 and len(thread["messages"]) == 4


def test_us2211_ca04_modelo_que_insiste_en_herramientas_es_error(service: ProjectService, ollama: FakeOllama) -> None:
    router = _router(service, ollama_url=ollama.url, ollama_model="qwen2.5:0.5b")
    call = {"tool_calls": [{"function": {"name": "backlog_overview", "arguments": {}}}]}
    ollama.state.script, ollama.state.script_always = [call] * (MAX_TOOL_ROUNDS + 1), True
    chat = ChatService(service, BacklogService(service, router), router)
    with pytest.raises(EngineError, match="no devolvió una respuesta completa"):
        chat.send(ADMIN, P, "bucle sin fin")
    assert chat.threads(ADMIN, P)["threads"] == []  # nunca se guarda una respuesta vacía como si fuera válida
