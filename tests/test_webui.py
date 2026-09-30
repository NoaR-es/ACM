"""SPRINT-007 — interfaz web (e2e con Chromium contra ACM real): US-31.06/07/08, US-06.06/07, US-31.01/02/04,
US-21.09, US-45.02/03, US-01.02 CA-03.

Requiere Playwright y Chromium. Localmente usa `/opt/pw-browsers/chromium` si existe. En CI (`ACM_E2E_REQUIRED=1`)
un entorno sin navegador hace fallar la suite en lugar de saltarse estos tests.
"""

from __future__ import annotations

import os
import re
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from acm.domain.backlog import BacklogService
from acm.webui_app import webui_available
from tests.live import ADMIN, Acm

try:
    from playwright.sync_api import Browser, Page, WebSocketRoute, expect, sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore[assignment]

REQUIRED = os.environ.get("ACM_E2E_REQUIRED") == "1"
LOCAL_CHROMIUM = Path("/opt/pw-browsers/chromium")


def _unavailable(reason: str) -> None:
    if REQUIRED:
        pytest.fail(f"e2e obligatorio pero no disponible: {reason}")
    pytest.skip(reason)


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    if sync_playwright is None:
        _unavailable("playwright no instalado")
    if not webui_available():
        _unavailable("interfaz no compilada: npm run build en web/")
    with sync_playwright() as p:
        kwargs = {"executable_path": str(LOCAL_CHROMIUM)} if LOCAL_CHROMIUM.exists() else {}
        b = p.chromium.launch(**kwargs)
        yield b
        b.close()


def seed(acm: Acm) -> None:
    for pid, name in (("alpha", "Plataforma Alpha"), ("beta", "App móvil Beta")):
        acm.service.create(ADMIN, pid, name, f"Proyecto {name}")
        b = BacklogService(acm.service)
        b.create_requirement(ADMIN, pid, "Gestionar proyectos", "Descripción del requisito")
        b.create_requirement(ADMIN, pid, "Requisito huérfano")
        b.create_epic(ADMIN, pid, "Proyectos", "Gestionar el ciclo de vida", "Crear y abrir", ["REQ-001"])
        b.create_feature(ADMIN, pid, "EPIC-01", "Creación", "Alta de proyectos")
        b.create_story(
            ADMIN,
            pid,
            "FEAT-01.01",
            "operador",
            "crear proyectos",
            "separar contextos",
            ["REQ-001"],
            ["Un nombre vacío se rechaza", "Un duplicado no se crea"],
        )
        b.create_story(ADMIN, pid, "FEAT-01.01", "operador", "abrir proyectos", "trabajar", ["REQ-001"], ["Abre"])
        b.create_story(ADMIN, pid, "FEAT-01.01", "operador", "exportar informes", "compartir", ["REQ-001"])
        b.mark_ready(ADMIN, pid, "US-01.01")
        b.set_status(ADMIN, pid, "US-01.01", "IN_PROGRESS")
        b.mark_ready(ADMIN, pid, "US-01.02")


@pytest.fixture
def ui(acm: Acm, browser: Browser) -> Iterator[tuple[Acm, Page]]:
    seed(acm)
    page = login(acm, browser, acm.token(ADMIN))
    yield acm, page
    page.context.close()


def login(acm: Acm, browser: Browser, token: str, **context: object) -> Page:
    page = browser.new_context(viewport={"width": 1600, "height": 1000}, **context).new_page()
    page.goto(f"{acm.url}/")
    page.fill("#token", token)
    page.click("button[type=submit]")
    expect(page.locator("[data-live=live]")).to_be_visible(timeout=10_000)
    return page


def go(page: Page, acm: Acm, route: str) -> None:
    page.goto(f"{acm.url}/#{route}")


def in_thread(fn) -> None:  # noqa: ANN001
    """Ejecuta un agente MCP async en otro hilo: el hilo del test ya tiene el bucle de Playwright."""
    import threading

    import anyio

    errors: list[BaseException] = []

    def run() -> None:
        try:
            anyio.run(fn)
        except BaseException as exc:  # noqa: BLE001 — se re-lanza en el hilo del test
            errors.append(exc)

    t = threading.Thread(target=run)
    t.start()
    t.join(timeout=60)
    if errors:
        raise errors[0]


def card(page: Page, project: str, story: str):
    return page.locator(f'[data-card="{project}/{story}"]')


