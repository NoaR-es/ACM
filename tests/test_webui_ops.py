"""SPRINT-008 — operar ACM desde la interfaz (e2e con Chromium contra ACM real): US-31.09..31.12, sprints (US-05.02,
05.03, 05.05, 05.09), supervisor ágil (US-13.14 CA-05, US-13.15 CA-03), modelos (US-50.09) y asistente local
(US-22.10, US-22.11). Los motores de IA son servidores simulados (Ollama, Ollaya) conectados por configuración real.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

from acm.domain.backlog import BacklogService
from tests.fake_ollama import FakeOllama
from tests.fake_ollaya import FakeOllaya
from tests.live import ADMIN, Acm, running_acm
from tests.test_webui import browser, go, login, seed  # noqa: F401 — fixture `browser` reutilizada

try:
    from playwright.sync_api import Browser, Page, expect
except ImportError:  # pragma: no cover
    pass


@pytest.fixture
def ui(acm: Acm, browser: Browser) -> Iterator[tuple[Acm, Page]]:  # noqa: F811
    seed(acm)
    page = login(acm, browser, acm.token(ADMIN))
    yield acm, page
    page.context.close()


@pytest.fixture
def ai(tmp_path: Path, browser: Browser) -> Iterator[tuple[Acm, Page, FakeOllama, FakeOllaya]]:  # noqa: F811
    with FakeOllama() as ollama, FakeOllaya() as ollaya:
        settings = {
            "ollama_url": ollama.url,
            "ollama_model": "qwen2.5:0.5b",
            "jev_url": ollaya.url,
            "jev_model": "laya",
        }
        with running_acm(tmp_path / "data", **settings) as acm:
            seed(acm)
            page = login(acm, browser, acm.token(ADMIN))
            yield acm, page, ollama, ollaya
            page.context.close()


def form(page: Page, name: str):
    return page.get_by_role("form", name=name)


def open_form(page: Page, label: str) -> None:
    page.get_by_role("button", name=f"+ {label}").first.click()


# ---------------------------------------------------------------- US-31.09 proyectos y configuración
def test_us3109_ca01_crear_proyecto_desde_el_panel(ui) -> None:
    acm, page = ui
    go(page, acm, "/")
    open_form(page, "Nuevo proyecto")
    f = form(page, "Nuevo proyecto")
    f.get_by_label("Clave (project_id)").fill("Con Espacios")
    f.get_by_label("Nombre").fill("Gamma")
    f.get_by_role("button", name="Crear proyecto").click()
    expect(f.locator("[data-field=key] .field-error")).to_contain_text("INVALID_ARGUMENT")
    expect(f.get_by_label("Nombre")).to_have_value("Gamma")  # no se pierde lo escrito
    f.get_by_label("Clave (project_id)").fill("alpha")
    f.get_by_role("button", name="Crear proyecto").click()
    expect(f.get_by_role("alert")).to_contain_text("ALREADY_EXISTS")
    f.get_by_label("Clave (project_id)").fill("gamma")
    f.get_by_role("button", name="Crear proyecto").click()
    expect(page.locator("[data-project=gamma]")).to_be_visible()


def test_us3109_ca02_editar_configuracion(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha/config")
    row = page.locator("[data-param='context.max_tokens']")
    row.get_by_role("spinbutton").fill("100")
    row.get_by_role("button", name="Guardar").click()
    expect(row.locator(".field-error")).to_contain_text("256")
    assert acm.service.get_config(ADMIN, "alpha")["parameters"][1]["value"] == 8000  # no se guardó
    mode = page.locator("[data-param='supervisor.mode']")
    mode.get_by_role("combobox").select_option("propose")
    mode.get_by_role("button", name="Guardar").click()
    expect(mode.get_by_role("button", name="Guardar")).to_be_disabled()  # guardado: el valor mostrado es el nuevo
    expect(mode.get_by_role("combobox")).to_have_value("propose")
    values = {p["key"]: p["value"] for p in acm.service.get_config(ADMIN, "alpha")["parameters"]}
    assert values["supervisor.mode"] == "propose"


def test_us3109_ca03_miembro_no_edita_configuracion(acm: Acm, browser: Browser) -> None:  # noqa: F811
    seed(acm)
    acm.identity.create_principal(ADMIN, "bea", "user")
    acm.identity.set_member(ADMIN, "alpha", "bea", "member")
    page = login(acm, browser, acm.token("bea"))
    go(page, acm, "/p/alpha/config")
    expect(page.get_by_text("Solo el owner del proyecto o un administrador")).to_be_visible()
    expect(page.get_by_role("button", name="Guardar")).to_have_count(0)
    page.context.close()


# ---------------------------------------------------------------- US-31.10 construir el backlog
def test_us3110_ca01_ca04_crear_backlog_desde_la_interfaz(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/beta/backlog")
    open_form(page, "Nuevo requisito")
    f = form(page, "Nuevo requisito")
    f.get_by_label("Título").fill("Exportar datos")
    f.get_by_role("button", name="Crear requisito").click()
    expect(f.get_by_role("status")).to_contain_text("Requisito creado")
    open_form(page, "Nueva épica")
    f = form(page, "Nueva épica")
    f.get_by_label("Título").fill("Exportación")
    f.get_by_label("Objetivo").fill("Sacar datos de ACM")
    f.get_by_label("Alcance").fill("CSV")
    f.get_by_label("REQ-003 Exportar datos").check()
    f.get_by_role("button", name="Crear épica").click()
    expect(page.locator("summary", has_text="EPIC-02")).to_be_visible()
    open_form(page, "Nueva feature en EPIC-02")
    f = form(page, "Nueva feature en EPIC-02")
    f.get_by_label("Título").fill("CSV")
    f.get_by_role("button", name="Crear feature").click()
    expect(page.locator("summary", has_text="FEAT-02.01")).to_be_visible()
    open_form(page, "Nueva historia")
    f = form(page, "Nueva historia")
    f.get_by_label("Feature").select_option("FEAT-02.01")
    f.get_by_label("Como").fill("analista")
    f.get_by_label("Quiero").fill("   ")
    f.get_by_label("Para").fill("analizar")
    f.get_by_label("REQ-003 Exportar datos").check()
    f.get_by_label("Criterios de aceptación (uno por línea)").fill("Descarga un CSV\nIncluye cabecera")
    f.get_by_role("button", name="Crear historia").click()
    expect(f.locator("[data-field=i_want] .field-error")).to_contain_text("es obligatorio")  # CA-04: junto al campo
    expect(f.get_by_label("Para")).to_have_value("analizar")
    f.get_by_label("Quiero").fill("exportar a CSV")
    f.get_by_role("button", name="Crear historia").click()
    expect(page.get_by_role("link", name="US-02.01")).to_be_visible()
    story = BacklogService(acm.service).get_story(ADMIN, "beta", "US-02.01")
    assert [c["text"] for c in story["acceptance_criteria"]] == ["Descarga un CSV", "Incluye cabecera"]


def test_us3110_ca02_anadir_criterios_desde_la_ficha(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha/s/US-01.03")
    open_form(page, "Añadir criterios")
    form(page, "Añadir criterios").get_by_label("Criterios (uno por línea)").fill("Genera un PDF")
    form(page, "Añadir criterios").get_by_role("button", name="Añadir").click()
    expect(page.locator(".criteria")).to_contain_text("CA-01 Genera un PDF")


def test_us3110_ca03_enlazar_confirmar_y_dividir(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha/backlog")
    open_form(page, "Enlazar requisitos a EPIC-01")
    page.get_by_label("REQ-002 Requisito huérfano").check()
    page.get_by_role("button", name="Enlazar", exact=True).click()
    expect(page.locator("summary", has_text="EPIC-01")).to_contain_text("REQ-001, REQ-002")
    page.get_by_role("button", name="Confirmar cobertura de EPIC-01").click()
    expect(page.locator("summary", has_text="EPIC-01")).to_contain_text("cobertura confirmada")
    open_form(page, "Dividir FEAT-01.01")
    f = form(page, "Dividir FEAT-01.01")
    f.get_by_label("Título de la parte 1").fill("Alta")
    f.get_by_label("Título de la parte 2").fill("Resto")
    f.get_by_label("US-01.02 va a la parte").select_option("1")
    f.get_by_label("US-01.03 va a la parte").select_option("1")
    f.get_by_role("button", name="Dividir").click()
    expect(page.get_by_text("dividida en FEAT-01.02,FEAT-01.03")).to_be_visible()


# ---------------------------------------------------------------- US-31.11 acceso
def test_us3111_ca01_ca02_principales_y_miembros(ui) -> None:
    acm, page = ui
    go(page, acm, "/system")
    open_form(page, "Nuevo principal")
    f = form(page, "Nuevo principal")
    f.get_by_label("Identificador").fill("bot-ci")
    f.get_by_role("button", name="Crear principal").click()
    row = page.locator("[data-principal=bot-ci]")
    expect(row).to_contain_text("agente")
    row.get_by_label("Rol global de bot-ci").select_option("admin")
    expect(row.get_by_label("Rol global de bot-ci")).to_have_value("admin")
    assert acm.identity.get_principal(ADMIN, "bot-ci")["role"] == "admin"
    go(page, acm, "/p/alpha/members")
    open_form(page, "Añadir miembro")
    f = form(page, "Añadir miembro")
    f.get_by_label("Principal (usuario o agente)").fill("bot-ci")
    f.get_by_role("button", name="Añadir").click()
    expect(page.get_by_label("Rol de bot-ci")).to_have_value("member")
    page.get_by_label("Rol de bot-ci").select_option("owner")
    expect(page.get_by_label("Rol de bot-ci")).to_have_value("owner")
    page.get_by_role("row", name=re.compile("bot-ci")).get_by_role("button", name="Retirar").click()
    expect(page.get_by_label("Rol de bot-ci")).to_have_count(0)


def test_us3111_ca03_ca04_token_una_vez_y_revocar(ui) -> None:
    acm, page = ui
    acm.identity.create_principal(ADMIN, "bea", "user")
    go(page, acm, "/system")
    open_form(page, "Nuevo token")
    f = form(page, "Nuevo token")
    f.get_by_label("Principal").select_option("bea")
    f.get_by_label("Nombre del token").fill("portátil")
    f.get_by_role("button", name="Crear token").click()
    secret = page.locator("[data-secret]").inner_text()
    assert secret.startswith("acm_")
    expect(page.get_by_text("no se volverá a mostrar")).to_be_visible()
    assert httpx.get(f"{acm.url}/api/v1/me", headers={"Authorization": f"Bearer {secret}"}).status_code == 200
    page.reload()
    expect(page).to_have_url(re.compile("#/system$"))  # BUG-002: recargar una vista de admin no la abandona
    expect(page.locator("[data-secret]")).to_have_count(0)  # no se vuelve a mostrar
    expect(page.get_by_text(secret)).to_have_count(0)
    page.get_by_role("row", name=re.compile("portátil")).get_by_role("button", name="Revocar").click()
    expect(page.get_by_role("row", name=re.compile("portátil"))).to_contain_text("revocado")
    assert httpx.get(f"{acm.url}/api/v1/me", headers={"Authorization": f"Bearer {secret}"}).status_code == 401


# ---------------------------------------------------------------- US-31.12 motores
def test_us3112_ca01_ca02_ca03_motores_desde_la_interfaz(ai) -> None:
    acm, page, _ollama, _ollaya = ai
    go(page, acm, "/system")
    engines = page.get_by_role("region", name="Motores de inferencia")
    page.get_by_role("button", name="Comprobar motores").click()
    for name, kind in (
        ("jev:laya", "decisión"),
        ("ollama:qwen2.5:0.5b", "generación"),
        ("ollama-decide:qwen2.5:0.5b", "decisión"),
    ):
        row = engines.get_by_role("row", name=re.compile(re.escape(name)))
        expect(row).to_contain_text(kind)
        expect(row).to_contain_text("ok")
    go(page, acm, "/p/alpha/config")
    order = page.locator("[data-param='decision.engine_order']")
    order.get_by_role("textbox").fill("jev, rules")
    order.get_by_role("button", name="Guardar").click()
    expect(order.get_by_role("button", name="Guardar")).to_be_disabled()
    expect(order.get_by_role("textbox")).to_have_value("jev, rules")
    values = {p["key"]: p["value"] for p in acm.service.get_config(ADMIN, "alpha")["parameters"]}
    assert values["decision.engine_order"] == ["jev", "rules"]


# ---------------------------------------------------------------- sprints desde la interfaz
def test_us0502_us0505_us0509_us0503_sprint_completo(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha/sprints")
    open_form(page, "Nuevo sprint")
    f = form(page, "Nuevo sprint")
    f.get_by_label("Nombre").fill("Sprint 1")
    f.get_by_label("Objetivo del sprint").fill("Crear y abrir proyectos")
    f.get_by_label("Inicio").fill("2026-10-01")
    f.get_by_label("Fin").fill("2026-10-14")
    f.get_by_label("Capacidad (historias)").fill("1")
    f.get_by_role("button", name="Crear sprint").click()
    sprint = page.locator("[data-sprint=SPRINT-01]")
    expect(sprint).to_contain_text("Planificado")
    sprint.get_by_role("button", name="+ Planificar historias en SPRINT-01").click()
    sprint.get_by_role("checkbox", name=re.compile(r"US-01\.01")).check()
    sprint.get_by_role("checkbox", name=re.compile(r"US-01\.02")).check()
    sprint.get_by_role("button", name="Añadir al sprint").click()
    expect(sprint).to_contain_text("sobrecargado")
    sprint.get_by_role("button", name="Iniciar sprint").click()
    expect(sprint.get_by_role("alert")).to_contain_text("sobrecargado")
    sprint.get_by_role("button", name="Iniciar igualmente (sobrecargado)").click()
    expect(sprint).to_contain_text("Activo")
    expect(sprint.locator("[data-card]")).to_have_count(2)  # tablero del sprint
    sprint.get_by_role("button", name="Cerrar sprint").click()
    expect(sprint).to_contain_text("Cerrado")
    expect(sprint.locator(".report")).to_contain_text("0 de 2 historias terminadas")


# ---------------------------------------------------------------- supervisor ágil en la interfaz
def test_us1314_ca05_us1315_ca03_informe_acciones_y_deshacer(ai) -> None:
    acm, page, _ollama, ollaya = ai
    ollaya.state.answers = {
        "invest": {"type": "noul", "noul": 0.97},
        "criteria_verifiable": {"type": "noul", "noul": 0.97},
        "size": {
            "type": "choice",
            "choice": "small",
            "confidence": 0.95,
            "probabilities": {"small": 0.95, "medium": 0.04, "large": 0.01},
        },
    }
    BacklogService(acm.service).add_criteria(
        ADMIN, "alpha", "US-01.03", ["Genera un PDF"]
    )  # completa: lista para READY
    go(page, acm, "/p/alpha/governance")
    page.get_by_role("button", name="Auditar ahora").click()
    report = page.get_by_role("region", name=re.compile("Informe del supervisor"))
    expect(report).to_contain_text("Pendiente")
    applied = page.get_by_role("region", name=re.compile("Acciones aplicadas por ACM"))
    row = applied.locator("[data-action='story.mark_ready']")
    expect(row).to_contain_text("US-01.03")
    expect(row).to_contain_text("jev:laya")
    assert BacklogService(acm.service).get_story(ADMIN, "alpha", "US-01.03")["status"] == "READY"
    row.get_by_role("button", name="Deshacer").click()
    expect(row).to_contain_text("deshecho")
    assert BacklogService(acm.service).get_story(ADMIN, "alpha", "US-01.03")["status"] == "PLANNED"


# ---------------------------------------------------------------- modelos
def test_us5009_modelos_desde_la_interfaz(ai) -> None:
    acm, page, _ollama, _ollaya = ai
    go(page, acm, "/system")
    jev = page.get_by_role("region", name=re.compile("Ollaya"))
    expect(jev.locator("[data-model='laya:latest']")).to_contain_text("Enrutador")  # guía de uso
    expect(jev.locator("[data-model='decider:latest']")).to_contain_text("Decodificadores Qwen3.5")
    f = form(page, "Elegir modelos de Ollaya")
    f.get_by_label("Modelo para agile.sprint_review").select_option("decider:latest")
    page.get_by_label("Nota de decider:latest").fill("Riesgo de sprint")
    f.get_by_role("button", name="Guardar modelos de Ollaya").click()
    expect(jev.locator("[data-model='decider:latest']")).to_contain_text("agile.sprint_review")
    o = form(page, "Elegir modelo de Ollama")
    o.get_by_label("Modelo de Ollama").select_option("llama3.2:1b")
    o.get_by_role("button", name="Usar este modelo").click()
    expect(page.get_by_role("region", name=re.compile("Ollama"))).to_contain_text("elegido: llama3.2:1b")


# ---------------------------------------------------------------- asistente local
def test_us2210_us2211_asistente_del_proyecto(ai) -> None:
    acm, page, ollama, _ollaya = ai
    ollama.state.script = [
        {"tool_calls": [{"function": {"name": "search_stories", "arguments": {"text": "abrir"}}}]},
        {"content": "**US-01.02** (abrir proyectos) está READY."},
    ]
    go(page, acm, "/p/alpha/assistant")
    page.get_by_role("textbox", name="Mensaje").fill("¿Cómo va abrir proyectos?")
    page.get_by_role("button", name="Enviar").click()
    chat = page.locator(".chat")
    expect(chat).to_contain_text("US-01.02 (abrir proyectos) está READY.")
    expect(chat).to_contain_text("Consulta ACM: search_stories")
    expect(page.get_by_role("button", name=re.compile("TH-001"))).to_be_visible()
    ollama.state.reply = "Sigo en el mismo hilo."
    page.get_by_role("textbox", name="Mensaje").fill("¿Y ahora?")
    page.get_by_role("button", name="Enviar").click()
    expect(chat).to_contain_text("Sigo en el mismo hilo.")
    sent = ollama.state.requests[-1]["body"]["messages"]
    assert any(m["role"] == "tool" for m in sent)  # el hilo conserva también las consultas del agente interno
