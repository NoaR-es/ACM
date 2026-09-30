from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from acm.domain.projects import ProjectService

ADMIN = "local-admin"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def service(data_dir: Path) -> Iterator[ProjectService]:
    svc = ProjectService(data_dir)
    svc.ensure_principal(ADMIN, "admin")
    yield svc
    svc.close()


def add_member(data_dir: Path, project_id: str, principal_id: str, role: str = "member") -> None:
    """Fixture de datos: da de alta una pertenencia directamente en SQLite.

    La gestión de miembros es EPIC-20 (fuera de SPRINT-001); los tests la necesitan para verificar el filtrado
    por acceso de US-01.02 CA-01.
    """
    conn = sqlite3.connect(data_dir / "acm.db")
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO principals(id, role, created_at) VALUES (?, 'user', ?)",
            (principal_id, datetime.now(UTC).isoformat()),
        )
        conn.execute(
            "INSERT INTO project_members(project_id, principal_id, role, added_at) VALUES (?, ?, ?, ?)",
            (project_id, principal_id, role, datetime.now(UTC).isoformat()),
        )
    conn.close()