# ---------------------------------------------------------------- US-31.06 — revisar todo desde la interfaz
def test_us3106_ca01_cada_dato_tiene_vista(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha")
    expect(page.locator(".stats")).to_contain_text("Requisitos")
    expect(page.get_by_text("Requisitos sin historias:")).to_be_visible()  # huecos de trazabilidad
    views = {
        "backlog": ["EPIC-01", "FEAT-01.01", "US-01.01", "Gestionar el ciclo de vida"],
        "requirements": ["REQ-001", "Gestionar proyectos", "REQ-002"],
        "stories": ["crear proyectos", "exportar informes", "En curso"],
        "governance": ["Estado de gobernanza", "Histórico de auditorías"],
        "members": [ADMIN, "owner"],
        "config": ["context.max_tokens", "decision.engine_order"],
    }
    for tab, texts in views.items():
        go(page, acm, f"/p/alpha/{tab}")
        for text in texts:
            expect(page.locator("main")).to_contain_text(text)
    go(page, acm, "/p/alpha/requirements")
    page.get_by_role("button", name="Ver traza").first.click()
    expect(page.locator(".trace")).to_contain_text("EPIC-01")


def test_us3106_ca02_navegar_desde_una_historia(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/alpha/s/US-01.01")
    main = page.locator("main")
    for text in (
        "Como operador, quiero crear proyectos",
        "CA-01",
        "Un duplicado no se crea",
        "REQ-001",
        "EPIC-01 — Proyectos",
        "FEAT-01.01 — Creación",
        "Historial de estados",
    ):
        expect(main).to_contain_text(text)
    page.locator(".breadcrumb").get_by_role("link", name="EPIC-01").click()
    expect(page).to_have_url(re.compile(r"#/p/alpha/backlog$"))


def test_us3106_ca03_documentacion_de_acm(ui) -> None:
    acm, page = ui
    go(page, acm, "/docs")
    expect(page.locator(".markdown h1")).to_have_text("ACM — modelo y herramientas")
    expect(page.locator(".markdown")).to_contain_text("acm_story_set_status")
    page.get_by_role("button", name=re.compile("acm-invest")).click()
    expect(page.locator(".markdown")).to_contain_text("INVEST")
    expect(page.get_by_text("Flujo de estados de las historias")).to_be_visible()
    expect(page.locator("main")).to_contain_text("/api/v1/kanban")
    expect(page.locator("main")).to_contain_text("Tablero Kanban de uno o varios proyectos")


def test_us3106_ca04_solo_lo_accesible(acm: Acm, browser: Browser) -> None:
    seed(acm)
    acm.identity.create_principal(ADMIN, "ana", "user")
    acm.identity.set_member(ADMIN, "alpha", "ana", "member")
    page = login(acm, browser, acm.token("ana"))
    try:
        expect(page.locator("[data-project=alpha]")).to_be_visible()
        expect(page.locator("[data-project=beta]")).to_have_count(0)
        expect(page.get_by_role("link", name="Actividad")).to_have_count(0)  # vistas de admin ocultas
        go(page, acm, "/p/beta")
        expect(page.get_by_role("alert")).to_contain_text("NOT_FOUND")
    finally:
        page.context.close()


# ---------------------------------------------------------------- US-31.07 — legible y con contraste
CONTRAST_JS = """
() => {
  const parse = (c) => c.match(/[\\d.]+/g).slice(0, 3).map(Number);
  const ch = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const lum = ([r, g, b]) => 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b);
  const bgOf = (el) => {
    while (el) {
      const c = getComputedStyle(el).backgroundColor;
      if (c && !c.endsWith(', 0)') && c !== 'transparent') return c;
      el = el.parentElement;
    }
    return 'rgb(255,255,255)';
  };
  const sel = '.badge, .chip, .column-head, .card-title, .card-meta, h1, .muted, a, button, td, th';
  const out = [];
  for (const el of document.querySelectorAll(sel)) {
    if (!el.offsetParent || !el.textContent.trim()) continue;
    const [a, b] = [lum(parse(getComputedStyle(el).color)), lum(parse(bgOf(el)))].sort((x, y) => y - x);
    out.push({ text: el.textContent.trim().slice(0, 30), ratio: (a + 0.05) / (b + 0.05) });
  }
  return out;
}
"""


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_us3107_ca01_contraste_aa_en_ambos_temas(acm: Acm, browser: Browser, scheme: str) -> None:
    seed(acm)
    page = login(acm, browser, acm.token(ADMIN), color_scheme=scheme)
    try:
        for route in ("/kanban", "/", "/p/alpha/governance", "/p/alpha/stories"):
            go(page, acm, route)
            page.wait_for_selector("main table, main [data-card], main .project-card", timeout=10_000)
            expect(page.locator("html")).to_have_attribute("data-theme", scheme)
            ratios = page.evaluate(CONTRAST_JS)
            assert len(ratios) > 10, route
            low = [r for r in ratios if r["ratio"] < 4.5]
            assert not low, f"{scheme} {route}: {low[:5]}"
    finally:
        page.context.close()


def test_us3107_ca02_nunca_solo_color(ui) -> None:
    acm, page = ui
    go(page, acm, "/")
    for badge in page.locator(".semaphore").all():
        assert re.search(r"(Verde|Ámbar|Rojo|Sin auditar)", badge.inner_text())
    expect(page.locator("[data-live]")).to_contain_text("En vivo")
    go(page, acm, "/kanban")
    for head in page.locator(".column-head").all():
        assert head.inner_text().strip()
    for chip in page.locator("[data-card] .chip").all():
        assert chip.inner_text() in ("alpha", "beta")


def test_us3107_ca03_elegir_tema(ui) -> None:
    acm, page = ui
    select = page.get_by_label("Tema de color")
    select.select_option("dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    dark_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    select.select_option("light")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") != dark_bg
    select.select_option("dark")
    page.reload()
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")  # la preferencia se recuerda


def test_us3107_ca04_mover_con_teclado(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban?projects=alpha")
    mover = page.get_by_label("Mover alpha US-01.02 a")
    mover.focus()
    page.keyboard.press("ArrowDown")  # primera opción: En curso
    expect(page.locator('[data-column=IN_PROGRESS] [data-card="alpha/US-01.02"]')).to_be_visible()
    assert BacklogService(acm.service).get_story(ADMIN, "alpha", "US-01.02")["status"] == "IN_PROGRESS"
    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement.tagName")
    assert focused in ("A", "SELECT", "BUTTON", "INPUT")


# ---------------------------------------------------------------- US-31.08 — tiempo real en la interfaz
def test_us3108_ca01_cambio_de_agente_sin_recargar(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban")
    expect(card(page, "beta", "US-01.02")).to_have_attribute("data-status", "READY")
    page.evaluate("window.__noReload = true")
    BacklogService(acm.service).set_status(ADMIN, "beta", "US-01.02", "IN_PROGRESS", "lo coge un agente")
    moved = page.locator('[data-column=IN_PROGRESS] [data-card="beta/US-01.02"]')
    expect(moved).to_be_visible(timeout=5_000)
    expect(moved.locator(".live-tag")).to_have_text("actualizada")
    assert page.evaluate("window.__noReload") is True  # la página no se recargó
    go(page, acm, "/p/beta/s/US-01.02")
    BacklogService(acm.service).set_status(ADMIN, "beta", "US-01.02", "IMPLEMENTED")
    expect(page.locator("h1 .badge")).to_have_text("Implementada", timeout=5_000)


def test_us3108_ca02_indicador_de_conexion(ui) -> None:
    acm, page = ui
    indicator = page.locator("[data-live]")
    expect(indicator).to_have_attribute("data-live", "live")
    expect(indicator).to_have_text(re.compile("En vivo"))


def test_us3108_ca03_reconexion_recupera_los_cambios(acm: Acm, browser: Browser) -> None:
    seed(acm)
    routes: list[WebSocketRoute] = []
    context = browser.new_context(viewport={"width": 1600, "height": 1000})

    def through(ws: WebSocketRoute) -> None:
        ws.connect_to_server()
        routes.append(ws)

    context.route_web_socket(re.compile(r".*/api/v1/ws$"), through)
    page = context.new_page()
    try:
        page.goto(f"{acm.url}/")
        page.fill("#token", acm.token(ADMIN))
        page.click("button[type=submit]")
        expect(page.locator("[data-live=live]")).to_be_visible(timeout=10_000)
        go(page, acm, "/kanban")
        expect(card(page, "alpha", "US-01.02")).to_have_attribute("data-status", "READY")
        routes[-1].close()  # se corta la conexión
        expect(page.locator("[data-live]")).not_to_have_attribute("data-live", "live", timeout=5_000)
        BacklogService(acm.service).set_status(ADMIN, "alpha", "US-01.02", "IN_PROGRESS")  # ocurre desconectado
        expect(page.locator("[data-live=live]")).to_be_visible(timeout=15_000)  # se reconecta sola
        expect(page.locator('[data-column=IN_PROGRESS] [data-card="alpha/US-01.02"]')).to_be_visible(timeout=5_000)
        assert len(routes) >= 2
    finally:
        context.close()


# ---------------------------------------------------------------- US-06.07 — Kanban multiproyecto
def test_us0607_ca01_elegir_proyectos(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban")
    expect(page.locator("[data-card]")).to_have_count(6)
    beta = page.get_by_role("checkbox", name="beta")
    beta.click()  # casilla controlada por la URL: se comprueba el resultado, no el clic
    expect(beta).not_to_be_checked()
    expect(page).to_have_url(re.compile(r"projects=alpha"))
    expect(page.locator('[data-card^="beta/"]')).to_have_count(0)
    expect(page.locator('[data-card^="alpha/"]')).to_have_count(3)
    page.get_by_role("button", name="Todos").click()
    expect(page.locator("[data-card]")).to_have_count(6)


def test_us0607_ca02_color_y_nombre_del_proyecto(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban")
    alpha, beta = card(page, "alpha", "US-01.01"), card(page, "beta", "US-01.01")
    expect(alpha.locator(".chip")).to_have_text("alpha")
    expect(beta.locator(".chip")).to_have_text("beta")
    color = "getComputedStyle(arguments[0] || el).borderLeftColor"
    a = alpha.evaluate("el => getComputedStyle(el).borderLeftColor")
    b = beta.evaluate("el => getComputedStyle(el).borderLeftColor")
    assert a != b and color


def test_us0607_ca03_mezclados_o_por_carril(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban")
    expect(page.get_by_test_id("board-all")).to_be_visible()
    page.get_by_label("Vista").select_option("swimlanes")
    expect(page.get_by_test_id("board-alpha")).to_be_visible()
    expect(page.get_by_test_id("board-beta")).to_be_visible()
    expect(page.get_by_test_id("board-alpha").locator('[data-card^="beta/"]')).to_have_count(0)


def test_us0607_ca04_arrastrar_permitido_y_rechazo(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban?projects=alpha")
    backlog = BacklogService(acm.service)
    card(page, "alpha", "US-01.01").drag_to(page.locator("[data-column=IMPLEMENTED]"))
    expect(page.locator('[data-column=IMPLEMENTED] [data-card="alpha/US-01.01"]')).to_be_visible(timeout=5_000)
    assert backlog.get_story(ADMIN, "alpha", "US-01.01")["status"] == "IMPLEMENTED"
    card(page, "alpha", "US-01.02").drag_to(page.locator("[data-column=TESTING]"))  # READY → TESTING no permitido
    expect(page.locator(".flash.error")).to_contain_text("no está permitido")
    assert backlog.get_story(ADMIN, "alpha", "US-01.02")["status"] == "READY"


# ---------------------------------------------------------------- US-06.06 — abrir una tarjeta
def test_us0606_ca01_ca02_ca03_abrir_tarjeta_con_contexto(ui) -> None:
    acm, page = ui
    go(page, acm, "/kanban?projects=alpha")
    card(page, "alpha", "US-01.01").get_by_role("link", name="US-01.01").click()
    expect(page).to_have_url(re.compile(r"#/p/alpha/s/US-01.01$"))
    for text in ("Un nombre vacío se rechaza", "REQ-001", "EPIC-01", "FEAT-01.01", "Planificada"):
        expect(page.locator("main")).to_contain_text(text)
    page.get_by_role("button", name="Generar").click()
    expect(page.locator("main")).to_contain_text("chars/4@v1")
    expect(page.locator("main")).to_contain_text("tokens frente a")


# ---------------------------------------------------------------- US-31.01/02/04, US-21.09 — actividad
def test_us3104_us2109_feed_en_vivo_de_herramientas(ui) -> None:
    acm, page = ui
    go(page, acm, "/activity")
    expect(page.get_by_text("Esperando actividad…")).to_be_visible()
    from tests.live import mcp

    async def agent() -> None:
        async with mcp(acm, acm.token(ADMIN)) as client:
            await client.call_tool("acm_backlog_audit", {"project_id": "alpha"})
            await client.call_tool(
                "acm_story_set_status", {"project_id": "alpha", "story_id": "US-01.01", "status": "DONE"}
            )

    in_thread(agent)
    feed = page.locator(".feed").first
    expect(feed).to_contain_text("acm_backlog_audit", timeout=5_000)
    expect(feed).to_contain_text("alpha")
    expect(feed.locator("li.is-error")).to_contain_text("acm_story_set_status")  # CA: el error se distingue


def test_us3101_us3102_consola_filtrable(ui) -> None:
    acm, page = ui
    BacklogService(acm.service)  # datos creados por el seed (dominio, sin auditar)
    from tests.live import mcp

    async def calls() -> None:
        async with mcp(acm, acm.token(ADMIN)) as client:
            await client.call_tool("acm_project_list", {})
            await client.call_tool("acm_backlog_audit", {"project_id": "beta"})
            await client.call_tool(
                "acm_story_set_status", {"project_id": "beta", "story_id": "US-01.02", "status": "DONE"}
            )

    in_thread(calls)
    go(page, acm, "/activity")
    rows = page.locator("table tbody tr")
    expect(rows.first).to_be_visible()
    total = rows.count()
    assert total >= 3 and re.search(r"\d{2}:\d{2}:\d{2}", rows.first.inner_text())  # CA-02: timestamp
    page.get_by_label("Proyecto").fill("beta")
    expect(rows).to_have_count(2)
    for row in rows.all():
        assert "beta" in row.inner_text()
    page.get_by_label("Solo errores").check()
    expect(rows).to_have_count(1)
    expect(rows.first).to_have_class(re.compile("is-error"))
    page.get_by_role("button", name="Limpiar filtros").click()
    expect(rows).to_have_count(total)
    page.get_by_role("textbox", name="Principal").fill("nadie")  # CA-03: filtro por agente/principal
    expect(rows).to_have_count(0)
    expect(page.get_by_text("Ningún resultado con estos filtros.")).to_be_visible()
    page.get_by_role("textbox", name="Principal").fill(ADMIN)
    expect(rows).to_have_count(total)


# ---------------------------------------------------------------- US-45.02/03, US-01.02 CA-03
def test_us4503_panel_global_de_varios_proyectos(ui) -> None:
    acm, page = ui
    go(page, acm, "/")
    for pid in ("alpha", "beta"):
        project = page.locator(f"[data-project={pid}]")
        expect(project.locator(".semaphore")).to_be_visible()
        expect(project.locator(".statusbar")).to_have_attribute("aria-label", re.compile("En curso: 1"))
    BacklogService(acm.service).set_status(ADMIN, "beta", "US-01.02", "IN_PROGRESS")
    feed = page.get_by_role("region", name="Cambios en tiempo real")
    expect(feed).to_contain_text("US-01.02", timeout=5_000)
    expect(feed).to_contain_text("IN_PROGRESS")
    page.get_by_role("link", name="Kanban de todos").click()
    expect(page.locator("[data-card]")).to_have_count(6)


def test_us4502_acceder_a_elementos_desde_el_panel(ui) -> None:
    acm, page = ui
    go(page, acm, "/")
    page.locator("[data-project=alpha]").get_by_role("link", name="Plataforma Alpha").click()
    expect(page.locator("h1")).to_contain_text("Plataforma Alpha")
    go(page, acm, "/")
    BacklogService(acm.service).set_status(ADMIN, "alpha", "US-01.02", "IN_PROGRESS")
    page.get_by_role("region", name="Cambios en tiempo real").get_by_role("link", name="US-01.02").click()
    expect(page.locator(".breadcrumb")).to_contain_text("alpha")  # se conserva el contexto del proyecto
    go(page, acm, "/p/alpha/s/US-01.99")
    expect(page.get_by_role("alert")).to_contain_text("NOT_FOUND")


def test_us0102_ca03_proyecto_activo_identificado(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/beta/backlog")
    expect(page.locator("h1")).to_contain_text("App móvil Beta")
    expect(page.locator(".breadcrumb")).to_contain_text("beta")
    active = page.get_by_role("navigation", name="Secciones del proyecto").locator("[aria-current=page]")
    expect(active).to_have_text("Backlog")


def test_us0102_ca04_proyecto_inexistente_informa_y_no_queda_seleccionado(ui) -> None:
    acm, page = ui
    go(page, acm, "/p/fantasma/backlog")
    expect(page.get_by_role("alert")).to_contain_text("NOT_FOUND")
    expect(page.get_by_role("navigation", name="Secciones del proyecto")).to_have_count(0)
    expect(page.locator(".breadcrumb")).to_have_count(0)


def test_ui_sin_errores_de_consola_y_cabeceras_de_seguridad(ui) -> None:
    acm, page = ui
    errors: list[str] = []
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.on("pageerror", lambda e: errors.append(str(e)))
    for route in (
        "/",
        "/kanban",
        "/p/alpha",
        "/p/alpha/backlog",
        "/p/alpha/s/US-01.01",
        "/docs",
        "/activity",
        "/system",
    ):
        go(page, acm, route)
        page.wait_for_load_state("networkidle")
        time.sleep(0.2)
    assert errors == []
    response = page.request.get(f"{acm.url}/")
    csp = response.headers["content-security-policy"]
    assert "script-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert response.headers["x-content-type-options"] == "nosniff"
