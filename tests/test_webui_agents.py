"""SPRINT-009 — la interfaz para los agentes (e2e con Chromium contra ACM real): entrada local sin token (US-14.12
CA-04), aprobación de peticiones de acceso (US-14.15) y trabajo asignado visible en el Kanban (US-14.17 CA-03)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from acm.domain.access import AccessService
from acm.domain.backlog import BacklogService
from acm.domain.identity import IdentityService
from acm.domain.sprints import SprintService
from acm.domain.work import WorkService
from tests.live import ADMIN, Acm, running_acm
from tests.test_webui import browser, go, seed  # noqa: F401 — fixture `browser` reutilizada

try:
    from playwright.sync_api import Browser, Page, expect
except ImportError:  # pragma: no cover
    pass

A, B = "claude-code.portatil", "cursor.portatil"


@pytest.fixture
def local_ui(tmp_path: Path, browser: Browser) -> Iterator[tuple[Acm, Page]]:  # noqa: F811
    """ACM en modo local (como `acm serve --local`) y un navegador que NO tiene ningún token."""
    with running_acm(tmp_path / "data", local_mode=True) as acm:
        for agent in (A, B):
            acm.service.ensure_principal(agent, "user", "agent")
        seed(acm)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        yield acm, context.new_page()
        context.close()


# ---------------------------------------------------------------- US-14.12 CA-04 — sin pegar token
def test_us1412_ca04_la_interfaz_local_entra_sola(local_ui) -> None:
    acm, page = local_ui
    page.goto(f"{acm.url}/")
    expect(page.get_by_role("heading", name="Panel")).to_be_visible(timeout=10_000)
    expect(page.locator("#token")).to_have_count(0)  # no hay pantalla de acceso
    expect(page.locator("[data-live=live]")).to_be_visible()
    expect(page.locator("[data-project=alpha]")).to_be_visible()
    page.get_by_role("button", name="Salir").click()  # salir a propósito no vuelve a entrar solo
    expect(page.locator("#token")).to_be_visible()
    page.reload()
    expect(page.locator("#token")).to_be_visible()


def test_us1412_ca04_con_tokens_sigue_pidiendolos(acm: Acm, browser: Browser) -> None:  # noqa: F811
    """Un servidor normal (no local) no regala nada: la pantalla de acceso de siempre."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{acm.url}/")
    expect(page.locator("#token")).to_be_visible(timeout=10_000)
    context.close()


# ---------------------------------------------------------------- US-14.15 — aprobar o rechazar desde la interfaz
def test_us1415_ca01_ca02_ca03_aprobar_y_rechazar_en_tiempo_real(local_ui) -> None:
    acm, page = local_ui
    access = AccessService(acm.service)
    page.goto(f"{acm.url}/")
    expect(page.locator("[data-project=alpha]")).to_be_visible(timeout=10_000)
    expect(page.get_by_role("region", name="Solicitudes de acceso")).to_have_count(0)  # sin peticiones, no estorba
    read = access.request_join(A, "alpha", "write", "quiero ayudar con la API")  # llega mientras la página está abierta
    panel = page.get_by_role("region", name="Solicitudes de acceso")
    request = panel.locator(f"[data-request='{read['request_id']}']")
    expect(request).to_contain_text(A)
    expect(request).to_contain_text("alpha")
    expect(request).to_contain_text("pide escritura")
    expect(request).to_contain_text("quiero ayudar con la API")
    request.get_by_role("button", name="Aprobar solo lectura").click()
    expect(panel).to_have_count(0)  # decidida: desaparece
    assert access.join_status(A, "alpha") == {"project_id": "alpha", "status": "MEMBER", "role": "viewer"}
    rejected = access.request_join(B, "beta")
    expect(panel.locator(f"[data-request='{rejected['request_id']}']")).to_be_visible()
    panel.get_by_role("button", name="Rechazar").click()
    expect(panel).to_have_count(0)
    assert access.join_status(B, "beta")["status"] == "REJECTED"  # el agente lo sabe al consultarlo
    approved = access.request_join(B, "alpha", "write")
    panel.locator(f"[data-request='{approved['request_id']}']").get_by_role(
        "button", name="Aprobar con escritura"
    ).click()
    expect(panel).to_have_count(0)
    assert access.join_status(B, "alpha")["role"] == "member"


def test_us1415_ca04_expulsar_a_un_agente_desde_miembros(local_ui) -> None:
    acm, page = local_ui
    access = AccessService(acm.service)
    access.decide(ADMIN, access.request_join(A, "alpha")["request_id"], True)
    go(page, acm, "/p/alpha/members")
    row = page.locator("tr", has_text=A)
    expect(row).to_contain_text("agente")
    expect(row.get_by_label(f"Rol de {A}")).to_have_value("member")
    row.get_by_role("button", name="Retirar").click()
    expect(page.locator("tr", has_text=A)).to_have_count(0)
    assert access.join_status(A, "alpha")["status"] == "REMOVED"


# ---------------------------------------------------------------- US-14.17 CA-03 — quién trabaja en qué
def test_us1417_ca03_el_kanban_muestra_el_agente_asignado(local_ui) -> None:
    acm, page = local_ui
    IdentityService(acm.service).set_member(ADMIN, "alpha", A, "member")
    backlog = BacklogService(acm.service)
    sprints = SprintService(backlog)
    sprints.create(ADMIN, "alpha", "Sprint 1", "Entregar", "2026-10-01", "2026-10-14", None)
    sprints.add_stories(ADMIN, "alpha", "SPRINT-01", ["US-01.02"])
    sprints.start(ADMIN, "alpha", "SPRINT-01")
    work = WorkService(backlog)
    page.goto(f"{acm.url}/#/kanban?projects=alpha")
    expect(page.locator("[data-assigned]")).to_have_count(0)
    claimed = work.next_work(A, "alpha")  # el agente recibe trabajo mientras el tablero está abierto
    card = page.locator(f"[data-assigned='{A}']")
    expect(card).to_be_visible(timeout=10_000)
    expect(card).to_contain_text("Asignada a")
    assert claimed["item"] in page.locator("article, li, div").filter(has=card).first.inner_text()
    work.release(ADMIN, "alpha", claimed["item"])
    expect(page.locator("[data-assigned]")).to_have_count(0, timeout=10_000)
