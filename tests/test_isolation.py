"""US-24.01 y US-24.03 — varios proyectos con backlog y memoria independientes."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from acm.domain.backlog import BacklogService
from acm.domain.errors import NotFound
from acm.domain.projects import ProjectService
from tests.conftest import ADMIN, add_member


@pytest.fixture
def two(service: ProjectService) -> BacklogService:
    service.create(ADMIN, "alpha", "Alpha")
    service.create(ADMIN, "beta", "Beta")
    return BacklogService(service)


def test_us2401_ca01_multiples_proyectos(service: ProjectService) -> None:
    for key in ("uno", "dos", "tres"):
        service.create(ADMIN, key, key)
    assert [p["project_id"] for p in service.list_for(ADMIN)] == ["dos", "tres", "uno"]


def test_us2401_ca02_backlog_independiente(two: BacklogService) -> None:
    two.create_requirement(ADMIN, "alpha", "Solo alpha")
    two.create_epic(ADMIN, "alpha", "Épica alpha", "o", "s")
    two.create_requirement(ADMIN, "beta", "Solo beta")
    assert [r["title"] for r in two.list_requirements(ADMIN, "alpha")["requirements"]] == ["Solo alpha"]
    assert [r["title"] for r in two.list_requirements(ADMIN, "beta")["requirements"]] == ["Solo beta"]
    assert two.list_epics(ADMIN, "beta")["epics"] == []
    # mismos identificadores en ambos, sin conflicto
    assert two.list_requirements(ADMIN, "beta")["requirements"][0]["id"] == "REQ-001"


def test_us2401_ca03_memoria_independiente(two: BacklogService, data_dir: Path) -> None:
    two.create_requirement(ADMIN, "alpha", "SECRETO-ALPHA")
    a = sqlite3.connect(data_dir / "projects" / "alpha" / "project.db")
    b = sqlite3.connect(data_dir / "projects" / "beta" / "project.db")
    assert a.execute("SELECT COUNT(*) FROM requirements").fetchone()[0] == 1
    assert b.execute("SELECT COUNT(*) FROM requirements").fetchone()[0] == 0
    a.close()
    b.close()
    assert b"SECRETO-ALPHA" not in (data_dir / "projects" / "beta" / "project.db").read_bytes()


def test_us2401_ca04_cambiar_de_proyecto_cambia_contexto(two: BacklogService, service: ProjectService) -> None:
    service.set_config(ADMIN, "alpha", {"context.max_tokens": 1111})
    two.create_epic(ADMIN, "alpha", "Épica alpha", "o", "s")
    ctx_a, ctx_b = service.open(ADMIN, "alpha"), service.open(ADMIN, "beta")
    tokens = {
        c["project_id"]: next(p["value"] for p in c["config"] if p["key"] == "context.max_tokens")
        for c in (ctx_a, ctx_b)
    }
    assert tokens == {"alpha": 1111, "beta": 8000}
    assert [e["title"] for e in two.list_epics(ADMIN, "alpha")["epics"]] == ["Épica alpha"]
    assert two.list_epics(ADMIN, "beta")["epics"] == []


def test_us2403_ca01_agente_de_a_no_recupera_memoria_de_b(two: BacklogService, data_dir: Path) -> None:
    two.create_requirement(ADMIN, "beta", "Privado de beta")
    add_member(data_dir, "alpha", "agente-a")
    assert two.list_requirements("agente-a", "alpha")["requirements"] == []
    for call in (
        lambda: two.list_requirements("agente-a", "beta"),
        lambda: two.get_requirement("agente-a", "beta", "REQ-001"),
        lambda: two.create_requirement("agente-a", "beta", "intrusión"),
    ):
        with pytest.raises(NotFound):
            call()
    assert [r["title"] for r in two.list_requirements(ADMIN, "beta")["requirements"]] == ["Privado de beta"]


def test_us2403_ca03_consultas_limitadas_al_proyecto(two: BacklogService) -> None:
    two.create_epic(ADMIN, "alpha", "A1", "o", "s")
    two.create_epic(ADMIN, "beta", "B1", "o", "s")
    assert [e["title"] for e in two.list_epics(ADMIN, "alpha")["epics"]] == ["A1"]
    assert two.get_epic(ADMIN, "beta", "EPIC-01")["title"] == "B1"  # mismo ID, distinto proyecto
    assert two.audit(ADMIN, "alpha")["epics_without_features"] == ["EPIC-01"]
